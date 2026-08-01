from pathlib import Path
import numpy as np
import mne
from scipy.signal import welch

# ==========================
# CONFIGURAÇÃO
# ==========================

DATASET_ROOT = Path("datasets")

LOWCUT = 1
HIGHCUT = 40
NOTCH = 50

TMIN = 3.0      # início da imaginação
TMAX = 8.0      # fim da imaginação

TARGET_CLASS = 1        # Für Elise


# ==========================
# FEATURE EXTRACTION
# ==========================

def extract_features(epoch, sfreq):
    features = []
    freqs, psd = welch(
        epoch,
        fs=sfreq,
        nperseg=min(512, epoch.shape[-1]),
        axis=-1
    )

    bands = {
        "delta": (1,4),
        "theta": (4,8),
        "alpha": (8,13),
        "beta": (13,30),
        "gamma": (30,40)
    }

    for low, high in bands.values():
        idx = (freqs >= low) & (freqs <= high)
        band_power = np.mean(psd[:, idx], axis=1)
        features.extend(band_power)

    return np.array(features)


# ==========================
# DATASET
# ==========================

X = []
y = []

vhdr_files = sorted(DATASET_ROOT.rglob("*.vhdr"))

print(f"{len(vhdr_files)} ficheiros encontrados")

for file in vhdr_files:
    print(file.name)

    raw = mne.io.read_raw_brainvision(file,preload=True,verbose=False)
    raw.filter(LOWCUT,HIGHCUT,verbose=False)
    raw.notch_filter(NOTCH,verbose=False)
    
    events, event_dict = mne.events_from_annotations(raw)

    print("Primeiros 30 eventos:")
    for e in events[:30]:
        print(e)
    sfreq = raw.info["sfreq"]
    epochs = mne.Epochs(
        raw,
        events,
        event_id=event_dict,
        tmin=TMIN,
        tmax=TMAX,
        baseline=None,
        preload=True,
        verbose=False
    )

    labels = epochs.events[:,2]
    data = epochs.get_data()

    for eeg, label in zip(data, labels):
        feat = extract_features(eeg,sfreq)
        X.append(feat)

        if label == TARGET_CLASS:
            y.append(1)
        else:
            y.append(0)

X = np.array(X)
y = np.array(y)

print()
print("Dataset criado")
print("X:", X.shape)
print("y:", y.shape)

np.save("training/X.npy", X)
np.save("training/y.npy", y)

print("Guardado.")