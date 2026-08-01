import numpy as np
import scipy.signal as signal

class RhythmFeatureExtractor:
    def __init__(self, fs=125):
        self.fs = fs
        nyq = fs / 2

        # Bandpass 2-45 Hz
        self.b_band, self.a_band = signal.butter(
            4,
            [2/nyq, 45/nyq],
            btype="band"
        )

        # Notch 50 Hz
        self.b_notch, self.a_notch = signal.iirnotch(
            50,
            30,
            fs
        )

    def preprocess(self, eeg):
        eeg = np.asarray(eeg)
        # Remove tendência
        eeg = signal.detrend(eeg)
        # Bandpass
        eeg = signal.lfilter(self.b_band,self.a_band,eeg)
        # Notch
        eeg = signal.lfilter(self.b_notch,self.a_notch,eeg)

        return eeg

    def fft_power(self, eeg):
        freqs = np.fft.rfftfreq(len(eeg),d=1/self.fs)
        fft = np.abs(np.fft.rfft(eeg)) ** 2

        return freqs, fft

    def band_power(self, freqs, fft, low, high):
        idx = (freqs >= low) & (freqs < high)

        if np.sum(idx) == 0:
            return 0

        return np.mean(fft[idx])

    def extract(self, eeg):
        eeg = self.preprocess(eeg)
        freqs, fft = self.fft_power(eeg)

        theta = self.band_power(freqs, fft, 4, 8)
        alpha = self.band_power(freqs, fft, 8, 12)
        beta = self.band_power(freqs, fft, 12, 30)

        total = theta + alpha + beta + 1e-10

        features = {
            "theta": theta / total,
            "alpha": alpha / total,
            "beta": beta / total,
            "alpha_beta_ratio": alpha / (beta + 1e-10),
            "beta_theta_ratio": beta / (theta + 1e-10),
            "total_power":total
        }

        return features