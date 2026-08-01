"""
Gera um dataset sintético para treinar o classificador.
"""

import pandas as pd

from acquisition.simulator import EEGSimulator
from features.bandpower import BandPowerExtractor


class DatasetGenerator:

    def __init__(self):

        self.sim = EEGSimulator()

        self.extractor = BandPowerExtractor()

        self.rhythms = [
            "FIRE",
            "WATER",
            "EARTH",
            "WIND"
        ]

    def generate(self, samples_per_class=200):

        X = []

        y = []

        for rhythm in self.rhythms:

            print(f"Generating {rhythm}")

            for _ in range(samples_per_class):

                eeg = self.sim.generate(
                    rhythm,
                    duration=2
                )

                features = self.extractor.extract(eeg)

                X.append(features)

                y.append(rhythm)

        df = pd.DataFrame(X)

        df["label"] = y

        return df