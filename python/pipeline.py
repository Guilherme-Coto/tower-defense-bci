"""
pipeline.py

Liga todas as componentes do sistema.
"""

from preprocessing.window import SlidingWindow
from features.bandpower import BandPowerExtractor
from classifier.predictor import RhythmPredictor


class BCIPipeline:

    def __init__(self):
        self.window = SlidingWindow()
        self.extractor = BandPowerExtractor()
        self.predictor = RhythmPredictor()

    def process(self, eeg_chunk):
        """
        Recebe um bloco EEG.

        Retorna:
            None -> ainda não há janela completa

            FIRE/WATER/WIND/EARTH -> previsão
        """

        self.window.add_samples(eeg_chunk)

        if not self.window.is_ready():
            return None

        eeg = self.window.get_window()
        features = self.extractor.extract(eeg)
        prediction = self.predictor.predict(features)

        return prediction