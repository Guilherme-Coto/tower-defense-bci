import numpy as np
import scipy.io
import matplotlib.pyplot as plt

# ==========================================
# CONFIG
# ==========================================

PARTICIPANT = 0

CHANNELS = {
    "Motor Left (36)": 35,
    "Temporal Left (45)": 44,
    "Motor Right (104)": 103,
    "Temporal Right (108)": 107,
}

# ==========================================
# LOAD EEG
# ==========================================

mat = scipy.io.loadmat("./datasets/stanford/song21_Imputed.mat")

eeg = mat["data21"]
fs = int(mat["fs"][0][0])

# ==========================================
# LOAD TEMPLATE
# ==========================================

template = np.load("./beat_templates/song21_beats.npy")

# mesmo comprimento
N = min(template.size, eeg.shape[1])
template = template[:N]
time = np.arange(N) / fs

# ==========================================
# FIGURE
# ==========================================
fig, ax = plt.subplots(len(CHANNELS) + 1,1,figsize=(16, 9),sharex=True)

# ------------------------------------------
# Template
# ------------------------------------------
ax[0].plot(time,template,color="black",linewidth=1)
ax[0].set_title("Beat Template")
ax[0].set_ylim(-0.1, 1.2)

# ------------------------------------------
# EEG
# ------------------------------------------

i = 1

for name, ch in CHANNELS.items():
    signal = eeg[ch, :N, PARTICIPANT]
    signal = (signal - signal.mean()) / signal.std()
    ax[i].plot(time,signal,linewidth=0.8)
    ax[i].set_title(name)
    i += 1

ax[-1].set_xlabel("Time (s)")

plt.tight_layout()
plt.show()