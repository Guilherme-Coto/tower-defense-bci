"""
window.py

Responsável por acumular amostras EEG até formar
uma janela de processamento.

Depois devolve essa janela ao pipeline.
"""

import numpy as np


class SlidingWindow:

    def __init__(
        self,
        sampling_rate=250,
        window_seconds=2,
        step_seconds=0.5,
        channels=32
    ):

        self.samples = int(window_seconds * sampling_rate)
        self.step = int(step_seconds * sampling_rate)
        self.channels = channels
        self.buffer = np.empty((0, channels))

    def add_samples(self, new_samples):
        """
        new_samples:

        (N x canais)
        """
        self.buffer = np.vstack(
            (self.buffer, new_samples)
        )

    def is_ready(self):
        return len(self.buffer) >= self.samples

    def get_window(self):
        if not self.is_ready():
            return None

        window = self.buffer[:self.samples]
        self.buffer = self.buffer[self.step:]

        return window