import os
import numpy as np
import librosa
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    confusion_matrix, classification_report,
    precision_score, recall_score, f1_score
)
from tensorflow.keras.models import load_model

DATA_DIR = "dataset/augmented"
MODEL_PATH = "models/dementia_cnn_bilstm.h5"
SR = 16000
N_MFCC = 40
MAX_LEN = 300


def extract_mfcc(file_path):
    y, sr = librosa.load(file_path, sr=SR)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC).T
    if mfcc.shape[0] < MAX_LEN:
        pad_width = MAX_LEN - mfcc.shape[0]
        mfcc = np.pad(mfcc, ((0, pad_width), (0, 0)))
    else:
        mfcc = mfcc[:MAX_LEN, :]
    return mfcc

X, y = [], []
for label in ["dementia", "no_dementia"]:
    folder = os.path.join(DATA_DIR, label)
    for file in os.listdir(folder):
        if file.endswith(".wav"):
            try:
                X.append(extract_mfcc(os.path.join(folder, file)))
                y.append(label)
            except:
                pass

X = np.array(X)[..., np.newaxis]
le = LabelEncoder()
y = le.fit_transform(y)

model = load_model(MODEL_PATH)


y_pred_prob = model.predict(X)
y_pred = (y_pred_prob > 0.5).astype(int).ravel()

precision = precision_score(y, y_pred)
recall = recall_score(y, y_pred)
f1 = f1_score(y, y_pred)
cm = confusion_matrix(y, y_pred)

print("\n Evaluation Metrics:")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1-score  : {f1:.4f}")

print("\n Confusion Matrix:")
print(cm)

print("\n Classification Report:")
print(classification_report(y, y_pred, target_names=le.classes_))
