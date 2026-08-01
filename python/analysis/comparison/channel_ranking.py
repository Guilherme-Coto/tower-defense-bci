import numpy as np
import scipy.io
import matplotlib.pyplot as plt
import librosa

#carrega o dataset
mat = scipy.io.loadmat("./datasets/stanford/song21_Imputed.mat")

eeg = mat["data21"]          # (125, samples, participants)
fs = int(mat["fs"][0][0])

participant = 0

#carrega o áudio
audio, sr = librosa.load("./musics/song21.mp3", sr=None)
onset = librosa.onset.onset_strength(y=audio,sr=sr)
times = librosa.times_like(onset,sr=sr)

# -----------------------------
# Resample onset -> EEG timeline
# -----------------------------
duration = eeg.shape[1] / fs
eeg_time = np.arange(eeg.shape[1]) / fs
onset_interp = np.interp(eeg_time,times,onset)

#faz a normalização
onset_interp -= onset_interp.mean()
onset_interp /= onset_interp.std()

#correlação para cada canal
corrs = []

for ch in range(125):
    signal = eeg[ch, :, participant]
    signal = signal - signal.mean()
    signal = signal / signal.std()
    corr = np.corrcoef(signal, onset_interp)[0,1]
    corrs.append(corr)

corrs = np.array(corrs)

#faz o ranking
order = np.argsort(np.abs(corrs))[::-1]

print()
print("Top 15 channels")
print("----------------------------")

for i in range(15):
    c = order[i]
    print(f"{i+1:2d}. Channel {c+1:3d}   Corr = {corrs[c]:.4f}")

#coloca em gráfico
plt.figure(figsize=(10,4))
plt.bar(np.arange(1,126), corrs)
plt.xlabel("Channel")
plt.ylabel("Correlation")
plt.title("Correlation with Audio Onset Envelope")

plt.show()