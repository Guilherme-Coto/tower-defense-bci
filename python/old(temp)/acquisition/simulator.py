"""
simulator.py

Simulador de EEG para desenvolvimento sem o Nautilus.

Cada ritmo gera um padrão espectral diferente para que o
classificador consiga aprender e para testar todo o pipeline.

Autor: BCI Tower Defense
"""

import numpy as np


class EEGSimulator:

    def __init__(self,
                 sampling_rate=250,
                 channels=32,
                 noise=0.15):

        self.fs = sampling_rate
        self.channels = channels
        self.noise = noise

        # Frequências "dominantes" de cada ritmo
        self.rhythms = {
            "FIRE": 10,     # Alpha
            "WATER": 6,     # Theta
            "WIND": 20,     # Beta
            "EARTH": 14     # SMR / Beta baixa
        }

    def generate(self,
                 rhythm="FIRE",
                 duration=2.0):

        samples = int(duration * self.fs)
        t = np.arange(samples) / self.fs
        freq = self.rhythms[rhythm]
        eeg = np.zeros((samples, self.channels))

        for ch in range(self.channels):
            base_amplitude = {
                "FIRE": 20,
                "WATER": 10,
                "WIND": 35,
                "EARTH": 28
            }

            amplitude = base_amplitude[rhythm] + np.random.uniform(-2, 2)
            phase = np.random.uniform(0, 2*np.pi)

            signal = amplitude * np.sin(
                2*np.pi*freq*t + phase
            )

            # adicionar algum conteúdo extra
            signal += 0.3 * amplitude * np.sin(
                2*np.pi*(freq+2)*t
            )

            # ruído gaussiano
            signal += np.random.normal(
                0,
                amplitude*self.noise,
                samples
            )

            eeg[:, ch] = signal

        return eeg