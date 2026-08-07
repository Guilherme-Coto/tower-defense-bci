import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ==========================
# Carregar dataset
# ==========================

X = np.load("training/X.npy")
y = np.load("training/y.npy")

print("X:", X.shape)
print("y:", y.shape)

# ==========================
# Train/Test Split
# ==========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ==========================
# Normalização
# ==========================

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ==========================
# Modelo
# ==========================

clf = SVC(
    kernel="rbf",
    class_weight="balanced",
    random_state=42
)

clf.fit(X_train, y_train)

# ==========================
# Predição
# ==========================

pred = clf.predict(X_test)

# ==========================
# Resultados
# ==========================

print("\n========================")
print("RESULTADOS")
print("========================")

print(f"Accuracy: {accuracy_score(y_test, pred):.3f}")

print("\nClassification Report")
print(classification_report(y_test, pred))

print("\nConfusion Matrix")
print(confusion_matrix(y_test, pred))