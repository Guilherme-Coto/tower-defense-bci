"""
fft.py

Calcula o espectro de frequências do EEG.
"""
import numpy as np


class FFTExtractor:

    def __init__(self, sampling_rate=250):
        self.fs = sampling_rate

    def compute(self, signal):
        """
        signal -> vetor 1D (um canal)

        Returns:
            frequencies
            magnitude
        """

        n = len(signal)
        fft = np.fft.rfft(signal)
        magnitude = np.abs(fft)
        frequencies = np.fft.rfftfreq(n, d=1/self.fs)

        return frequencies, magnitude

    def fft_power(self, eeg):
        freqs = np.fft.rfftfreq(len(eeg),d=1/self.fs)
        fft = np.abs(np.fft.rfft(eeg))**2

        return freqs, fft