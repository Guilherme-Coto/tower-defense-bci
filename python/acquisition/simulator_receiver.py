"""
acquisition/simulator_receiver.py
=================================
Simulator Receiver compatible with the real-time BCI pipeline.
Streams simulated or replayed real EEG chunks.
"""

from acquisition.simulator import EEGSimulator
import config


class SimulatorReceiver:
    """
    Standard receiver interface wrapping EEGSimulator.
    """

    def __init__(self, initial_rhythm="FIRE", mode="bids_replay"):
        self.simulator = EEGSimulator(
            sampling_rate=config.SAMPLING_RATE,
            channels=config.N_CHANNELS,
            mode=mode,
            bids_root=config.BIDS_ROOT
        )
        self.rhythm = initial_rhythm
        self.connected = False

    def connect(self):
        self.simulator.set_rhythm(self.rhythm)
        self.connected = True
        print(f"[SimulatorReceiver] Connected in mode: '{self.simulator.mode}'. Initial rhythm: {self.rhythm}")
        return True

    def get_chunk(self, duration=config.WINDOW_STEP_SEC):
        """Returns next chunk of EEG samples as np.ndarray (n_samples, 32)."""
        return self.simulator.generate(rhythm=self.rhythm, duration=duration)

    def set_rhythm(self, rhythm):
        self.rhythm = rhythm
        self.simulator.set_rhythm(rhythm)

    def close(self):
        self.connected = False