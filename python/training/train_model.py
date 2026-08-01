"""
Treina um Random Forest para reconhecer ritmos EEG.
"""

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


class RhythmTrainer:

    def __init__(self):

        self.model = RandomForestClassifier(
            n_estimators=200,
            random_state=42
        )

    def train(self, dataset):
        X = dataset.drop(columns=["label"])
        y = dataset["label"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y

        )

        self.model.fit(
            X_train,
            y_train
        )

        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(
            y_test,
            predictions
        )

        print()
        print("====================")
        print(f"Accuracy: {accuracy:.4f}")
        print("====================")

        return accuracy

    def save(self, path="models/rhythm_model.pkl"):
        joblib.dump(
            self.model,
            path
        )