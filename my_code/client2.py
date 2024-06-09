import socket
import pickle

class DATA:
    def __init__(self, nb_bob, list_bob_settings, nb_food, list_food_settings):
        self.Nb_BOB = nb_bob
        self.List_BOB_COORD = list_bob_settings[0]
        self.List_BOB_ID = list_bob_settings[1]
        self.List_BOB_MASS = list_bob_settings[2]
        self.List_BOB_PERCEP = list_bob_settings[3]
        self.List_BOB_MEM = list_bob_settings[4]
        self.List_BOB_SPEED = list_bob_settings[5]
        self.List_BOB_ENERGY = list_bob_settings[6]
        self.Nb_FOOD = nb_food
        self.List_FOOD_COORD = list_food_settings[0]

class TRAM:
    def __init__(self, datasize, data, senderID, receiverID):
        self.datasize = datasize
        self.data = data
        self.senderID = senderID
        self.receiverID = receiverID

# Adresse IP et port du serveur
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12346

# Création du socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Liaison du socket à l'adresse et au port
server_socket.bind((SERVER_IP, SERVER_PORT))

# Attente de connexion
server_socket.listen(1)

print("Attente de connexion...")

# Acceptation de la connexion entrante
client_socket, client_address = server_socket.accept()

print("Connexion établie avec", client_address)

# Réception des données sérialisées
data = client_socket.recv(1024)

# Désérialisation des données
received_tram = pickle.loads(data)

# Affichage des données reçues
print("Données reçues de C - bob_coord:", received_tram.data.List_BOB_COORD)

# Fermeture du socket
client_socket.close()
