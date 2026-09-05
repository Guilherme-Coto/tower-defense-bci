"""
communication/udp_sender.py
===========================
Sends real-time game commands to the Godot Tower Defense engine over UDP.
Target: Godot oz_receiver.gd listening on 127.0.0.1:4242.
Supported Commands:
  - power:0 (FIRE)
  - power:1 (WATER)
  - power:2 (WIND)
  - power:3 (ELECTRICITY)
  - curar_jogador
  - kill_enemy
  - blink_box
"""

import socket
import time
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config


class UDPSender:
    """
    UDP socket client for sending commands to the Tower Defense game in Godot.
    """

    def __init__(self, host=config.GODOT_IP, port=config.GODOT_PORT):
        self.host = host
        self.port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.last_sent_cmd = None
        self.last_sent_time = 0.0

    def send_raw(self, cmd_str):
        """Sends a raw string command to Godot."""
        try:
            data = cmd_str.encode('utf-8')
            self.sock.sendto(data, (self.host, self.port))
            self.last_sent_cmd = cmd_str
            self.last_sent_time = time.time()
            return True
        except Exception as e:
            print(f"[UDPSender Error] Failed to send '{cmd_str}' to {self.host}:{self.port}: {e}")
            return False

    def send_power(self, element, cooldown=config.MIN_COOLDOWN_SEC):
        """
        Sends an elemental power selection command:
          power:0 -> FIRE
          power:1 -> WATER
          power:2 -> WIND
          power:3 -> ELECTRICITY

        Parameters:
            element: int (0..3) or str ("FIRE", "WATER", "WIND", "ELECTRICITY")
            cooldown: float, seconds to wait before repeating same command
        """
        if isinstance(element, str):
            elem_upper = element.upper()
            if elem_upper in config.ELEMENT_TO_ID:
                elem_id = config.ELEMENT_TO_ID[elem_upper]
            else:
                try:
                    elem_id = int(element)
                except ValueError:
                    print(f"[UDPSender Warning] Unknown element name: {element}")
                    return False
        else:
            elem_id = int(element)

        if elem_id not in config.ELEMENTS:
            print(f"[UDPSender Warning] Invalid element ID: {elem_id}")
            return False

        cmd = f"power:{elem_id}"

        # Cooldown check to prevent flooding Godot with identical commands
        now = time.time()
        if cmd == self.last_sent_cmd and (now - self.last_sent_time) < cooldown:
            return False

        success = self.send_raw(cmd)
        if success:
            elem_name = config.ELEMENTS.get(elem_id, str(elem_id))
            print(f"[UDPSender] >>> Triggered Godot Power: {elem_name} ({cmd})")
        return success

    def heal_player(self):
        """Triggers player healing in Godot."""
        return self.send_raw("curar_jogador")

    def kill_enemy(self):
        """Triggers an enemy kill in Godot."""
        return self.send_raw("kill_enemy")

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass
