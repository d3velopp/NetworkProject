#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char**argv) {
    // Chemin du fichier JSON à lire
    const char *chemin_fichier = "C:/Users/d3velopp/Desktop/Work_Project_CNewtork/data.json";
    // Ouvrir le fichier en lecture
    FILE *fichier = fopen(chemin_fichier, "r+");
    if (!fichier) {
        fprintf(stderr, "Impossible d'ouvrir le fichier.\n");
        return 1;
    }

    // Trouver la taille du fichier
    fseek(fichier, 0, SEEK_END);
    long taille_fichier = ftell(fichier);
    fseek(fichier, 0, SEEK_SET);

    // Allouer de la mémoire pour le contenu du fichier
    char *contenu = (char *)malloc(taille_fichier + 1);
    if (!contenu) {
        fclose(fichier);
        fprintf(stderr, "Allocation de mémoire échouée.\n");
        return 1;
    }

    // Lire le contenu du fichier dans la mémoire allouée
    fread(contenu, 1, taille_fichier, fichier);
    contenu[taille_fichier] = '\0';

    // Fermer le fichier
    fclose(fichier);

    // Maintenant, vous pouvez traiter la chaîne de caractères 'contenu' manuellement
    printf("Contenu du fichier JSON :\n%s\n", contenu);

    int donnee = 10;
    fprintf(fichier, "%d\n", donnee);
    

    // Libérer la mémoire allouée
    free(contenu);

    return 0;
}
