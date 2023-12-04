from client_class_noKB import Client
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


def main():
    ip = '132.72.80.203'
    host = 7777
    client1 = Client(ip, host)
    time.sleep(5)

    sender = threading.Thread(target=client1.sender)
    sender.start()

    reciver = threading.Thread(target=client1.reciver)
    reciver.start()

    reader = threading.Thread(target=client1.reader)
    reader.start()


    print('Started all threads')


    # Wait for the input thread to finish
    sender.join()
    reciver.join()
    reader.join()


if __name__ == '__main__':
    main()
