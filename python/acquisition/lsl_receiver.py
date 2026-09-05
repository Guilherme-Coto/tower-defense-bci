"""
acquisition/lsl_receiver.py
===========================
High-performance LSL Receiver for g.Nautilus EEG Streams.
Pulls multi-channel EEG chunks asynchronously at 250 Hz.
"""

import time
import numpy as np
from pylsl import StreamInlet, resolve_byprop, resolve_streams
import config


class LSLReceiver:
    """
    Connects to an EEG LSL stream (e.g. g.Nautilus PRO / Research)
    and pulls chunks for real-time processing.
    """

    def __init__(
        self,
        stream_name=config.LSL_STREAM_NAME,
        stream_type=config.LSL_STREAM_TYPE,
        expected_channels=config.N_CHANNELS,
        timeout=5.0
    ):
        self.stream_name = stream_name
        self.stream_type = stream_type
        self.expected_channels = int(expected_channels)
        self.timeout = float(timeout)
        self.inlet = None
        self.connected = False

    def connect(self):
        """Discovers and connects to the LSL EEG stream."""
        print(f"[LSLReceiver] Searching for LSL stream (type='{self.stream_type}', name='{self.stream_name}')...")
        streams = resolve_byprop('type', self.stream_type, timeout=self.timeout)

        if not streams:
            print("[LSLReceiver] No stream found by type. Trying general resolve_streams...")
            streams = resolve_streams(wait_time=self.timeout)

        if not streams:
            raise ConnectionError(f"No active LSL stream found for type '{self.stream_type}'")

        # Select stream matching name if available, else first stream
        target_stream = streams[0]
        for s in streams:
            if self.stream_name.lower() in s.name().lower():
                target_stream = s
                break

        self.inlet = StreamInlet(target_stream, max_chunklen=int(config.SAMPLING_RATE))
        info = self.inlet.info()
        ch_count = info.channel_count()
        srate = info.nominal_srate()

        print(f"[LSLReceiver] Connected to '{info.name()}' ({ch_count} channels @ {srate} Hz)")
        self.connected = True
        return True

    def get_chunk(self, duration=config.WINDOW_STEP_SEC, timeout=1.0):
        """
        Pulls EEG samples accumulated over duration (in seconds).
        Returns: np.ndarray of shape (n_samples, n_channels)
        """
        if not self.connected or self.inlet is None:
            raise RuntimeError("LSLReceiver is not connected. Call connect() first.")

        target_samples = int(duration * config.SAMPLING_RATE)
        collected_samples = []
        start_time = time.time()

        while len(collected_samples) < target_samples:
            chunk, timestamps = self.inlet.pull_chunk(
                timeout=0.05,
                max_samples=target_samples - len(collected_samples)
            )
            if chunk:
                collected_samples.extend(chunk)

            if time.time() - start_time > timeout:
                break

        if not collected_samples:
            return np.empty((0, self.expected_channels))

        arr = np.asarray(collected_samples, dtype=np.float32)

        # Slice to expected channel count if auxiliary or marker channels exist
        if arr.shape[1] > self.expected_channels:
            arr = arr[:, :self.expected_channels]

        return arr

    def close(self):
        if self.inlet is not None:
            try:
                self.inlet.close_stream()
            except Exception:
                pass
        self.connected = False