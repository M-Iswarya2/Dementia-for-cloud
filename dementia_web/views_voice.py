from flask import Blueprint, request, jsonify
import os
import uuid
from config import AUDIO_UPLOAD
from .predict_voice import predict_voice

# ✅ CREATE BLUEPRINT FIRST
voice_bp = Blueprint("voice", __name__)

@voice_bp.route("/analyze", methods=["POST"])
def analyze_voice():
    path = None

    try:
        os.makedirs(AUDIO_UPLOAD, exist_ok=True)

        if "audio" not in request.files:
            return jsonify({"success": False, "error": "No audio file provided"}), 400

        file = request.files["audio"]

        if file.filename == "":
            return jsonify({"success": False, "error": "Empty filename"}), 400

        filename = f"{uuid.uuid4()}.wav"
        path = os.path.join(AUDIO_UPLOAD, filename)

        file.save(path)

        label, prob = predict_voice(path)

        prob = float(prob)

        voice_score = prob
        dementia_risk = 1.0 - prob
        prediction = "no_dementia" if prob >= 0.5 else "dementia"

        return jsonify({
            "success": True,
            "prediction": prediction,
            "voice_score": round(voice_score, 4),
            "dementia_risk": round(dementia_risk, 4),
            "raw_probability_no_dementia": round(prob, 4)
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if path and os.path.exists(path):
            os.remove(path)