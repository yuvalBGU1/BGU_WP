import socket
import threading
import queue
import time

import keyboard
import pygame
from gtts import gTTS
from collections import deque
from io import BytesIO
from playsound import playsound
from pygame import mixer
from pvcheetah import CheetahActivationLimitError, create
from pvrecorder import PvRecorder
import os
import argparse
import json

class Server:
    def __init__(self, ip, host, n = 2):
        self.ip = ip
        self.host = host
        self.n = n

        self.connect()

    def connect(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        server_address = (self.ip, self.host)  # Bind the socket to a specific address and port
        server_socket.bind(server_address)

        server_socket.listen(self.n)  # Bind the socket to a specific address and port
        print("Waiting for a connection...")

        self.client1, client_address = server_socket.accept()  # Accept a connection from a client
        self.client2, client_address = server_socket.accept()
        print("Connected to:", client_address)

    def client_handler(self, client_socket, other_socket):
        while True:
            # Receive message from this client
            message = client_socket.recv(1024)
            if not message:
                continue
            # Forward the message to the other client
            other_socket.sendall(message)




    def manager(self):
        threading.Thread(target=self.client_handler, args=(self.client1, self.client2)).start()
        threading.Thread(target=self.client_handler, args=(self.client2, self.client1)).start()



def main():
    ip = '192.168.1.107'
    host = 7777
    server = Server(ip, host)
    time.sleep(10)
    server.manager()

if __name__ == '__main__':
    main()





