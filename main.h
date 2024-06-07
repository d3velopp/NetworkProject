//Variables globales
#define BROADCAST_PORT 54321
#define SERVER_PORT 12346
#define TCP_PORT 12345

#define MAX_CONNECTION_ATTEMPTS 30  // max tentatives co (TCP C-Python)
#define CONNECTION_DELAY_SECONDS 1 // délais en secondes entre 2 tentatives de connexion (TCP)



int createBroadcastSocket(struct sockaddr_in *broadcastAddr, int *broadcastSocket);
int createPlaySocket(struct sockaddr_in *serverAddr, int *playSocket);
int createTCPSocket(struct sockaddr_in *tcpServerAddr, int *tcpSocket);
void closeSockets(int *playSocket,int *tcpSocket, int *broadcastSocket);
void closeUDP(int *playSocket, int *broadcastSocket);
void closeTCP(int *tcpSocket);
int connectBroadcastSocket();
void disconnectBroadcastSocket(int *broadcastSocket);

void closeSocket(int *Socket);

int Connect_TCP(struct sockaddr_in tcpServerAddr, int *tcpSocket);

int UDP_Reception_Send_TCP(int playSocket, int tcpSocket, fd_set read_set);
int TCP_Reception_Send_UDP(int playSocket, int tcpSocket, int broadcastSocket, struct sockaddr_in broadcastAddr,  fd_set read_set);

