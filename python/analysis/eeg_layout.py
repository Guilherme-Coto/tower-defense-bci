import numpy as np
import matplotlib.pyplot as plt

FILE = "./analysis/Hydrocel_GSN_128_1.0.sfp"

labels = []
x = []
y = []

with open(FILE) as f:
    for line in f:
        parts = line.split()

        if len(parts) < 4:
            continue

        labels.append(parts[0])
        x.append(float(parts[1]))
        y.append(float(parts[2]))

x = np.array(x)
y = np.array(y)

plt.figure(figsize=(8,8))
plt.scatter(x, y, s=15)

for i, lab in enumerate(labels):
    if lab.startswith("E"):
        idx = int(lab[1:])
        if idx in [36,45,104,108]:
            plt.scatter(x[i],y[i],s=120,color="red")
            plt.text(x[i],y[i],lab,fontsize=12)

plt.axis("equal")
plt.title("EGI 128 Electrode Layout")
plt.show()