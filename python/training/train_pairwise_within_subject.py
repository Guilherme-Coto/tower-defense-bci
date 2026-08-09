import itertools
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupKFold

def train_pairwise_within_subject():
    data_dir = Path(__file__).resolve().parent

    print("Loading data...")
    try:
        X = np.load(data_dir / "X.npy")
        tracks = np.load(data_dir / "tracks.npy")
        groups = np.load(data_dir / "groups.npy")
    except FileNotFoundError:
        print("Data files not found. Please ensure X.npy, tracks.npy, and groups.npy exist in the training directory.")
        return

    print("=" * 70)
    print("PAIRWISE TRACK CLASSIFICATION - WITHIN-SUBJECT (GroupKFold)")
    print("=" * 70)
    print("Note: Using GroupKFold on global_trial_id to prevent data leakage")
    print("between overlapping windows of the same trial.")
    print("=" * 70)

    # We will use ExtraTrees as it was our best performer previously
    clf_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", ExtraTreesClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1))
    ])

    overall_results = []
    
    # K-Fold CV configurator (5 folds)
    gkf = GroupKFold(n_splits=5)

    # todas as combinações (1,2), (1,3), ...
    for track_a, track_b in itertools.combinations(range(1, 7), 2):
        print(f"\n========== Track {track_a} vs Track {track_b} ==========")

        # escolher apenas estas duas tracks
        mask = np.logical_or(tracks == track_a, tracks == track_b)

        X_pair = X[mask]
        y_pair = tracks[mask]
        groups_pair = groups[mask]

        # binário: Track A -> 0, Track B -> 1
        y_pair = (y_pair == track_b).astype(int)

        fold_acc = []
        fold_f1 = []
        
        # GroupKFold Cross-validation
        # This ensures that windows from the same trial ID stay in the same fold (train OR test)
        for train_idx, test_idx in gkf.split(X_pair, y_pair, groups=groups_pair):
            
            X_train, X_test = X_pair[train_idx], X_pair[test_idx]
            y_train, y_test = y_pair[train_idx], y_pair[test_idx]
            
            # Skip if a fold somehow doesn't have both classes (rare but possible with GroupKFold if not many trials)
            if len(np.unique(y_test)) < 2:
                 continue

            clf_pipeline.fit(X_train, y_train)
            preds = clf_pipeline.predict(X_test)

            fold_acc.append(accuracy_score(y_test, preds))
            fold_f1.append(f1_score(y_test, preds, average="macro"))

        if len(fold_acc) > 0:
            mean_acc = np.mean(fold_acc)
            mean_f1 = np.mean(fold_f1)
        else:
            mean_acc = 0.0
            mean_f1 = 0.0
            
        print(f"Accuracy: {mean_acc:.3f} | Macro F1: {mean_f1:.3f}")
        
        overall_results.append({
            "track_a": track_a,
            "track_b": track_b,
            "acc": mean_acc,
            "f1": mean_f1
        })

    print("\n" + "=" * 80)
    print("DETAILED RESULTS (WITHIN-SUBJECT)")
    print("=" * 80)
    
    avg_acc = np.mean([r["acc"] for r in overall_results])
    avg_f1 = np.mean([r["f1"] for r in overall_results])
    print(f"Overall Average Accuracy: {avg_acc:.3f}")
    print(f"Overall Average Macro F1: {avg_f1:.3f}")
    print("-" * 40)
    print(f"{'Track A':<10}{'Track B':<10}{'Accuracy':<12}{'Macro F1'}")
    
    for r in sorted(overall_results, key=lambda x: x["f1"], reverse=True):
        print(f"{r['track_a']:<10}{r['track_b']:<10}{r['acc']:<12.3f}{r['f1']:.3f}")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    train_pairwise_within_subject()
