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
        smoothing_alpha=getattr(config, "SMOOTHING_ALPHA", 0.35),
        cooldown_sec=getattr(config, "MIN_COOLDOWN_SEC", 1.2),
        auto_send_godot=False,
        sync_game_markers=True
    ):
        self.confidence_threshold = float(confidence_threshold)
        self.smoothing_alpha = float(smoothing_alpha)
        self.cooldown_sec = float(cooldown_sec)
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

        # Evidence accumulation & state tracking
        self.smoothed_probs = None
        self.last_game_state = None
        self.last_sent_time = 0.0
        self.last_prediction = None
        self.total_windows_processed = 0

    def reset_accumulator(self):
        """Resets accumulated probability distribution (e.g. at the start of Imagine phase)."""
        self.smoothed_probs = None

    def recalibrate(self, X_calib):
        """Adapts the underlying spatial model reference to current session EEG."""
        return self.predictor.recalibrate(X_calib)

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
              - 'confidence': float (smoothed)
              - 'probabilities': dict (smoothed)
              - 'raw_element': str
              - 'raw_confidence': float
              - 'raw_probabilities': dict
              - 'is_rhythm_active': bool
              - 'game_state': str
              - 'command_sent': bool
        """
        import time

        self.window.add_samples(eeg_chunk)

        if not self.window.is_ready():
            return None

        # 1. Extract raw window (750 samples, 32 channels)
        raw_window = self.window.get_window()

        # 2. Filter & Robust CAR reference -> (32 channels, 750 samples)
        clean_window = self.preprocessor.process(raw_window)

        # 3. Decode rhythm instant probabilities
        raw_result = self.predictor.predict(
            clean_window,
            confidence_threshold=self.confidence_threshold
        )

        # 4. State transition handling: reset evidence when entering IMAGINE
        game_state = self.game_listener.current_state if self.game_listener else "N/A"
        if game_state == "IMAGINE" and self.last_game_state != "IMAGINE":
            self.reset_accumulator()
        self.last_game_state = game_state

        # 5. Temporal Evidence Accumulation (Exponential Moving Average)
        ordered_elements = ["FIRE", "WATER", "WIND", "ELECTRICITY"]
        curr_vec = np.array([raw_result['probabilities'].get(el, 0.25) for el in ordered_elements], dtype=np.float64)

        if self.smoothed_probs is None:
            self.smoothed_probs = curr_vec.copy()
        else:
            self.smoothed_probs = (
                self.smoothing_alpha * curr_vec + (1.0 - self.smoothing_alpha) * self.smoothed_probs
            )
        self.smoothed_probs = self.smoothed_probs / (np.sum(self.smoothed_probs) + 1e-12)

        # Smoothed decision
        smoothed_pred_id = int(np.argmax(self.smoothed_probs))
        smoothed_conf = float(self.smoothed_probs[smoothed_pred_id])
        smoothed_elem = config.ELEMENTS.get(smoothed_pred_id, "UNKNOWN")
        smoothed_prob_dict = {
            config.ELEMENTS[i]: float(self.smoothed_probs[i])
            for i in range(len(ordered_elements))
        }

        is_active = smoothed_conf >= self.confidence_threshold

        result = {
            'element': smoothed_elem,
            'element_id': smoothed_pred_id,
            'confidence': smoothed_conf,
            'probabilities': smoothed_prob_dict,
            'raw_element': raw_result['element'],
            'raw_confidence': raw_result['confidence'],
            'raw_probabilities': raw_result['probabilities'],
            'is_rhythm_active': is_active,
            'game_state': game_state,
            'command_sent': False
        }

        # 6. Optionally trigger Godot power with cooldown check
        now = time.time()
        if self.auto_send_godot and is_active:
            if game_state in ["IMAGINE", "IDLE", "N/A"]:
                if (now - self.last_sent_time) >= self.cooldown_sec:
                    sent = self.udp_sender.send_power(smoothed_pred_id)
                    result['command_sent'] = sent
                    if sent:
                        self.last_sent_time = now

        self.last_prediction = result
        self.total_windows_processed += 1
        return result

    def close(self):
        """Clean shutdown of background threads and sockets."""
        if self.game_listener:
            self.game_listener.stop()
        if self.udp_sender:
            self.udp_sender.close()