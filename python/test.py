from scipy.io import loadmat

mat = loadmat("datasets/stanford/song21_Imputed.mat")

print(mat.keys())

for k, v in mat.items():
    if not k.startswith("__"):
        print(k, type(v))
        try:
            print(v.shape)
        except:
            pass