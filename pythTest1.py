import json

# Création d'un dictionnaire contenant des données
id_tram = 0
datasize = 1
my_iD = 1
data = {"id_tram":id_tram, "DATA_SIZE":datasize, "DATA":, "senderID":}

# Chemin du fichier où vous souhaitez écrire les données JSON
chemin_fichier = "C:/Users/d3velopp/Desktop/Work_Project_CNewtork/data.json"

# Écriture des données JSON dans le fichier
with open(chemin_fichier, "w") as f:
    json.dump(data, f)

print("Données écrites avec succès dans le fichier JSON.")
