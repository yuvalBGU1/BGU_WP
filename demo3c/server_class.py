import socket


class Server:
    def __init__(self, ip = 'satts', host = 0):
        self.ip = ip
        self.host = host
        self.connect()


    def connect(self):
        print(socket.getaddrinfo('satts', 5555))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        server_address = (self.ip, self.host)  # Bind the socket to a specific address and port
        server_socket.bind(server_address)

        server_socket.listen(2)  # Bind the socket to a specific address and port
        print("Waiting for a connection...")

        self.sender, client_address = server_socket.accept()  # Accept a connection from a client
        self.reciver, client_address = server_socket.accept()
        print("Connected to Sender and Reciver")


    def sends_text(self):
        while True:

            # Receive data from one client
            data = self.sender.recv(1024)
            if not data:
                print('hi')
                break
            print(data)

            # Send data to the other client
            self.reciver.sendall(data)


def main():
    ser = Server(ip = '169.254.208.240',host=5555)
    # ser.connect()
    print('hoiiiiigfdisojewqpfkvfdnbkvorde')
    ser.sends_text()


if __name__ == "__main__":
    main()


