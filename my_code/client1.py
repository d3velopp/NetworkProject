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

#donnée fictif
bob_settings = [[(1,2),(3,4)],[5,6],[7,8],[9,10],[11,12],[13,14],[15,16]]
food_settings = [[(17,18),(19,20),(21,22)]]
mydata = DATA(2,bob_settings, 3, food_settings)


#tram fictif
tram = TRAM(10, mydata, 123, 567)

# la chaine en entier [10,[2,[[(1,2),(3,4)],[5,6],[7,8],[9,10],[11,12],[13,14],[15,16]], 3, [[(17,18),(19,20),(21,22)]]], 123,567]

#sérialiser la tram
tram_serial = pickle.dumps(tram)
print(tram_serial)


# Créer un socket TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Définir l'adresse et le port du serveur
host = '127.0.0.1'  # Adresse IP du serveur
port = 12345        # Port sur lequel le serveur écoute

# Se connecter au serveur
client.connect((host, port))
print("Connexion établie avec le serveur C")

# Envoyer des données au serveur
client.sendall(tram_serial)

# Fermer la connexion
client.close()
