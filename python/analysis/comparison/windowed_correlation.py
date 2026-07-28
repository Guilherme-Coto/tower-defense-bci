import numpy as np
import scipy.io
import matplotlib.pyplot as plt

#NOTA: Este script mostrou que não existe correlação


PARTICIPANT = 0

CHANNELS = {
    "Motor Left (36)": 35,
    "Temporal Left (45)": 44,
    "Motor Right (104)": 103,
    "Temporal Right (108)": 107,
}

WINDOW_SECONDS = 10

#carrega o eeg
mat = scipy.io.loadmat("./datasets/stanford/song21_Imputed.mat")
eeg = mat["data21"]
fs = int(mat["fs"][0][0])

#carrega a template
template = np.load("./beat_templates/song21_beats.npy")
N = min(template.size, eeg.shape[1])
template = template[:N]
window = WINDOW_SECONDS * fs


for name, ch in CHANNELS.items():
    signal = eeg[ch, :N, PARTICIPANT]
    signal = (signal - signal.mean()) / signal.std()
    correlations = []
    starts = []

    for start in range(0, N - window, window):
        stop = start + window

        eeg_seg = signal[start:stop]
        tmp_seg = template[start:stop]

        if np.std(tmp_seg) == 0:
            continue

        corr = np.corrcoef(eeg_seg, tmp_seg)[0, 1]

        correlations.append(corr)
        starts.append(start / fs)

    correlations = np.array(correlations)

    print("=" * 50)
    print(name)
    print(f"Mean correlation : {np.mean(correlations):.4f}")
    print(f"Max correlation  : {np.max(correlations):.4f}")
    print(f"Min correlation  : {np.min(correlations):.4f}")

    plt.figure(figsize=(12,4))
    plt.plot(starts, correlations)
    plt.title(name)
    plt.xlabel("Time (s)")
    plt.ylabel("Correlation")
    plt.grid(True)
    plt.show()