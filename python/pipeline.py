"""
pipeline.py
===========
Real-time BCI Pipeline for Tower Defense 4-Class Mental Rhythm Decoding:
  1. Ingests streaming EEG chunks (LSL or Simulator)
  2. Buffers in a 3.0s sliding window (750 samples @ 250 Hz)
  3. Preprocesses window (Bandpass 1-45 Hz, Notch 50 Hz, Robust CAR Referencing)
  4. Decodes 4 rhythm classes (FIRE, WATER, WIND, ELECTRICITY) via FilterBank CSP
  5. Computes confidence and determines whether the player is thinking in a rhythm
  6. Optionally communicates predictions to Godot over UDP (127.0.0.1:4242)
"""

from pathlib import Path
import sys
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from classifier.rhythm_decoder import RhythmPredictor
from preprocessing.window import SlidingWindow
from preprocessing.preprocessor import EEGPreprocessor
from communication.udp_sender import UDPSender
from communication.game_state_listener import GameStateListener


class BCIPipeline:
    """
    Master Real-Time BCI Pipeline for rhythm decoding in Tower Defense.
    """

    def __init__(
        self,
        model_path=config.MODEL_PATH,
        confidence_threshold=config.CONFIDENCE_THRESHOLD,
        auto_send_godot=False,
        sync_game_markers=True
    ):
        self.confidence_threshold = float(confidence_threshold)
        self.auto_send_godot = auto_send_godot

        # Windowing and preprocessing
        self.window = SlidingWindow(
            sampling_rate=config.SAMPLING_RATE,
            window_seconds=config.WINDOW_SIZE_SEC,
            step_seconds=config.WINDOW_STEP_SEC,
            channels=config.N_CHANNELS
        )
        self.preprocessor = EEGPreprocessor(
            sfreq=config.SAMPLING_RATE,
            l_freq=config.LOWCUT,
            h_freq=config.HIGHCUT,
            notch_freq=config.NOTCH,
            spatial_mode=config.SPATIAL_FILTER
        )

        # Classifier / Rhythm predictor
        self.predictor = RhythmPredictor(model_path=model_path)

        # Game Communication
        self.udp_sender = UDPSender()
        self.game_listener = GameStateListener() if sync_game_markers else None
        if self.game_listener:
            self.game_listener.start()

        self.last_prediction = None
        self.total_windows_processed = 0

    def process_chunk(self, eeg_chunk):
        """
        Receives an EEG chunk from the acquisition source.

        Parameters:
            eeg_chunk: np.ndarray of shape (n_samples, 32)

        Returns:
            None if the sliding window is not yet ready,
            or dict containing:
              - 'element': str ("FIRE", "WATER", "WIND", "ELECTRICITY")
              - 'element_id': int (0..3)
              - 'confidence': float
              - 'probabilities': dict
              - 'is_rhythm_active': bool
              - 'game_state': str
              - 'command_sent': bool
        """
        self.window.add_samples(eeg_chunk)

        if not self.window.is_ready():
            return None

        # 1. Extract raw window (750 samples, 32 channels)
        raw_window = self.window.get_window()

        # 2. Filter & Robust CAR reference -> (32 channels, 750 samples)
        clean_window = self.preprocessor.process(raw_window)

        # 3. Decode rhythm & class probabilities
        result = self.predictor.predict(
            clean_window,
            confidence_threshold=self.confidence_threshold
        )

        # 4. Attach game state information
        game_state = self.game_listener.current_state if self.game_listener else "N/A"
        result['game_state'] = game_state
        result['command_sent'] = False

        # 5. Optionally trigger Godot power
        if self.auto_send_godot and result['is_rhythm_active']:
            # If game state sync is active, trigger when in IMAGINE or FREE play
            if game_state in ["IMAGINE", "IDLE", "N/A"]:
                sent = self.udp_sender.send_power(result['element_id'])
                result['command_sent'] = sent

        self.last_prediction = result
        self.total_windows_processed += 1
        return result

    def close(self):
        """Clean shutdown of background threads and sockets."""
        if self.game_listener:
            self.game_listener.stop()
        if self.udp_sender:
            self.udp_sender.close()