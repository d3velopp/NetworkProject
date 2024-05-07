#include "connection.h"


int main(int argc, char** argv){
    // char ip_server[CHAR_SIZE];
    // int port;
    // int first_player;
    // printf("Is the first player? (0/1): ");
    // scanf("%d", &updated_player);
    // if(updated_player == 0){
    //     printf("Enter the server IP: ");
    //     scanf("%s", ip_server);
    //     printf("Enter the server port: ");
    //     scanf("%d", &port);
    // }
    s_port = atoi(argv[1]);
    printf("Port: %d\n", s_port);
    return init_connection();
}

char* extractIpAddress(){
    struct ifaddrs *ifaddr, *ifa;
    int family, s;
    char host[1025];
    char *loopbackIP = NULL;

    if (getifaddrs(&ifaddr) == -1) {
        perror("getifaddrs");
        return NULL;
    }

    // Walk through linked list, maintaining head pointer so we can free list later
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == NULL) {
            continue;
        }

        family = ifa->ifa_addr->sa_family;

        if (family == AF_INET && strcmp(ifa->ifa_name, "wlp4s0") == 0) {
            s = getnameinfo(ifa->ifa_addr, sizeof(struct sockaddr_in), host, 1025, NULL, 0, 1);
            if (s != 0) {
                printf("getnameinfo() failed: %s\n", gai_strerror(s));
                return NULL;
            }
            loopbackIP = strdup(host); // strdup allocates memory and copies the string
            break; // We've found the loopback interface, no need to continue
        }
    }
    freeifaddrs(ifaddr);
    return loopbackIP;
}

int init_connection(){


    // if (updated_player == 0){
    //     struct sockaddr_in server_addr;
    //     if ( inet_aton(ip_server, &server_addr.sin_addr) == 0){
    //         printf("Invalid IP address\n");
    //         return -1;
    //     }
    //     connect_to_server(ip_server, port, 1);
    // } else {
    //     main_port = port_generator();
    // }
    // if (main_port == -1){
    //     return -1;
    // }
    python_socket = connect_to_py(s_port);
    game_listen();

    if ( close(listen_socket) == -1){
        perror("close");
        return -1;
    }
}

int connect_to_server(const char* ip_server, int port_server,int new_player){
    struct sockaddr_in sock_adresse = {0};
    sock_adresse.sin_port = htons(port_server);
    sock_adresse.sin_addr.s_addr = inet_addr(ip_server);
    sock_adresse.sin_family = AF_INET;

    int socket_server = socket(AF_INET, SOCK_STREAM, 0);
    if ( socket_server == -1){
        perror("socket");
        return -1;
    }

    if ( connect(socket_server, (struct sockaddr*)&sock_adresse, sizeof(sock_adresse)) == -1){
        perror("connect");
        close(socket_server);
        return -1;
    }

    game_packet* packet = create_game_packet();

    fd_set fd_connect;

    do {
        FD_ZERO(&fd_connect);
        FD_SET(socket_server, &fd_connect);
        select(socket_server + 1, &fd_connect, NULL, NULL, NULL);
        if ( !FD_ISSET(socket_server, &fd_connect)){
            printf("Error with address %s", inet_ntoa(sock_adresse.sin_addr));
            close(socket_server);
            return -1;
        }
        if ( receive_packet(packet, socket_server) == 0){
            printf("Server disconnected\n");
            close(socket_server);
            return 1;
        }
        print_game_packet(packet);
        if ( packet-> type == MSG_CONNECT_START){
            if ( new_player){
                main_port = port_generator();
                printf("Port generated: %d\n", main_port);
                init_game_packet(packet, MSG_CONNECT_NEW, 0);
                if ( send_game_packet(packet, socket_server) == -1){
                    printf("Error sending packet\n");
                    close(socket_server);
                    return -1;
                }
            } else {
                init_game_packet(packet, MSG_CONNECT_REQ, 0);
                if ( send_game_packet(packet, socket_server) == -1){
                    printf("Error sending packet\n");
                    close(socket_server);
                    return -1;
                }
            }
            packet-> type = MSG_BAD_PORT;
        }
    }
    while ( packet->type != MSG_CONNECT_OK);
    client* current_client = add_client(socket_server, port_server, sock_adresse);
    python_packet* py_packet = create_python_packet();
    if (init_python_packet(py_packet, PYMSG_CLIENT_ADD, current_client-> port, 0) == -1){
        return -1;
    }
    if (send_python_packet(py_packet, python_socket) == -1){
        return -1;
    }
    if (new_player){
            if ( send_nodata_msg(MSG_REQ_IP_PORT, socket_server) == -1){
                return -1;
            }
            printf("Requesting IP and port\n");
        }
    return 0;
}



