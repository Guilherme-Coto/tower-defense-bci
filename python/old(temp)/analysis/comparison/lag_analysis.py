import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt

# ==========================================
# CONFIG
# ==========================================

MAT_FILE = "./datasets/stanford/song21_Imputed.mat"
ONSET_FILE = "song21_onset125.npy"

PARTICIPANT = 0
CHANNEL = 45          # Temporal esquerdo (EGI)

FS = 125

# ==========================================
# LOAD EEG
# ==========================================
mat = sio.loadmat(MAT_FILE)
eeg = mat["data21"][:, :, PARTICIPANT]
signal = eeg[:, CHANNEL]

# ==========================================
# LOAD ONSET
# ==========================================
onset = np.load(ONSET_FILE)

# Mesmo comprimento
N = min(len(signal), len(onset))
signal = signal[:N]
onset = onset[:N]

# Normalizar
signal = (signal - np.mean(signal)) / np.std(signal)
onset = (onset - np.mean(onset)) / np.std(onset)

# ==========================================
# TESTAR VÁRIOS LAGS
# ==========================================

lags_ms = np.arange(0, 501, 50)
correlations = []

for lag in lags_ms:
    shift = int(lag * FS / 1000)
    eeg_shift = signal[shift:]
    onset_shift = onset[:len(eeg_shift)]
    corr = np.corrcoef(eeg_shift,onset_shift)[0,1]
    correlations.append(corr)

print()
print("Lag (ms) | Correlation")
print("----------------------")
for lag, corr in zip(lags_ms, correlations):
    print(f"{lag:7d} | {corr:.4f}")

best = np.argmax(np.abs(correlations))

print("\nBest Lag")
print(f"{lags_ms[best]} ms")
print(f"Correlation = {correlations[best]:.4f}")

# ==========================================
# FIGURE
# ==========================================

plt.figure(figsize=(10,5))
plt.plot(lags_ms,correlations,marker="o")
plt.grid()
plt.xlabel("Lag (ms)")
plt.ylabel("Correlation")
plt.title("EEG vs Onset Envelope")

plt.show()