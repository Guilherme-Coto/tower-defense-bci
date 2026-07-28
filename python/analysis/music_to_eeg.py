import librosa
import numpy as np
import matplotlib.pyplot as plt

AUDIO_FILE = "./musics/song21.mp3"
TARGET_FS = 125

# ------------------------
# Load
# ------------------------
y, sr = librosa.load(AUDIO_FILE,sr=None)

# ------------------------
# Onset envelope
# ------------------------
onset = librosa.onset.onset_strength(y=y,sr=sr)

# Tempo correspondente ao onset
times = librosa.times_like(onset,sr=sr)

# ------------------------
# Reamostrar para 125 Hz
# ------------------------

duration = len(y) / sr
target_time = np.arange(0,duration,1 / TARGET_FS)
onset_interp = np.interp(target_time,times,onset)

# ------------------------
# Normalizar
# ------------------------
onset_interp -= onset_interp.min()
onset_interp /= onset_interp.max()

print("Samples:", len(onset_interp))
print("Duration:", duration)

# ------------------------
# Save
# ------------------------
np.save("song21_onset125.npy",onset_interp)

# ------------------------
# Plot
# ------------------------
plt.figure(figsize=(15,4))
plt.plot(target_time,onset_interp)
plt.title("Onset Envelope @125Hz")
plt.xlabel("Time (s)")
plt.ylabel("Normalized")
plt.grid()
plt.show()