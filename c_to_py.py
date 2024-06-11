import json
import time

JSON_FILE = 'data.json'

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def main():
    while True:
        try:
            data = read_json_file(JSON_FILE)
            print(f"Données reçues : {json.dumps(data['donnees_recues'], indent=4)}")
        except FileNotFoundError:
            print(f"Erreur : le fichier {JSON_FILE} est introuvable.")
            return
        except json.JSONDecodeError:
            print(f"Erreur : le fichier {JSON_FILE} est corrompu.")
            return

        # Pause pour espacer les itérations (attendre que le fichier soit mis à jour)
        time.sleep(1)

if __name__ == "__main__":
    main()
