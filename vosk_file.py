import os
import json
import wave
from vosk import Model, KaldiRecognizer
import socket

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server's IP address and port
server_address = ('127.0.0.1', 7778)
client_socket.connect(server_address)

# Path to the model - update this with the actual path on your system
model_path = "C:\\Users\\Administrator\\Downloads\\vosk-model-small-en-us-0.15"
# model_path = "C:\\Users\\Administrator\\Downloads\\vosk-model-en-us-0.22"
filename = "Did The Past Really Happen_resampled.wav"

if not os.path.exists(model_path):
    print("Model path is incorrect. Please check the path to the Vosk model.")
    exit(1)

wf = wave.open(filename, "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print("Audio file must be WAV format mono PCM.")
    exit(1)

# Load Vosk model
model = Model(model_path)

# Create a recognizer
recognizer = KaldiRecognizer(model, wf.getframerate())

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if recognizer.AcceptWaveform(data):  # returns true when detecting silence
        result = recognizer.Result()
        result_dict = json.loads(result)
        if 'text' in result_dict and result_dict['text']:
            print("text: " + result_dict['text'])
            for part in result_dict['text'].split(" "):
                # input()
                buffer = part.encode()
                buffer_len = len(buffer)
                client_socket.send(buffer_len.to_bytes(2, 'big'))
                client_socket.send(buffer)
    else:
        result = recognizer.PartialResult()
        result_dict = json.loads(result)
        if 'partial' in result_dict and result_dict['partial']:
            print("partial: " + result_dict['partial'])
            for part in result_dict['partial'].split(" "):
                # input()
                buffer = part.encode()
                buffer_len = len(buffer)
                client_socket.send(buffer_len.to_bytes(2, 'big'))
                client_socket.send(buffer)

            recognizer.Reset()
            # print(result_dict)

