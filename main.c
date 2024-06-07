#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include "socket.h"
#include "json_reader.h"

int broadcastSocket, tcpSocket;
int playSocket = -1;

char sharing_json[1024] = {0};

int count = 0;

int main() {
    struct sockaddr_in broadcastAddr, tcpServerAddr;


    // UDP
    if (createTCPSocket(&tcpServerAddr, &tcpSocket) == -1) {
        perror("Erreur lors de la création de la socket TCP");
        exit(EXIT_FAILURE);
    } else {
        printf("Socket TCP créée avec succès.\n");
    }

    if (createBroadcastSocket(&broadcastAddr, &broadcastSocket) == -1) {
        perror("Erreur lors de la création de la socket TCP");
        exit(EXIT_FAILURE);
    } else {
        printf("Socket Broadcast créée avec succès.\n");
    }
    
    // Tentatives de connexion à la socket TCP (bloquant jusqu'à la connexion)
    while (Connect_TCP(tcpServerAddr, &tcpSocket) != 0) {
        printf("Tentative de connexion TCP en cours...\n");
        sleep(3); //3s entre les tentativess
    }

    fd_set read_set;
    struct timeval timeout;
    int client_port;

    while (1) {
        FD_ZERO(&read_set);
        if (playSocket != -1) {
            FD_SET(playSocket, &read_set);
        }
        FD_SET(tcpSocket, &read_set);

        timeout.tv_sec = 0;
        timeout.tv_usec = 100000;  // 100 ms

        int ready = select(FD_SETSIZE, &read_set, NULL, NULL, &timeout);

        if (ready == -1) {
            perror("Erreur lors de l'appel à select");
            exit(EXIT_FAILURE);
        } else if (ready > 0) {
            // PLAY SOCKET
            printf("caca.\n");
            if (FD_ISSET(playSocket, &read_set)) {
                handlePlay(playSocket,tcpSocket);
            }

            // Traitement des données sur la socket TCP
            if (FD_ISSET(tcpSocket, &read_set)) {
                char buffer[1024];
                ssize_t received_bytes = recv(tcpSocket, buffer, sizeof(buffer) - 1, 0);
                if (received_bytes <= 0) {
                    perror("Erreur lors de la réception TCP");
                    continue;
                }
                buffer[received_bytes] = '\0';
                            printf("PIPI.\n");
                JSON_Message message;
                if (is_valid_json(buffer)) {
                    message = lire_json(buffer);
                    printf("PROUT.\n");
                    printf(message.order);
                }

                if (message.order == NULL) {
                } else if (strcmp(message.order, "share") == 0) {
                    if (createPlaySocket(&playSocket, 0) == -1) {
                        perror("Erreur lors de la création de la socket de jeu");
                        // TODO : Gérer l'erreur...
                    } else {
                        printf("Socket de jeu créée avec succès (port aléatoire).\n");
                        strncpy(sharing_json, buffer, sizeof(sharing_json));
                        start_sharing();
                        FD_SET(playSocket, &read_set); 
                    }
                } else if (strcmp(message.order, "stop_share") == 0) {
                    if (playSocket != -1) {
                        closeSocket(&playSocket);
                        playSocket = -1;
                        stop_sharing();
                        FD_CLR(playSocket, &read_set); 
                        printf("Socket de jeu fermée avec succès.\n");
                    }
                } else if (strcmp(message.order, "search") == 0) {
                    start_search();
                } else if (strcmp(message.order, "stop_search") == 0) {
                    stop_search();
                } else if (strcmp(message.order, "game") == 0) {
                    // pseudo est une chaîne vide -> envoyer en broadcast
                    if (strcmp(message.pseudo, "") == 0) {
                        printf("\n\nON A ENVOYER GAME\n\n");
                        send_Game_Broadcast(playSocket, buffer, client_port);
                    } else {
                        // si une personne est spécifiée
                        sendToPlayer(message.pseudo, buffer);
                    }
                } else if (strcmp(message.order, "connect") == 0) {
                    if (message.pseudo == NULL || strlen(message.pseudo) == 0) {
                        // TODO : Gérer erreur
                        printf("Erreur: Aucun pseudo spécifié pour la commande 'connect'.\n");
                    } else {
                        client_port = findClientPort(message.pseudo);
                        if (client_port != -1) {
                            if (createPlaySocket(&playSocket, client_port) == -1) {
                                perror("Erreur lors de la création de la socket de jeu avec le port spécifié");
                                printf("salut a tous c daaaaaavid\n");
                                // TODO : Gérer l'erreur...
                            } else {
                                printf("Socket de jeu créée avec succès pour le pseudo '%s' avec le port %d.\n", message.pseudo, client_port);
                                printf("salut a tous c BG\n");
                            }
                        } else {
                            printf("Erreur: Le pseudo '%s' n'existe pas dans la table des clients.\n", message.pseudo);
                            printf("salut a tous c david\n");
                            // TODO : Gérer erreur
                        }
                    }
                } else if (strcmp(message.order, "disconnect") == 0) {
                    if (playSocket != -1) {
                        closeSocket(&playSocket);
                        printf("Socket de jeu fermée suite à la commande 'disconnect'.\n");
                    } else {
                        printf("Aucune socket de jeu ouverte à fermer.\n");
                    }
                } else {
                    // TODO Gérer l'ordre inconnu (réponse à python ?)
                }
                
                free(message.order);
                free(message.pseudo);
            }
        }

        count = count + 1;
        // BROADCAST SOCKET
        if (search_active) {
            handle_search(broadcastSocket, tcpSocket);
        }

        if (sharing_active && count > 50) {
            count = 0;
            handle_share(broadcastSocket, sharing_json);
        }
    }

    closeSocket(&tcpSocket);
    closeSocket(&broadcastSocket);

    return 0;
}
