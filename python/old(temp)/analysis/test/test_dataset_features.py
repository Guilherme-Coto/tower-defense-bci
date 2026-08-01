from scipy.io import loadmat

from features.rhythm_features import RhythmFeatureExtractor

mat = loadmat("./datasets/stanford/song21_Imputed.mat")
data = mat["data21"]
fs = int(mat["fs"][0,0])

participant = 0

channels = {
    "Motor L":35,
    "Temporal L":44,
    "Motor R":103,
    "Temporal R":107
}

extractor = RhythmFeatureExtractor(fs)

for name, ch in channels.items():
    eeg = data[ch,:,participant]
    features = extractor.extract(eeg[:2*fs])
    print("\n",name)
    for k,v in features.items():
        print(f"{k:20s}: {v:.4f}")