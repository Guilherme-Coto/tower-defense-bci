import numpy as np
import pandas as pd

# ==========================
# CONFIG
# ==========================

CSV_FILE = "features_song21.csv"

TEMPLATE_FILE = "./beat_templates/song21_beats.npy"

FS = 125

WINDOW_SECONDS = 2

# ==========================

print("Loading files...")

df = pd.read_csv(CSV_FILE)
template = np.load(TEMPLATE_FILE)
window = int(WINDOW_SECONDS * FS)
similarity = []

print("Calculating rhythm score...")

for _, row in df.iterrows():
    start = int(row["window_start"] * FS)
    end = start + window
    beat_window = template[start:end]

    if len(beat_window) < window:
        similarity.append(0.0)
        continue

    score = np.mean(beat_window)
    similarity.append(score)

df["rhythm_similarity"] = similarity
print(df.head())
print()
print("Saving...")

df.to_csv("features_song21_rhythm.csv",index=False)

print("Done.")
print(df.shape)