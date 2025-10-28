import socket
import threading
import time
import sounddevice as sd
import customtkinter as ctk
import queue
import json
import os
import sys
from vosk import Model, KaldiRecognizer

# ================================================================
# CONFIGURATION
# ================================================================
HOST = "127.0.0.1"
PORT = 6500

KEYWORD_MAP = {
    "fish": "undyne",
    "undyne": "undyne",
    "water": "undyne",
    "spear": "undyne",

    "snas": "sans",
    "snaz": "sans",
    "sans": "sans",
    "patrick": "sans",
    "lazy": "sans",
    "joke": "sans",
    "puns": "sans",
    "grill": "sans",

    "truck": "asgore",
    "burgentruck": "asgore",
    "burgen": "asgore",
    "asgore": "asgore",
    "king": "asgore",
    "throne": "asgore",
    "crown": "asgore",
    "fire": "asgore",

    "papyrus": "papyrus",
    "papy": "papyrus",
    "bones": "papyrus",
    "spaghetti": "papyrus",
    "blue": "papyrus",
    "skeleton": "papyrus",

    "asriel": "asriel",
    "as real": "asriel",
    "israel": "asriel",
    "god": "asriel",
    "flower": "asriel",
    "flowey": "asriel",

    "hurt": "ouch",
    "damage": "ouch",
    "attack": "ouch",
    "pain": "ouch",
    "injury": "ouch",
    "hit": "ouch",
    "bleed": "ouch",
    "ouchie": "ouch",
    "ouch": "ouch",

    "dummy": "maddummy",
    "caretaker": "toriel",
    "toriel": "toriel",

    "togo": "togore",
    "togore": "togore",
    "tagore": "togore",
    "togor": "togore",

    "jevil": "jevil",
    "general": "jevil",

    "toby": "toby",
    "fox": "toby",
    "tobey": "toby",
    "tobias": "toby",
    
    "refused": "heal",
    
    "puzzle": "puzzle"
}
GAME_KEYWORDS = list(KEYWORD_MAP.keys())

# ================================================================
# GLOBALS
# ================================================================
last_sent_words = set()
word_timeout = {}
selected_device_index = None
gm_client = None
audio_queue = queue.Queue()
stream = None
vosk_model = None
recognizer = None


# ================================================================
# UTILITY FUNCTIONS
# ================================================================
def send_string(sock, text):
    """Send UTF-8 string with null terminator to GameMaker."""
    if sock is None:
        print("[!] Socket is None, not sending")
        return
    try:
        text_bytes = text.encode("utf-8")
        sock.sendall(text_bytes + b"\x00")
        print(f"[->] Sent to GM: [{text}] ({len(text_bytes)} bytes)")
    except Exception as e:
        print(f"[!] Failed to send: {e}")


def get_active_microphones():
    """Return dict of available microphone devices as {name: index}."""
    active = {}
    for i, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0:
            active[dev["name"]] = i
    return active


def audio_callback(indata, frames, time_info, status):
    """Audio stream callback for real-time queueing."""
    if status:
        print(f"[!] Audio status: {status}")
    audio_queue.put(bytes(indata))


# ================================================================
# GAME CLIENT
# ================================================================
class GMClient:
    """TCP client for GameMaker networking."""

    def __init__(self, host, port, ui_ref=None):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.lock = threading.Lock()
        self.keep_running = True
        self.ui_ref = ui_ref
        self.reconnect_delay = 1.0
        self.max_reconnect_delay = 5.0
        threading.Thread(target=self._maintain_connection, daemon=True).start()

    def _maintain_connection(self):
        """Maintain connection with auto-reconnect."""
        while self.keep_running:
            if not self.connected:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect((self.host, self.port))
                    s.setblocking(True)
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    with self.lock:
                        self.sock = s
                        self.connected = True
                    self.reconnect_delay = 1.0
                    print(f"[+] Connected to GameMaker on {self.host}:{self.port}")
                    if self.ui_ref:
                        self.ui_ref.update_status("Connected")
                except ConnectionRefusedError:
                    print(f"[!] Connection refused by {self.host}:{self.port}")
                    if self.ui_ref:
                        self.ui_ref.update_status(
                            f"Connection refused – retrying in {self.reconnect_delay:.1f}s..."
                        )
                    time.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(self.reconnect_delay * 1.5, self.max_reconnect_delay)
                except Exception as e:
                    print(f"[!] Connection error: {e}")
                    if self.ui_ref:
                        self.ui_ref.update_status(
                            f"Disconnected – retrying in {self.reconnect_delay:.1f}s..."
                        )
                    time.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(self.reconnect_delay * 1.5, self.max_reconnect_delay)
            else:
                time.sleep(0.5)

    def send(self, data):
        """Send data string to GameMaker server."""
        if not self.connected:
            print("[!] Not connected, cannot send")
            return False
        with self.lock:
            try:
                send_string(self.sock, data)
                return True
            except Exception as e:
                print(f"[!] Send failed: {e}")
                self.connected = False
                try:
                    self.sock.close()
                except:
                    pass
                self.sock = None
                if self.ui_ref:
                    self.ui_ref.update_status("Disconnected – reconnecting...")
                return False

    def close(self):
        """Close client connection."""
        self.keep_running = False
        with self.lock:
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            self.sock = None
            self.connected = False


