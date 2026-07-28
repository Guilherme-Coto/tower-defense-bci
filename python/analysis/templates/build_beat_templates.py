import os
import numpy as np
import librosa

MUSIC_FOLDER = "musics"
OUTPUT_FOLDER = "beat_templates"

TARGET_FS = 125

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for file in sorted(os.listdir(MUSIC_FOLDER)):
    if not file.endswith(".mp3"):
        continue

    print("="*50)
    print(file)

    path = os.path.join(MUSIC_FOLDER, file)
    y, sr = librosa.load(path, sr=None)

    # Beat tracking
    onset_env = librosa.onset.onset_strength(
        y=y,
        sr=sr
    )

    peaks = librosa.util.peak_pick(
        onset_env,
        pre_max=3,
        post_max=3,
        pre_avg=3,
        post_avg=5,
        delta=0.5,
        wait=10
    )

    beat_times = librosa.frames_to_time(
        peaks,
        sr=sr
    )

    print("Detected peaks:", len(beat_times))
    print(beat_times[:10])
    duration = librosa.get_duration(y=y, sr=sr)
    n_samples = int(duration * TARGET_FS)
    template = np.zeros(n_samples)

    for t in beat_times:

        idx = int(round(t * TARGET_FS))

        if 0 <= idx < n_samples:
            template[idx] = 1
    print("Template samples:", len(template))
    print("Detected beats:", int(np.sum(template)))
    np.save(os.path.join(OUTPUT_FOLDER,file.replace(".mp3","_beats.npy")),template)

    print("Detected peaks:", len(beat_times))

print("\nDone.")