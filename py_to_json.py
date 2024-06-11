import json
import random
import time

JSON_FILE_1 = 'client_1.json'
JSON_FILE_2 = 'client_2.json'

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def generate_random_data(num_entries):
    return [random.randint(0, 99999) for _ in range(num_entries)]

def main():
    while True:
        # Lire le fichier JSON client_1.json pour la configuration initiale
        try:
            data_1 = read_json_file(JSON_FILE_1)
            print(f"Données reçues (client_1.json) : {json.dumps(data_1['donnees_recues'], indent=4)}")
        except FileNotFoundError:
            print(f"Erreur : le fichier {JSON_FILE_1} est introuvable.")
            return
        except json.JSONDecodeError:
            print(f"Erreur : le fichier {JSON_FILE_1} est corrompu.")
            return

        # Lire le fichier JSON client_2.json pour la configuration initiale
        try:
            data_2 = read_json_file(JSON_FILE_2)
            print(f"Données reçues (client_2.json) : {json.dumps(data_2['donnees_recues'], indent=4)}")
        except FileNotFoundError:
            print(f"Erreur : le fichier {JSON_FILE_2} est introuvable.")
            return
        except json.JSONDecodeError:
            print(f"Erreur : le fichier {JSON_FILE_2} est corrompu.")
            return

        # Génération de données aléatoires
        random_data = generate_random_data(5)
        
        # Mise à jour des données dans data_2
        data_2['donnees_recues'] = random_data
        
        # Écriture dans le fichier JSON client_2.json
        write_json_file(JSON_FILE_2, data_2)
        print(f"Données aléatoires écrites sur le fichier JSON (client_2.json) : {json.dumps(random_data, indent=4)}")
        
        # Pause (facultatif) pour espacer les itérations
        time.sleep(1)

if __name__ == "__main__":
    main()