int create_listen_socket(){
    main_port = port_generator();
    listen_socket = socket(AF_INET, SOCK_STREAM, 6);
    if (listen_socket == -1){
        perror("socket");
        return -1;
    }
    // Local test 
    // char addresse_ip[CHAR_SIZE];
    // printf("Enter the listen IP: ");
    // scanf("%s", addresse_ip);
    //
    char* addresse_ip = extractIpAddress();
    printf("[C] IP: %s\n", addresse_ip);
    printf("[C] Port: %d\n", main_port);

    struct sockaddr_in listen_addr = {0};
    listen_addr.sin_family = AF_INET;
    listen_addr.sin_port = htons(main_port);
    // Local test: 
    listen_addr.sin_addr.s_addr = inet_addr(addresse_ip);
    // printf("IP: %d\n", listen_addr.sin_addr.s_addr);
    // listen_addr.sin_addr.s_addr = INADDR_ANY;
    if (bind(listen_socket, (struct sockaddr*)&listen_addr, sizeof(listen_addr)) == -1){
        perror("bind");
        close(listen_socket);
        return -1;
    }
    if (listen(listen_socket, 5) == -1){
        perror("listen");
        close(listen_socket);
        return -1;
    }
    python_packet* packet = create_python_packet();
    if (init_python_packet(packet, PYMSG_REP_PORT, main_port, 0) == -1){
        return -1;
    }
    if (send_python_packet(packet, python_socket) == -1){
        return -1;
    }
    return listen_socket;

}

int game_listen(){
    fd_set fd_listen;
    int nb_fd;
    int max_fd = 0;
    while(1){
        FD_ZERO(&fd_listen);
        if (listen_socket != -1){
            FD_SET(listen_socket, &fd_listen);
        }
        FD_SET(python_socket, &fd_listen);
        set_max_fd_all_client(&fd_listen, &max_fd);
        if (max_fd < listen_socket){
            max_fd = listen_socket;
        }
        if (max_fd < python_socket){
            max_fd = python_socket;
        }

        nb_fd = select(max_fd + 1, &fd_listen, NULL, NULL, NULL);
        if (nb_fd == -1){
            perror("select");
            return -1;
        }
        if (FD_ISSET(python_socket, &fd_listen)){
            if (listen_from_python() == -1){
                return -1;
            }
        }
        if ( FD_ISSET(listen_socket, &fd_listen)){
            if (accept_new_client(listen_socket) == NULL){
                return -1;
            }
        }
        listen_all_client(&fd_listen);
    }
}

int listen_from_python(){
    python_packet *packet = create_python_packet();
    if (receive_python_packet(packet, python_socket) == 0){
        printf("Python disconnected\n");
        close(python_socket);
        return 1;
    }
    if ( pymsg_type_handler(packet) == -1){
        return -1;
    }
    
}

int pymsg_type_handler(python_packet* packet){
    switch (packet->type){
        case PYMSG_CREATE_ROOM:
            return create_listen_socket();
        case PYMSG_JOIN_ROOM:
            return join_room(packet);
    }
}

int join_room(python_packet* packet){
    uint32_t* ip_port = (uint32_t*) packet->data;
    in_addr_t ip_addr = ip_port[0];
    struct in_addr addr;
    addr.s_addr = ip_addr;
    char* ip = inet_ntoa(addr);
    u_int32_t port = ip_port[1];
    printf("Joining room with IP: %s and port: %d\n", ip, port);
    if (connect_to_server(ip, port, 1) == -1){
        return -1;
    }
    if (create_listen_socket() == -1){
        return -1;
    }
    return 1;
}


