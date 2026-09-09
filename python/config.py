"""
config.py
=========
Global Configuration for BCI Tower Defense Real-Time Rhythm Decoding.
"""

from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent
MODELS_DIR = ROOT_DIR / "models"

# Automatic resolution of BIDS dataset directory across environments (Linux/Windows)
_candidate_bids = [
    ROOT_DIR.parent.parent / "nautilus_bci" / "scripts" / "bids" / "bids_tower_defense",
    ROOT_DIR.parent / "nautilus_bci" / "scripts" / "bids" / "bids_tower_defense",
    Path("/home/guilhermecoto/Documentos/Lasige/nautilus_bci/scripts/bids/bids_tower_defense"),
]
BIDS_ROOT = next((p for p in _candidate_bids if p.exists()), _candidate_bids[0])

# Models
MODEL_PATH_OLD_PKL = MODELS_DIR / "rhythm_model.pkl"
MODEL_PATH_OLD_JOBLIB = MODELS_DIR / "rhythm_model.joblib"
MODEL_PATH_WATER_NEW = MODELS_DIR / "rhythm_model_water_new.joblib"
MODEL_PATH_WATER_NEW_PKL = MODELS_DIR / "rhythm_model_water_new.pkl"

# Active Model: defaults to the new water music model if available, otherwise old model
MODEL_PATH = MODEL_PATH_WATER_NEW if MODEL_PATH_WATER_NEW.exists() else (
    MODEL_PATH_OLD_JOBLIB if MODEL_PATH_OLD_JOBLIB.exists() else MODEL_PATH_OLD_PKL
)

# Hardware / EEG Acquisition
SAMPLING_RATE = 250.0
N_CHANNELS = 32
LSL_STREAM_NAME = "g.Nautilus"
LSL_STREAM_TYPE = "EEG"

# Preprocessing & Spatial Filters
LOWCUT = 1.0
HIGHCUT = 45.0
NOTCH = 50.0
SPATIAL_FILTER = "robust_car"  # Options: 'robust_car', 'car', 'laplacian', 'none'

# Window Configuration for Real-Time Inference
WINDOW_SIZE_SEC = 3.0   # 3.0 seconds = 750 samples (optimal for rhythm entrainment)
WINDOW_STEP_SEC = 0.25  # 0.25 seconds step = 4 predictions/second (high responsiveness)
SAMPLES_PER_WINDOW = int(WINDOW_SIZE_SEC * SAMPLING_RATE)
SAMPLES_PER_STEP = int(WINDOW_STEP_SEC * SAMPLING_RATE)

# Rhythm Bands for Filter Bank CSP
BANDS = [
    ('Theta', 4.0, 8.0),
    ('Alpha', 8.0, 12.0),
    ('Low-Beta', 12.0, 20.0),
    ('High-Beta', 20.0, 32.0),
    ('Gamma', 32.0, 45.0)
]

# Tower Defense Elements (Matches Godot Weak_System & audio_settings)
ELEMENTS = {
    0: "FIRE",
    1: "WATER",
    2: "WIND",
    3: "ELECTRICITY"
}

ELEMENT_TO_ID = {v: k for k, v in ELEMENTS.items()}

# Godot Game Communication
GODOT_IP = "127.0.0.1"
GODOT_PORT = 4242       # Port where Godot oz_receiver.gd listens for power:X commands
GAME_MARKER_PORT = 9000 # Port where Godot bci_marker_send.gd broadcasts event JSONs

# Inference & Decision Thresholds
CONFIDENCE_THRESHOLD = 0.35  # Minimal probability to trigger an element switch (chance is 0.25)
MIN_COOLDOWN_SEC = 1.0       # Minimum seconds between successive automated power triggers
