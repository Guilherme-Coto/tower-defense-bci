from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch

FILE = "./datasets/stanford/song21_Imputed.mat"

mat = loadmat(FILE)

eeg = mat["data21"]
fs = int(mat["fs"][0][0])

print("Shape:", eeg.shape)
print("Sampling rate:", fs)

participant = 0
channel = 0

signal = eeg[channel, :, participant]

time = np.arange(len(signal)) / fs
start = 60      
duration = 10   

i0 = start * fs
i1 = (start + duration) * fs

plt.figure(figsize=(15,4))
plt.plot(time[i0:i1], signal[i0:i1])
plt.title(f"Participant {participant} - Channel {channel}")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)

plt.show()

freqs, psd = welch(signal, fs=fs)

plt.figure(figsize=(10,4))
plt.semilogy(freqs, psd)

plt.title("Power Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power")
plt.grid(True)

plt.figure(figsize=(15,5))

plt.specgram(signal,
             Fs=fs,
             NFFT=256,
             noverlap=128)

plt.xlabel("Time (s)")
plt.ylabel("Frequency (Hz)")
plt.title("EEG Spectrogram")