int listen_all_client(fd_set *fd_listen){
    client* current_client = first_client();
    game_packet* packet = create_game_packet();
    while(current_client != NULL){
        if ( FD_ISSET( current_client-> socket_client, fd_listen)){
            // printf("[C]Receiving packet from client with port %d\n", current_client->port);
            if ( receive_packet(packet, current_client->socket_client) == 0){
                printf("Client with port %d disconnected\n", current_client->port);
                remove_client(current_client);
                python_packet* py_packet = create_python_packet();
                if (init_python_packet(py_packet, PYMSG_CLIENT_REMOVE, current_client->port, 0) == -1){
                    return -1;
                }
                if (send_python_packet(py_packet, python_socket) == -1){
                    return -1;
                }
                current_client = current_client->next; 
                continue;
            }
            print_game_packet(packet);
            if ( message_type_handler(packet, current_client) == -1){
                return -1;
            }
            
        }
        current_client = current_client->next;
    }

}

int message_type_handler(game_packet* packet, client* current_client){
    switch (packet->type){
        case MSG_CONNECT_NEW:
            return new_connection(current_client, packet);
        case MSG_CONNECT_REQ:
            return req_connection(current_client, packet);
        case MSG_REQ_IP_PORT:
            return send_all_ip_port(current_client);
        case MSG_REP_IP_PORT:
            return affiche_all_ip_port(packet);
    }
}

int affiche_all_ip_port(game_packet* packet){
    uint32_t * ip_port = (uint32_t*) packet->data;
    for (int i = 0; i < (packet->size)/sizeof(uint32_t)/2; i++){
        in_addr_t ip_addr = ip_port[2*i + 1];
        struct in_addr addr;
        addr.s_addr = ip_addr;
        printf("Port: %d, IP: %s\n", ip_port[2*i], inet_ntoa(addr));
        connect_to_server(inet_ntoa(addr), ip_port[2*i], 0);
    }
}

int send_all_ip_port(client* current_client){
    client* current = first_client();
    game_packet* packet = create_game_packet();
    init_game_packet(packet, MSG_REP_IP_PORT, 0);
    packet -> size = (get_number_of_client() - 1)*sizeof(uint32_t)*2;
    packet -> data = calloc(packet->size, 1);
    uint32_t* ip_port = get_all_ip_port(current_client);
    memcpy(packet->data,(char*) ip_port, packet->size);
    if ( send_game_packet(packet, current_client->socket_client) == -1){
        return -1;
    }
    return 0;
}

int new_connection( client* current_client, game_packet* packet ){
    if ( port_exist(first_client(), packet->port)){
        if(send_nodata_msg(MSG_BAD_PORT, current_client->socket_client) < 0){
            return -1;
        }
        return 0;
    }
    return req_connection(current_client, packet);
}

int req_connection( client* current_client, game_packet* packet){
    current_client->port = packet->port;
    affiche_client(first_client());
    if ( send_nodata_msg(MSG_CONNECT_OK, current_client->socket_client) < 0){
        return -1;
    }
    python_packet* py_packet = create_python_packet();
    if (init_python_packet(py_packet, PYMSG_CLIENT_ADD, current_client-> port, 0) == -1){
        return -1;
    }
    if (send_python_packet(py_packet, python_socket) == -1){
        return -1;
    }
    return 0;
}

client* accept_new_client(int listen_socket){
    int socket_new_client;
    int len = sizeof(struct sockaddr_in);
    struct sockaddr_in sockaddr_client;
    if ( (socket_new_client = accept(listen_socket,(struct sockaddr*) &sockaddr_client, &len)) == -1){
        perror("accept");
        return NULL;
    }
    client* new_client = add_client(socket_new_client, 0, sockaddr_client);


    if ( new_client == NULL){
        return NULL;
    }
    int byte = send_nodata_msg(MSG_CONNECT_START, socket_new_client);
    if ( byte == -1){
        return NULL;
    }
    printf("Connecting to client with port %d and ip address: %s\n", new_client->port, inet_ntoa(sockaddr_client.sin_addr));
    return new_client;



}

// int new_connection( client* current_client, game_packet* packet ){
    
// }