#ifndef SOCKET_H
#define SOCKET_H

#define BROADCAST_PORT 50000
#define START_PORT 50500
#define END_PORT 50550
#define TCP_PORT 12345
extern int PLAY_PORT;

#define MAX_PLAYERS 2

#include <netinet/in.h>
#include <sys/select.h>
#include <arpa/inet.h>

// Structure pour stocker les couples pseudo et @IP
typedef struct {
    char pseudo[256];
    char ip[INET_ADDRSTRLEN];
    int port;
} PlayerInfo;

extern int sharing_active;
extern int search_active;
void start_sharing();
void stop_sharing();
void start_search();
void stop_search();

void addClient(const char *pseudo, const char *ip, int port);
int findClientPort(const char *pseudo);

int createBroadcastSocket(struct sockaddr_in *broadcastAddr, int *broadcastSocket);
int createPlaySocket(int *playSocket, int specifiedPort);
int createTCPSocket(struct sockaddr_in *tcpServerAddr, int *tcpSocket);
void closeSockets(int *playSocket,int *tcpSocket, int *broadcastSocket);
void closeUDP(int *playSocket, int *broadcastSocket);
void closeTCP(int *tcpSocket);
int connectBroadcastSocket();
void disconnectBroadcastSocket(int *broadcastSocket);
void closeSocket(int *Socket);
int Connect_TCP(struct sockaddr_in tcpServerAddr, int *tcpSocket);

void handle_search(int broadcastSocket, int tcpSocket);
void handle_share(int broadcastSocket, const char *sharing_json);
void handlePlay(int playSocket, int tcpSocket);

void sendBroadcast(int broadcastSocket, const char *json_string);
void sendToPlayer(const char *pseudo, const char *json_string);

void send_Game_Broadcast(int broadcastSocket, const char *json_string, int port_game);
#endif /* SOCKET_H */
