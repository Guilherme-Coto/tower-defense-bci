"""
communication/game_state_listener.py
====================================
Listens in the background for real-time BCI markers broadcast by Godot
(from tower_defense/scripts/network/bci_marker_send.gd on UDP 127.0.0.1:9000).

Tracks game state:
  - 'LISTEN'   (when audio rhythm is playing)
  - 'BLINK'    (when visual prompt flickers)
  - 'IMAGINE'  (when player actively recalls/imagines the rhythm)
  - 'REST'     (between enemy waves / trials)
  - 'FINISHED' (when game ends)
"""

import socket
import json
import threading
import time
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config


class GameStateListener:
    """
    Background UDP listener for real-time synchronization with Godot game events.
    """

    def __init__(self, host="127.0.0.1", port=config.GAME_MARKER_PORT):
        self.host = host
        self.port = int(port)
        self.running = False
        self.thread = None
        self.sock = None

        self.current_state = "IDLE"
        self.target_element = None
        self.last_marker = None
        self.last_marker_time = 0.0
        self.last_duration = 0.0
        self.marker_history = []
        self.callbacks = []

    def start(self):
        """Starts the background listening thread."""
        if self.running:
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.settimeout(0.2)
            self.running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            print(f"[GameStateListener] Listening for Godot markers on {self.host}:{self.port}")
        except Exception as e:
            print(f"[GameStateListener Warning] Could not bind port {self.port} (maybe bridge running): {e}")

    def register_callback(self, callback_func):
        """Registers a function to be called on every new marker: callback(marker_name, duration)"""
        self.callbacks.append(callback_func)

    def _listen_loop(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(2048)
                msg = data.decode('utf-8').strip()
                self._handle_message(msg)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    time.sleep(0.05)

    def _handle_message(self, raw_msg):
        try:
            payload = json.loads(raw_msg)
            marker_name = payload.get("name", "")
            duration = float(payload.get("duration", 0.0))
        except json.JSONDecodeError:
            marker_name = raw_msg
            duration = 0.0

        if not marker_name:
            return

        self.last_marker = marker_name
        self.last_duration = duration
        self.last_marker_time = time.time()
        self.marker_history.append((self.last_marker_time, marker_name))

        # Update high-level state
        name_lower = marker_name.lower()
        if "start listen" in name_lower:
            self.current_state = "LISTEN"
        elif "end listen" in name_lower:
            self.current_state = "LISTEN_ENDED"
        elif "box start" in name_lower or "start to blink" in name_lower or "start blinking" in name_lower:
            self.current_state = "BLINKING"
        elif "box stop" in name_lower or "stop blinking" in name_lower or "stop to blink" in name_lower:
            self.current_state = "BLINKING_ENDED"
        elif "imagine" in name_lower:
            self.current_state = "IMAGINE"
        elif "rest" in name_lower:
            self.current_state = "REST"
        elif "game finished" in name_lower:
            self.current_state = "FINISHED"

        # Check for element cues
        for elem in ["FIRE", "WATER", "WIND", "ELECTRICITY"]:
            if elem in marker_name.upper():
                self.target_element = elem

        for cb in self.callbacks:
            try:
                cb(marker_name, duration)
            except Exception as ex:
                print(f"[GameStateListener Callback Error] {ex}")

    @property
    def is_in_imagine_phase(self):
        """Returns True if the game is currently expecting the user to imagine a rhythm."""
        return self.current_state == "IMAGINE"

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
