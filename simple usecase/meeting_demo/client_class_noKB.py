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


class Client:

    def __init__(self, ip, host):
        self.ip = ip
        self.host = host
        self.speaker = 0  # speaker turn
        self.text_queue = queue.Queue()  # Global queue to hold the text to be read
        self.queue_lock = threading.Lock()  # Lock for synchronizing access to the text queue

        print('Build STT')
        self.connection()
        print('Build STT')
        self.cheetah = self.build_cheetah()

    def connection(self):
        print("Waiting for a connection...")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.ip, self.host))
        print("Connected!")
        self.client_socket = client_socket

    def build_cheetah(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--access_key', default='usoc8dB3k01E0DByG2Fl9AaChlkJYBM31HSzSYe6xdO5hgY0eT0SKQ==',
            help='AccessKey obtained from Picovoice Console (https://console.picovoice.ai/)')
        parser.add_argument(
            '--library_path',
            help='Absolute path to dynamic library. Default: using the library provided by `pvcheetah`')
        parser.add_argument(
            '--model_path',
            help='Absolute path to Cheetah model. Default: using the model provided by `pvcheetah`')
        parser.add_argument(
            '--endpoint_duration_sec',
            type=float,
            default=1.,
            help='Duration in seconds for speechless audio to be considered an endpoint')
        parser.add_argument(
            '--disable_automatic_punctuation',
            action='store_true',
            help='Disable insertion of automatic punctuation')
        parser.add_argument('--audio_device_index', type=int, default=0, help='Index of input audio device')
        parser.add_argument('--show_audio_devices', default=False, action='store_true',
                            help='Only list available devices and exit')
        global ARGS
        ARGS = parser.parse_args()
        if ARGS.show_audio_devices:
            for index, name in enumerate(PvRecorder.get_available_devices()):
                print('Device #%d: %s' % (index, name))
            return

        if not ARGS.access_key:
            print('--access_key is required.')
            return
        global CHEETAH
        CHEETAH = create(
            access_key=ARGS.access_key,
            library_path=ARGS.library_path,
            model_path=ARGS.model_path,
            endpoint_duration_sec=ARGS.endpoint_duration_sec,
            enable_automatic_punctuation=not ARGS.disable_automatic_punctuation)
        print('Cheetah version : %s' % CHEETAH.version)
        return CHEETAH

    def sender(self):
        recorder = PvRecorder(frame_length=self.cheetah.frame_length, device_index=ARGS.audio_device_index)
        recorder.start()
        print('Listening... (press Ctrl+C to stop)')
        print("Speak Now!")

        while True:
            partial_transcript, is_endpoint = self.cheetah.process(recorder.read())
            if partial_transcript != '':
                self.client_socket.send(partial_transcript.encode())
                print(f"Record {partial_transcript}")
            if is_endpoint:
                text_to_socket = self.cheetah.flush()
                self.client_socket.send(text_to_socket.encode())
                print(f"Record {text_to_socket}")

            recorder.stop()
            print('Stop Recording!!')

    def reciver(self):
        while True:
            data = self.client_socket.recv(1024).decode()
            if not data:
                continue
            self.text_queue.put(data)

    def engine(text):
        mp3_fp = BytesIO()
        tts = gTTS(text, lang='en', slow=False)
        tts.write_to_fp(mp3_fp)
        return mp3_fp

    def reader(self):
        pygame.init()
        pygame.mixer.init()
        while True:
            if self.speaker == 2:
                text = self.text_queue.get()
                if text is None:
                    continue
                print(f'Engine: {text}')
                text_l = len(text)
                sound = self.engine(text)
                sound.seek(0)
                pygame.mixer.music.load(sound)
                pygame.mixer.music.play()
                time.sleep(0.1 * text_l ** 0.5)
                print('-' * 50)
