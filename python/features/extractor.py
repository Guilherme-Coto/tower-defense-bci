"""
extractor.py

Extrai características do EEG.

Primeira versão:
    - média
    - desvio padrão
    - energia
    - máximo
    - mínimo

Mais tarde será adicionado FFT, PSD e bandas EEG.
"""

import numpy as np


class FeatureExtractor:

    def __init__(self):
        pass

    def extract(self, eeg_window):
        """
        eeg_window
        shape:
            (samples, channels)
        return:
            vetor de features
        """
        features = []

        # Uma feature por canal
        for ch in range(eeg_window.shape[1]):
            signal = eeg_window[:, ch]
            mean = np.mean(signal)
            std = np.std(signal)
            energy = np.sum(signal ** 2)
            maximum = np.max(signal)
            minimum = np.min(signal)
            features.extend([
                mean,
                std,
                energy,
                maximum,
                minimum
            ])

        return np.array(features)