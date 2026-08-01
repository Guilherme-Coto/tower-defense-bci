"""
bandpower.py

Calcula a potência das bandas EEG.

Theta : 4-8 Hz
Alpha : 8-12 Hz
Beta  : 13-30 Hz
"""

import numpy as np
from features.fft import FFTExtractor

class BandPowerExtractor:
    def __init__(self, sampling_rate=250):
        self.fft = FFTExtractor(sampling_rate)
        self.bands = {

            "theta": (4, 8),

            "alpha": (8, 12),

            "beta": (13, 30)

        }

    def extract(self, eeg_window):
        features = []
        channels = eeg_window.shape[1]

        for ch in range(channels):
            signal = eeg_window[:, ch]
            freqs, mag = self.fft.compute(signal)
            for low, high in self.bands.values():
                idx = np.where(
                    (freqs >= low) &
                    (freqs <= high)
                )[0]
                power = np.sum(
                    mag[idx] ** 2
                )
                features.append(power)

        return np.array(features)