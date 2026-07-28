import numpy as np
import matplotlib.pyplot as plt

template = np.load("templates/song21_template.npy")

t = np.arange(len(template)) / 125

plt.figure(figsize=(14,4))

plt.plot(t, template)

plt.xlabel("Time (s)")
plt.ylabel("Normalized")

plt.title("Rhythm Template @125Hz")

plt.grid(True)

plt.show()

print("Samples:", len(template))
print("Duration:", len(template)/125)