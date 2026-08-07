import itertools
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def train_pairwise():

    data_dir = Path(__file__).resolve().parent

    X = np.load(data_dir / "X.npy")
    tracks = np.load(data_dir / "tracks.npy")
    sessions = np.load(data_dir / "sessions.npy")

    unique_sessions = np.unique(sessions)

    print("=" * 50)
    print("PAIRWISE TRACK CLASSIFICATION (LOSO)")
    print("=" * 50)

    results = []

    # todas as combinações (1,2), (1,3), ...
    for track_a, track_b in itertools.combinations(range(1, 7), 2):

        print(f"\n========== Track {track_a} vs Track {track_b} ==========")

        # escolher apenas estas duas tracks
        mask = np.logical_or(
            tracks == track_a,
            tracks == track_b
        )

        X_pair = X[mask]
        y_pair = tracks[mask]
        session_pair = sessions[mask]

        # binário
        # Track A -> 0
        # Track B -> 1
        y_pair = (y_pair == track_b).astype(int)

        clf = SVC(
            kernel="rbf",
            C=1.0,
            class_weight="balanced",
            random_state=42
        )

        fold_acc = []
        fold_f1 = []

        y_true_all = []
        y_pred_all = []

        for test_session in unique_sessions:
            train_mask = session_pair != test_session
            test_mask = session_pair == test_session

            if np.sum(test_mask) == 0:
                continue

            X_train = X_pair[train_mask]
            X_test = X_pair[test_mask]

            y_train = y_pair[train_mask]
            y_test = y_pair[test_mask]

            scaler = StandardScaler()

            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            clf.fit(X_train, y_train)

            preds = clf.predict(X_test)

            fold_acc.append(
                accuracy_score(y_test, preds)
            )

            fold_f1.append(
                f1_score(y_test, preds, average="macro")
            )

            y_true_all.extend(y_test)
            y_pred_all.extend(preds)

        mean_acc = np.mean(fold_acc)
        mean_f1 = np.mean(fold_f1)

        print(f"Accuracy : {mean_acc:.3f}")
        print(f"Macro F1 : {mean_f1:.3f}")
        print(confusion_matrix(y_true_all, y_pred_all))

        results.append(
            (
                track_a,
                track_b,
                mean_acc,
                mean_f1
            )
        )

    print("\n")
    print("=" * 60)
    print("RESULTADOS FINAIS")
    print("=" * 60)
    print(f"{'Track A':<10}{'Track B':<10}{'Accuracy':<12}{'Macro F1'}")

    for r in sorted(results, key=lambda x: x[3], reverse=True):
        print(
            f"{r[0]:<10}"
            f"{r[1]:<10}"
            f"{r[2]:<12.3f}"
            f"{r[3]:.3f}"
        )


if __name__ == "__main__":
    train_pairwise()
