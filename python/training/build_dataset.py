from pathlib import Path
import re

import mne
import numpy as np
import pandas as pd
from scipy.signal import welch

# ==========================
# CONFIGURAÇÃO
# ==========================

DATASET = Path("datasets")

LOWCUT = 1
HIGHCUT = 40

# Música que queremos reconhecer (binário)
TARGET_TRACK = 1

# ==========================
# FEATURE EXTRACTION
# ==========================

def extract_features(epoch, fs):
    """
    epoch -> (n_channels, n_samples)
    """

    freqs, psd = welch(
        epoch,
        fs=fs,
        axis=1,
        nperseg=min(512, epoch.shape[1])
    )

    bands = [
        (1, 4),    # Delta
        (4, 8),    # Theta
        (8, 13),   # Alpha
        (13, 30),  # Beta
        (30, 40),  # Gamma
    ]

    features = []

    for low, high in bands:
        idx = (freqs >= low) & (freqs <= high)
        band_power = psd[:, idx].mean(axis=1)
        features.extend(band_power)

    return np.array(features)


# ==========================
# DATASET
# ==========================

X = []
y = []

vhdr_files = sorted(DATASET.rglob("*.vhdr"))
print(f"\nEncontrados {len(vhdr_files)} ficheiros EEG.\n")

for vhdr in vhdr_files:
    print(f"A processar: {vhdr}")

    raw = mne.io.read_raw_brainvision(
        vhdr,
        preload=True,
        verbose=False
    )

    raw.filter(LOWCUT, HIGHCUT, verbose=False)
    raw.notch_filter(50, verbose=False)

    fs = raw.info["sfreq"]

    events_file = vhdr.with_name(
        vhdr.name.replace("_eeg.vhdr", "_events.tsv")
    )

    if not events_file.exists():
        print("events.tsv não encontrado.")
        continue

    events = pd.read_csv(events_file, sep="\t")

    recalls = events[
        events["trial_type"].str.contains(
            "Task_Recall",
            na=False
        )
    ]

    print(f"  {len(recalls)} eventos Task_Recall encontrados.")

    for _, row in recalls.iterrows():
        trial = row["trial_type"]
        match = re.search(r"Track_(\d+)", trial)

        if match is None:
            continue

        track = int(match.group(1))
        start = int(row["sample"])
        duration = int(row["duration"] * fs)

        if duration <= 0:
            continue

        stop = start + duration
        eeg = raw.get_data(
            start=start,
            stop=stop
        )

        # Normalização por canal
        eeg = eeg - eeg.mean(axis=1, keepdims=True)
        eeg = eeg / (eeg.std(axis=1, keepdims=True) + 1e-8)

        feat = extract_features(eeg, fs)

        X.append(feat)

        if track == TARGET_TRACK:
            y.append(1)
        else:
            y.append(0)


X = np.array(X)
y = np.array(y)

print("\n==========================")
print("DATASET CRIADO")
print("==========================")

print("X:", X.shape)
print("y:", y.shape)

unique, counts = np.unique(y, return_counts=True)

print("\nDistribuição:")

for cls, cnt in zip(unique, counts):

    print(f"Classe {cls}: {cnt}")

Path("training").mkdir(exist_ok=True)

np.save("training/X.npy", X)
np.save("training/y.npy", y)

print("\nGuardado em training/X.npy")
print("Guardado em training/y.npy")