#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <json-c/json.h>

#define JSON_FILE "data.json"

void read_json_file(const char *filename) {
    struct json_object *parsed_json;
    struct json_object *donnees_recues;
    FILE *fp = fopen(filename, "r");
    char buffer[1024];

    if (fp == NULL) {
        perror("Erreur lors de l'ouverture du fichier JSON");
        return;
    }

    fread(buffer, 1024, 1, fp);
    fclose(fp);

    parsed_json = json_tokener_parse(buffer);

    // Extraction des données du fichier JSON
    json_object_object_get_ex(parsed_json, "donnees_recues", &donnees_recues);

    // Utiliser les données extraites du JSON comme nécessaire
    printf("Données reçues : %s\n", json_object_to_json_string_ext(donnees_recues, JSON_C_TO_STRING_PRETTY));
}

int main() {
    while (1) {
        read_json_file(JSON_FILE);

        // Pause pour espacer les itérations (attendre que le fichier soit mis à jour)
        sleep(1);
    }

    return 0;
}
