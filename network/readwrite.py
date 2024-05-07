import pickle
import struct

port = 0

PYMSG_REQ_PORT = 30
PYMSG_REP_PORT = 31
PYMSG_CONNECT_OK = 32


class Package:
    def __init__(self, type):
        global port
        self.type = type
        self.port = port
        self.size = 0
        self.data = []

    def addData(self, data):
        self.data.append(data)


    def packData(self):
        if self.data == [] and self.size == 0:
            a = struct.pack('BII',self.type, self.port ,self.size)
            print(a);
            return a
        else:
            dat = pickle.dumps(self.data)
            self.size = len(dat)
            a = struct.pack('BII',self.type, self.port ,self.size)
            a += dat
            return a
    
    def unpackHeader(self, data):
        self.type, self.port, self.size = struct.unpack('BII', data)
    
    def unpackData(self, data):
        self.data = pickle.loads(data)

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

import socket

c_socket = None

def initiate_socket():
    host = ''
    port = 3000         # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    return s

def accept_socket(s):
    global c_socket, port
    c_socket, addr = s.accept()
    print('Connected by', addr)
    packet = Package(PYMSG_REQ_PORT)
    send_package(packet)
    while packet.type != PYMSG_REP_PORT:
        packet = Package(PYMSG_REQ_PORT)
        send_package(packet)
        s = receive_package(packet)
        print("Received", s)
    port = packet.port
    packet = Package(PYMSG_CONNECT_OK)
    send_package(packet)
    print("Accepted")
    return c_socket

def listen_socket():
    global c_socket
    while True: 
        pkg = Package(0)
        size = receive_package(pkg)
        # print("Received:", size )
        # print(pkg.port, pkg.type, pkg.size)
        # pkg = init_package()
        # send_package(pkg)



def receive_package(pkg):
    global c_socket, port
    c_socket.setblocking(0)
    try:
        data = c_socket.recv(12)
        size = len(data)
        print(size)
        if size == 0:
            return size
    except BlockingIOError:
        return 0
    pkg.unpackHeader(data)
    if pkg.size != 0:
        c_socket.setblocking(1)
        data = c_socket.recv(pkg.size)
        if len(data):
            size += len(data)
            pkg.unpackData(data)
    print("Size: ", size)
    return size

def flush_socket():
    global c_socket
    s = c_socket.recv(1024)
    
def send_package(pkg):
    global c_socket
    data = pkg.packData()
    c_socket.setblocking(1)
    c_socket.sendall(data)

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


socket = initiate_socket()
accept_socket(socket)
listen_socket()





