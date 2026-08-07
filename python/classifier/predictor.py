from pathlib import Path
import sys

import joblib
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config


class RhythmPredictor:

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = ROOT_DIR / "models" / "rhythm_model.joblib"

        self.model_path = Path(model_path)
        self.scaler = None
        self.model = None
        self.mode = "binary"

        if not self.model_path.exists():
            print(f"[Aviso] Modelo não encontrado em {self.model_path}. Por favor, corra python training/train.py")
        else:
            artifact = joblib.load(self.model_path)
            if isinstance(artifact, dict):
                self.scaler = artifact.get("scaler")
                self.model = artifact.get("model")
                self.mode = artifact.get("mode", "binary")
            else:
                self.model = artifact

    def predict(self, features):
        if self.model is None:
            return "UNKNOWN", 0.0

        features = np.asarray(features, dtype=np.float32).reshape(1, -1)

        if self.scaler is not None:
            features = self.scaler.transform(features)

        prediction_id = self.model.predict(features)[0]

        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(features)[0]
            confidence = float(np.max(probs))
        else:
            confidence = 1.0

        # Mapeamento para rótulo legível do jogo
        if self.mode == "binary":
            label = "FIRE" if prediction_id == 1 else "OTHER"
        else:
            # Multi-classe (Track 1..6 -> Mapeamento de Elementos)
            track_mapping = {
                1: "FIRE",
                2: "WATER",
                3: "WIND",
                4: "EARTH",
                5: "LIGHTNING",
                6: "ICE"
            }
            label = track_mapping.get(prediction_id, f"TRACK_{prediction_id}")

        return label, confidence