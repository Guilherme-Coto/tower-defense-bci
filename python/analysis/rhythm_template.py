import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

# =====================================================
# CONFIG
# =====================================================

AUDIO_FILE = "./musics/song21.mp3"
SAVE_RESULTS = False

# =====================================================
# LOAD AUDIO
# =====================================================

y, sr = librosa.load(AUDIO_FILE, sr=None)

print("=" * 50)
print(f"File: {os.path.basename(AUDIO_FILE)}")
print(f"Sample Rate: {sr} Hz")
print(f"Duration: {len(y) / sr:.2f} s")
print("=" * 50)

# =====================================================
# BEAT TRACKING
# =====================================================

tempo, beat_frames = librosa.beat.beat_track(y=y,sr=sr)

# Compatibilidade entre versões do librosa
tempo = np.asarray(tempo).flatten()[0]
beat_times = librosa.frames_to_time(beat_frames,sr=sr)

# =====================================================
# ONSET ENVELOPE
# =====================================================

onset_env = librosa.onset.onset_strength(y=y,sr=sr)

# Intensidade em cada beat
beat_strengths = onset_env[beat_frames]

# Normalizar entre 0 e 1
beat_strengths = beat_strengths / np.max(beat_strengths)

# =====================================================
# INTERVALOS (mantemos porque também interessa)
# =====================================================

intervals = np.diff(beat_times)
mean_interval = np.mean(intervals)
normalized_intervals = intervals / mean_interval

# =====================================================
# PRINT INFO
# =====================================================

print(f"\nBPM: {tempo:.2f}")

print("\nPrimeiros beats:")
for b in beat_times[:10]:
    print(f"{b:.3f}")

print("\nPrimeiros intervalos:")
for i in intervals[:10]:
    print(f"{i:.3f}")

print("\n===== RHYTHM TEMPLATE =====\n")
for i, strength in enumerate(beat_strengths[:32]):
    bars = "█" * int(strength * 20)
    print(f"{i+1:02d}: {bars:<20} {strength:.2f}")

# =====================================================
# FIGURE
# =====================================================

plt.figure(figsize=(16,10))

# -----------------------------
# Waveform
# -----------------------------

plt.subplot(3,1,1)
librosa.display.waveshow(y,sr=sr,alpha=0.7)

for beat in beat_times:
    plt.axvline(beat,color="red",alpha=0.15)

plt.title("Audio Waveform + Detected Beats")

# -----------------------------
# Onset Envelope
# -----------------------------

plt.subplot(3,1,2)

times = librosa.times_like(onset_env, sr=sr)

plt.plot(times,onset_env,label="Onset Envelope")
plt.scatter(beat_times,beat_strengths * np.max(onset_env),color="green",s=20,label="Beat Strength")
plt.title("Onset Envelope")
plt.legend()

# -----------------------------
# Rhythm Template
# -----------------------------

plt.subplot(3,1,3)
plt.plot(beat_times,beat_strengths,marker="o")

plt.title("Normalized Beat Strength Template")
plt.xlabel("Time (s)")
plt.ylabel("Strength")

plt.grid(True)

plt.tight_layout()

# =====================================================
# SAVE
# =====================================================

if SAVE_RESULTS:
    os.makedirs("results", exist_ok=True)
    np.save("results/song21_template.npy",beat_strengths)

    plt.savefig("results/song21_template.png",dpi=300)

plt.show()