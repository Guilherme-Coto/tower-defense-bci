import argparse
from pathlib import Path
import sys

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Adicionar pasta raiz ao sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config


def train_sessions(mode="binary", classifier="svm"):

    data_dir = Path(__file__).resolve().parent

    X = np.load(data_dir / "X.npy")
    sessions = np.load(data_dir / "sessions.npy")

    if mode == "binary":
        y = np.load(data_dir / "y.npy")
        target_name = f"Track {config.TARGET_TRACK} vs Rest"
    else:
        y = np.load(data_dir / "tracks.npy")
        target_name = "Multiclass"

    unique_sessions = np.unique(sessions)

    print("\n==========================================")
    print("LEAVE ONE SESSION OUT")
    print("==========================================")
    print(f"Modo: {target_name}")
    print(f"Sessões encontradas: {list(unique_sessions)}")

    if classifier.lower() == "lda":
        clf = LinearDiscriminantAnalysis(
            solver="lsqr",
            shrinkage="auto"
        )
    else:
        clf = SVC(
            kernel="rbf",
            C=1.0,
            class_weight="balanced",
            random_state=42
        )

    accs = []
    f1s = []

    y_true_all = []
    y_pred_all = []

    for session in unique_sessions:

        print(f"\nTeste -> {session}")

        train_mask = sessions != session
        test_mask = sessions == session

        X_train = X[train_mask]
        X_test = X[test_mask]

        y_train = y[train_mask]
        y_test = y[test_mask]

        scaler = StandardScaler()

        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        clf.fit(X_train, y_train)

        preds = clf.predict(X_test)

        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="macro")

        print(f"Accuracy : {acc:.3f}")
        print(f"Macro F1 : {f1:.3f}")

        print(confusion_matrix(y_test, preds))

        accs.append(acc)
        f1s.append(f1)

        y_true_all.extend(y_test)
        y_pred_all.extend(preds)

    print("\n==========================================")
    print("RESULTADO FINAL")
    print("==========================================")
    print(f"Accuracy Média : {np.mean(accs):.3f} (+/- {np.std(accs):.3f})")
    print(f"Macro F1 Médio : {np.mean(f1s):.3f}")

    print("\nConfusão Global")
    print(confusion_matrix(y_true_all, y_pred_all))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        default="binary",
        choices=["binary", "multiclass"]
    )

    parser.add_argument(
        "--classifier",
        default="svm",
        choices=["svm", "lda"]
    )

    args = parser.parse_args()

    train_sessions(
        mode=args.mode,
        classifier=args.classifier
    )
