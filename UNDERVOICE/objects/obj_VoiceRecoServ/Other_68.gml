var type = async_load[? "type"];

if (type == network_type_connect) {
    client_socket = async_load[? "socket"];
    show_debug_message("Python connected: " + string(client_socket));
}
if (type == network_type_disconnect) {
    show_debug_message("Python disconnected");
    client_socket = -1;
}
if (type == network_type_data) {
    show_debug_message("DATA EVENT TRIGGERED!");
    var buffer = async_load[? "buffer"];
    buffer_seek(buffer, buffer_seek_start, 0);
    var msg = buffer_read(buffer, buffer_string);
    msg = string_trim(msg);
    var msg_lower = string_lower(msg);
    last_message = msg;
    show_debug_message("Received: [" + msg + "]");
    switch (msg_lower) {
        case "undyne":
            show_debug_message("Undyne :3");
            scr_battlforce("undyne");
        break;

        case "sans":
            show_debug_message("Snas :3");
            scr_battlforce("sans");
        break;

        case "asgore":
            show_debug_message("Asgore :3");
            scr_battlforce("asgore");
        break;

        case "papyrus":
            show_debug_message("Papyrus :3");
            scr_battlforce("papyrus");
        break;

        case "asriel":
            show_debug_message("Asriel :3");
            scr_battlforce("asriel");
        break;

        case "ouch":
            show_debug_message("damage :3");
            audio_play_sound(snd_damage, 1, false);
            var dmg = 4;
            if (global.hp <= 20) dmg += 1;
            if (global.hp > 20) dmg += 2;
            if (global.hp >= 30) dmg += 3;
            if (global.hp >= 40) dmg += 4;
            if (global.hp >= 50) dmg += 5;
            if (global.hp >= 60) dmg += 6;
            if (global.hp >= 70) dmg += 7;
            if (global.hp >= 80) dmg += 8;
            if (global.hp >= 90) dmg += 9;
            global.hp -= dmg;
        break;

        case "maddummy":
            show_debug_message("Mad Dummy :3");
            scr_battlforce("dummy");
        break;

        case "toriel":
            show_debug_message("Toriel :3");
            scr_battlforce("toriel");
        break;

        case "togore":
            show_debug_message("Togore :3");
            audio_play_sound(snd_togore, 1, false);
        break;

        case "jevil":
            show_debug_message("Jevil :3");
            audio_play_sound(snd_jevil, 1, false);
        break;

        case "toby":
            show_debug_message("toby fox moment");
            if (irandom(1) == 0) {
                tobysnd = snd_toby;
            } else { 
                tobysnd = snd_toby_ruff; 
            }
            audio_play_sound(tobysnd, 0, false);
        break;

        case "heal":
            show_debug_message("i mean... it healed...");
            global.hp++
        break;
        case "puzzle":
            show_debug_message("lowkey added this, and then couldent figure out a good way to implement it.")
        break;
    }
}
