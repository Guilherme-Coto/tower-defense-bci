import os
import numpy as np
import librosa

# ------------------------------------------
# CONFIG
# ------------------------------------------

MUSIC_FOLDER = "musics"
OUTPUT_FOLDER = "templates"

TARGET_FS = 125        # igual ao EEG

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ------------------------------------------
# PROCESS ALL SONGS
# ------------------------------------------

for file in sorted(os.listdir(MUSIC_FOLDER)): 
    if not file.endswith(".mp3"):
        continue

    print("=" * 50)
    print(file)

    path = os.path.join(MUSIC_FOLDER, file)

    # --------------------------------------
    # Load audio
    # --------------------------------------

    y, sr = librosa.load(path, sr=None)

    duration = librosa.get_duration(y=y, sr=sr)

    print(f"Duration : {duration:.2f} s")
    print(f"Sample rate : {sr}")

    # --------------------------------------
    # Onset envelope
    # --------------------------------------
    onset = librosa.onset.onset_strength(y=y,sr=sr)
    onset_time = librosa.times_like(onset,sr=sr)
    # --------------------------------------
    # Resample to 125 Hz
    # --------------------------------------
    eeg_time = np.arange(0,duration,1 / TARGET_FS)
    template = np.interp(eeg_time,onset_time,onset)

    # --------------------------------------
    # Normalize
    # --------------------------------------
    template -= template.min()

    if template.max() > 0:
        template /= template.max()

    # --------------------------------------
    # Save
    # --------------------------------------
    name = os.path.splitext(file)[0]
    np.save(os.path.join(OUTPUT_FOLDER,name + "_template.npy"),template)
    print(f"Samples : {len(template)}")

print("\nTemplates created successfully.")