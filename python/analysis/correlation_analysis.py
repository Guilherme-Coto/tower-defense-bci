import numpy as np
from scipy.io import loadmat
from scipy.signal import resample
import librosa

# ---------- CONFIG ----------
AUDIO_FILE = "./musics/song21.mp3"
EEG_FILE = "./datasets/stanford/song21_Imputed.mat"
PARTICIPANT = 2
# ----------------------------

# Carregar áudio
y, sr = librosa.load(AUDIO_FILE, sr=None)

# Envelope do áudio
audio_env = librosa.onset.onset_strength(y=y, sr=sr)

# Carregar EEG
mat = loadmat(EEG_FILE)
eeg = mat["data21"]

# RMS dos 125 canais
eeg_rms = np.sqrt(np.mean(eeg[:, :, PARTICIPANT] ** 2, axis=0))

# Reamostrar envelope para o mesmo nº de amostras do EEG
audio_env = resample(audio_env, len(eeg_rms))

# Normalizar ambos
audio_env = (audio_env - np.mean(audio_env)) / np.std(audio_env)
eeg_rms = (eeg_rms - np.mean(eeg_rms)) / np.std(eeg_rms)

print("Participant | Correlation")
print("--------------------------")

for p in range(eeg.shape[2]):
    eeg_rms = np.sqrt(np.mean(eeg[:, :, p] ** 2,axis=0))
    eeg_norm = (eeg_rms - np.mean(eeg_rms)) / np.std(eeg_rms)
    corr = np.corrcoef(audio_env, eeg_norm)[0, 1]
    print(f"{p:>10} | {corr:.4f}")