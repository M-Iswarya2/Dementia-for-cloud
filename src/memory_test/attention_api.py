from flask import Blueprint, request, jsonify
from src.memory_test.attention_logic import generate_attention_sequence, evaluate_attention

attention_bp = Blueprint("attention", __name__)

ATTENTION_SESSIONS = {}


@attention_bp.route("/start", methods=["POST"])
def start_attention_test():
    session_id = f"attention_{len(ATTENTION_SESSIONS) + 1}"
    
    test_data = generate_attention_sequence()
    
    ATTENTION_SESSIONS[session_id] = {
        "sequence": test_data["sequence"],
        "responses": []
    }
    
    return jsonify({
        "session_id": session_id,
        "sequence": test_data["sequence"],
        "total_trials": len(test_data["sequence"])
    })


@attention_bp.route("/submit", methods=["POST"])
def submit_attention_test():
    data = request.get_json()
    session_id = data.get("session_id")
    responses = data.get("responses", [])
    
    if session_id not in ATTENTION_SESSIONS:
        return jsonify({"error": "Invalid session"}), 400
    
    session = ATTENTION_SESSIONS[session_id]
    sequence = session["sequence"]
    
    results = evaluate_attention(responses, sequence)
    
    # Calculate normalized attention score (0-1)
    total_trials = len(sequence)
    target_count = sum(1 for s in sequence if s == "🔵")
    max_score = target_count * 2  # Perfect hits with no penalties
    
    # Normalize score (can be negative, so we clamp to 0-1 range)
    normalized_score = max(0, min(1, results["raw_score"] / max_score)) if max_score > 0 else 0
    results["attention_score"] = round(normalized_score, 2)
    
    # Clean up session
    ATTENTION_SESSIONS.pop(session_id)
    
    return jsonify({
    "success": True,
    "attention_score": results["attention_score"],  # <-- top-level for easy access
    "details": results
})