# ================================================================
# VOSK SPEECH RECOGNITION
# ================================================================
def init_vosk():
    """Initialize the Vosk model with flexible path search."""
    global vosk_model, recognizer
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    model_path = os.path.join(base_path, "model")

    if os.path.exists(model_path):
        try:
            print(f"[i] Loading Vosk model from: {model_path}")
            vosk_model = Model(model_path)
            recognizer = KaldiRecognizer(vosk_model, 16000)
            recognizer.SetWords(True)
            recognizer.SetPartialWords(True)
            print("[i] Vosk model loaded successfully")
            return True
        except Exception as e:
            print(f"[!] Failed to load model from {model_path}: {e}")

    print("[!] Could not find any valid Vosk model folder")
    return False


def should_send_word(word):
    """Throttle repeated word sends (debounce)."""
    current_time = time.time()
    if word in word_timeout and current_time - word_timeout[word] < 0.5:
        return False
    word_timeout[word] = current_time
    return True


def listen_loop():
    """Main recognition + send loop."""
    global selected_device_index, gm_client, stream, recognizer

    if not init_vosk():
        return

    while True:
        if selected_device_index is None or gm_client is None:
            time.sleep(0.1)
            continue

        if stream is None or not stream.active:
            try:
                stream = sd.RawInputStream(
                    samplerate=16000,
                    blocksize=4000,
                    device=selected_device_index,
                    dtype="int16",
                    channels=1,
                    callback=audio_callback,
                )
                stream.start()
                print(f"[i] Audio stream started (device {selected_device_index})")
            except Exception as e:
                print(f"[!] Failed to start audio stream: {e}")
                stream = None
                time.sleep(1)
                continue

        try:
            data = audio_queue.get(timeout=1)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower().strip()

                if not text:
                    continue

                print(f"[VOSK FINAL] {text}")
                if text in KEYWORD_MAP and should_send_word(text):
                    canonical = KEYWORD_MAP[text]
                    app.update_text(canonical)
                    gm_client.send(canonical)
                    print(f"[heard] {canonical}")
                    continue
                for word in text.split():
                    if word in KEYWORD_MAP and should_send_word(word):
                        canonical = KEYWORD_MAP[word]
                        app.update_text(canonical)
                        gm_client.send(canonical)
                        print(f"[heard] {canonical}")

            else:
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "").lower().strip()
                if partial_text:
                    print(f"[VOSK PARTIAL] {partial_text}")

        except queue.Empty:
            continue
        except Exception as e:
            print(f"[!] Recognition error: {e}")
            time.sleep(0.5)


# ================================================================
# USER INTERFACE
# ================================================================
class VoiceUI(ctk.CTk):
    """Simple CustomTkinter UI for keyword recognition status."""

    def __init__(self):
        super().__init__()
        self.title("Voice Detection")
        self.geometry("690x420")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.status_label = ctk.CTkLabel(self, text="Disconnected", font=("Consolas", 16))
        self.status_label.pack(pady=5)

        self.mic_devices = get_active_microphones()
        mic_names = list(self.mic_devices.keys()) or ["No active microphones found"]
        default_text = mic_names[0]

        self.mic_dropdown = ctk.CTkOptionMenu(
            self, values=mic_names, command=self.on_mic_selected
        )
        self.mic_dropdown.set(default_text)
        self.mic_dropdown.pack(pady=10)

        self.refresh_btn = ctk.CTkButton(self, text="Refresh Devices", command=self.refresh_mics)
        self.refresh_btn.pack(pady=5)

        self.text_label = ctk.CTkLabel(self, text="Listening for keywords...", font=("Consolas", 18))
        self.text_label.pack(pady=10)

        self.textbox = ctk.CTkTextbox(self, width=460, height=100, wrap="word")
        self.textbox.pack(pady=10)
        self.textbox.insert("end", "Waiting for keywords...")

        info_text = f"Active Keywords ({len(GAME_KEYWORDS)}):\n" + ", ".join(sorted(GAME_KEYWORDS))

        self.info_box = ctk.CTkTextbox(self, width=460, height=120, wrap="word")
        self.info_box.pack(pady=5)
        self.info_box.insert("end", info_text)
        self.info_box.configure(state="disabled")

    def on_mic_selected(self, choice):
        global selected_device_index, stream
        if stream:
            try:
                stream.stop()
                stream.close()
            except:
                pass
        stream = None
        selected_device_index = self.mic_devices.get(choice)
        print(f"[i] Switching to mic: {choice} (index {selected_device_index})")
        self.update_text(f"Switching to mic: {choice}")

    def refresh_mics(self):
        self.mic_devices = get_active_microphones()
        mic_names = list(self.mic_devices.keys()) or ["No active microphones found"]
        self.mic_dropdown.configure(values=mic_names)
        self.mic_dropdown.set(mic_names[0])
        self.update_text("Microphone list refreshed.")

    def update_text(self, text):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", text)
        self.update_idletasks()

    def update_status(self, text):
        self.status_label.configure(text=text)
        self.update_idletasks()

    def on_closing(self):
        global gm_client, stream
        if gm_client:
            gm_client.close()
        if stream:
            try:
                stream.stop()
                stream.close()
            except:
                pass
        self.destroy()


# ================================================================
# MAIN ENTRY
# ================================================================
if __name__ == "__main__":
    app = VoiceUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    gm_client = GMClient(HOST, PORT, ui_ref=app)

    if app.mic_devices:
        first_mic = list(app.mic_devices.keys())[0]
        selected_device_index = app.mic_devices[first_mic]
        print(f"[i] Auto-selected mic: {first_mic}")

    threading.Thread(target=listen_loop, daemon=True).start()
    app.mainloop()
