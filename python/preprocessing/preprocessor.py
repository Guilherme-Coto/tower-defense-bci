"""
preprocessing/preprocessor.py
=============================
Real-time EEG Preprocessing Module for BCI Tower Defense.
Applies:
  1. Zero-phase Butterworth Bandpass (1.0 - 45.0 Hz)
  2. IIR Notch Filter (50.0 Hz)
  3. Robust Common Average Referencing (Robust CAR / Median CAR)
"""

import numpy as np
import scipy.signal as signal
from preprocessing.spatial_filters import apply_spatial_filter, detect_bad_channels


class EEGPreprocessor:
    """
    Standardizes and filters continuous multi-channel EEG windows in real time.
    """

    def __init__(
        self,
        sfreq=250.0,
        l_freq=1.0,
        h_freq=45.0,
        notch_freq=50.0,
        spatial_mode="robust_car",
        ch_names=None
    ):
        self.sfreq = float(sfreq)
        self.l_freq = float(l_freq)
        self.h_freq = float(h_freq)
        self.notch_freq = float(notch_freq)
        self.spatial_mode = spatial_mode
        self.ch_names = ch_names if ch_names else [f"EEG{i+1:03d}" for i in range(32)]

        # Precompute filter coefficients
        nyq = self.sfreq / 2.0
        self.b_band, self.a_band = signal.butter(
            4,
            [self.l_freq / nyq, self.h_freq / nyq],
            btype='band'
        )
        self.b_notch, self.a_notch = signal.iirnotch(
            self.notch_freq,
            30.0,
            self.sfreq
        )

    def process(self, eeg_data):
        """
        Filters an EEG window.
        Input:
            eeg_data: np.ndarray of shape (n_samples, n_channels) or (n_channels, n_samples)
        Returns:
            clean_eeg: np.ndarray in (n_channels, n_samples) format for decoding
        """
        eeg = np.asarray(eeg_data, dtype=np.float64)

        # Ensure (n_samples, n_channels) for time-axis filtering along axis=0
        transposed = False
        if eeg.ndim == 2:
            if eeg.shape[0] < eeg.shape[1] and eeg.shape[0] <= 32:
                # Given (n_channels, n_samples) -> transpose to (n_samples, n_channels)
                eeg = eeg.T
                transposed = True
        else:
            raise ValueError(f"Expected 2D EEG array, got {eeg.shape}")

        # 1. Bandpass filter
        filt_eeg = signal.filtfilt(self.b_band, self.a_band, eeg, axis=0)

        # 2. Notch filter
        filt_eeg = signal.filtfilt(self.b_notch, self.a_notch, filt_eeg, axis=0)

        # 3. Spatial Referencing (Robust CAR / Median CAR)
        if self.spatial_mode == "robust_car":
            stds = np.std(filt_eeg, axis=0)
            good_mask = (stds > 2.0) & (stds < 250.0)
            good_indices = np.where(good_mask)[0]
            if len(good_indices) == 0:
                good_indices = np.arange(filt_eeg.shape[1])
            median_ref = np.median(filt_eeg[:, good_indices], axis=1, keepdims=True)
            clean_eeg = filt_eeg - median_ref
        elif self.spatial_mode in ["car", "laplacian"]:
            clean_eeg = apply_spatial_filter(
                filt_eeg,
                self.ch_names,
                mode=self.spatial_mode
            )
        else:
            clean_eeg = filt_eeg - np.mean(filt_eeg, axis=0, keepdims=True)

        # Return standardized in (n_channels, n_samples) format for the decoder
        return clean_eeg.T
