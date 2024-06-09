# Définir le compilateur
CC = gcc

# Définir les options de compilation
CFLAGS = -Wall -Wextra -Werror

# Définir les fichiers sources
SOURCES = C_client.c network.c

# Définir le nom du fichier exécutable
EXECUTABLE = client

# Règle par défaut
all: $(EXECUTABLE)

# Règle pour générer l'exécutable
$(EXECUTABLE): $(SOURCES)
	$(CC) $(CFLAGS) -o $@ $^

# Règle pour nettoyer les fichiers générés
clean:
	rm -f $(EXECUTABLE)

# Règle pour forcer la recompilation
re: clean all
