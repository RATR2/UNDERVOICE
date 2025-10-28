persistent = true
port = 6500;
listener = network_create_server_raw(network_socket_tcp, port, 32);
show_debug_message("VoiceRecoServ created. Listening on port " + string(port));
client_socket = -1;