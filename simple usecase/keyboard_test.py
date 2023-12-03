import keyboard
import time
import threading
import socket
from pvcheetah import CheetahActivationLimitError, create
from pvrecorder import PvRecorder
import queue
import argparse
from io import BytesIO
from gtts import gTTS
import pygame

FLAG = 1
CHEETAH = None
text_queue = queue.Queue()  # Global queue to hold the text to be read
queue_lock = threading.Lock()  # Lock for synchronizing access to the text queue
reading_queue = queue.Queue()

TEXT = ["May I have your attention please",
       "may I have your attention please",
       "will the real slim shady please stand up",
       "I repeat will the real slim shady please stand up",
       "were gonna have a problem here........."]


def engine(text):
    mp3_fp = BytesIO()
    tts = gTTS(text, lang='en', slow=False)
    tts.write_to_fp(mp3_fp)
    return mp3_fp

def read_text_from_client():
    global FLAG
    pygame.init()
    pygame.mixer.init()
    while True:
        if FLAG == 0:
            print("Listen Now!")
            text = text_queue.get()
            if text is None:
                continue
            print(f'Engine: {text}')
            text_l = len(text)
            sound = engine(text)
            sound.seek(0)
            pygame.mixer.music.load(sound)
            pygame.mixer.music.play()
            time.sleep(0.1 * text_l ** 0.5)
            print('-' * 50)



def get_send_text():
    global FLAG, TEXT
    i = 0
    while True:
        if keyboard.is_pressed('space'):
            FLAG = 1
            print('Listening... (press Ctrl+C to stop)')
            print("Speak Now!")
            while not keyboard.is_pressed('s'):
                print('Recording....')
                time.sleep(0.5)
            print('Stopped!')
        else:
            FLAG = 0
            data = TEXT[i]
            text_queue.put(data)
            print(f'Text: {data}')
            i += 1
            if i == len(TEXT):
                i = 0
            time.sleep(1)


def main():
    text_t = threading.Thread(target=get_send_text)  # Start the input thread
    text_t.start()
    time.sleep(2)

    read_thread = threading.Thread(target=read_text_from_client)  # Start the read thread
    read_thread.start()
    print('Started all trheads')

    # Wait for the input thread to finish
    text_t.join()
    read_thread.join()


if __name__ == '__main__':
    main()