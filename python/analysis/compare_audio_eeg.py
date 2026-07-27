from scipy.io import loadmat
from scipy.signal import welch

import librosa
import librosa.display

import matplotlib.pyplot as plt
import numpy as np


# -----------------------------
# CONFIG
# -----------------------------

AUDIO_FILE = "./musics/song21.mp3"
EEG_FILE = "./datasets/stanford/song21_Imputed.mat"

PARTICIPANT = 0
CHANNEL = 0

START = 60      # segundos
DURATION = 20   # segundos

# -----------------------------
# AUDIO
# -----------------------------

y, sr_audio = librosa.load(AUDIO_FILE, sr=None)
onset_env = librosa.onset.onset_strength(y=y,sr=sr_audio)
times_audio = librosa.times_like(onset_env,sr=sr_audio)

# -----------------------------
# EEG
# -----------------------------

mat = loadmat(EEG_FILE)
eeg = mat["data21"]
fs = int(mat["fs"][0][0])

signal = np.sqrt(np.mean(eeg[:, :, PARTICIPANT] ** 2,axis=0))
time = np.arange(len(signal)) / fs

# intervalo
i0 = int(START * fs)
i1 = int((START + DURATION) * fs)

signal_crop = signal[i0:i1]
time_crop = time[i0:i1]

# -----------------------------
# FFT
# -----------------------------
freqs, psd = welch(signal_crop,fs=fs,nperseg=512)

# -----------------------------
# FIGURE
# -----------------------------
fig, ax = plt.subplots(4,1,figsize=(16,12))

# AUDIO
librosa.display.waveshow(y,sr=sr_audio,ax=ax[0])

ax[0].set_xlim(START,START + DURATION)
ax[0].set_title("Audio Waveform")

# ENVELOPE
ax[1].plot(times_audio,onset_env)
ax[1].set_xlim(START,START + DURATION)
ax[1].set_title("Onset Envelope")

# EEG
ax[2].plot(time_crop,signal_crop)
ax[2].set_title("Global EEG Activity")

# FFT
ax[3].semilogy(freqs,psd)
ax[3].set_xlim(0,40)
ax[3].set_title("EEG Power Spectrum")

plt.tight_layout()
plt.show()