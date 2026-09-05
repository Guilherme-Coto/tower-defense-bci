"""
training/train_rhythm_decoder.py
===============================
Trains the 4-class mental rhythm decoding model for BCI Tower Defense.
Uses the algorithms and findings from analyze_tower_defense_rhythm_decoding.py:
  - Filter Bank CSP (FBCSP) across 5 rhythm frequency bands
  - One-vs-Rest CSP spatial filters
  - Regularized classification on pooled / transfer auditory perception and mental imagery
  - Exports trained model to models/rhythm_model.joblib
"""

import os
import sys
import json
import argparse
from pathlib import Path
import numpy as np
import joblib

# Ensure root dir is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from classifier.rhythm_decoder import FilterBankCSPClassifier, ELEMENT_NAMES
from analysis.analyze_tower_defense_rhythm_decoding import (
    load_single_session_raw,
    preprocess_continuous_eeg,
    extract_session_epochs
)
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, confusion_matrix


def train_and_export_rhythm_decoder(
    bids_root=None,
    sub_id="01",
    ses_id="01",
    output_path=None,
    report_path=None
):
    if bids_root is None:
        bids_root = getattr(config, "BIDS_ROOT", "/home/guilhermecoto/Documentos/Lasige/nautilus_bci/scripts/bids/bids_tower_defense")

    if output_path is None:
        output_path = ROOT_DIR / "models" / "rhythm_model.joblib"
    else:
        output_path = Path(output_path)

    if report_path is None:
        report_path = ROOT_DIR / "models" / "rhythm_decoding_report.json"
    else:
        report_path = Path(report_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" TRAINING 4-CLASS REAL-TIME RHYTHM DECODER FOR BCI TOWER DEFENSE ".center(80, "="))
    print("=" * 80)
    print(f"[*] BIDS Root : {bids_root}")
    print(f"[*] Subject   : sub-{sub_id}")
    print(f"[*] Session   : ses-{ses_id}")
    print(f"[*] Output    : {output_path}")

    # 1. Load raw data and preprocess
    raw_uv, df_events, sfreq, ch_names = load_single_session_raw(bids_root, sub_id, ses_id)
    print(f"[+] Loaded raw EEG: {raw_uv.shape[0]} samples, {raw_uv.shape[1]} channels @ {sfreq} Hz")

    clean_eeg = preprocess_continuous_eeg(
        raw_uv,
        sfreq=sfreq,
        l_freq=config.LOWCUT,
        h_freq=config.HIGHCUT,
        notch_freq=config.NOTCH,
        spatial_mode="robust_car",
        ch_names=ch_names
    )
    print("[+] Preprocessing completed (Bandpass 1-45 Hz, Notch 50 Hz, Robust CAR)")

    # 2. Extract epochs
    X_im, X_lis, X_blk, y, df_meta, class_names = extract_session_epochs(
        clean_eeg,
        df_events,
        ses_id=ses_id,
        sfreq=sfreq,
        win_len_s=config.WINDOW_SIZE_SEC
    )
    print(f"[+] Extracted Trials: Imagine={len(X_im)}, Listen={len(X_lis)}, Blinking={len(X_blk)}")

    # 3. Cross-Validation Benchmarking
    print("\n" + "-" * 80)
    print(" 5-FOLD CROSS-VALIDATION EVALUATION ".center(80, "-"))
    print("-" * 80)

    # A. Cross-Condition Zero-Shot Transfer: Train Listen -> Test Imagine
    clf_transfer = FilterBankCSPClassifier(sfreq=sfreq, n_components=4, clf_type="logreg", C=0.5)
    clf_transfer.fit(X_lis, y)
    p_im_transfer = clf_transfer.predict(X_im)
    acc_transfer = float(accuracy_score(y, p_im_transfer))
    f1_transfer = float(f1_score(y, p_im_transfer, average="macro"))
    cm_transfer = confusion_matrix(y, p_im_transfer).tolist()

    print(f"[*] Transfer (Train Listen -> Test Imagine) : Acc = {acc_transfer*100:.2f}%, F1 = {f1_transfer:.3f}")

    # B. Pooled Listen + Imagine 5-fold CV
    X_pooled = np.concatenate([X_lis, X_im], axis=0)
    y_pooled = np.concatenate([y, y], axis=0)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_accs = []
    cv_f1s = []
    oof_preds = np.zeros_like(y_pooled)

    for tr_idx, te_idx in cv.split(X_pooled, y_pooled):
        clf_fold = FilterBankCSPClassifier(sfreq=sfreq, n_components=4, clf_type="logreg", C=0.5)
        clf_fold.fit(X_pooled[tr_idx], y_pooled[tr_idx])
        p_fold = clf_fold.predict(X_pooled[te_idx])
        oof_preds[te_idx] = p_fold
        cv_accs.append(accuracy_score(y_pooled[te_idx], p_fold))
        cv_f1s.append(f1_score(y_pooled[te_idx], p_fold, average="macro"))

    mean_cv_acc = float(np.mean(cv_accs))
    std_cv_acc = float(np.std(cv_accs))
    mean_cv_f1 = float(np.mean(cv_f1s))
    cm_pooled = confusion_matrix(y_pooled, oof_preds).tolist()

    print(f"[*] Pooled Listen+Imagine 5-Fold CV         : Acc = {mean_cv_acc*100:.2f}% ± {std_cv_acc*100:.2f}%, F1 = {mean_cv_f1:.3f}")
    print(f"[*] Theoretical Chance Baseline             : 25.00% (4 classes)")

    # 4. Train Final Production Model on Pooled Auditory + Imagery Representations
    print("\n[*] Training final production model on full pooled dataset (152 epochs)...")
    final_model = FilterBankCSPClassifier(sfreq=sfreq, n_components=4, clf_type="logreg", C=0.5)
    final_model.fit(X_pooled, y_pooled)

    # Quick sanity check on self-prediction
    train_acc = float(accuracy_score(y_pooled, final_model.predict(X_pooled)))
    print(f"[+] Final Model Fit Completed. Self-Fit Accuracy: {train_acc*100:.2f}%")

    # 5. Export Model Artifact
    export_dict = {
        'model': final_model,
        'model_name': 'FilterBankCSP_LogisticRegression_4Class',
        'classes': class_names,
        'element_mapping': ELEMENT_NAMES,
        'sfreq': sfreq,
        'window_size_sec': config.WINDOW_SIZE_SEC,
        'train_samples': len(y_pooled),
        'metrics': {
            'transfer_accuracy': acc_transfer,
            'transfer_f1': f1_transfer,
            'pooled_cv_accuracy': mean_cv_acc,
            'pooled_cv_std': std_cv_acc,
            'pooled_cv_f1': mean_cv_f1,
            'self_accuracy': train_acc
        }
    }

    joblib.dump(export_dict, output_path)
    print(f"[+] Successfully exported model artifact to: {output_path}")

    # 6. Save JSON Report
    report = {
        'model_name': 'FilterBankCSP_LogisticRegression_4Class',
        'subject': sub_id,
        'session': ses_id,
        'classes': class_names,
        'metrics': {
            'transfer_accuracy': acc_transfer,
            'transfer_f1': f1_transfer,
            'pooled_cv_accuracy': mean_cv_acc,
            'pooled_cv_std': std_cv_acc,
            'pooled_cv_f1': mean_cv_f1,
            'self_accuracy': train_acc
        },
        'confusion_matrices': {
            'transfer_listen_to_imagine': cm_transfer,
            'pooled_cv': cm_pooled
        }
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"[+] Saved decoding report to: {report_path}")

    print("\n" + "=" * 80)
    print(" RHYTHM MODEL TRAINING COMPLETED SUCCESSFULLY! ".center(80, "="))
    print("=" * 80 + "\n")

    return final_model, report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train 4-Class Rhythm Decoder for Tower Defense")
    parser.add_argument("--bids-root", type=str, default=None, help="Path to BIDS dataset")
    parser.add_argument("--sub", type=str, default="01", help="Subject ID")
    parser.add_argument("--ses", type=str, default="01", help="Session ID")
    parser.add_argument("--output", type=str, default=None, help="Output joblib file path")
    args = parser.parse_args()

    train_and_export_rhythm_decoder(
        bids_root=args.bids_root,
        sub_id=args.sub,
        ses_id=args.ses,
        output_path=args.output
    )
