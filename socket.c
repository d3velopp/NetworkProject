#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include "socket.h"
#include <time.h>
#include "json_reader.h"

PlayerInfo clients[MAX_PLAYERS];
int numClients = 0;
int PLAY_PORT;
int sharing_active = 0;
int search_active = 0;

void start_sharing() {
    sharing_active = 1;
}

void stop_sharing() {
    sharing_active = 0;
}

void start_search() {
    search_active = 1;
}

void stop_search() {
    search_active = 0;
}

int random_available_port() {
    int available_ports[END_PORT - START_PORT + 1];
    int num_available_ports = 0;
    int sockfd, port;
    struct sockaddr_in addr;

    // random
    srand(time(NULL));

    // recherche ports dispos
    for (port = START_PORT; port <= END_PORT; ++port) {
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd < 0) {
            perror("socket");
            exit(EXIT_FAILURE);
        }

        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK); // INADDR_ANY pour tester tous les interfaces
        addr.sin_port = htons(port);

        if (connect(sockfd, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
            available_ports[num_available_ports++] = port;
        }

        close(sockfd);
    }

    if (num_available_ports == 0) {
        printf("Aucun port disponible dans la plage spécifiée.\n");
        return -1; // -1 si aucun port disponible
    }

    return available_ports[rand() % num_available_ports];
}

/**
    Fonction pour ajouter un joeur 
*/ 
int addPlayer(const char *pseudo, const char *ip, int port) {
    for (int i = 0; i < numClients; i++) {
        if (strcmp(clients[i].pseudo, pseudo) == 0) {
            // màj
            strncpy(clients[i].ip, ip, sizeof(clients[i].ip));
            clients[i].port = port;
            return 6; 
        }
    }

    // add
    if (numClients < MAX_PLAYERS) {
        strncpy(clients[numClients].pseudo, pseudo, sizeof(clients[numClients].pseudo));
        strncpy(clients[numClients].ip, ip, sizeof(clients[numClients].ip));
        clients[numClients].port = port;
        numClients++;
    } else {
        fprintf(stderr, "Nombre maximal de clients atteint.\n");
    }
    return 0;
}

/**
    Trouve le port associé à un pseudo
*/
int findClientPort(const char *pseudo) {
    for (int i = 0; i < numClients; i++) {
        if (strcmp(clients[i].pseudo, pseudo) == 0) {
            return clients[i].port;
        }
    }
    return -1; 
}


