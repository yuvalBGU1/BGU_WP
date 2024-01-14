import socket

from RealtimeTTS import SystemEngine, TextToAudioStream, CoquiEngine


class Reciver:
    def __init__(self, ip='127.0.0.1', host=5555, engine=0):
        self.client_socket = None
        self.ip = ip
        self.host = host
        self.connect()
        print('connect')
        if engine == 0:
            self.engine = SystemEngine()  # replace with your TTS engine
        else:
            if engine == 1:
                self.engine = CoquiEngine()
            else:
                self.engine = CoquiEngine(voice="vocals/id1/tr01.wav", speed=2.0)
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
    import socket
    import threading
    import torch
    import argparse

    from RealtimeTTS import TextToAudioStream, CoquiEngine, SystemEngine

    parser = argparse.ArgumentParser()
    # Cheetah arguments:
    parser.add_argument(
        '--TTS_engine', default=0,
        help='0 - system engine\n 1 - coqui engine\n 2 - coqui DF engine')
    parser.add_argument(
        '--ip', default='127.0.0.1')
    parser.add_argument(
        '--host', default=5555)
    rec = Reciver(ip=argparse.ip, host=argparse.host, engine=argparse.TTS_engine)

    print("is GPU available: " + str(torch.cuda.is_available()))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

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
