#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>


#define SERVER_ADDRESS "127.0.0.1"
//#define PYTHON_SERVER_PORT 12346
#include <string.h>

char* listen_server(int PORT)
{
    int server_socket, client_socket;
    struct sockaddr_in server_address, client_address;
    char buffer[10000];
    
    // Création du socket
    if ((server_socket = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
    
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(PORT);
    
    // Attachement du socket à l'adresse et au port
    if (bind(server_socket, (struct sockaddr *)&server_address, sizeof(server_address))<0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    
    // Attente de connexion
    if (listen(server_socket, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    
    // Acceptation de la connexion entrante
    int addrlen = sizeof(client_address);
    printf("en attente de connexion : \n");
    if ((client_socket = accept(server_socket, (struct sockaddr *)&client_address, (socklen_t*)&addrlen))<0) {
        perror("accept");
        exit(EXIT_FAILURE);
    }
    
    // Lecture des données envoyées par le client
    int bytes_received = read(client_socket, buffer, sizeof(buffer));
    if (bytes_received < 0) {
        perror("read failed");
        exit(EXIT_FAILURE);
    }
    printf("Data received : %s\n", buffer);

    // Allouer de la mémoire pour la chaîne de retour
    char* return_str = malloc(10000);
    if (return_str == NULL) {
        perror("malloc failed");
        exit(EXIT_FAILURE);
    }
    printf("%s",return_str);

    // Copier les données reçues dans la chaîne de retour
    strncpy(return_str, buffer, bytes_received);
    return_str[bytes_received] = '\0';  // Assurez-vous que la chaîne est terminée par NULL


    return return_str;
}


void send_server(int PORT, char *message)
{
    int client_socket;
    struct sockaddr_in server_addr;
    int server_port = PORT;

    // Créer un socket client
    client_socket = socket(AF_INET, SOCK_STREAM, 0);
    
    // Spécifier l'adresse du serveur et se connecter
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(server_port);
    inet_pton(AF_INET, SERVER_ADDRESS, &server_addr.sin_addr);
    
    connect(client_socket, (struct sockaddr *)&server_addr, sizeof(server_addr));

    // Échanger des données avec le serveur
    send(client_socket, message, strlen(message), 0);

}