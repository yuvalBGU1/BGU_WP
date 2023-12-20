import os
import json
from vosk import Model, KaldiRecognizer
import pyaudio


# Initialize PyAudio
p = pyaudio.PyAudio()


def print_devices():
    device_num = p.get_device_count()
    index = 0
    while index < device_num:
        print(p.get_device_info_by_index(index))
        index += 1


print_devices()

# Path to the model - update this with the actual path on your system
# model_path = "C:\\Users\\Administrator\\Downloads\\vosk-model-small-en-us-0.15"
model_path = "C:\\Users\\Administrator\\Downloads\\vosk-model-en-us-0.22"

if not os.path.exists(model_path):
    print("Model path is incorrect. Please check the path to the Vosk model.")
    exit(1)

# Load Vosk model
model = Model(model_path)

# Open stream
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=8000)
stream.start_stream()
print("started stream")

# Create a recognizer
recognizer = KaldiRecognizer(model, 44100)

while True:
    data = stream.read(1024, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):  # returns true when detecting silence
        result = recognizer.Result()
        result_dict = json.loads(result)
        if 'text' in result_dict and result_dict['text']:
            print("text: " + result_dict['text'])
    else:
        result = recognizer.PartialResult()
        result_dict = json.loads(result)
        if 'partial' in result_dict and result_dict['partial']:
            print("partial: " + result_dict['partial'])
            recognizer.Reset()
            # print(result_dict)

# Stop and close the stream 
stream.stop_stream()
stream.close()

# Close PyAudio
p.terminate()
