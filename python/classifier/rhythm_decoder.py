"""
classifier/rhythm_decoder.py
===========================
Rhythm Decoder for BCI Tower Defense 4-Class Mental Imagery & Auditory Perception.
Elements / Classes:
  0: FIRE
  1: WATER
  2: WIND
  3: ELECTRICITY

Implements:
  - FilterBankCSPClassifier: Multi-band One-vs-Rest CSP spatial filtering + Scaler + LogisticRegression/LDA
  - RhythmPredictor: High-level inference engine for single real-time EEG windows
"""

import numpy as np
import scipy.signal as signal
from scipy.linalg import eigh
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import joblib

# Default EEG rhythm bands
DEFAULT_BANDS = [
    ('Theta', 4.0, 8.0),
    ('Alpha', 8.0, 12.0),
    ('Low-Beta', 12.0, 20.0),
    ('High-Beta', 20.0, 32.0),
    ('Gamma', 32.0, 45.0)
]

ELEMENT_NAMES = {
    0: "FIRE",
    1: "WATER",
    2: "WIND",
    3: "ELECTRICITY"
}

ELEMENT_IDS = {v: k for k, v in ELEMENT_NAMES.items()}


def compute_ovr_csp(X, y, n_components=4):
    """
    Computes One-vs-Rest CSP spatial filters.
    X: shape (n_epochs, n_channels, n_samples)
    y: shape (n_epochs,)
    n_components: number of CSP filters per class (half from each end)
    """
    n_epochs, n_ch, _ = X.shape
    classes = np.unique(y)
    covs = [np.cov(X[i]) / (np.trace(np.cov(X[i])) + 1e-12) for i in range(n_epochs)]

    filters = []
    for c_id in classes:
        mask = (y == c_id)
        if not np.any(mask) or np.all(mask):
            continue
        cov_target = np.mean([covs[k] for k in range(len(covs)) if mask[k]], axis=0) + 1e-5 * np.eye(n_ch)
        cov_rest = np.mean([covs[k] for k in range(len(covs)) if not mask[k]], axis=0) + 1e-5 * np.eye(n_ch)
        vals, vecs = eigh(cov_target, cov_target + cov_rest)
        half = max(1, n_components // 2)
        filters.append(np.hstack([vecs[:, -half:], vecs[:, :half]]))

    if not filters:
        raise ValueError("Could not extract CSP filters: check class distribution.")

    return np.hstack(filters)


def project_csp_features(X, W):
    """
    Projects epochs through CSP spatial filters to log-variance features.
    X: shape (n_epochs, n_channels, n_samples)
    W: shape (n_channels, n_filters)
    Returns: shape (n_epochs, n_filters)
    """
    n_epochs = len(X)
    feats = np.zeros((n_epochs, W.shape[1]), dtype=np.float32)
    for i in range(n_epochs):
        proj = np.dot(W.T, X[i])  # (n_filters, n_samples)
        var = np.var(proj, axis=1)
        feats[i] = np.log(var + 1e-12)
    return feats


class FilterBankCSPClassifier(BaseEstimator, ClassifierMixin):
    """
    Filter Bank Common Spatial Pattern (FBCSP) Classifier.
    Extracts multi-band spatial filters and predicts 4-class mental rhythm probabilities.
    """

    def __init__(self, bands=None, sfreq=250.0, n_components=4, clf_type="logreg", C=0.5, random_state=42):
        self.bands = bands if bands is not None else DEFAULT_BANDS
        self.sfreq = float(sfreq)
        self.n_components = int(n_components)
        self.clf_type = clf_type
        self.C = float(C)
        self.random_state = random_state

        self.filters_ = []      # list of (b, a, W_csp)
        self.scaler_ = None
        self.classifier_ = None
        self.classes_ = None

    def _filter_epoch(self, epoch, b, a):
        # epoch: (n_channels, n_samples)
        return signal.filtfilt(b, a, epoch, axis=-1)

    def fit(self, X, y):
        """
        Fit FBCSP model on training data.
        X: shape (n_epochs, n_channels, n_samples)
        y: shape (n_epochs,)
        """
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.int32)

        if X.ndim != 3:
            raise ValueError(f"Expected 3D array (n_epochs, n_channels, n_samples), got {X.shape}")

        self.classes_ = np.unique(y)
        nyq = self.sfreq / 2.0
        self.filters_ = []
        band_feats = []

        for band_name, fmin, fmax in self.bands:
            b, a = signal.butter(4, [fmin / nyq, fmax / nyq], btype='band')
            X_filt = np.array([self._filter_epoch(X[i], b, a) for i in range(len(X))])
            W_csp = compute_ovr_csp(X_filt, y, n_components=self.n_components)
            self.filters_.append({
                'band_name': band_name,
                'b': b,
                'a': a,
                'W': W_csp
            })
            feats = project_csp_features(X_filt, W_csp)
            band_feats.append(feats)

        X_all_feats = np.hstack(band_feats)

        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(X_all_feats)

        if self.clf_type == "logreg":
            self.classifier_ = LogisticRegression(
                C=self.C,
                max_iter=500,
                random_state=self.random_state,
                solver='lbfgs'
            )
        elif self.clf_type == "lda":
            self.classifier_ = LinearDiscriminantAnalysis(solver='lsqr', shrinkage='auto')
        else:
            raise ValueError(f"Unknown classifier type: {self.clf_type}")

        self.classifier_.fit(X_scaled, y)
        return self

    def transform(self, X):
        """
        Extracts FBCSP feature representations.
        X: shape (n_epochs, n_channels, n_samples) or (n_channels, n_samples)
        """
        X = np.asarray(X, dtype=np.float64)
        if X.ndim == 2:
            X = X[np.newaxis, ...]

        band_feats = []
        for filt_info in self.filters_:
            b = filt_info['b']
            a = filt_info['a']
            W = filt_info['W']
            X_filt = np.array([self._filter_epoch(X[i], b, a) for i in range(len(X))])
            feats = project_csp_features(X_filt, W)
            band_feats.append(feats)

        all_feats = np.hstack(band_feats)
        return self.scaler_.transform(all_feats)

    def predict_proba(self, X):
        """
        Returns class probabilities for input windows.
        """
        features = self.transform(X)
        return self.classifier_.predict_proba(features)

    def predict(self, X):
        """
        Predicts class IDs.
        """
        features = self.transform(X)
        return self.classifier_.predict(features)


