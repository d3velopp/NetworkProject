import json
import random
import time

JSON_FILE = 'data.json'

def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def generate_random_data(num_entries):
    return [random.randint(0, 99999) for _ in range(num_entries)]

def main():
    while True:
        # Génération de données aléatoires
        random_data = generate_random_data(5)
        
        # Création de l'objet JSON
        data = {
            "donnees_recues": random_data
        }

        # Écriture dans le fichier JSON
        write_json_file(JSON_FILE, data)
        print(f"Données aléatoires écrites sur le fichier JSON : {json.dumps(random_data, indent=4)}")
        
        # Pause pour espacer les itérations
        time.sleep(1)

if __name__ == "__main__":
    main()
