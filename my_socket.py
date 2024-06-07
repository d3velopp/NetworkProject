import socket
import select

class SocketCommunication:
    def __init__(self, host='localhost', port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(1)
        self.connection, self.address = self.socket.accept()
        self.socket.setblocking(False)

    def send_data(self, data):
        self.connection.sendall(data.encode())

    def receive_data(self):
        try:
            # select pour vérifier si la socket est prête à être lue
            readable, _, _ = select.select([self.connection], [], [], 0)
            if self.connection in readable:
                data = self.connection.recv(1024)
                if data:
                    return data.decode()
        except Exception as e:
            print(f"Error receiving data: {e}")
        return None

    def close_connection(self):
        self.connection.close()