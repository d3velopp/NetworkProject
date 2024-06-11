#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <json-c/json.h>
#include <pthread.h>
#include <unistd.h> 

#define BUF_SIZE 1024
#define JSON_FILE "client_2.json"

void update_json_file(const char *filename, struct json_object *jobj) {
    // Écriture de l'objet JSON mis à jour dans le fichier
    FILE *fp = fopen(filename, "w");
    if (fp == NULL) {
        perror("Erreur lors de l'ouverture du fichier pour mise à jour");
        return;
    }
    const char *updated_json_str = json_object_to_json_string(jobj);
    fprintf(fp, "%s", updated_json_str);
    fclose(fp);
}

void *receive_data(void *args) {
    int sockfd = *((int *)args);
    struct sockaddr_in cliaddr;
    socklen_t len = sizeof(cliaddr);
    char recv_buffer[BUF_SIZE]; // Tampon dédié à la réception des données du socket
    char file_buffer[BUF_SIZE]; // Tampon dédié à la lecture du fichier JSON

    while (1) {
        int n = recvfrom(sockfd, recv_buffer, BUF_SIZE, 0, (struct sockaddr *)&cliaddr, &len);
        recv_buffer[n] = '\0';
        
        // Ouvrir le fichier JSON pour mise à jour
        FILE *fp = fopen(JSON_FILE, "r");
        if (fp == NULL) {
            perror("Erreur lors de l'ouverture du fichier JSON");
            continue;
        }
        fread(file_buffer, 1, BUF_SIZE, fp); // Utiliser file_buffer pour lire le fichier
        fclose(fp);
        
        // Parser le contenu du fichier JSON lu dans file_buffer
        struct json_object *parsed_json = json_tokener_parse(file_buffer);
        struct json_object *donnees_recues;

        // S'assurer que le parsing a réussi avant de continuer
        if (parsed_json == NULL) {
            printf("Erreur lors du parsing du fichier JSON\n");
            continue;
        }

        json_object_object_get_ex(parsed_json, "donnees_recues", &donnees_recues);
        
        // Convertir les données reçues du socket en JSON et les ajouter
        struct json_object *new_data = json_object_new_int(atoi(recv_buffer));
        json_object_array_add(donnees_recues, new_data);
        
        // Mettre à jour le fichier JSON avec les nouvelles données reçues
        update_json_file(JSON_FILE, parsed_json);
        
        printf("Données reçues et mises à jour dans le fichier JSON.\n");
    }

    return NULL;
}


void send_data(struct json_object *les_adresses_destination, struct json_object *les_ports_destination, struct json_object *donnees_a_envoyer, int sockfd, struct sockaddr_in *cliaddr) {
    size_t nb_destinations = json_object_array_length(les_adresses_destination);
    for (size_t i = 0; i < nb_destinations; i++) {
        const char *addr = json_object_get_string(json_object_array_get_idx(les_adresses_destination, i));
        int port = json_object_get_int(json_object_array_get_idx(les_ports_destination, i));
        
        cliaddr->sin_family = AF_INET;
        cliaddr->sin_port = htons(port);
        inet_pton(AF_INET, addr, &cliaddr->sin_addr);
        
        size_t nb_data = json_object_array_length(donnees_a_envoyer);
        for (size_t j = 0; j < nb_data; j++) {
            int data = json_object_get_int(json_object_array_get_idx(donnees_a_envoyer, j));
            char message[BUF_SIZE];
            sprintf(message, "%d", data);
            
            sendto(sockfd, message, strlen(message), 0, (struct sockaddr *)cliaddr, sizeof(*cliaddr));
            printf("Données envoyées : %s à %s:%d\n", message, addr, port);
        }
    }
}


void send_ack(int sockfd, struct sockaddr_in *cliaddr) {
    const char *ack_message = "bien_reçu";
    sendto(sockfd, ack_message, strlen(ack_message), 0, (struct sockaddr *)cliaddr, sizeof(*cliaddr));
}


int main() {
    // Lire le fichier JSON pour la configuration initiale
    struct json_object *parsed_json, *mon_adresse, *mon_port, *les_adresses_destination, *les_ports_destination, *donnees_a_envoyer, *donnees_recues;
    FILE *fp = fopen(JSON_FILE, "r");
    char buffer[BUF_SIZE];

    if (fp == NULL) {
        perror("Erreur lors de l'ouverture du fichier JSON");
        return 1;
    }

    fread(buffer, BUF_SIZE, 1, fp);
    fclose(fp);

    parsed_json = json_tokener_parse(buffer);

    // Extraction des données du fichier JSON
    json_object_object_get_ex(parsed_json, "mon_adresse", &mon_adresse);
    json_object_object_get_ex(parsed_json, "mon_port", &mon_port);
    json_object_object_get_ex(parsed_json, "les_adresses_destination", &les_adresses_destination);
    json_object_object_get_ex(parsed_json, "les_ports_destination", &les_ports_destination);
    json_object_object_get_ex(parsed_json, "donnees_a_envoyer", &donnees_a_envoyer);
    json_object_object_get_ex(parsed_json, "donnees_recues", &donnees_recues);

    
    
    
    
    // Suite du code pour l'envoi et la réception des données UDP...
    
    // Création du socket UDP
    int sockfd;
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur de création du socket");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in servaddr, cliaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    int port = json_object_get_int(mon_port);
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY); // Écoute sur toutes les interfaces
    servaddr.sin_port = htons(port);

    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("Erreur de liaison");
        exit(EXIT_FAILURE);
    }

    // Démarrage du thread de réception


    pthread_t thread_id;
    if (pthread_create(&thread_id, NULL, receive_data, &sockfd) != 0) {
        perror("Impossible de créer le thread de réception");
        exit(EXIT_FAILURE);
    }

    // Envoi de données
    send_data(les_adresses_destination, les_ports_destination, donnees_a_envoyer, sockfd, &cliaddr);

    pthread_join(thread_id, NULL);

    close(sockfd);
    return 0;
}

