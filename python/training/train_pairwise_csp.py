import itertools
from pathlib import Path
import numpy as np
import scipy.signal as signal
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import ExtraTreesClassifier
from mne.decoding import CSP

# ---------------------------------------------------------
# HELPER FOR FILTERING
# ---------------------------------------------------------
def apply_bandpass(X, lowcut, highcut, fs=250.0, order=4):
    """
    Apply a Butterworth bandpass filter to the EEG data.
    X shape: (trials, channels, time)
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    
    # Apply filter along the time axis (axis=-1)
    X_filtered = signal.filtfilt(b, a, X, axis=-1)
    return X_filtered

def train_pairwise_fbcsp():
    data_dir = Path(__file__).resolve().parent

    print("Loading raw dataset for FBCSP...")
    try:
        X = np.load(data_dir / "X_raw.npy")
        tracks = np.load(data_dir / "tracks.npy")
        groups = np.load(data_dir / "groups.npy")
    except FileNotFoundError:
        print("Data files not found. Ensure X_raw.npy exists (run build_dataset_raw.py).")
        return

    print("=" * 70)
    print("PAIRWISE TRACK CLASSIFICATION - FBCSP + WITHIN-SUBJECT")
    print("=" * 70)
    print(f"Loaded X_raw shape: {X.shape}")
    print("=" * 70)

    # Filter Bands for FBCSP
    bands = {
        "Theta": (4.0, 8.0),
        "Alpha": (8.0, 13.0),
        "Beta": (13.0, 30.0)
    }

    # Number of CSP components PER band
    n_components_per_band = 4 

    overall_results = []
    gkf = GroupKFold(n_splits=5)

    # We will test two classifiers on the concatenated CSP features
    # 1. LDA
    # 2. Extra Trees
    clf_names = ["FBCSP + LDA", "FBCSP + Extra Trees"]

    for track_a, track_b in itertools.combinations(range(1, 7), 2):
        print(f"\n========== Track {track_a} vs Track {track_b} ==========")

        mask = np.logical_or(tracks == track_a, tracks == track_b)
        X_pair = X[mask]
        y_pair = tracks[mask]
        groups_pair = groups[mask]

        # binarize
        y_pair = (y_pair == track_b).astype(int)

        fold_metrics = {name: {"acc": [], "f1": []} for name in clf_names}
        
        for train_idx, test_idx in gkf.split(X_pair, y_pair, groups=groups_pair):
            X_train_raw, X_test_raw = X_pair[train_idx], X_pair[test_idx]
            y_train, y_test = y_pair[train_idx], y_pair[test_idx]
            
            if len(np.unique(y_test)) < 2:
                 continue

            # -------------------------------------------------
            # FBCSP FEATURE EXTRACTION
            # -------------------------------------------------
            X_train_features = []
            X_test_features = []
            
            for band_name, (low, high) in bands.items():
                # 1. Filter data for the specific band
                X_tr_filt = apply_bandpass(X_train_raw, low, high)
                X_te_filt = apply_bandpass(X_test_raw, low, high)
                
                # 2. Fit CSP on the training data of this band
                csp = CSP(n_components=n_components_per_band, reg=None, log=True, norm_trace=False)
                
                # csp.fit_transform returns (trials, n_components)
                feats_tr = csp.fit_transform(X_tr_filt, y_train)
                feats_te = csp.transform(X_te_filt)
                
                X_train_features.append(feats_tr)
                X_test_features.append(feats_te)
                
            # 3. Concatenate all band features
            # Resulting shape: (trials, 3_bands * 4_components) = (trials, 12)
            X_train_fbcsp = np.hstack(X_train_features)
            X_test_fbcsp = np.hstack(X_test_features)
            
            # 4. Scale features
            scaler = StandardScaler()
            X_train_fbcsp = scaler.fit_transform(X_train_fbcsp)
            X_test_fbcsp = scaler.transform(X_test_fbcsp)
            
            # -------------------------------------------------
            # CLASSIFICATION
            # -------------------------------------------------
            # Model 1: LDA
            lda = LinearDiscriminantAnalysis()
            lda.fit(X_train_fbcsp, y_train)
            preds_lda = lda.predict(X_test_fbcsp)
            fold_metrics["FBCSP + LDA"]["acc"].append(accuracy_score(y_test, preds_lda))
            fold_metrics["FBCSP + LDA"]["f1"].append(f1_score(y_test, preds_lda, average="macro"))
            
            # Model 2: Extra Trees
            et = ExtraTreesClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1)
            et.fit(X_train_fbcsp, y_train)
            preds_et = et.predict(X_test_fbcsp)
            fold_metrics["FBCSP + Extra Trees"]["acc"].append(accuracy_score(y_test, preds_et))
            fold_metrics["FBCSP + Extra Trees"]["f1"].append(f1_score(y_test, preds_et, average="macro"))

        # Aggregate Results
        for name in clf_names:
            if len(fold_metrics[name]["acc"]) > 0:
                mean_acc = np.mean(fold_metrics[name]["acc"])
                mean_f1 = np.mean(fold_metrics[name]["f1"])
            else:
                mean_acc, mean_f1 = 0.0, 0.0
                
            print(f"[{name:<20}] Accuracy: {mean_acc:.3f} | Macro F1: {mean_f1:.3f}")
            
            overall_results.append({
                "pipeline": name,
                "track_a": track_a,
                "track_b": track_b,
                "acc": mean_acc,
                "f1": mean_f1
            })

    print("\n" + "=" * 80)
    print("AVERAGE RESULTS ACROSS ALL PAIRS (FBCSP)")
    print("=" * 80)
    
    pipe_avg_acc = {}
    pipe_avg_f1 = {}
    
    for name in clf_names:
        pipe_results = [r for r in overall_results if r["pipeline"] == name]
        if pipe_results:
            pipe_avg_acc[name] = np.mean([r["acc"] for r in pipe_results])
            pipe_avg_f1[name] = np.mean([r["f1"] for r in pipe_results])
            
    sorted_pipes = sorted(pipe_avg_f1.keys(), key=lambda p: pipe_avg_f1[p], reverse=True)
    
    print(f"{'Pipeline':<20} | {'Avg Accuracy':<15} | {'Avg Macro F1'}")
    print("-" * 55)
    for p in sorted_pipes:
        print(f"{p:<20} | {pipe_avg_acc[p]:.3f}           | {pipe_avg_f1[p]:.3f}")

    print("\n" + "=" * 80)
    print("DETAILED RESULTS FOR THE BEST FBCSP PIPELINE")
    print("=" * 80)
    best_pipe = sorted_pipes[0]
    best_pipe_results = [r for r in overall_results if r["pipeline"] == best_pipe]
    
    print(f"Best Pipeline: {best_pipe}")
    print(f"{'Track A':<10}{'Track B':<10}{'Accuracy':<12}{'Macro F1'}")
    
    for r in sorted(best_pipe_results, key=lambda x: x["f1"], reverse=True):
        print(f"{r['track_a']:<10}{r['track_b']:<10}{r['acc']:<12.3f}{r['f1']:.3f}")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    train_pairwise_fbcsp()
