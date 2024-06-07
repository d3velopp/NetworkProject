#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cJSON.h"
#include "json_reader.h"

/**
    Lis le json et récupère les informations
*/
JSON_Message lire_json(const char *json_string) {
    JSON_Message message = {NULL, NULL, NULL}; 
    
    cJSON *racine = cJSON_Parse(json_string);
    if (!racine) {
        fprintf(stderr, "Erreur lors de l'analyse du JSON.\n");
        return message;
    }

    cJSON *order = cJSON_GetObjectItemCaseSensitive(racine, "order");
    cJSON *pseudo = cJSON_GetObjectItemCaseSensitive(racine, "pseudo");
    cJSON *port = cJSON_GetObjectItemCaseSensitive(racine, "port");

    if (cJSON_IsString(order) && cJSON_IsString(pseudo) &&
        order->valuestring && pseudo->valuestring) {
        message.order = strdup(order->valuestring);
        message.pseudo = strdup(pseudo->valuestring);
        printf("Order reçu : %s, Pseudo reçu : %s\n", message.order, message.pseudo);
    }

    if (cJSON_IsString(port)) {
        // convertion en entier
        message.port = atoi(port->valuestring);
    }

    cJSON_Delete(racine);
    return message;
}




int is_valid_json(const char *json_string) {
    cJSON *racine = cJSON_Parse(json_string);
    if (racine) {
        cJSON_Delete(racine);
        return 1; // La chaîne est un JSON valide
    }
    return 0; // La chaîne n'est pas un JSON valide
}

char *add_attribute_to_json(const char *original_json, const char *key, const char *value) {
    cJSON *json = cJSON_Parse(original_json);
    if (!json) {
        fprintf(stderr, "Erreur lors de l'analyse du JSON dans add_attribute_to_json.\n");
        return NULL;
    }

    cJSON_AddStringToObject(json, key, value);

    char *updated_json_string = cJSON_PrintUnformatted(json);
    cJSON_Delete(json); // Ne pas oublier de supprimer l'objet cJSON

    if (!updated_json_string) {
        fprintf(stderr, "Erreur lors de la création de la chaîne JSON dans add_attribute_to_json.\n");
        return NULL;
    }

    // Afficher la chaîne JSON modifiée (facultatif)
    //printf("JSON mis à jour avec l'attribut ajouté : %s\n", updated_json_string);

    return updated_json_string;
}


void remove_attribute_from_json(const char *json_string, const char *key) {
    cJSON *racine = cJSON_Parse(json_string);
    if (!racine) {
        fprintf(stderr, "Erreur lors de l'analyse du JSON dans remove_attribute_from_json.\n");
        return;
    }

    cJSON_DeleteItemFromObject(racine, key);

    char *updated_json_string = cJSON_PrintUnformatted(racine);
    cJSON_Delete(racine);
    printf("JSON mis à jour avec l'attribut supprimé : %s\n", updated_json_string);
    free(updated_json_string);
}