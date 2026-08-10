"""
features/extractor.py

Extração de características para sinal EEG em BCI Tower Defense:
- Potência espectral logarítmica em 5 bandas clássicas (Delta, Theta, Alpha, Beta, Gamma)
- Parâmetros de Hjorth (Atividade, Mobilidade, Complexidade)
"""

import numpy as np
from scipy.signal import welch
import config


class BCIFeatureExtractor:

    def __init__(self, fs=config.SAMPLING_RATE, bands=config.BANDS):
        self.fs = fs
        self.bands = bands

    def extract_hjorth(self, signal):
        """
        Calcula os parâmetros de Hjorth para um vetor 1D de sinal:
        - Activity: variância da amplitude do sinal
        - Mobility: estimativa da frequência média
        - Complexity: estimativa da variação da frequência
        """
        diff1 = np.diff(signal)
        diff2 = np.diff(diff1)

        var0 = np.var(signal)
        var1 = np.var(diff1)
        var2 = np.var(diff2)

        if var0 < 1e-12:
            return 0.0, 0.0, 0.0

        activity = var0
        mobility = np.sqrt(var1 / var0) if var0 > 0 else 0.0
        
        mob_diff1 = np.sqrt(var2 / var1) if var1 > 0 else 0.0
        complexity = mob_diff1 / mobility if mobility > 0 else 0.0

        return activity, mobility, complexity

    def extract(self, eeg_window):
        """
        eeg_window: array com shape (n_channels, n_samples) ou (n_samples, n_channels)
        Retorna: array 1D com todas as features
        """
        eeg = np.asarray(eeg_window)

        # Garantir shape (n_channels, n_samples)
        if eeg.ndim == 2 and eeg.shape[0] > eeg.shape[1]:
            eeg = eeg.T

        n_channels, n_samples = eeg.shape

        # 1. PSD por Welch
        nperseg = min(512, n_samples)
        freqs, psd = welch(eeg, fs=self.fs, axis=1, nperseg=nperseg)

        features = []

        # Potência espectral por banda
        for low, high in self.bands:
            idx = (freqs >= low) & (freqs <= high)
            if np.any(idx):
                band_p = psd[:, idx].mean(axis=1)
            else:
                band_p = np.zeros(n_channels)
            # Aplicar log(1 + p) para estabilizar variância
            features.extend(np.log1p(band_p))

        # 2. Parâmetros de Hjorth por canal
        for ch in range(n_channels):
            act, mob, comp = self.extract_hjorth(eeg[ch])
            features.extend([act, mob, comp])

        return np.array(features, dtype=np.float32)