/**
 * Crée la socket d'envoie (broadcast pour partage / rechercher partie)
*/
int createBroadcastSocket(struct sockaddr_in *broadcastAddr, int *broadcastSocket) {
    if ((*broadcastSocket = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
        perror("Erreur lors de la création de la socket de diffusion");
        return -1;
    }

    int broadcastEnable = 1;
    setsockopt(*broadcastSocket, SOL_SOCKET, SO_BROADCAST, &broadcastEnable, sizeof(broadcastEnable));

    memset(broadcastAddr, 0, sizeof(*broadcastAddr));
    broadcastAddr->sin_family = AF_INET;
    broadcastAddr->sin_addr.s_addr = INADDR_BROADCAST; 
    broadcastAddr->sin_port = htons(BROADCAST_PORT);

    if (bind(*broadcastSocket, (struct sockaddr *)broadcastAddr, sizeof(*broadcastAddr)) == -1) {
        perror("Erreur lors de la liaison de la socket broadcast");
        close(*broadcastSocket);
        return -1;
    }

    return *broadcastSocket;
}

/**
 * Crée la socket de communication avec les autres joueurs dans la partie
*/
int createPlaySocket(int *playSocket, int specifiedPort) {
    struct sockaddr_in serverAddr;

    if (specifiedPort == 0) {
        PLAY_PORT = random_available_port();
        if (PLAY_PORT == -1) {
            fprintf(stderr, "Erreur lors de la génération du port de jeu aléatoire.\n");
            return -1;
        }
    } else {
        PLAY_PORT = specifiedPort;
    }

    *playSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (*playSocket == -1) {
        perror("Erreur lors de la création de la socket de jeu");
        return -1;
    }

    int broadcastEnable = 1;
    if (setsockopt(*playSocket, SOL_SOCKET, SO_BROADCAST, &broadcastEnable, sizeof(broadcastEnable)) == -1) {
        perror("Erreur lors du paramétrage de la socket de jeu en mode diffusion");
        close(*playSocket);
        return -1;
    }

    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(PLAY_PORT);

    if (bind(*playSocket, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) == -1) {
        perror("Erreur lors de la liaison de la socket de jeu");
        close(*playSocket);
        return -1;
    }

    printf("Socket de jeu créée et liée avec succès sur le port %d.\n", PLAY_PORT);

    return PLAY_PORT;
}

/**
 * Crée la socket TCP pour communiquer avec le code python
*/
int createTCPSocket(struct sockaddr_in *tcpServerAddr, int *tcpSocket) {
    if ((*tcpSocket = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("Erreur lors de la création de la socket TCP");
        return -1;
    }

    memset(tcpServerAddr, 0, sizeof(*tcpServerAddr));
    tcpServerAddr->sin_family = AF_INET;
    tcpServerAddr->sin_port = htons(TCP_PORT);
    tcpServerAddr->sin_addr.s_addr = inet_addr("127.0.0.1");

    return 0;
}

void disconnectBroadcastSocket(int *broadcastSocket) {
    if (*broadcastSocket != -1) {
        close(*broadcastSocket);
        printf("La socket de diffusion a été déconnectée et fermée.\n");
        *broadcastSocket = -1;
    }
}

void closePlaySocket(int *playSocket) {
    if (*playSocket != -1) {
        close(*playSocket);
        printf("La socket de jeu a été fermée avec succès.\n");
        *playSocket = -1;
    }
}


void closeSocket(int *Socket) {
	close(*Socket);
}

int Connect_TCP(struct sockaddr_in tcpServerAddr, int *tcpSocket) {
    if (connect(*tcpSocket, (struct sockaddr *)&tcpServerAddr, sizeof(tcpServerAddr)) == 0) {
        printf("Connexion TCP établie avec succès.\n");
        return 0; // succès
    } else {
        fprintf(stderr, "Erreur lors de la connexion TCP : %s\n", strerror(errno));
        return -1; // échec
    }
}

void handle_share(int broadcastSocket, const char *sharing_json) {
    char port_str[10]; 
    snprintf(port_str, sizeof(port_str), "%d", PLAY_PORT);
    char *updated_json = add_attribute_to_json(sharing_json, "port", port_str);
    
    // envoie chaîne JSON modifiée en diffusion
    sendBroadcast(broadcastSocket, updated_json);
    free(updated_json);
}


void handle_search(int broadcastSocket, int tcpSocket) {
    char buffer[256];
    int test = 0;
    struct sockaddr_in senderAddr;
    socklen_t senderAddrLen = sizeof(senderAddr);
    //printf("ici");
    // Non bloquant
    fcntl(broadcastSocket, F_SETFL, O_NONBLOCK);
    ssize_t bytes_received = recvfrom(broadcastSocket, buffer, sizeof(buffer), 0, (struct sockaddr *)&senderAddr, &senderAddrLen);
    if (bytes_received == -1) {
        // Aucune donnée disponible 
        //printf("Aucune donnée disponible sur le socket de diffusion.\n");
    } else {
        buffer[bytes_received] = '\0';
        JSON_Message message = lire_json(buffer);
        char *pseudo = message.pseudo;
        int port = message.port;
        test = addPlayer(pseudo, inet_ntoa(senderAddr.sin_addr), port);
        if (test == 6) {
            printf("Client ajouté : Pseudo = %s, IP = %s, Port = %d\n", pseudo, inet_ntoa(senderAddr.sin_addr), port);
        }
        ssize_t bytes_sent = send(tcpSocket, buffer, strlen(buffer), 0);
        if (bytes_sent == -1) {
            perror("Erreur lors de l'envoi des données via TCP");
            exit(EXIT_FAILURE);
        }
        printf("C sent (TCP): %s\n", buffer);
    }
}

void handlePlay(int playSocket, int tcpSocket) {
    char buffer[1024];
    int test = 0;
    struct sockaddr_in senderAddr;
    socklen_t senderAddrLen = sizeof(senderAddr);

    printf("\n\nSOCKET DE JEU\n");
    fcntl(playSocket, F_SETFL, O_NONBLOCK);

    ssize_t bytes_received = recvfrom(playSocket, buffer, sizeof(buffer), 0, (struct sockaddr *)&senderAddr, &senderAddrLen);
    if (bytes_received == -1) {
        // Aucune donnée 
        printf("Aucune donnée disponible sur le socket de jeu.\n");
    } else {

        buffer[bytes_received] = '\0';
        JSON_Message message = lire_json(buffer);
        char *pseudo = message.pseudo;
        int port = message.port;
        test = addPlayer(pseudo, inet_ntoa(senderAddr.sin_addr), port);
        if (test == 6) {
            printf("Client ajouté : Pseudo = %s, IP = %s, Port = %d\n", pseudo, inet_ntoa(senderAddr.sin_addr), port);
        }
        printf("\n\nPROUT\n");
        ssize_t bytes_sent = send(tcpSocket, buffer, strlen(buffer), 0);
        if (bytes_sent == -1) {
            perror("Erreur lors de l'envoi des données via TCP");
            exit(EXIT_FAILURE);
        }
        printf("C sent (TCP): %s\n", buffer);
    }
}



void sendBroadcast(int broadcastSocket, const char *json_string) {
    struct sockaddr_in broadcastAddr;
    memset(&broadcastAddr, 0, sizeof(broadcastAddr));
    broadcastAddr.sin_family = AF_INET;
    broadcastAddr.sin_addr.s_addr = INADDR_BROADCAST;
    broadcastAddr.sin_port = htons(BROADCAST_PORT);

    // Envoyer le JSON en broadcast sur la broadcast socket
    if (sendto(broadcastSocket, json_string, strlen(json_string), 0, (struct sockaddr *)&broadcastAddr, sizeof(broadcastAddr)) == -1) {
        perror("Erreur lors de l'envoi en diffusion");
        exit(EXIT_FAILURE);
    }
    //printf("C sent (sharing broadcast): %s\n", json_string);
}

void send_Game_Broadcast(int broadcastSocket, const char *json_string, int port_game) {
    struct sockaddr_in broadcastAddr;
    memset(&broadcastAddr, 0, sizeof(broadcastAddr));
    broadcastAddr.sin_family = AF_INET;
    broadcastAddr.sin_addr.s_addr = INADDR_BROADCAST;
    broadcastAddr.sin_port = htons(PLAY_PORT);

    // Envoyer le JSON en broadcast sur la broadcast socket
    if (sendto(broadcastSocket, json_string, strlen(json_string), 0, (struct sockaddr *)&broadcastAddr, sizeof(broadcastAddr)) == -1) {
        perror("Erreur lors de l'envoi en diffusion");
        exit(EXIT_FAILURE);
    }
    //printf("C sent (sharing broadcast): %s\n", json_string);
}

void sendToPlayer(const char *pseudo, const char *json_string) {
    // Rechercher le client dans la table
    for (int i = 0; i < numClients; i++) {
        if (strcmp(clients[i].pseudo, pseudo) == 0) {
            // Trouvé le client, envoyer le JSON à son IP
            struct sockaddr_in playerAddr;
            memset(&playerAddr, 0, sizeof(playerAddr));
            playerAddr.sin_family = AF_INET;
            playerAddr.sin_addr.s_addr = inet_addr(clients[i].ip);
            playerAddr.sin_port = htons(PLAY_PORT); 

            int playSocket;
            if ((playSocket = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
                perror("Erreur lors de la création de la socket de jeu");
                exit(EXIT_FAILURE);
            }

            // Envoyer le JSON au joueur spécifié
            if (sendto(playSocket, json_string, strlen(json_string), 0, (struct sockaddr *)&playerAddr, sizeof(playerAddr)) == -1) {
                perror("Erreur lors de l'envoi au joueur spécifié");
                close(playSocket);
                exit(EXIT_FAILURE);
            }

            printf("JSON envoyé à %s (%s)\n", clients[i].pseudo, clients[i].ip);

            // Fermer la socket de jeu
            close(playSocket);

            return; // Sortir de la fonction après l'envoi
        }
    }

    // Si le pseudo n'est pas trouvé dans la table des clients
    printf("Le pseudo '%s' n'est pas présent dans la table des clients.\n", pseudo);
}



