import numpy as np

from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ==========================
# Carregar Dataset
# ==========================

X = np.load("training/X.npy")
y = np.load("training/y.npy")

print("=" * 50)
print("DATASET")
print("=" * 50)

print(f"X: {X.shape}")
print(f"y: {y.shape}")

unique, counts = np.unique(y, return_counts=True)

print("\nDistribuição:")

for cls, cnt in zip(unique, counts):
    print(f"Classe {cls}: {cnt}")

# ==========================
# Modelo
# ==========================

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(
        kernel="rbf",
        class_weight="balanced",
        random_state=42
    ))
])

# ==========================
# Cross Validation
# ==========================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scores = []

print("\n" + "=" * 50)
print("VALIDAÇÃO CRUZADA")
print("=" * 50)

for fold, (train_idx, test_idx) in enumerate(cv.split(X, y), start=1):

    X_train = X[train_idx]
    X_test = X[test_idx]

    y_train = y[train_idx]
    y_test = y[test_idx]

    pipeline.fit(X_train, y_train)

    pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, pred)

    scores.append(acc)

    print(f"\nFold {fold}")
    print(f"Accuracy: {acc:.3f}")

    print("\nConfusion Matrix")
    print(confusion_matrix(y_test, pred))

    print("\nClassification Report")
    print(classification_report(
        y_test,
        pred,
        zero_division=0
    ))

# ==========================
# Resultado Final
# ==========================

print("\n" + "=" * 50)
print("RESULTADO FINAL")
print("=" * 50)

print(f"Accuracy média : {np.mean(scores):.3f}")
print(f"Desvio padrão  : {np.std(scores):.3f}")

# ==========================
# Treinar modelo final
# ==========================

pipeline.fit(X, y)

print("\nModelo treinado com todos os dados.")