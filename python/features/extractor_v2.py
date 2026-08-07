"""
features/extractor.py

Feature extractor para EEG - BCI Tower Defense

Features:
- Absolute Band Power
- Relative Band Power
- Band Ratios
- Spectral Entropy
- Hjorth Parameters
"""

import numpy as np
from scipy.signal import welch

import config


class BCIFeatureExtractor:

    def __init__(self,
                 fs=config.SAMPLING_RATE,
                 bands=config.BANDS):

        self.fs = fs
        self.bands = bands

    ############################################################
    # Hjorth
    ############################################################

    def extract_hjorth(self, signal):

        diff1 = np.diff(signal)
        diff2 = np.diff(diff1)

        var0 = np.var(signal)
        var1 = np.var(diff1)
        var2 = np.var(diff2)

        if var0 < 1e-12:
            return 0.0, 0.0, 0.0

        activity = var0

        mobility = np.sqrt(var1 / var0)

        if var1 < 1e-12:
            complexity = 0.0
        else:
            complexity = np.sqrt(var2 / var1) / (mobility + 1e-12)

        return activity, mobility, complexity

    ############################################################
    # Spectral Entropy
    ############################################################

    def spectral_entropy(self, psd):

        p = psd / (np.sum(psd) + 1e-12)

        return -np.sum(
            p * np.log2(p + 1e-12)
        )

    ############################################################
    # Relative Power
    ############################################################

    def relative_power(self, band, total):

        return band / (total + 1e-12)

    ############################################################
    # Main Extraction
    ############################################################

    def extract(self, eeg_window):

        eeg = np.asarray(eeg_window)

        # Garantir (canais x amostras)
        if eeg.ndim == 2 and eeg.shape[0] > eeg.shape[1]:
            eeg = eeg.T

        n_channels = eeg.shape[0]

        ########################################################
        # PSD
        ########################################################

        nperseg = min(512, eeg.shape[1])

        freqs, psd = welch(
            eeg,
            fs=self.fs,
            axis=1,
            nperseg=nperseg
        )

        total_power = np.sum(psd, axis=1)

        absolute = []
        relative = []

        ########################################################
        # Band Powers
        ########################################################

        for low, high in self.bands:

            idx = np.logical_and(
                freqs >= low,
                freqs <= high
            )

            if np.any(idx):
                power = np.trapezoid(
                    psd[:, idx],
                    freqs[idx],
                    axis=1
                )
            else:
                power = np.zeros(n_channels)

            absolute.append(power)

            relative.append(
                self.relative_power(
                    power,
                    total_power
                )
            )

        features = []

        ########################################################
        # Absolute Power
        ########################################################

        for band in absolute:

            features.extend(
                np.log1p(band)
            )

        ########################################################
        # Relative Power
        ########################################################

        for band in relative:

            features.extend(
                band
            )

        ########################################################
        # Band Ratios
        ########################################################

        delta = relative[0]
        theta = relative[1]
        alpha = relative[2]
        beta = relative[3]
        gamma = relative[4]

        alpha_beta = alpha / (beta + 1e-12)

        theta_beta = theta / (beta + 1e-12)

        beta_gamma = beta / (gamma + 1e-12)

        features.extend(alpha_beta)
        features.extend(theta_beta)
        features.extend(beta_gamma)

        ########################################################
        # Spectral Entropy
        ########################################################

        for ch in range(n_channels):

            features.append(
                self.spectral_entropy(
                    psd[ch]
                )
            )

        ########################################################
        # Hjorth
        ########################################################

        for ch in range(n_channels):

            act, mob, comp = self.extract_hjorth(
                eeg[ch]
            )

            features.append(act)
            features.append(mob)
            features.append(comp)

        return np.asarray(
            features,
            dtype=np.float32
        )