class RhythmPredictor:
    """
    Inference wrapper for real-time BCI rhythm decoding.
    Handles window formatting, spatial referencing, and confidence thresholding.
    """

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = Path(__file__).resolve().parent.parent / "models" / "rhythm_model.joblib"

        self.model_path = Path(model_path)
        self.model = None
        self.model_metadata = {}
        self.load_model()

    def load_model(self):
        if not self.model_path.exists():
            print(f"[RhythmPredictor Warning] Model not found at {self.model_path}. Please run training/train_rhythm_decoder.py")
            self.model = None
            return False

        data = joblib.load(self.model_path)
        if isinstance(data, dict):
            self.model = data.get("model")
            self.model_metadata = data
        else:
            self.model = data
            self.model_metadata = {}

        print(f"[RhythmPredictor] Successfully loaded model from {self.model_path.name}")
        return True

    def predict(self, eeg_window, confidence_threshold=0.35):
        """
        Predicts rhythm from a single EEG window.

        Parameters:
            eeg_window: np.ndarray of shape (n_channels, n_samples) or (n_samples, n_channels)
            confidence_threshold: float, minimal probability to consider rhythm active

        Returns:
            dict containing:
              - 'element': str ("FIRE", "WATER", "WIND", "ELECTRICITY")
              - 'element_id': int (0, 1, 2, 3)
              - 'confidence': float (max probability)
              - 'probabilities': dict mapping element name to float probability
              - 'is_rhythm_active': bool (confidence >= confidence_threshold)
        """
        if self.model is None:
            return {
                'element': "UNKNOWN",
                'element_id': -1,
                'confidence': 0.0,
                'probabilities': {name: 0.25 for name in ELEMENT_NAMES.values()},
                'is_rhythm_active': False
            }

        eeg = np.asarray(eeg_window, dtype=np.float64)

        # Standardize to (n_channels, n_samples)
        if eeg.ndim == 2:
            if eeg.shape[0] > eeg.shape[1] and eeg.shape[1] == 32:
                # Transpose from (n_samples, n_channels) to (n_channels, n_samples)
                eeg = eeg.T
        elif eeg.ndim == 1:
            raise ValueError("Expected 2D EEG window")

        # Predict probabilities
        probs = self.model.predict_proba(eeg)[0]
        pred_id = int(np.argmax(probs))
        confidence = float(probs[pred_id])
        pred_name = ELEMENT_NAMES.get(pred_id, f"CLASS_{pred_id}")

        prob_dict = {
            ELEMENT_NAMES.get(i, f"CLASS_{i}"): float(probs[i])
            for i in range(len(probs))
        }

        is_active = confidence >= confidence_threshold

        return {
            'element': pred_name,
            'element_id': pred_id,
            'confidence': confidence,
            'probabilities': prob_dict,
            'is_rhythm_active': is_active
        }
