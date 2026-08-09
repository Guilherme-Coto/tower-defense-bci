import itertools
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

def train_pairwise_v2():
    data_dir = Path(__file__).resolve().parent

    print("Loading data...")
    try:
        X = np.load(data_dir / "X.npy")
        tracks = np.load(data_dir / "tracks.npy")
        sessions = np.load(data_dir / "sessions.npy")
    except FileNotFoundError:
        print("Data files not found. Please ensure X.npy, tracks.npy, and sessions.npy exist in the training directory.")
        return

    unique_sessions = np.unique(sessions)

    print("=" * 70)
    print("PAIRWISE TRACK CLASSIFICATION (LOSO) - MULTIPLE PIPELINES")
    print("=" * 70)

    # Define different pipelines to test
    pipelines = {
        "Baseline SVM": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="rbf", C=1.0, class_weight="balanced", random_state=42))
        ]),
        "SVM + SelectKBest(20)": Pipeline([
            ("scaler", StandardScaler()),
            ("selector", SelectKBest(f_classif, k=20)),
            ("clf", SVC(kernel="rbf", C=1.0, class_weight="balanced", random_state=42))
        ]),
        "SVM + PCA(0.95)": Pipeline([
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=0.95, random_state=42)),
            ("clf", SVC(kernel="rbf", C=1.0, class_weight="balanced", random_state=42))
        ]),
        "Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1))
        ]),
        "Extra Trees": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", ExtraTreesClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1))
        ])
    }

    # Dict to store overall results per pipeline: {(pipeline_name, track_a, track_b): (acc, f1)}
    overall_results = []

    # todas as combinações (1,2), (1,3), ...
    for track_a, track_b in itertools.combinations(range(1, 7), 2):
        print(f"\n========== Track {track_a} vs Track {track_b} ==========")

        # escolher apenas estas duas tracks
        mask = np.logical_or(tracks == track_a, tracks == track_b)

        X_pair = X[mask]
        y_pair = tracks[mask]
        session_pair = sessions[mask]

        # binário: Track A -> 0, Track B -> 1
        y_pair = (y_pair == track_b).astype(int)

        for pipe_name, clf_pipeline in pipelines.items():
            fold_acc = []
            fold_f1 = []
            
            # LOSO Cross-validation
            for test_session in unique_sessions:
                train_mask = session_pair != test_session
                test_mask = session_pair == test_session

                if np.sum(test_mask) == 0:
                    continue

                X_train = X_pair[train_mask]
                X_test = X_pair[test_mask]
                y_train = y_pair[train_mask]
                y_test = y_pair[test_mask]

                clf_pipeline.fit(X_train, y_train)
                preds = clf_pipeline.predict(X_test)

                fold_acc.append(accuracy_score(y_test, preds))
                fold_f1.append(f1_score(y_test, preds, average="macro"))

            mean_acc = np.mean(fold_acc)
            mean_f1 = np.mean(fold_f1)
            
            print(f"[{pipe_name:<22}] Accuracy: {mean_acc:.3f} | Macro F1: {mean_f1:.3f}")
            
            overall_results.append({
                "pipeline": pipe_name,
                "track_a": track_a,
                "track_b": track_b,
                "acc": mean_acc,
                "f1": mean_f1
            })

    print("\n" + "=" * 80)
    print("AVERAGE RESULTS ACROSS ALL PAIRS")
    print("=" * 80)
    
    # Calculate average performance for each pipeline across all pairs
    pipe_avg_acc = {}
    pipe_avg_f1 = {}
    
    for pipe_name in pipelines.keys():
        pipe_results = [r for r in overall_results if r["pipeline"] == pipe_name]
        if pipe_results:
            pipe_avg_acc[pipe_name] = np.mean([r["acc"] for r in pipe_results])
            pipe_avg_f1[pipe_name] = np.mean([r["f1"] for r in pipe_results])
            
    # Sort pipelines by Average F1
    sorted_pipes = sorted(pipe_avg_f1.keys(), key=lambda p: pipe_avg_f1[p], reverse=True)
    
    print(f"{'Pipeline':<25} | {'Avg Accuracy':<15} | {'Avg Macro F1'}")
    print("-" * 65)
    for p in sorted_pipes:
        print(f"{p:<25} | {pipe_avg_acc[p]:.3f}           | {pipe_avg_f1[p]:.3f}")

    print("\n" + "=" * 80)
    print("DETAILED RESULTS FOR THE BEST PIPELINE")
    print("=" * 80)
    best_pipe = sorted_pipes[0]
    best_pipe_results = [r for r in overall_results if r["pipeline"] == best_pipe]
    
    print(f"Best Pipeline: {best_pipe}")
    print(f"{'Track A':<10}{'Track B':<10}{'Accuracy':<12}{'Macro F1'}")
    
    for r in sorted(best_pipe_results, key=lambda x: x["f1"], reverse=True):
        print(f"{r['track_a']:<10}{r['track_b']:<10}{r['acc']:<12.3f}{r['f1']:.3f}")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning) # Ignore some sklearn warnings if they occur
    train_pairwise_v2()
