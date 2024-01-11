import socket
import threading
import os
import json
import wave
from vosk import Model, KaldiRecognizer
import pyaudio
import time


class Sender:
    def __init__(self, ip='satts', host=0, speakers=['LJ001'], mode='mic'):
        self.ip = ip
        self.host = host
        self.speaker_ls = speakers
        self.directory = 'C:\\Users\\Administrator\\Desktop\\git_proj\\BGU_WP'
        self.data = {}
        self.wavs = {}
        self.csv = {}
        # self.connect()
        print('connect')
        # if mode.lower() == 'mic':
        #     self.model = self.build_vosk()
        # else:
        #     pass

    def get_paths(self):
        for s in self.speaker_ls:
            self.data[s] = {}
            self.wavs[s] = []
            self.csv[s] = []
            speaker_path = f'{self.directory}\\data\\LJSpeech\\{s}'
            files = [f for f in os.listdir(speaker_path) if os.path.isfile(os.path.join(speaker_path, f))]
            for file in files:
                if file.endswith('.wav'):
                    self.wavs[s].append(speaker_path + '\\' + file)
                elif file.endswith('.csv'):
                    self.csv[s].append(speaker_path + '\\' + file)

    def send(self):
        for s in self.speaker_ls:
            print(s)
            pass

    def send_text(self):
        self.p = pyaudio.PyAudio()
        stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=8000)
        stream.start_stream()
        print("started stream")

        pass

    def send_voice(self):
        pass

    def send_dict(self):
        pass

        pass


def main():
    sen = Sender(ip="169.254.208.240", host=5555)
    sen.get_paths()


if __name__ == '__main__':
    main()
