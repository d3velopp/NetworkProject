#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <json-c/json.h>
#include <unistd.h>

#define JSON_FILE "data.json"

void write_json_file(const char *filename, struct json_object *jobj) {
    FILE *fp = fopen(filename, "w");
    if (fp == NULL) {
        perror("Erreur lors de l'ouverture du fichier pour mise à jour");
        return;
    }
    const char *json_str = json_object_to_json_string_ext(jobj, JSON_C_TO_STRING_PRETTY);
    fprintf(fp, "%s", json_str);
    fclose(fp);
}

struct json_object* generate_random_data(int num_entries) {
    struct json_object *jarray = json_object_new_array();
    for (int i = 0; i < num_entries; i++) {
        int random_data = rand() % 100000; // Générer un nombre aléatoire entre 0 et 99999
        struct json_object *jint = json_object_new_int(random_data);
        json_object_array_add(jarray, jint);
    }
    return jarray;
}

int main() {
    srand(time(NULL));
    while (1) {
        struct json_object *jobj = json_object_new_object();
        struct json_object *random_data = generate_random_data(5);

        json_object_object_add(jobj, "donnees_recues", random_data);
        write_json_file(JSON_FILE, jobj);

        printf("Données aléatoires écrites sur le fichier JSON : %s\n", json_object_to_json_string_ext(random_data, JSON_C_TO_STRING_PRETTY));

        json_object_put(jobj); // Libérer la mémoire

        // Pause pour espacer les itérations
        sleep(1);
    }
    return 0;
}
