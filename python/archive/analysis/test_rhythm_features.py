import numpy as np

from features.rhythm_features import RhythmFeatureExtractor

# Simular 2 segundos
fs = 125

signal = np.random.randn(fs * 2)

extractor = RhythmFeatureExtractor(fs)

features = extractor.extract(signal)

print("\nFeatures:")
print("----------------")

for k, v in features.items():
    print(f"{k:20s}: {v:.4f}")