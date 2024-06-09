#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 12345
#define PYTHON_SERVER_IP "127.0.0.1"
#define PYTHON_SERVER_PORT 12346

int main() {
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
    printf("Data received from Python: %s\n", buffer);
    
    // Fermeture des sockets
    close(client_socket);
    close(server_socket);
    

    //je renvoie les données vers un autre python 
    // Envoi des données reçues vers un autre programme Python
    int python_socket;
    struct sockaddr_in python_server_address;

    // Création du socket pour communiquer avec le serveur Python
    if ((python_socket = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Python socket failed");
        exit(EXIT_FAILURE);
    }

    python_server_address.sin_family = AF_INET;
    python_server_address.sin_addr.s_addr = inet_addr(PYTHON_SERVER_IP);
    python_server_address.sin_port = htons(PYTHON_SERVER_PORT);

    // Connexion au serveur Python
    if (connect(python_socket, (struct sockaddr *)&python_server_address, sizeof(python_server_address)) < 0) {
        perror("Python connect failed");
        exit(EXIT_FAILURE);
    }

    // Envoi des données au serveur Python
    int bytes_sent = send(python_socket, buffer, bytes_received, 0);
    if (bytes_sent < 0) {
        perror("send failed");
        exit(EXIT_FAILURE);
    }
    // Fermeture du socket vers le serveur Python
    close(python_socket);

    return 0;
}
