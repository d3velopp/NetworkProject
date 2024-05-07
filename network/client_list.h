#ifndef CLIENT_LIST
#define CLIENT_LIST

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

#include "game_packet.h"




struct client
{
    int socket_client;
    uint32_t port;
    uint8_t color;
    struct sockaddr_in sockaddr_client;
    struct client *next;
};

typedef struct client client;

extern client* first_client();
extern int append_client( client* new_client);
extern int port_exist( client* targeted_client, int port);
extern client* last_client();
extern client* add_client( int socket_client, int port, struct sockaddr_in sockaddr_client);
extern int remove_client( client* targeted_client);
extern void set_max_fd_all_client(fd_set *fd_listen, int *max_fd);
extern int affiche_client();   
extern uint32_t* get_all_ip_port(client* current_client); 
extern int get_number_of_client();

#endif