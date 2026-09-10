"""
training/train_rhythm_decoder.py
===============================
Trains the 4-class mental rhythm decoding model for BCI Tower Defense.
Uses state-of-the-art Riemannian Tangent Space geometry and Filter Bank CSP:
  - Supports multi-session pooling (e.g. sub-02 all 5 sessions or single session)
  - Evaluates 5-fold Stratified Cross-Validation
  - Exports trained model to models/rhythm_model_sub02_riemann.joblib (or specified path)
"""

import os
import sys
import glob
import json
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

# Ensure root dir is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from classifier.rhythm_decoder import (
    RiemannianTangentSpaceClassifier,
    FilterBankCSPClassifier,
    ELEMENT_NAMES
)
from analysis.analyze_tower_defense_rhythm_decoding import (
    find_available_sessions,
    load_single_session_raw,
    preprocess_continuous_eeg,
    extract_session_epochs
)
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, confusion_matrix, cohen_kappa_score


def train_and_export_rhythm_decoder(
    bids_root=None,
    sub_id="02",
    ses_id="all",
    model_type="riemann",
    output_path=None,
    report_path=None,
    C=0.1
):
    if bids_root is None:
        bids_root = getattr(config, "BIDS_ROOT", "/home/guilhermecoto/Documentos/Lasige/nautilus_bci/scripts/bids/bids_tower_defense")

    sub_clean = sub_id.replace("sub-", "")
    
    # Resolve target sessions
    if ses_id.lower() == "all":
        available_ses = find_available_sessions(bids_root, sub_clean)
        target_sessions = available_ses
    else:
        target_sessions = [s.strip().replace("ses-", "") for s in ses_id.split(",") if s.strip()]

    if not target_sessions:
        raise ValueError(f"No valid sessions found for sub-{sub_clean} in {bids_root}")

    # Default output path
    tag = f"sub{sub_clean}_{model_type}"
    if len(target_sessions) == 1:
        tag += f"_ses{target_sessions[0]}"
    else:
        tag += f"_pooled_{len(target_sessions)}sessions"

    if output_path is None:
        output_path = ROOT_DIR / "models" / f"rhythm_model_{tag}.joblib"
    else:
        output_path = Path(output_path)

    if report_path is None:
        report_path = ROOT_DIR / "models" / f"rhythm_decoding_report_{tag}.json"
    else:
        report_path = Path(report_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" TRAINING 4-CLASS REAL-TIME RHYTHM DECODER FOR BCI TOWER DEFENSE ".center(80, "="))
    print("=" * 80)
    print(f"[*] BIDS Root     : {bids_root}")
    print(f"[*] Subject       : sub-{sub_clean}")
    print(f"[*] Sessions ({len(target_sessions)}): {target_sessions}")
    print(f"[*] Model Type    : {model_type.upper()}")
    print(f"[*] Output Model  : {output_path}")
    print(f"[*] Output Report : {report_path}")

    # 1. Load and pool all target sessions
    all_X_im, all_X_lis, all_y = [], [], []
    sfreq = 250.0
    class_names = ["FIRE", "WATER", "WIND", "ELECTRICITY"]

    for ses in target_sessions:
        print(f"\n---> Loading & Preprocessing Session ses-{ses}...")
        raw_uv, df_events, sfreq, ch_names = load_single_session_raw(bids_root, sub_clean, ses)
        clean_eeg = preprocess_continuous_eeg(
            raw_uv,
            sfreq=sfreq,
            l_freq=config.LOWCUT,
            h_freq=config.HIGHCUT,
            notch_freq=config.NOTCH,
            spatial_mode="robust_car",
            ch_names=ch_names
        )
        X_im, X_lis, _, y, _, _ = extract_session_epochs(
            clean_eeg,
            df_events,
            ses_id=ses,
            sfreq=sfreq,
            win_len_s=config.WINDOW_SIZE_SEC
        )
        print(f"     [+] ses-{ses}: Extracted {len(y)} trials {dict(pd.Series(y).value_counts())}")
        all_X_im.append(X_im)
        all_X_lis.append(X_lis)
        all_y.append(y)

    X_im_pooled = np.concatenate(all_X_im, axis=0)
    X_lis_pooled = np.concatenate(all_X_lis, axis=0)
    y_pooled = np.concatenate(all_y, axis=0)

    print("\n" + "=" * 80)
    print(f" TOTAL DATASET: {len(y_pooled)} TRIALS ACROSS {len(target_sessions)} SESSIONS ".center(80, "="))
    print(f" Class Breakdown: {dict(pd.Series(y_pooled).value_counts())}")
    print(f" Epoch Shape    : {X_im_pooled.shape}")
    print("=" * 80)

    # Helper function to instantiate classifier
    def make_clf():
        if model_type == "riemann":
            return RiemannianTangentSpaceClassifier(C=C, max_iter=500, random_state=42)
        elif model_type == "fbcsp":
            return FilterBankCSPClassifier(sfreq=sfreq, n_components=4, clf_type="logreg", C=0.5, random_state=42)
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

    # 2. 5-Fold Cross-Validation on Mental Imagery
    print("\n" + "-" * 80)
    print(" 5-FOLD CROSS-VALIDATION EVALUATION (MENTAL IMAGERY) ".center(80, "-"))
    print("-" * 80)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_accs = []
    cv_f1s = []
    cv_kappas = []
    oof_preds = np.zeros_like(y_pooled)

    for tr_idx, te_idx in cv.split(X_im_pooled, y_pooled):
        clf = make_clf()
        clf.fit(X_im_pooled[tr_idx], y_pooled[tr_idx])
        p_te = clf.predict(X_im_pooled[te_idx])
        oof_preds[te_idx] = p_te
        cv_accs.append(accuracy_score(y_pooled[te_idx], p_te))
        cv_f1s.append(f1_score(y_pooled[te_idx], p_te, average="macro"))
        cv_kappas.append(cohen_kappa_score(y_pooled[te_idx], p_te))

    mean_acc = float(np.mean(cv_accs))
    std_acc = float(np.std(cv_accs))
    mean_f1 = float(np.mean(cv_f1s))
    mean_kappa = float(np.mean(cv_kappas))
    cm_oof = confusion_matrix(y_pooled, oof_preds).tolist()

    print(f"[*] 5-Fold CV Accuracy (Imagine): {mean_acc*100:.2f}% ± {std_acc*100:.2f}%")
    print(f"[*] 5-Fold Macro F1             : {mean_f1:.3f}")
    print(f"[*] 5-Fold Cohen's Kappa        : {mean_kappa:.3f}")
    print(f"[*] Theoretical Chance Baseline : 25.00% (4 classes)")

    # 3. Train Final Model on All Data
    print(f"\n[*] Training final production {model_type.upper()} model on full {len(y_pooled)} trials...")
    final_model = make_clf()
    final_model.fit(X_im_pooled, y_pooled)

    train_acc = float(accuracy_score(y_pooled, final_model.predict(X_im_pooled)))
    print(f"[+] Final Model Fit Complete. Self-Accuracy: {train_acc*100:.2f}%")

    # 4. Export Artifacts
    export_dict = {
        'model': final_model,
        'model_name': f"{model_type.upper()}_4Class_TowerDefense",
        'model_type': model_type,
        'subject': sub_clean,
        'sessions': target_sessions,
        'classes': class_names,
        'element_mapping': ELEMENT_NAMES,
        'sfreq': sfreq,
        'window_size_sec': config.WINDOW_SIZE_SEC,
        'n_trials': len(y_pooled),
        'metrics': {
            'cv_accuracy_mean': mean_acc,
            'cv_accuracy_std': std_acc,
            'cv_f1_macro': mean_f1,
            'cv_cohen_kappa': mean_kappa,
            'self_accuracy': train_acc
        },
        'confusion_matrix': cm_oof
    }

    joblib.dump(export_dict, output_path)
    print(f"[+] Exported joblib artifact: {output_path}")

    # Also export pickle version
    pkl_output_path = output_path.with_suffix(".pkl")
    try:
        import pickle
        with open(pkl_output_path, "wb") as f:
            pickle.dump(export_dict, f)
        print(f"[+] Exported pickle artifact: {pkl_output_path}")
    except Exception as e:
        print(f"[!] Warning: Could not export pickle artifact: {e}")

    # 5. Export JSON Report
    report = {
        'model_name': export_dict['model_name'],
        'model_type': model_type,
        'subject': f"sub-{sub_clean}",
        'sessions_trained': target_sessions,
        'n_total_trials': len(y_pooled),
        'metrics': export_dict['metrics'],
        'confusion_matrix': cm_oof
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"[+] Exported JSON report: {report_path}")

    print("\n" + "=" * 80)
    print(" RHYTHM MODEL TRAINING COMPLETED SUCCESSFULLY! ".center(80, "="))
    print("=" * 80 + "\n")

    return final_model, report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train 4-Class Rhythm Decoder for Tower Defense")
    parser.add_argument("--bids-root", type=str, default=None, help="Path to BIDS dataset")
    parser.add_argument("--sub", type=str, default="02", help="Subject ID (default: 02)")
    parser.add_argument("--ses", type=str, default="all", help="Session IDs ('all', '05', '01,02,03,04,05')")
    parser.add_argument("--model-type", type=str, default="riemann", choices=["riemann", "fbcsp"], help="Model architecture")
    parser.add_argument("--C", type=float, default=0.1, help="Regularization parameter")
    parser.add_argument("--output", type=str, default=None, help="Output joblib file path")
    parser.add_argument("--report", type=str, default=None, help="Output JSON report path")
    args = parser.parse_args()

    train_and_export_rhythm_decoder(
        bids_root=args.bids_root,
        sub_id=args.sub,
        ses_id=args.ses,
        model_type=args.model_type,
        output_path=args.output,
        report_path=args.report,
        C=args.C
    )
