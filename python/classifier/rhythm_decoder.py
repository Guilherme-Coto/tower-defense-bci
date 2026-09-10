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


def compute_covariance_matrices(X):
    """
    Computes regularized trace-normalized covariance matrices.
    X: shape (n_epochs, n_channels, n_samples)
    Returns: (n_epochs, n_channels, n_channels)
    """
    n_epochs, n_ch, _ = X.shape
    covs = np.zeros((n_epochs, n_ch, n_ch), dtype=np.float64)
    for i in range(n_epochs):
        c = np.cov(X[i])
        c = c / (np.trace(c) + 1e-12)
        c += 1e-5 * np.eye(n_ch)
        covs[i] = c
    return covs


def compute_riemannian_mean(covmats, max_iter=25, tol=1e-6):
    """
    Fréchet geometric mean on the SPD manifold under the affine-invariant Riemannian metric.
    covmats: shape (n_epochs, n_channels, n_channels)
    """
    C_mean = np.mean(covmats, axis=0)
    for _ in range(max_iter):
        vals, vecs = eigh(C_mean)
        vals = np.maximum(vals, 1e-8)
        sqrt_C = vecs @ np.diag(np.sqrt(vals)) @ vecs.T
        inv_sqrt_C = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T

        tangents = []
        for i in range(len(covmats)):
            m = inv_sqrt_C @ covmats[i] @ inv_sqrt_C
            v, w = eigh(m)
            v = np.maximum(v, 1e-8)
            log_m = w @ np.diag(np.log(v)) @ w.T
            tangents.append(log_m)

        mean_t = np.mean(tangents, axis=0)
        if np.linalg.norm(mean_t, ord='fro') < tol:
            break
        v, w = eigh(mean_t)
        exp_t = w @ np.diag(np.exp(v)) @ w.T
        C_mean = sqrt_C @ exp_t @ sqrt_C

    return C_mean


def project_to_riemannian_tangent_space(covmats, C_ref=None):
    """
    Projects covariance matrices onto Euclidean Tangent Space at reference point C_ref.
    covmats: shape (n_epochs, n_channels, n_channels)
    Returns:
        ts_vectors: shape (n_epochs, n_channels * (n_channels + 1) // 2)
        C_ref: reference Riemannian mean covariance
    """
    if C_ref is None:
        C_ref = compute_riemannian_mean(covmats)

    vals, vecs = eigh(C_ref)
    vals = np.maximum(vals, 1e-8)
    inv_sqrt_C = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T

    n_epochs, n_ch, _ = covmats.shape
    triu_idx = np.triu_indices(n_ch)
    diag_mask = (triu_idx[0] == triu_idx[1])

    ts_vectors = []
    for i in range(n_epochs):
        m = inv_sqrt_C @ covmats[i] @ inv_sqrt_C
        v, w = eigh(m)
        v = np.maximum(v, 1e-8)
        log_m = w @ np.diag(np.log(v)) @ w.T
        vec = log_m[triu_idx].copy()
        vec[~diag_mask] *= np.sqrt(2.0)
        ts_vectors.append(vec)

    return np.array(ts_vectors, dtype=np.float64), C_ref


class RiemannianTangentSpaceClassifier(BaseEstimator, ClassifierMixin):
    """
    Riemannian Tangent Space Classifier for 4-Class Mental Rhythm BCI.
    Projects regularized covariance matrices onto Riemannian tangent space,
    followed by standard scaling and regularized multi-class Logistic Regression.
    """

    def __init__(self, C=0.1, max_iter=500, random_state=42):
        self.C = float(C)
        self.max_iter = int(max_iter)
        self.random_state = random_state

        self.C_ref_ = None
        self.scaler_ = None
        self.classifier_ = None
        self.classes_ = None

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.int32)

        if X.ndim != 3:
            raise ValueError(f"Expected 3D array (n_epochs, n_channels, n_samples), got {X.shape}")

        self.classes_ = np.unique(y)
        covs = compute_covariance_matrices(X)
        ts_vecs, self.C_ref_ = project_to_riemannian_tangent_space(covs)

        self.scaler_ = StandardScaler()
        ts_scaled = self.scaler_.fit_transform(ts_vecs)

        self.classifier_ = LogisticRegression(
            C=self.C,
            max_iter=self.max_iter,
            fit_intercept=False,
            random_state=self.random_state,
            solver='lbfgs'
        )
        self.classifier_.fit(ts_scaled, y)
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        if X.ndim == 2:
            X = X[np.newaxis, ...]

        covs = compute_covariance_matrices(X)
        ts_vecs, _ = project_to_riemannian_tangent_space(covs, C_ref=self.C_ref_)
        return self.scaler_.transform(ts_vecs)

    def predict_proba(self, X):
        feats = self.transform(X)
        return self.classifier_.predict_proba(feats)

    def predict(self, X):
        feats = self.transform(X)
        return self.classifier_.predict(feats)

    def recalibrate_reference(self, X_calib):
        """Adapts the reference point C_ref_ using new calibration data."""
        X_calib = np.asarray(X_calib, dtype=np.float64)
        if X_calib.ndim == 2:
            X_calib = X_calib[np.newaxis, ...]
        covs_calib = compute_covariance_matrices(X_calib)
        self.C_ref_ = compute_riemannian_mean(covs_calib)
        print("[RiemannianTangentSpaceClassifier] Reference covariance adapted to new calibration session.")


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

    def recalibrate(self, X_calib):
        """Adapts the underlying model with online calibration data if supported."""
        if self.model is not None and hasattr(self.model, "recalibrate_reference"):
            self.model.recalibrate_reference(X_calib)
            return True
        return False
