import struct
import pickle
import socket
from network.pymsg_type import *
import subprocess
import os
import random
import ipaddress
import ctypes

class Network:
    instance = None

    def __init__(self):
        self.process = 0
        self.port = 0
        self.clientList = {"Red": None, "Blue": None, "Green": None, "Purple": None}
        self.this_client = None
        self.c_socket = None
        self.s_socket = None
        self.s_port = random.randint(3000, 4000)

    def init_listen(self):
        self.initiate_socket()
        self.run_c_process()
        self.accept_socket()


    def initiate_socket(self):
        host = ''
        self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s_socket.bind((host, self.s_port))
        self.s_socket.listen(1)
        return self.s_socket
    
    def kill_c_process(self):
        try:
            # Send the termination signal to the process
            os.kill(self.process.pid, 9)  # 9 is the signal number for SIGKILL
            print(f"Process with PID {self.process.pid} has been killed.")
        except OSError as e:
            print(f"Failed to kill process with PID {self.process.pid}: {e}")
    def close_socket(self):
        self.c_socket.close()
        self.s_socket.close()
        self.kill_c_process()
        for key, value in self.clientList.items():
            if value != None:
                self.clientList[key] = None

    def run_c_process(self):
        from GameControl.EventManager import EtatJeu
        etat = EtatJeu.getEtatJeuInstance()
        path = "./network/client"
        if not os.path.exists(path):
            print("Client not found")
            etat.kill()
            return
        c_file = [path, str(self.s_port)]
        self.process = subprocess.Popen(c_file)

    def accept_socket(self):
        self.c_socket, addr = self.s_socket.accept()
        print('[Py] Connected by', addr)
        packet = Package(PYMSG_CONNECT_OK)
        self.send_package(packet)
        print("[Py] Accepted")
        return self.c_socket

    # def listen_socket(self):
    #     while True: 
    #         pkg = Package(0)
    #         size = self.receive_package(pkg)
    #         # print("Received:", size )
    #         # print(pkg.port, pkg.type, pkg.size)
    #         # pkg = init_package()
    #         # send_package(pkg)

    def receive_package(self, pkg):
        self.c_socket.setblocking(0)
        try:
            data = self.c_socket.recv(9)
            size = len(data)
            if size == 0:
                return size
            pkg.unpackHeader(data)
        except BlockingIOError:
            return 0
        if pkg.size != 0:
            self.c_socket.setblocking(1)
            data = self.c_socket.recv(pkg.size)
            if len(data):
                size += len(data)
                pkg.toBytes(data)
        print("[Py] [Receive] Type:", pkg.type, "Port:", pkg.port, "Size:", pkg.size)
        self.c_socket.setblocking(1)
        return size

    def flush_socket(self):
        s = self.c_socket.recv(1024)
        
    def send_package(self, pkg):
        self.c_socket.setblocking(1)
        self.c_socket.sendall(pkg.byte)
        print("[Py] [Send] Size:", pkg.size, "Type:", pkg.type, "Port:", pkg.port)
    
    def listen(self):
        pkg = Package(0)
        size = self.receive_package(pkg)
        if size == 0:
            return
        else:
            self.msg_handler(pkg)

    def pack_ip_port(self, ip, port):
        ip_add = ip_to_int(ip)
        print(ip_add)
        byte = struct.pack('!I', ip_add)
        byte += struct.pack('I', port)
        return byte
    
    
    def msg_handler(self, pkg):
        if pkg.type == PYMSG_REP_PORT:
            self.assign_port(pkg)
        elif pkg.type == PYMSG_CLIENT_ADD:
            self.add_client(pkg)
        elif pkg.type == PYMSG_CLIENT_REMOVE:
            self.remove_client(pkg)
        elif pkg.type == PYMSG_GAME_READY:
            for key, value in self.clientList.items():
                if value != None and value.port == pkg.port:
                    value.ready = True
                    break

    def assign_port(self, pkg):
        self.port = pkg.port
        main_client = Client( self.port, struct.unpack('B', pkg.byte)[0], True)
        if main_client.color == 1:
            self.clientList["Red"] = main_client
        elif main_client.color == 2:
            self.clientList["Blue"] = main_client
        elif main_client.color == 3:
            self.clientList["Green"] = main_client
        elif main_client.color == 4:
            self.clientList["Purple"] = main_client
        self.this_client = main_client
        print(self.clientList)

    def remove_client(self, pkg):
        for key, value in self.clientList.items():
            if value != None and value.port == pkg.port:
                self.clientList[key] = None
                print("[Py] Player", key, "removed")
                break

    def add_client(self, pkg):
        player = Client(pkg.port, struct.unpack('B', pkg.byte)[0], False)
        if player.color == 1:
            self.clientList["Red"] = player
        elif player.color == 2:
            self.clientList["Blue"] = player
        elif player.color == 3:
            self.clientList["Green"] = player
        elif player.color == 4:
            self.clientList["Purple"] = player

    @staticmethod
    def getNetworkInstance():
        if Network.instance == None:
            Network.instance = Network()
        return Network.instance


def init_package():
    bob = BobStatus()
    data1 = Data(1)
    data1.setData(bob)
    data2 = Data(2)
    data2.setData(bob)
    pkg = Package(0)
    pkg.addData(data1)
    pkg.addData(data2)
    return pkg

def ip_to_int(ip_address):
    # Parse the IP address
    ip = ipaddress.IPv4Address(ip_address)
    return int(ip)




class Package:
    def __init__(self, type):
        net = Network.getNetworkInstance()
        self.type = type
        self.port = net.port
        self.size = 0
        self.data = []
        self.byte = b''
        self.packHeader()

    def addData(self, data):
        self.data.append(data)


    def packData(self):
        if self.data == [] and self.size == 0:
            self.packHeader()
            return self.byte
        else:
            dat = pickle.dumps(self.data)
            self.size = len(dat)
            self.packHeader()
            self.byte += dat
            return self.byte
    
    def packHeader(self):
        self.byte = struct.pack('B',self.type)
        self.byte += struct.pack('I',self.port)
        self.byte += struct.pack('I',self.size)


    def concatData(self, data):
        self.size += len(data)
        self.packHeader()
        self.byte += data

    def unpackHeader(self, data):
        self.type = struct.unpack('B', data[0:1])[0]
        self.port = struct.unpack('I', data[1:5])[0]
        self.size = struct.unpack('I', data[5:9])[0]
    
    def toBytes(self, data):
        self.byte = data

class Data:
    def __init__(self, type):
        self.type = type
        self.data = None

    def setData(self, data):
        self.data = data

class BobStatus:
    def __init__(self):
        self.id = 1
        self.energy = 100
        self.mass = 100
        self.velolcity = 0
        self.currentPos = (1, 1)
        self.previousPos = [(1, 0), (1, 1)]

class Client:
    def __init__(self, port, color, is_this_client):
        self.port = port
        self.color = color
        self.listBob = []
        self.ready = False
        self.is_this_client = is_this_client

    def addBob(self, bob):
        self.listBob.append(bob)
    
    def removeBob(self, bob):
        self.listBob.remove(bob)
