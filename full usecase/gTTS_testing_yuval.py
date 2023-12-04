import queue
import socket
import threading
import time
from typing import IO

import numpy as np
import pygame
from IPython.utils import timing
from gtts import gTTS
from io import BytesIO

from pydub import AudioSegment, silence

import real_time_vc as play

# Global var
text_queue = queue.Queue()  # Global queue to hold the text to be read
queue_lock = threading.Lock()  # Lock for synchronizing access to the text queue
reading_queue = queue.Queue()

sound_files_queue = queue.Queue()
sound_file_queue_lock = threading.Lock()


def engine(text):
    mp3_fp = BytesIO()
    # print("Engine got text: " + text)
    tts = gTTS(text, lang='en', slow=False)
    tts.write_to_fp(mp3_fp)
    return mp3_fp


def read_text_from_queue():
    # initiating vars
    pygame.init()
    pygame.mixer.init()
    speaker_num = 273
    global_max = 0.6483659

    while True:
        file_path = sound_files_queue.get()
        if file_path is None:
            continue
        recording_chunks = play.stargan_soundcard_player(global_max, speaker_num, file_path)


def push_text_from_client_to_queue():
    """
        Initiating the reciving server.
        Creating a socket connection with the client
    """
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_address = ('127.0.0.1', 7777)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)

    print("Waiting for a connection...")

    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print("Connected to:", client_address)

    counter = 0
    while True:
        data_len_buffer = client_socket.recv(2)
        if data_len_buffer:
            data_len = int.from_bytes(data_len_buffer, 'big')
            data = client_socket.recv(data_len).decode()
            if not data:
                continue

            # convert to sound here
            counter += 1
            name_not_modidied = "./outputs/" + str(counter) + "_not_modified.mp3"
            name_modidied = "./outputs/" + str(counter) + "_modified.mp3"
            # print("resive from queue: " + data)
            tts = gTTS(data, lang='en', slow=False)
            # tts.stream()
            with open(name_not_modidied, "wb+") as f:
                tts.write_to_fp(f)
                f.seek(0)
                segment = AudioSegment.from_file(f, "mp3")
            silences = silence.detect_silence(segment, min_silence_len=10, silence_thresh=-500)
            for section in reversed(silences):
                if section[0] == 0:
                    segment = segment[section[1]:]
                if section[1] == len(segment):
                    segment = segment[:section[0]]

            f = open(name_modidied, "wb+")
            segment.export(f, format='mp3')

            f.close()
            sound_files_queue.put(name_modidied)
            with queue_lock:
                print("push to queue: " + data)
                text_queue.put(data)


def main():
    # Start the input thread
    input_thread = threading.Thread(target=push_text_from_client_to_queue)
    input_thread.start()

    # Start the read thread
    read_thread = threading.Thread(target=read_text_from_queue)
    read_thread.start()

    # Wait for the input thread to finish
    input_thread.join()
    read_thread.join()


def test_punctuation():
    # initiating vars
    pygame.init()
    pygame.mixer.init()
    mp3_fp = BytesIO()

    tts = gTTS("this is a punctuation test. trying, to see. how the model, is doing! good?", lang='en')
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    pygame.mixer.music.load(mp3_fp)
    pygame.mixer.music.play()


if __name__ == '__main__':
    main()

    # test_punctuation()
