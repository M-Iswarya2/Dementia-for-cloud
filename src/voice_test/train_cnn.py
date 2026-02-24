import os
import librosa
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, BatchNormalization,
    Reshape, Bidirectional, LSTM,
    Dense, Dropout
)
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score
)


DATA_DIR = "dataset/augmented"
SR = 16000
N_MFCC = 40
MAX_LEN = 300  
BATCH_SIZE = 16
EPOCHS = 15

def extract_mfcc(file_path):
    y, sr = librosa.load(file_path, sr=SR)

    mfcc = librosa.feature.mfcc(
        y=y, sr=sr, n_mfcc=N_MFCC
    )

    mfcc = mfcc.T

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

X = np.array(X)
X = X[..., np.newaxis]  

le = LabelEncoder()
y = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

model = Sequential([
    Conv2D(32, (3, 3), activation="relu", padding="same",
           input_shape=(MAX_LEN, N_MFCC, 1)),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Conv2D(64, (3, 3), activation="relu", padding="same"),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Conv2D(128, (3, 3), activation="relu", padding="same"),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Reshape((-1, 128)),
    Bidirectional(LSTM(64, return_sequences=False)),

    Dense(64, activation="relu"),
    Dropout(0.4),
    Dense(1, activation="sigmoid")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.summary()


history = model.fit(
    X_train, y_train,
    validation_split=0.1,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    verbose=1
)


loss, acc = model.evaluate(X_test, y_test)
print(f"\n Test Accuracy: {acc * 100:.2f}%")

model.save("dementia_cnn_bilstm.h5")

y_pred_prob = model.predict(X_test)
y_pred = (y_pred_prob > 0.5).astype(int).ravel()

precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n Evaluation Metrics:")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1-score  : {f1:.4f}")


cm = confusion_matrix(y_test, y_pred)
print("\n Confusion Matrix:")
print(cm)

print("\n Classification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=le.classes_
))
