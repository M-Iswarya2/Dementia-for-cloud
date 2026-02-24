import numpy as np
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
from tensorflow.keras.models import load_model
from config import MODEL_PATH

# ===== SAME SETTINGS AS TRAINING =====
SR = 16000
N_MELS = 128
MAX_LEN = 300

# Load trained model
model = load_model(MODEL_PATH)


def extract_logmel(file_path):
    y, sr = librosa.load(file_path, sr=SR)

    mel = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=N_MELS,
        fmax=8000
    )

    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_db = mel_db.T

    # Normalize (same as training)
    mel_db = (mel_db - np.mean(mel_db)) / (np.std(mel_db) + 1e-6)

    # Pad / truncate
    if mel_db.shape[0] < MAX_LEN:
        pad_width = MAX_LEN - mel_db.shape[0]
        mel_db = np.pad(mel_db, ((0, pad_width), (0, 0)))
    else:
        mel_db = mel_db[:MAX_LEN, :]

    return mel_db


def predict_voice(file_path):
    features = extract_logmel(file_path)

    X = features[np.newaxis, ..., np.newaxis]

    prob = model.predict(X, verbose=0)[0][0]

    label = "no_dementia" if prob >= 0.5 else "dementia"

    return label, float(prob)


if __name__ == "__main__":
    test_file = "uploads/test_audio.wav"

    label, prob = predict_voice(test_file)

    print("\n====== VOICE MODEL TEST ======")
    print(f"Prediction             : {label}")
    print(f"No-dementia probability: {prob:.3f}")
    print(f"Dementia risk          : {1 - prob:.3f}")'''