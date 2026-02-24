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
from sklearn.metrics import classification_report, confusion_matrix

# --- CONFIGURATION ---
DATA_DIR = "dataset/augmented"
SR = 16000
N_MFCC = 40
MAX_LEN = 300  
BATCH_SIZE = 16
EPOCHS = 20 # Increased slightly for better convergence with normalization

def extract_mfcc(file_path):
    # 1. Load audio and force Mono
    y, sr = librosa.load(file_path, sr=SR, mono=True)

    # 2. Basic Noise/Silence Removal (Trim leading/trailing silence)
    y, _ = librosa.effects.trim(y)

    # 3. Volume Normalization (Ensures live voice matches dataset volume)
    if len(y) > 0:
        y = librosa.util.normalize(y)

    # 4. Feature Extraction
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
    mfcc = mfcc.T

    # 5. Global Feature Scaling (CRITICAL for Neural Networks)
    # This centers the data around 0
    mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-8)

    # 6. Padding/Truncating
    if mfcc.shape[0] < MAX_LEN:
        pad_width = MAX_LEN - mfcc.shape[0]
        mfcc = np.pad(mfcc, ((0, pad_width), (0, 0)), mode='constant')
    else:
        mfcc = mfcc[:MAX_LEN, :]

    return mfcc

# --- DATA PREPARATION ---
X, y = [], []

print("Loading dataset...")
for label in ["dementia", "no_dementia"]:
    folder = os.path.join(DATA_DIR, label)
    if not os.path.exists(folder): continue
    
    for file in os.listdir(folder):
        if file.endswith(".wav"):
            try:
                feat = extract_mfcc(os.path.join(folder, file))
                X.append(feat)
                y.append(label)
            except Exception as e:
                print(f"Error processing {file}: {e}")

X = np.array(X)
X = X[..., np.newaxis] # Shape: (samples, 300, 40, 1)

le = LabelEncoder()
y = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# --- MODEL ARCHITECTURE ---
model = Sequential([
    # CNN Layers to extract spatial features from MFCCs
    Conv2D(32, (3, 3), activation="relu", padding="same", input_shape=(MAX_LEN, N_MFCC, 1)),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Conv2D(64, (3, 3), activation="relu", padding="same"),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    # Reshape for the Sequence model (RNN)
    # Height is reduced by pooling twice (300 -> 150 -> 75)
    Reshape((75, -1)), 
    
    # Bi-LSTM to capture temporal patterns in speech
    Bidirectional(LSTM(64, return_sequences=False)),

    Dense(64, activation="relu"),
    Dropout(0.4),
    Dense(1, activation="sigmoid")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# --- TRAINING ---
print("\nStarting Training...")
history = model.fit(
    X_train, y_train,
    validation_split=0.15,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    verbose=1
)

# --- EVALUATION ---
loss, acc = model.evaluate(X_test, y_test)
print(f"\nFinal Test Accuracy: {acc * 100:.2f}%")

model.save("dementia_cnn_bilstm.h5")
print("Model saved as dementia_cnn_bilstm_gem.h5")