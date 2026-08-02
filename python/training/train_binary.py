import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X = np.load("training/X.npy")
y = np.load("training/y.npy")

print("X:", X.shape)
print("y:", y.shape)

scaler = StandardScaler()
X = scaler.fit_transform(X)

clf = SVC(kernel="rbf")

clf.fit(X, y)

pred = clf.predict(X)

print("\nPredições:")
print(pred)

print("\nLabels reais:")
print(y)

acc = (pred == y).mean()

print(f"\nAccuracy (treino): {acc:.2f}")