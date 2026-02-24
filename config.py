import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
AUDIO_UPLOAD = os.path.join(UPLOAD_FOLDER, "audio")

MODEL_PATH = os.path.join(BASE_DIR, "models", "dementia_cnn_bilstm.h5")

ALLOWED_AUDIO = {"wav", "mp3"}
