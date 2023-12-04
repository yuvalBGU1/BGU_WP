# load packages
import random
import yaml
from munch import Munch
import numpy as np
import torch
# import noisereduce as nr
# from pydub import AudioSegment as am

# from torch import nn
# import torch.nn.functional as F
import torchaudio
import librosa
# import pyaudio
import IPython
# import numpy
import time
# import soundfile as sf
# import os
# import audioop  # new
# import scipy.io.wavfile
import soundcard as sc

# os.rename('StarGANv2-VC', 'StarGANv2')
from Utils.ASR.models import ASRCNN
from Utils.JDC.model import JDCNet
from models import Generator, MappingNetwork, StyleEncoder
# from scipy.ndimage import interpolation
# matplotlib inline

# Source: http://speech.ee.ntu.edu.tw/~jjery2243542/resource/model/is18/en_speaker_used.txt
# Source: https://github.com/jjery2243542/voice_conversion


# Model related functions
# speakers = [228, 229, 230, 231, 233, 236, 240, 244, 226, 227, 232, 243, 254, 256, 258, 259, 273]
speakers = [228, 273]

to_mel = torchaudio.transforms.MelSpectrogram(
    n_mels=80, n_fft=2048, win_length=1200, hop_length=300)
mean, std = -4, 4

print(torch.cuda.is_available())
device = 'cuda' if torch.cuda.is_available() else 'cpu'

def preprocess(wave):
    wave_tensor = torch.from_numpy(wave).float()
    mel_tensor = to_mel(wave_tensor)
    mel_tensor = (torch.log(1e-5 + mel_tensor.unsqueeze(0)) - mean) / std
    return mel_tensor


def build_model(model_params={}):
    args = Munch(model_params)
    generator = Generator(args.dim_in, args.style_dim, args.max_conv_dim, w_hpf=args.w_hpf, F0_channel=args.F0_channel)
    mapping_network = MappingNetwork(args.latent_dim, args.style_dim, args.num_domains, hidden_dim=args.max_conv_dim)
    style_encoder = StyleEncoder(args.dim_in, args.style_dim, args.num_domains, args.max_conv_dim)

    nets_ema = Munch(generator=generator,
                     mapping_network=mapping_network,
                     style_encoder=style_encoder)

    return nets_ema


def compute_style(speaker_dicts):
    reference_embeddings = {}
    for key, (path, speaker) in speaker_dicts.items():
        if path == "":
            label = torch.LongTensor([speaker]).to(device)
            latent_dim = starganv2.mapping_network.shared[0].in_features
            ref = starganv2.mapping_network(torch.randn(1, latent_dim).to(device), label)
        else:
            wave, sr = librosa.load(path, sr=24000)
            audio, index = librosa.effects.trim(wave, top_db=30)
            if sr != 24000:
                wave = librosa.resample(wave, sr, 24000)
            mel_tensor = preprocess(wave).to(device)

            with torch.no_grad():
                label = torch.LongTensor([speaker])
                ref = starganv2.style_encoder(mel_tensor.unsqueeze(1), label)
        reference_embeddings[key] = (ref, label)

    return reference_embeddings

# load F0 model

F0_model = JDCNet(num_class=1, seq_len=192)
if device == 'cpu':
    params = torch.load("./Utils/JDC/bst.t7", map_location=torch.device(device))['net']
else:
    params = torch.load("./Utils/JDC/bst.t7")['net']
F0_model.load_state_dict(params)
_ = F0_model.eval()
# F0_model = F0_model.to('cuda')
F0_model = F0_model.to(device)

# load vocoder
from parallel_wavegan.utils import load_model

# vocoder = load_model("./StarGANv2/vocoder/checkpoint-400000steps.pkl").to('cuda').eval()
vocoder = load_model("./Vocoder/checkpoint-400000steps.pkl").to(device).eval()


vocoder.remove_weight_norm()
_ = vocoder.eval()

# load starganv2

#gdown.download("https://drive.google.com/uc?export=download&id=1D38kaL2o26cH83m7Dd6eUO9fEwJx3ewX", model_path)


# with Lior's pretrained model (epoch_00148.pth)
# model_path = "./epoch_00148.pth"


# uncomment to download


model_path = "./Models/epoch_00150.pth"
# gdown.download("https://drive.google.com/uc?export=download&id=10N7z3T5heaxPuL8oCN2sWoLkBVvHBCVm", model_path)


with open('./Configs/config.yml') as f:
    starganv2_config = yaml.safe_load(f)
starganv2 = build_model(model_params=starganv2_config["model_params"])
if device == 'cpu':
    params = torch.load(model_path, map_location=torch.device('cpu'))
else:
    params = torch.load(model_path)
params = params['model_ema']
_ = [starganv2[key].load_state_dict(params[key]) for key in starganv2]
_ = [starganv2[key].eval() for key in starganv2]
starganv2.style_encoder = starganv2.style_encoder.to(device)
starganv2.mapping_network = starganv2.mapping_network.to(device)
starganv2.generator = starganv2.generator.to(device)

