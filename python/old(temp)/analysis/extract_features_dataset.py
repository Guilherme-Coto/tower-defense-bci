from scipy.io import loadmat
import pandas as pd

from features.rhythm_features import RhythmFeatureExtractor

# ===========================
# CONFIG
# ===========================

MAT_FILE = "./datasets/stanford/song21_Imputed.mat"

WINDOW_SECONDS = 2
STEP_SECONDS = 0.5

CHANNELS = {
    "motor_left":35,
    "temporal_left":44,
    "motor_right":103,
    "temporal_right":107
}

# ===========================

print("Loading dataset...")

mat = loadmat(MAT_FILE)

data = mat["data21"]

fs = int(mat["fs"][0,0])

extractor = RhythmFeatureExtractor(fs)

window = int(WINDOW_SECONDS * fs)
step = int(STEP_SECONDS * fs)

rows = []

n_channels, n_samples, n_participants = data.shape

print(f"Participants : {n_participants}")
print(f"Samples      : {n_samples}")
print(f"Sampling Hz  : {fs}")

for participant in range(n_participants):

    print(f"Participant {participant+1}/{n_participants}")

    start = 0

    while start + window <= n_samples:

        row = {
            "participant": participant + 1,
            "window_start": start / fs,
            "window_end": (start + window) / fs
        }

        for name, ch in CHANNELS.items():

            eeg = data[ch, start:start+window, participant]

            features = extractor.extract(eeg)

            for feat_name, value in features.items():

                row[f"{name}_{feat_name}"] = value

        rows.append(row)

        start += step

print()

print("Creating dataframe...")

df = pd.DataFrame(rows)

print(df.head())

print()

print("Saving CSV...")

df.to_csv("features_song21.csv", index=False)

print("Done!")

print(df.shape)