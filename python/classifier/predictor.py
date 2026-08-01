import joblib
import numpy as np

class RhythmPredictor:

    def __init__(self,model_path="models/rhythm_model.pkl"):
        self.model = joblib.load(model_path)

    def predict(self, features):
        features = np.array(features).reshape(1, -1)
        prediction = self.model.predict(features)[0]

        confidence = np.max(self.model.predict_proba(features))

        return prediction, confidence