import os

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np


MUSIC = "./musics/song21.mp3" 

y, sr = librosa.load(MUSIC, sr=None)

duration = librosa.get_duration(y=y, sr=sr)

print(f"File: {os.path.basename(MUSIC)}")
print(f"Sample rate: {sr} Hz")
print(f"Duration: {duration:.2f} s")

# -----------------------------
# Beat tracking
# -----------------------------

tempo, beats = librosa.beat.beat_track(y=y, sr=sr, trim=True)
tempo = float(np.atleast_1d(tempo)[0])

beat_times = librosa.frames_to_time(beats, sr=sr)

print(f"BPM: {tempo:.2f}")
print(f"Detected beats: {len(beats)}")

#envelope
onset_env = librosa.onset.onset_strength(y=y,sr=sr)
times = librosa.times_like(onset_env, sr=sr)

#faz o plot
fig, ax = plt.subplots(3,1,figsize=(16,10),sharex=True)

# Waveform
librosa.display.waveshow(y,sr=sr,ax=ax[0])

ax[0].set_title("Waveform")

# Envelope
ax[1].plot(times, onset_env)
ax[1].set_title("Onset Envelope")

# Beats
librosa.display.waveshow(y,sr=sr,ax=ax[2],alpha=0.4)

for bt in beat_times:
    ax[2].axvline(bt,color="red",alpha=0.5)

ax[2].set_title("Detected Beats")

plt.tight_layout()
plt.show()