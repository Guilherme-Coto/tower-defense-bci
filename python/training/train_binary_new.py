import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from joblib import dump

X=np.load("training/X.npy")
y=np.load("training/y.npy")

X_train,X_test,y_train,y_test=train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

scaler=StandardScaler()

X_train=scaler.fit_transform(X_train)
X_test=scaler.transform(X_test)

clf=SVC(
    kernel="rbf",
    probability=True
)

clf.fit(X_train,y_train)
pred=clf.predict(X_test)

print(classification_report(y_test,pred))

dump(scaler,"models/scaler.joblib")
dump(clf,"models/svm_track1.joblib")