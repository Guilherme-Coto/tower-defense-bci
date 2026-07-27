from scipy.io import loadmat

data = loadmat("datasets/stanford/song21_Imputed.mat")

print(type(data["data21"]))
print(data["data21"].shape)

print(type(data["fs"]))
print(data["fs"])

print(type(data["subs21"]))
print(data["subs21"].shape)

import numpy as np

eeg = data["data21"]

print(eeg.dtype)

print(eeg[0])