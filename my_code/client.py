import socket
import pickle
import sys


def send_data(trame, port, host):

    # Créer un socket TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Se connecter au serveur
    client.connect((host, port))
    print("Connexion établie avec le serveur C \n")

    # Envoyer des données au serveur
    client.sendall(trame)


def receive_data(port, host):
    # Adresse IP et port du serveur
    SERVER_IP = host
    SERVER_PORT = port

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
    data = client_socket.recv(10000)
    return data


class AllPlayerData:
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

class Testing:
    def __init__(self, word):
        self.word = word

host = '127.0.0.1'  # Adresse IP du serveur
my_port = int(sys.argv[1])
C_port = int(sys.argv[2])
mode = int(sys.argv[3])
#send_data(mode, C_port, host)

while True:        
    if (mode == 1):

        #donnée fictif
        bob_settings = [[(1,2),(3,4)],[5,6],[7,8],[9,10],[11,12],[13,14],[15,16]]
        food_settings = [[(17,18),(19,20),(21,22)]]
        mydata = AllPlayerData(2,bob_settings, 3, food_settings)


        #tram fictif
        tram =  Testing("bonjour") #TRAM(10, mydata, 123, 567)
        tram_serial = pickle.dumps(tram)
        print(tram_serial)
        send_data(tram_serial,C_port,host)
        mode = 0

    elif (mode ==0):
        data = receive_data(my_port, host)
        #print(data)
        received_tram = pickle.loads(data)
        #print("Données reçues de C - bob_coord:", received_tram.data.List_BOB_COORD)
        print("Données reçues :", receive_data.word)
        mode = 1




# la chaine en entier [10,[2,[[(1,2),(3,4)],[5,6],[7,8],[9,10],[11,12],[13,14],[15,16]], 3, [[(17,18),(19,20),(21,22)]]], 123,567]

#sérialiser la tram
#tram_serial = pickle.dumps(tram)
#print(tram_serial)



