from flask import Blueprint, request, jsonify
from src.memory_test.memory_logic import generate_round, evaluate_round
import time

memory_bp = Blueprint("memory_bp", __name__)

# In-memory session store (replace with DB in production)
sessions = {}

# -----------------------------
# Start a new memory session
# -----------------------------
@memory_bp.route("/start", methods=["POST"])
def memory_start():
    # For simplicity, generate a session_id
    session_id = f"memory_{int(time.time())}"
    
    # Initialize session
    session_data = generate_round(used_words=[])
    session_data["current_round"] = 1
    session_data["scores"] = []
    session_data["used_words"] = []  # optional: track words across rounds
    
    sessions[session_id] = session_data

    return jsonify({
        "session_id": session_id,
        "memorize_words": session_data["memorized_words"],
        "options": session_data["options"]
    })

# -----------------------------
# Submit round selections
# -----------------------------
@memory_bp.route("/submit", methods=["POST"])
def memory_submit():
    data = request.json
    session_id = data.get("session_id")
    selected_words = data.get("selected_words", [])

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    session_data = sessions[session_id]

    # Evaluate current round
    result = evaluate_round(
        selected_words,
        session_data["correct_choices"],
        session_data["start_time"]
    )

    # Store score for this round
    session_data["scores"].append(result["score"])

    # Prepare next round or finish
    current_round = session_data.get("current_round", 1)

    if current_round < 2:
        # Round 2
        session_data["current_round"] += 1
        new_round_data = generate_round(used_words=session_data.get("used_words", []))
        session_data.update(new_round_data)

        return jsonify({
            "memory_score": result["score"],         # current round score
            "next_round": True,
            "round": session_data["current_round"],
            "memorize_words": new_round_data["memorized_words"],
            "options": new_round_data["options"]
        })
    else:
        # Final round complete
        total_score = sum(session_data.get("scores", [])) / 2  # average 2 rounds
        sessions.pop(session_id, None)

        return jsonify({
            "memory_score": total_score,
            "next_round": False
        })
