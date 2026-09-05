"""
preprocessing/window.py
======================
Sliding window ring buffer for real-time multi-channel EEG processing.
Accumulates samples and produces overlapping windows for inference.
"""

from pathlib import Path
import sys
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config


class SlidingWindow:
    """
    Maintains a rolling FIFO buffer of multi-channel EEG data.
    """

    def __init__(
        self,
        sampling_rate=config.SAMPLING_RATE,
        window_seconds=config.WINDOW_SIZE_SEC,
        step_seconds=config.WINDOW_STEP_SEC,
        channels=config.N_CHANNELS
    ):
        self.sampling_rate = float(sampling_rate)
        self.samples = int(window_seconds * sampling_rate)
        self.step = int(step_seconds * sampling_rate)
        self.channels = int(channels) if channels else None
        self.buffer = np.empty((0, self.channels)) if self.channels is not None else None

    def add_samples(self, new_samples):
        """
        Adds new samples to buffer.
        new_samples: np.ndarray of shape (n_samples, n_channels)
        """
        if new_samples is None or len(new_samples) == 0:
            return

        new_arr = np.asarray(new_samples, dtype=np.float64)
        if new_arr.ndim == 1:
            new_arr = new_arr.reshape(1, -1)

        if self.buffer is None or self.buffer.shape[1] != new_arr.shape[1]:
            self.channels = new_arr.shape[1]
            self.buffer = new_arr.copy()
        else:
            self.buffer = np.vstack((self.buffer, new_arr))

    def is_ready(self):
        """Returns True if the buffer contains at least one full window."""
        if self.buffer is None:
            return False
        return len(self.buffer) >= self.samples

    def get_window(self):
        """
        Returns the oldest window (samples, channels) and advances the buffer by `step` samples.
        """
        if not self.is_ready():
            return None

        window = self.buffer[:self.samples].copy()
        self.buffer = self.buffer[self.step:]
        return window

    def peek_latest_window(self):
        """
        Returns the most recent full window without advancing the buffer.
        """
        if not self.is_ready():
            return None
        return self.buffer[-self.samples:].copy()

    def reset(self):
        """Clears the buffer."""
        if self.channels is not None:
            self.buffer = np.empty((0, self.channels))
        else:
            self.buffer = None

    @property
    def buffer_fill_ratio(self):
        """Returns percentage of window currently filled (0.0 to 1.0+)."""
        if self.buffer is None:
            return 0.0
        return min(1.0, len(self.buffer) / self.samples)