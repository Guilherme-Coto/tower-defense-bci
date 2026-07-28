import numpy as np
import matplotlib.pyplot as plt
import librosa

beats = np.load("beat_templates/song21_beats.npy")
print(type(beats))
print(beats[:20])
print("Number of beats:", len(beats))

t = np.arange(len(beats))/125
plt.figure(figsize=(15,3))
plt.plot(t, beats)
plt.ylim(-0.1,1.2)
plt.title("Beat Template")
plt.xlabel("Time (s)")
plt.show()