import socket
import threading
import os
import json
import wave
from vosk import Model, KaldiRecognizer
import pyaudio
import time

class Sender:
    def __init__(self, ip = 'satts', host = 0, speakers = ['001'], mode = 'mic'):
        self.ip = ip
        self.host = host
        self.speaker_ls = speakers
        self.connect()
        print('connect')
        if mode.lower() == 'mic':
            self.model = self.build_vosk()
        else:
            pass



    def build_vosk(self):
        model_path = "C:\\Users\\Administrator\\Downloads\\vosk-model-small-en-us-0.15"
        return Model(model_path)


    def build_cheetah(self):
        pass


    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.ip, self.host)
        self.client_socket.connect(server_address)
        self.client_socket.send("sen".encode())


    def send(self):
        self.p = pyaudio.PyAudio()
        stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=8000)
        stream.start_stream()
        print("started stream")

        # Create a recognizer
        recognizer = KaldiRecognizer(self.model, 44100)

        while True:
            data = stream.read(1024, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):  # returns true when detecting silence
                result = recognizer.Result()
                result_dict = json.loads(result)
                if 'text' in result_dict and result_dict['text']:
                    print("text: " + result_dict['text'])
                    for part in result_dict['text'].split(" "):
                        # input()
                        buffer = part.encode()
                        buffer_len = len(buffer)
                        self.client_socket.send(buffer_len.to_bytes(2, 'big'))
                        self.client_socket.send(buffer)
            else:
                result = recognizer.PartialResult()
                result_dict = json.loads(result)
                if 'partial' in result_dict and result_dict['partial']:
                    print("partial: " + result_dict['partial'])
                    for part in result_dict['partial'].split(" "):
                        # input()
                        buffer = part.encode()
                        buffer_len = len(buffer)
                        self.client_socket.send(buffer_len.to_bytes(2, 'big'))
                        self.client_socket.send(buffer)
                    recognizer.Reset()
                    # print(result_dict)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Close PyAudio
        self.p.terminate()




def main():
    sen = Sender(ip = "192.168.1.116", host= 5555)
    time.sleep(3)
    sen.send()

if __name__ == '__main__':
    main()