#configuring selected speaker's speaking style

selected_speakers = speakers
speaker_dicts = {}
for s in selected_speakers:
    k = s
    speaker_dicts['p' + str(s)] = ('./Demo/VCTK-corpus/p' + str(k) + '/p' + str(k) + '_023.wav', speakers.index(s))
reference_embeddings = compute_style(speaker_dicts)
# print(reference_embeddings)


def display_deepfake_audio(audio):
    IPython.display.display(IPython.display.Audio(audio, rate=24000))


def display_speaker_audio(num_speaker):
    print("sample of speaker number " + str(num_speaker))
    IPython.display.display(IPython.display.Audio(
        './Demo/VCTK-corpus/p' + str(num_speaker) + '/p' + str(
            num_speaker) + '_023.wav'))

mics = sc.all_microphones(include_loopback=True)
# print(mics)
sc.all_speakers()


def stargan_soundcard(global_max, speaker_num):
    one_speaker = sc.default_speaker()
    one_mic = sc.default_microphone()
    numb_start = np.linspace(0.5, 1, 500)
    numb_end = np.linspace(1, 0.5, 500)
    ref, _ = reference_embeddings["p" + str(speaker_num)]

    recording = []

    wav_path = "recordings/001_24.wav"
    og_sr = librosa.get_samplerate(wav_path)
    print("OG SR= " + str(og_sr))
    ## adding down sampling
    # sound = am.from_file(wav_path, format='wav', frame_rate=48000)
    # sound = sound.set_frame_rate(24000)
    # sound.export(wav_path, format='wav')  # override
    # new_sr = librosa.get_samplerate(wav_path)
    # print("New SR= " + str(new_sr))

    sound_file = librosa.load("recordings/001_24.wav", sr=24000)
    rec = sound_file[0]
    # rec = librosa.resample(rec, orig_sr=48000, target_sr=24000)
    with one_mic.recorder(samplerate=24000, blocksize=24000) as mic, \
            one_speaker.player(samplerate=24000, blocksize=24000) as sp:
        for _ in range(15):

            audio = rec[_*24000:(_+1)*24000]
            # audio = mic.record(numframes=24000)[:, 0]

            # smoothing audio
            # audio[:500] = np.multiply(audio[:500], numb_start)
            # audio[-500:] = np.multiply(audio[-500:], numb_end)

            # ignoring frames of background noise
            if np.max(np.abs(audio)) < 0.04:
                audio = audio / global_max
                sp.play(audio)
                continue

            # normalization
            audio = audio / global_max
            source = preprocess(audio).to(device)

            with torch.no_grad():
                start_time = time.time()
                f0_feat = F0_model.get_feature_GAN(source.unsqueeze(1))
                out = starganv2.generator(source.unsqueeze(1), ref, F0=f0_feat)
                c = out.transpose(-1, -2).squeeze().to(device)
                y_out = vocoder.inference(c)
                y_out = y_out.view(-1).cpu()
                recording.append(y_out)
                end_time = time.time()
                print("process time: " + str(end_time-start_time))
            sp.play(audio)

        return recording


# speaker_num = 273
# global_max = 0.6483659
# recording_chunks = stargan_soundcard(global_max, speaker_num)
# recording = np.concatenate(recording_chunks)


def stargan_soundcard_player(global_max, speaker_num, sound):
    print("sleeping...")
    time.sleep(5)
    print("trying to play:" + sound)
    one_speaker = sc.default_speaker()
    ref, _ = reference_embeddings["p" + str(speaker_num)]
    recording = []

    sound_file = librosa.load(sound, sr=24000)
    rec = sound_file[0]
    # rec = librosa.resample(rec, orig_sr=48000, target_sr=24000)
    with one_speaker.player(samplerate=24000, blocksize=24000) as sp:
        for _ in range(15):
            audio = rec[_*24000:(_+1)*24000]

            # audio = mic.record(numframes=24000)[:, 0]

            # smoothing audio
            # audio[:500] = np.multiply(audio[:500], numb_start)
            # audio[-500:] = np.multiply(audio[-500:], numb_end)

            # ignoring frames of background noise
            # if np.max(np.abs(audio)) < 0.04:
            #     audio = audio / global_max
            #     sp.play(audio)
            #     continue

            # normalization
            if audio.shape[0] == 0:
                print("audio shape of " + sound + " was non, return")
                return
            audio = audio / global_max
            source = preprocess(audio).to(device)

            with torch.no_grad():
                start_time = time.time()
                print("trying to process")
                f0_feat = F0_model.get_feature_GAN(source.unsqueeze(1))
                out = starganv2.generator(source.unsqueeze(1), ref, F0=f0_feat)
                c = out.transpose(-1, -2).squeeze().to(device)
                y_out = vocoder.inference(c)
                y_out = y_out.view(-1).cpu()
                recording.append(y_out)
                end_time = time.time()
                print("process time: " + str(end_time-start_time))
            print("trying to play")
            sp.play(audio)

        return recording
