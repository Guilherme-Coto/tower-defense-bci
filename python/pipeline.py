"""
pipeline.py

Pipeline de tempo real do BCI Tower Defense:
- Recebe blocos de EEG do receptor/simulador
- Gere a janela deslizante (SlidingWindow)
- Extrai características de frequência (PSD) e domínio do tempo (Hjorth)
- Classifica a faixa/ritmo e retorna (rótulo, confiança)
"""

from classifier.predictor import RhythmPredictor
from features.extractor import BCIFeatureExtractor
from preprocessing.window import SlidingWindow
import config


class BCIPipeline:

    def __init__(self):
        self.window = SlidingWindow()
        self.extractor = BCIFeatureExtractor(
            fs=config.SAMPLING_RATE,
            bands=config.BANDS
        )
        self.predictor = RhythmPredictor()

    def process(self, eeg_chunk):
        """
        Recebe um bloco EEG.

        Retorna:
            None -> se a janela deslizante ainda não estiver pronta
            (label, confidence) -> previsão do elemento do jogo e confiança
        """

        self.window.add_samples(eeg_chunk)

        if not self.window.is_ready():
            return None

        eeg_window = self.window.get_window()
        features = self.extractor.extract(eeg_window)
        prediction = self.predictor.predict(features)

        return prediction