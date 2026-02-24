from flask import Flask, jsonify
from flask_cors import CORS

# Import blueprints from your modules
from src.memory_test.memory_api import memory_bp
from src.memory_test.attention_api import attention_bp  # ✅ ADD THIS
from src.voice_test.voice_api import voice_bp
from src.questionnaire.questionnaire_api import questionnaire_bp
from src.evaluation.final_result import evaluation_bp

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes and origins (good for local dev)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register Blueprints with URL prefixes
app.register_blueprint(memory_bp, url_prefix="/memory")
app.register_blueprint(attention_bp, url_prefix="/attention")  # ✅ ADD THIS
app.register_blueprint(voice_bp, url_prefix="/voice")
app.register_blueprint(questionnaire_bp, url_prefix="/questionnaire")
app.register_blueprint(evaluation_bp, url_prefix="/evaluate")

# Health check route
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "Backend is running!"}), 200

# Error handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

# Error handler for 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Main entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)