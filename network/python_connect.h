#ifndef PYTHON_CONNECT_H
#define PYTHON_CONNECT_H


#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/select.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <ifaddrs.h>
#include <netinet/in.h>
#include <netdb.h>
#include <errno.h>

// struct python_header {
//     uint8_t type;
//     uint32_t port;
//     uint32_t size;
// };
// typedef struct python_header python_header;
struct python_packet {
    uint8_t type;
    uint32_t port;
    uint32_t size;
    char* data;
};



typedef struct python_packet python_packet;
extern int init_python_packet( python_packet* packet, uint8_t type, uint32_t port, uint32_t size );
extern python_packet *create_python_packet();
extern int receive_python_packet( python_packet *packet, int socket);
extern int send_python_packet( python_packet* packet, int socket);
extern void flush_python_socket( int socket);
extern int connect_to_py( int s_port);
extern void print_python_packet( python_packet* packet);


#endif