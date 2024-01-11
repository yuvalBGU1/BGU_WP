import argparse
import socket
import threading
import os
import json
import wave
from vosk import Model, KaldiRecognizer
import pyaudio
import time
from pvcheetah import CheetahActivationLimitError, create
from pvrecorder import PvRecorder


class Sender:
    def __init__(self, access_key, library_path, model_path, endpoint_duration_sec, disable_automatic_punctuation,
                 ip='satts', host=0, speakers=['001'], mode='mic', model_index=0):
        self.client_socket = None
        self.p = None
        self.disable_automatic_punctuation = disable_automatic_punctuation
        self.endpoint_duration_sec = endpoint_duration_sec
        self.model_path = model_path
        self.library_path = library_path
        self.access_key = access_key
        self.ip = ip
        self.host = host
        self.speaker_ls = speakers
        self.connect()
        self.model_index = model_index
        print('connect')

        if model_index == 2:  # build cheetah model
            self.model = self.build_cheetah()
        else:  # build vosk model
            self.model = self.build_vosk()

    def build_vosk(self):
        model_path_small = "C:\\Users\\Administrator\\Downloads\\vosk-model-small-en-us-0.15"
        model_path_large = "C:\\Users\\Administrator\\Downloads\\vosk-model-en-us-0.22"
        model_path = model_path_small if self.model_index == 0 else model_path_large
        return Model(model_path)

    def build_cheetah(self):
        return create(
            access_key=self.access_key,
            library_path=self.library_path,
            model_path=self.model_path,
            endpoint_duration_sec=self.endpoint_duration_sec,
            enable_automatic_punctuation=not self.disable_automatic_punctuation)

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.ip, self.host)
        self.client_socket.connect(server_address)
        self.client_socket.send("sen".encode())

    def send_cheetah(self):
        cheetah = self.model
        try:
            print('Cheetah version : %s' % cheetah.version)

            recorder = PvRecorder(frame_length=cheetah.frame_length, device_index=self.audio_device_index)
            recorder.start()
            print('Listening... (press Ctrl+C to stop)')

            try:
                while True:
                    partial_transcript, is_endpoint = cheetah.process(recorder.read())
                    if partial_transcript != '':
                        # print(partial_transcript, end='', flush=True)
                        self.client_socket.send(partial_transcript.encode())
                        # time_array.append(["send", time.time()])
                        print(partial_transcript)
                    else:  # keeping open flow
                        self.client_socket.send(" ".encode())

                    if is_endpoint:
                        text_to_socket = cheetah.flush()
                        # print(text_to_socket + "\n")
                        self.client_socket.send(text_to_socket.encode())
                        # time_array.append(["send", time.time()])
                        print(text_to_socket)
                        # print(time_array)

            finally:
                print()
                recorder.stop()

        except KeyboardInterrupt:
            pass
        except CheetahActivationLimitError:
            print('AccessKey has reached its processing limit.')
        finally:
            cheetah.delete()

    def send_vosk(self):
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
    parser = argparse.ArgumentParser()
    # Cheetah arguments:
    parser.add_argument(
        '--access_key',
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
    parser.add_argument('--audio_device_index', type=int, default=2, help='Index of input audio device')
    parser.add_argument('--show_audio_devices', default=True, action='store_true',
                        help='Only list available devices and exit')
    # Program arguments:
    parser.add_argument('--stt_model', type=int, default=0,
                        help='0 - small vosk\n 1 - large vosk\n 2 - cheetah model')
    args = parser.parse_args()

    if args.show_audio_devices:
        for index, name in enumerate(PvRecorder.get_available_devices()):
            print('Device #%d: %s' % (index, name))

    sen = Sender(access_key=args.access_key, library_path=args.library_path, model_path=args.model_path,
                 endpoint_duration_sec=args.endpoint_duration_sec,
                 disable_automatic_punctuation=args.disable_automatic_punctuation, ip="192.168.1.116",
                 host=5555, model_index=args.stt_model)
    time.sleep(3)

    if args.stt_model == 2:
        if not args.access_key:
            print('--access_key is required in cheetah model')
            return
        sen.send_cheetah()
    else:
        sen.send_vosk()


if __name__ == '__main__':
    main()
