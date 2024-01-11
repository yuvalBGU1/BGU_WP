import socket
import threading
import os
import json
import wave
from vosk import Model, KaldiRecognizer
import pyaudio
import socket
import threading
import time
import pydub

from RealtimeTTS import TextToAudioStream, SystemEngine, AzureEngine, ElevenlabsEngine


class Reciver:
    def __init__(self, ip='0', host=0):
        self.ip = ip
        self.host = host
        self.connect()
        print('connect')
        self.engine = SystemEngine()  # replace with your TTS engine
        print('made engine')
        self.stream = TextToAudioStream(self.engine)
        print('made stream')

    def read_text_from_queue(self):
        while True:
            self.stream.play()

    def get_text(self):
        print('starting!!!!!!')
        while True:
            data_len_buffer = self.client_socket.recv(2)
            if data_len_buffer:
                data_len = int.from_bytes(data_len_buffer, 'big')
                data = self.client_socket.recv(data_len).decode()
                if not data:
                    continue
                self.stream.feed(data)
                print("feed: " + data)

    def connect(self):

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.ip, self.host)
        self.client_socket.connect(server_address)
        self.client_socket.send("rec".encode())


def main():
    rec = Reciver(ip="132.72.80.206", host=5555)
    # Start the input thread
    input_thread = threading.Thread(target=rec.get_text)
    input_thread.start()

    # Start the read thread
    read_thread = threading.Thread(target=rec.read_text_from_queue)
    read_thread.start()

    # Wait for the input thread to finish
    input_thread.join()
    read_thread.join()


if __name__ == '__main__':
    main()
