from flask import Blueprint, request, jsonify
from .scoring import calculate_questionnaire_score

questionnaire_bp = Blueprint("questionnaire", __name__)

@questionnaire_bp.route("/submit", methods=["POST"])
def submit_questions():
    try:
        data = request.get_json()
        answers = data.get("answers", {})
        
        print(f"Received answers: {answers}")  # Debug
        
        # Calculate score (should return 0-1 scale)
        score = calculate_questionnaire_score(answers)
        
        print(f"Calculated score: {score}")  # Debug
        
        # Ensure score is between 0 and 1
        normalized_score = max(0.0, min(1.0, float(score)))
        
        return jsonify({
            "success": True,
            "score": normalized_score,  # Frontend expects "score"
            "questionnaire_score": normalized_score,  # Also include this for compatibility
            "normalized_score": normalized_score
        }), 200
        
    except Exception as e:
        print(f"Error in questionnaire submission: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500