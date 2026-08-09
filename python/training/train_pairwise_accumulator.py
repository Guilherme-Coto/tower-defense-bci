import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.pipeline import Pipeline

def train_pairwise_accumulator():
    data_dir = Path(__file__).resolve().parent

    print("Loading data...")
    try:
        X = np.load(data_dir / "X.npy")
        tracks = np.load(data_dir / "tracks.npy")
        sessions = np.load(data_dir / "sessions.npy")
        groups = np.load(data_dir / "groups.npy")
    except FileNotFoundError:
        print("Data files not found. Ensure X.npy, tracks.npy, sessions.npy, and groups.npy exist.")
        return

    unique_sessions = np.unique(sessions)

    print("=" * 80)
    print("PAIRWISE TRACK CLASSIFICATION - ACCUMULATOR DEMONSTRATION (LOSO)")
    print("=" * 80)

    # Dictionary to hold the final results
    results = []

    clf_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", ExtraTreesClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1))
    ])

    for track_a, track_b in itertools.combinations(range(1, 7), 2):
        print(f"\n========== Track {track_a} vs Track {track_b} ==========")

        mask = np.logical_or(tracks == track_a, tracks == track_b)
        X_pair = X[mask]
        y_pair = tracks[mask]
        session_pair = sessions[mask]
        groups_pair = groups[mask]

        # binarize: Track A -> 0, Track B -> 1
        y_pair = (y_pair == track_b).astype(int)

        all_y_true_windows = []
        all_y_pred_windows = []
        
        # Para guardar os resultados por trial (época acumulada)
        trial_y_true = []
        trial_y_pred = []
        
        for test_session in unique_sessions:
            train_mask = session_pair != test_session
            test_mask = session_pair == test_session

            if np.sum(test_mask) == 0:
                continue

            X_train = X_pair[train_mask]
            X_test = X_pair[test_mask]
            y_train = y_pair[train_mask]
            y_test = y_pair[test_mask]
            
            # The test trial IDs for accumulator logic
            groups_test = groups_pair[test_mask]

            clf_pipeline.fit(X_train, y_train)
            
            # Normal Hard Predictions (Window-Level)
            preds_hard = clf_pipeline.predict(X_test)
            all_y_true_windows.extend(y_test)
            all_y_pred_windows.extend(preds_hard)
            
            # Soft Predictions (Probabilities for Accumulator)
            preds_proba = clf_pipeline.predict_proba(X_test)[:, 1] # Probability of Class 1 (Track B)
            
            # Accumulator Logic (Trial-Level)
            unique_test_trials = np.unique(groups_test)
            
            for trial_id in unique_test_trials:
                idx = (groups_test == trial_id)
                # True label for this trial
                true_label = y_test[idx][0]
                
                # Average probability across all windows of this trial
                avg_prob = np.mean(preds_proba[idx])
                
                # Final decision: > 0.5 means Track B (1), otherwise Track A (0)
                final_decision = 1 if avg_prob > 0.5 else 0
                
                trial_y_true.append(true_label)
                trial_y_pred.append(final_decision)

        acc_window = accuracy_score(all_y_true_windows, all_y_pred_windows)
        f1_window = f1_score(all_y_true_windows, all_y_pred_windows, average="macro")
        
        acc_trial = accuracy_score(trial_y_true, trial_y_pred)
        f1_trial = f1_score(trial_y_true, trial_y_pred, average="macro")
        
        print(f"[Window-Level] Accuracy: {acc_window:.3f} | Macro F1: {f1_window:.3f} (Trained on Single Windows)")
        print(f"[Trial-Level]  Accuracy: {acc_trial:.3f} | Macro F1: {f1_trial:.3f} (Accumulated per 5s Epoch)")
        print(f"-> Gained: +{(acc_trial - acc_window)*100:.1f}% Accuracy")
        
        results.append({
            "track_a": track_a,
            "track_b": track_b,
            "acc_window": acc_window,
            "acc_trial": acc_trial,
            "f1_window": f1_window,
            "f1_trial": f1_trial
        })

    print("\n" + "=" * 80)
    print("FINAL COMPARISON (AVERAGE ACROSS ALL PAIRS)")
    print("=" * 80)
    
    avg_acc_win = np.mean([r["acc_window"] for r in results])
    avg_acc_trl = np.mean([r["acc_trial"] for r in results])
    
    avg_f1_win = np.mean([r["f1_window"] for r in results])
    avg_f1_trl = np.mean([r["f1_trial"] for r in results])

    print(f"Average Window-Level Accuracy: {avg_acc_win:.3f}")
    print(f"Average Trial-Level Accuracy : {avg_acc_trl:.3f}")
    print(f"Overall Accuracy BOOST       : +{(avg_acc_trl - avg_acc_win)*100:.1f}%\n")
    
    print(f"{'Pair':<10} | {'Window Acc':<12} | {'Trial Acc (5s)':<16} | {'Improvement'}")
    print("-" * 60)
    for r in sorted(results, key=lambda x: x["acc_trial"], reverse=True):
        pair = f"{r['track_a']} vs {r['track_b']}"
        diff = (r['acc_trial'] - r['acc_window']) * 100
        print(f"{pair:<10} | {r['acc_window']:.3f}        | {r['acc_trial']:.3f}            | +{diff:.1f}%")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    train_pairwise_accumulator()
