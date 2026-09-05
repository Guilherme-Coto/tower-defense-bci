"""
classifier/predictor.py
=======================
Compatibility alias for the 4-class BCI Tower Defense Rhythm Predictor.
Redirects to classifier/rhythm_decoder.py.
"""

from classifier.rhythm_decoder import RhythmPredictor, FilterBankCSPClassifier, ELEMENT_NAMES, ELEMENT_IDS

__all__ = ["RhythmPredictor", "FilterBankCSPClassifier", "ELEMENT_NAMES", "ELEMENT_IDS"]