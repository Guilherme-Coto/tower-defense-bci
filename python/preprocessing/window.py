"""
window.py

Responsável por acumular amostras EEG até formar uma janela de processamento.
Depois devolve essa janela ao pipeline.
"""

from pathlib import Path
import sys
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config


class SlidingWindow:

    def __init__(
        self,
        sampling_rate=config.SAMPLING_RATE,
        window_seconds=config.WINDOW_SIZE_SEC,
        step_seconds=config.WINDOW_STEP_SEC,
        channels=None
    ):
        self.samples = int(window_seconds * sampling_rate)
        self.step = int(step_seconds * sampling_rate)
        self.channels = channels
        self.buffer = np.empty((0, channels)) if channels is not None else None

    def add_samples(self, new_samples):
        """
        new_samples: (samples x channels)
        """
        new_samples = np.asarray(new_samples)

        if self.buffer is None:
            self.channels = new_samples.shape[1]
            self.buffer = new_samples.copy()
        else:
            self.buffer = np.vstack((self.buffer, new_samples))

    def is_ready(self):
        if self.buffer is None:
            return False
        return len(self.buffer) >= self.samples

    def get_window(self):
        if not self.is_ready():
            return None

        window = self.buffer[:self.samples]
        self.buffer = self.buffer[self.step:]

        return window