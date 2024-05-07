#include "game_packet.h"
#include "connection.h"
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <errno.h>



static char* buffer; 
static unsigned int buffer_size = 0;
static const uint32_t header_size = sizeof(game_packet) - sizeof(char*);

int port_generator(){
    srand(time(NULL));
    main_port = rand() % 1000 + 8000;
    return main_port;
}
static void resize_buffer( int size ){
    if(buffer_size){
        free(buffer);
    }
    buffer = calloc( size , 1);
    buffer_size = size;
}

int print_game_packet( const game_packet* packet){
    printf("---------------Packet-----------------\n");
    printf("Packet type: %d\n", packet->type);\
    printf("Packet port: %d\n",(int) packet->port);
    printf("Packet size: %d\n", packet->size);
    if (packet->size > 0 && has_data(packet)){
        printf("Packet data: %s\n", packet->data);
    }
    printf("-------------------------------------\n");
    return 0;
}

game_packet *create_game_packet(){
    game_packet *new_packet = calloc(sizeof(game_packet), 1);
    if (new_packet == NULL){
        return NULL;
    }
    new_packet->data = NULL;
    return new_packet;
}
void init_game_packet( game_packet* packet, uint8_t type, uint32_t size ){
    packet->port = main_port;
    packet->type = type;
    packet->size = size;
    packet->data = calloc(size, 1);
}

int has_data( const game_packet* packet){
    switch (packet->type)
    {
    case MSG_REP_IP_PORT:
        return 1;
    default:
        return 0;
    }
}
int is_valid_packet( const game_packet* packet){
    return (
        packet->type == MSG_CONNECT_START ||
        packet->type == MSG_CONNECT_NEW ||
        packet->type == MSG_CONNECT_REQ ||
        packet->type == MSG_CONNECT_OK ||
        packet->type == MSG_REQ_IP_PORT ||
        packet->type == MSG_REP_IP_PORT
    );
}

int send_nodata_msg( const uint8_t type, int socket){
    game_packet* message = create_game_packet();
    init_game_packet(message, type, 0);
    // print_game_packet(message);
    int send_size = send(socket, message, header_size, 0);
    if (send_size == -1){
        perror("send");
        return -1;
    }
    free(message);
    return send_size;
}

int send_game_packet( game_packet* packet, int socket){
    uint32_t send_size = header_size;
    int contain_data = has_data(packet);
    if ( packet -> size > 0 && has_data(packet) && packet -> data != NULL){
        send_size += packet -> size;
        contain_data = 1;
    }
    if ( send_size > buffer_size){
        resize_buffer(send_size);
    }
    memset(buffer, '\0', send_size);
    if ( memcpy( buffer, packet, header_size) == NULL){
        return -1;
    }
    if (contain_data){
        if (memcpy(buffer + header_size, packet -> data, packet -> size) == NULL){
            return -1;
        }
    }
    int a = (int) send(socket, buffer, send_size, 0);
    printf("Sent %d bytes\n", a);
    return a;

}

int receive_packet( game_packet *recieve_packet, int socket ){
    // printf("Receiving packet\n");
    int received_size = recv(socket, recieve_packet, header_size, 0);
    if (received_size == -1){
        perror("recv");
        return -1;
    }
    if (received_size == 0){
        return 0;
    }
    if (received_size < header_size || !is_valid_packet(recieve_packet)){
        return -1;
    }
    if (recieve_packet -> size > 0 && has_data(recieve_packet)){
        recieve_packet -> data = calloc(recieve_packet -> size, 1);
        received_size += recv(socket, recieve_packet -> data, recieve_packet -> size, MSG_WAITALL);
    }
    printf("Received %d bytes\n", received_size);
    flush_socket(socket);
    return received_size;


}

void flush_socket( int socket){
    int received_size;
    char buffer[1024];
    do{
        received_size = recv(socket, buffer, 1024, MSG_DONTWAIT);
        if (received_size == -1 && errno == EAGAIN){
            return;
        }
    } while (received_size >= 1024);
}