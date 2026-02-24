'''import numpy as np
import librosa
from tensorflow.keras.models import load_model
from config import MODEL_PATH 

SR = 16000       # expected sample rate
N_MFCC = 40
MAX_LEN = 300


model = load_model(MODEL_PATH)

def extract_mfcc(file_path):
    
    y, sr = librosa.load(file_path, sr=SR, mono=True)

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=N_MFCC
    ).T

    # Pad or truncate
    if mfcc.shape[0] < MAX_LEN:
        mfcc = np.pad(
            mfcc,
            ((0, MAX_LEN - mfcc.shape[0]), (0, 0)),
            mode="constant"
        )
    else:
        mfcc = mfcc[:MAX_LEN, :]

    return mfcc


def predict_voice(file_path):
    mfcc = extract_mfcc(file_path)
    X = mfcc[np.newaxis, ..., np.newaxis]

    prob_no_dementia = model.predict(X, verbose=0)[0][0]
    label = "no_dementia" if prob_no_dementia >= 0.5 else "dementia"

    return label, float(prob_no_dementia)


if __name__ == "__main__":
    test_file = "uploads/test_audio.wav"

    label, prob = predict_voice(test_file)

    print("\n====== VOICE MODEL TEST ======")
    print(f"Prediction             : {label}")
    print(f"No-dementia probability: {prob:.3f}")
    print(f"Dementia risk          : {1 - prob:.3f}")

'''

import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras.models import load_model

# Must match training config exactly
SR = 16000
N_MFCC = 40
MAX_LEN = 300
MODEL_PATH = "models\dementia_cnn_bilstm_gem.h5"

# Load the model once
model = load_model(MODEL_PATH)

def extract_mfcc_live(file_path):
    # 1. Load (Force Mono and 16kHz)
    y, sr = librosa.load(file_path, sr=SR, mono=True)

    # 2. Trim silence (Crucial if you have a delay starting/stopping recording)
    y, _ = librosa.effects.trim(y)

    # 3. Volume Normalization
    if len(y) > 0:
        y = librosa.util.normalize(y)
    else:
        return None

    # 4. Extract MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
    mfcc = mfcc.T

    # 5. Feature Scaling (Must match training logic!)
    # This prevents the model from being confused by different mic gains
    mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-8)

    # 6. Pad/Truncate to MAX_LEN
    if mfcc.shape[0] < MAX_LEN:
        pad_width = MAX_LEN - mfcc.shape[0]
        mfcc = np.pad(mfcc, ((0, pad_width), (0, 0)), mode='constant')
    else:
        mfcc = mfcc[:MAX_LEN, :]

    return mfcc

def predict_voice(file_path):
    features = extract_mfcc_live(file_path)
    
    if features is None:
        return "Error: Silent file", 0.0

    # Reshape for model: (Batch, Time, Features, Channels)
    X = features[np.newaxis, ..., np.newaxis]

    # Get raw probability
    prob = model.predict(X, verbose=0)[0][0]

    # In your LabelEncoder: 
    # Usually 'dementia' is 0 and 'no_dementia' is 1 (alphabetical)
    # Check your training output to confirm!
    label = "Healthy (No Dementia)" if prob >= 0.5 else "Potential Dementia"

    return label, float(prob)

if __name__ == "__main__":
    # Point this to your recorded .wav file
    test_file = "uploads/test_audio.wav" 

    try:
        label, confidence = predict_voice(test_file)
        
        print("\n" + "="*30)
        print("      VOICE ANALYSIS RESULTS      ")
        print("="*30)
        print(f"Result      : {label}")
        print(f"Confidence  : {confidence if confidence > 0.5 else (1-confidence):.2%}")
        print(f"Raw Score   : {confidence:.4f}")
        print("="*30)
        
    except Exception as e:
        print(f"Prediction failed: {e}")