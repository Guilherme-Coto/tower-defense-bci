"""
acquisition/simulator.py
========================
Multi-mode EEG Simulator for BCI Tower Defense:
  1. 'bids_replay': Replays real 32-channel RAW EEG trials from the BIDS dataset (sub-01/ses-01)
  2. 'synthetic': Generates rhythmic frequency modulations corresponding to the 4 elements:
       - FIRE: Alpha band (8-12 Hz) entrainment
       - WATER: Theta band (4-8 Hz) entrainment
       - WIND: Beta band (13-30 Hz) entrainment
       - ELECTRICITY: Gamma band (30-45 Hz) entrainment
"""

import os
import time
from pathlib import Path
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
import config


class EEGSimulator:
    """
    Simulates or replays 32-channel EEG streams at 250 Hz.
    """

    def __init__(
        self,
        sampling_rate=config.SAMPLING_RATE,
        channels=config.N_CHANNELS,
        mode="bids_replay",
        bids_root=config.BIDS_ROOT
    ):
        self.fs = float(sampling_rate)
        self.channels = int(channels)
        self.mode = mode
        self.bids_root = Path(bids_root)

        # Real BIDS epochs dictionary: { "FIRE": [...], "WATER": [...], ... }
        self.real_epochs = {}
        self.trial_indices = {"FIRE": 0, "WATER": 0, "WIND": 0, "ELECTRICITY": 0}
        self.current_rhythm = "FIRE"
        self.current_stream_buffer = np.empty((0, self.channels))

        # Distinct rhythm base frequencies (Hz) for synthetic mode
        self.rhythm_frequencies = {
            "FIRE": 10.0,         # Alpha (10 Hz)
            "WATER": 6.0,         # Theta (6 Hz)
            "WIND": 20.0,         # Beta (20 Hz)
            "ELECTRICITY": 35.0   # Gamma (35 Hz)
        }

        if self.mode == "bids_replay":
            self._load_bids_data()

    def _load_bids_data(self):
        """Loads real raw Imagine epochs from the Tower Defense BIDS dataset."""
        try:
            from analysis.analyze_tower_defense_rhythm_decoding import (
                load_single_session_raw,
                extract_session_epochs
            )
            raw_uv, df_events, sfreq, ch_names = load_single_session_raw(self.bids_root, "01", "01")
            # Extract raw epochs directly so the real-time preprocessor filters them
            X_im, X_lis, _, y, _, class_names = extract_session_epochs(
                raw_uv,
                df_events,
                "01",
                sfreq=sfreq,
                win_len_s=config.WINDOW_SIZE_SEC
            )

            # Store trials by element
            for c_id, name in enumerate(class_names):
                mask = (y == c_id)
                im_trials = [X_im[k].T for k in range(len(X_im)) if mask[k]]
                self.real_epochs[name] = im_trials

            print(f"[EEGSimulator] Loaded {sum(len(v) for v in self.real_epochs.values())} real raw BIDS trials across 4 elements.")
        except Exception as e:
            print(f"[EEGSimulator Warning] Could not load real BIDS trials ({e}). Falling back to synthetic mode.")
            self.mode = "synthetic"

    def set_rhythm(self, rhythm_name):
        """Sets the active mental rhythm to simulate/replay."""
        rhythm_upper = rhythm_name.upper()
        if rhythm_upper in config.ELEMENT_TO_ID:
            if self.current_rhythm != rhythm_upper:
                self.current_rhythm = rhythm_upper
                # Clear buffer so transition is immediate
                self.current_stream_buffer = np.empty((0, self.channels))
        else:
            print(f"[EEGSimulator Warning] Unknown rhythm '{rhythm_name}'. Keeping {self.current_rhythm}.")

    def generate(self, rhythm=None, duration=0.5):
        """
        Generates/streams EEG samples of the specified duration (in seconds).
        Returns: np.ndarray of shape (n_samples, n_channels)
        """
        if rhythm is not None:
            self.set_rhythm(rhythm)

        n_samples = int(duration * self.fs)

        if self.mode == "bids_replay" and self.real_epochs.get(self.current_rhythm):
            epochs = self.real_epochs[self.current_rhythm]
            idx = self.trial_indices[self.current_rhythm] % len(epochs)
            selected_trial = epochs[idx]  # shape: (n_trial_samples, 32)

            # Replenish buffer from trial
            while len(self.current_stream_buffer) < n_samples:
                self.current_stream_buffer = np.vstack([self.current_stream_buffer, selected_trial])
                self.trial_indices[self.current_rhythm] += 1
                idx = self.trial_indices[self.current_rhythm] % len(epochs)
                selected_trial = epochs[idx]

            chunk = self.current_stream_buffer[:n_samples]
            self.current_stream_buffer = self.current_stream_buffer[n_samples:]
            return chunk

        # Synthetic generator fallback
        t = np.arange(n_samples) / self.fs
        freq = self.rhythm_frequencies.get(self.current_rhythm, 10.0)
        eeg = np.zeros((n_samples, self.channels))

        for ch in range(self.channels):
            # Baseline rhythmic oscillation
            amplitude = 15.0 + 3.0 * np.sin(ch * 0.2)
            phase = np.random.uniform(0, 2 * np.pi)
            signal_ch = amplitude * np.sin(2 * np.pi * freq * t + phase)
            # Harmonic
            signal_ch += 0.3 * amplitude * np.sin(2 * np.pi * (freq * 2) * t)
            # Broadband 1/f-like noise
            noise = np.random.normal(0, 5.0, n_samples)
            eeg[:, ch] = signal_ch + noise

        return eeg