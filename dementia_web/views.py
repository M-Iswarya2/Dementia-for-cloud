import json
import random
import time

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from assessments.models import TestStatus, DementiaAssessment


# =====================================================
# PUBLIC PAGES
# =====================================================


from django.shortcuts import render

def trail_test(request):
    return render(request, "pages/trail_test.html")



from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


# ================= HOME =================
def home(request):
    return render(request, "pages/home.html")


# ================= MEMORY SELECT =================
def memory_select(request):
    return render(request, "pages/memory_select.html")


# ================= MEMORY TEST =================
def memory_test(request):
    return render(request, "pages/memory_test.html")


# ================= TRAIL MAKING TEST =================
def trail_test(request):
    return render(request, "pages/trail_test.html")



# ================= SAVE SCORE API =================
@csrf_exempt
def save_score(request):
    if request.method == "POST":
        data = json.loads(request.body)
        score = data.get("score")

        print("Score received:", score)

        return JsonResponse({"status": "success"})
    
    return JsonResponse({"error": "Invalid request"})

def about(request):
    return render(request, "pages/about.html")





# =====================================================
# AUTHENTICATION
# =====================================================

def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=identifier, password=password)

        # Try login via email
        if user is None:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username/email or password")

    return render(request, "pages/login.html")


def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        phone = request.POST.get("phone")

        errors = {}

        if not full_name:
            errors["full_name"] = "Full name is required"

        if not email:
            errors["email"] = "Email is required"
        elif User.objects.filter(email=email).exists():
            errors["email"] = "Email already exists"

        if not username:
            errors["username"] = "Username is required"
        elif User.objects.filter(username=username).exists():
            errors["username"] = "Username already exists"

        if not password:
            errors["password"] = "Password is required"
        elif len(password) < 6:
            errors["password"] = "Password must be at least 6 characters"

        if password != confirm_password:
            errors["confirm_password"] = "Passwords do not match"

        if not phone or len(phone) != 10:
            errors["phone"] = "Phone must be 10 digits"

        if errors:
            return render(request, "pages/register.html", {
                "errors": errors,
                "form_data": request.POST
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Registration successful! Please login.")
        return redirect("login")

    return render(request, "pages/register.html")


def logout_view(request):
    logout(request)
    return redirect("home")


# =====================================================
# DASHBOARD
# =====================================================

@login_required
def dashboard(request):
    assessment_history = (
        DementiaAssessment.objects
        .filter(user=request.user)
        .order_by("id")
    )

    return render(request, "pages/dashboard.html", {
        "assessment_history": assessment_history
    })


# =====================================================
# TEST HUB
# =====================================================

@login_required
def take_test(request):
    status, _ = TestStatus.objects.get_or_create(user=request.user)
    return render(request, "pages/take_test.html", {"status": status})


# =====================================================
# TEST UI PAGES
# =====================================================

@login_required
def memory_select(request):
    return render(request, "pages/memory_select.html")


@login_required
def memory_test(request):
    return render(request, "pages/memory_test.html")


@login_required
def attention_test(request):
    return render(request, "pages/attention_test.html")


@login_required
def digit_span_test(request):
    return render(request, "pages/digit_span_test.html", {})



@login_required
def trail_b_test(request):
    return render(request, "pages/trail_b.html")


@login_required
def voice_test(request):
    return render(request, "pages/voice_test.html")


@login_required
def questions(request):
    return render(request, "pages/questions.html")

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import time
from .memory_logic import generate_round, evaluate_round

# In-memory session store
MEMORY_SESSIONS = {}

@csrf_exempt
def memory_start(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)
    
    session_id = f"memory_{int(time.time())}"
    session_data = generate_round(used_words=[])
    session_data["current_round"] = 1
    session_data["scores"] = []
    session_data["used_words"] = []

    MEMORY_SESSIONS[session_id] = session_data

    return JsonResponse({
        "session_id": session_id,
        "memorize_words": session_data["memorized_words"],
        "options": session_data["options"]
    })


@csrf_exempt
def memory_submit(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)
    
    data = json.loads(request.body)
    session_id = data.get("session_id")
    selected_words = data.get("selected_words", [])

    if not session_id or session_id not in MEMORY_SESSIONS:
        return JsonResponse({"error": "Invalid session"}, status=400)

    session_data = MEMORY_SESSIONS[session_id]

    result = evaluate_round(
        selected_words,
        session_data["correct_choices"],
        session_data["start_time"]
    )

    session_data["scores"].append(result["score"])
    current_round = session_data.get("current_round", 1)

    if current_round < 2:
        session_data["current_round"] += 1
        new_round_data = generate_round(used_words=session_data.get("used_words", []))
        session_data.update(new_round_data)

        return JsonResponse({
            "memory_score": result["score"],
            "next_round": True,
            "round": session_data["current_round"],
            "memorize_words": new_round_data["memorized_words"],
            "options": new_round_data["options"]
        })
    else:
        total_score = sum(session_data.get("scores", [])) / 2
        MEMORY_SESSIONS.pop(session_id, None)
        return JsonResponse({
            "memory_score": total_score,
            "next_round": False
        })
# =====================================================
# ATTENTION TEST LOGIC
# =====================================================

STIMULI = ["🔵", "🔴", "🟣", "🟢"]
TOTAL_TRIALS = 30
TARGET_RATIO = 0.3


def generate_attention_sequence():
    target = random.choice(STIMULI)
    sequence = []

    for _ in range(TOTAL_TRIALS):
        if random.random() < TARGET_RATIO:
            sequence.append(target)
        else:
            sequence.append(random.choice([s for s in STIMULI if s != target]))

    return {
        "target": target,
        "sequence": sequence,
        "total_trials": TOTAL_TRIALS
    }
from .attention_logic import generate_attention_sequence, evaluate_attention


# In-memory session store for attention test
ATTENTION_SESSIONS = {}

# ===================== START TEST =====================
@csrf_exempt
def attention_start(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    # Create unique session ID
    session_id = f"attention_{len(ATTENTION_SESSIONS) + 1}"

    # Generate random sequence and targets (per trial)
    test_data = generate_attention_sequence()  # now returns "sequence" and "targets"

    # Save session
    ATTENTION_SESSIONS[session_id] = {
        "sequence": test_data["sequence"],
        "targets": test_data["targets"],  # list of target per trial
        "responses": []
    }

    # Return session info to frontend
    return JsonResponse({
        "session_id": session_id,
        "sequence": test_data["sequence"],
        "targets": test_data["targets"],  # <-- send targets array
        "total_trials": len(test_data["sequence"])
    })

# ===================== SUBMIT TEST =====================
@csrf_exempt
def attention_submit(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    try:
        data = json.loads(request.body)
        session_id = data.get("session_id")
        responses = data.get("responses", [])

        if session_id not in ATTENTION_SESSIONS:
            return JsonResponse({"error": "Invalid session"}, status=400)

        session = ATTENTION_SESSIONS[session_id]
        sequence = session["sequence"]
        targets = session["targets"]  # <-- list of targets per trial

        # Evaluate responses per trial
        hits = 0
        misses = 0
        false_alarms = 0
        reaction_times = []

        response_map = {r["index"]: r["reaction_time"] for r in responses}

        for i, stim in enumerate(sequence):
            target = targets[i]
            if stim == target:
                if i in response_map:
                    hits += 1
                    reaction_times.append(response_map[i])
                else:
                    misses += 1
            else:
                if i in response_map:
                    false_alarms += 1

        avg_rt = round(sum(reaction_times)/len(reaction_times), 3) if reaction_times else 0
        raw_score = (hits * 2) - false_alarms - misses

        # Normalize score
        total_targets = sum(1 for t, s in zip(targets, sequence) if t == s)
        max_score = total_targets * 2
        normalized_score = max(0, min(1, raw_score / max_score)) if max_score > 0 else 0

        ATTENTION_SESSIONS.pop(session_id, None)

        return JsonResponse({
            "success": True,
            "attention_score": round(normalized_score, 2),
            "details": {
                "hits": hits,
                "misses": misses,
                "false_alarms": false_alarms,
                "avg_reaction_time": avg_rt,
                "raw_score": raw_score
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)

# =====================================================
# RECEIVE SCORES (AJAX)
# =====================================================

@csrf_exempt
@login_required
def submit_memory_score(request):
    if request.method == "POST":
        data = json.loads(request.body)
        score = float(data.get("score", 0))

        status, _ = TestStatus.objects.get_or_create(user=request.user)
        status.memory_done = True
        status.memory_score = score
        status.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


@csrf_exempt
@login_required
def submit_attention_score(request):
    if request.method == "POST":
        data = json.loads(request.body)
        score = float(data.get("score", 0))

        status, _ = TestStatus.objects.get_or_create(user=request.user)
        status.attention_done = True
        status.attention_score = score
        status.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


@csrf_exempt
@login_required
def submit_digit_span_score(request):
    if request.method == "POST":
        data = json.loads(request.body)

        forward = float(data.get("forward", 0))
        backward = float(data.get("backward", 0))

        total_score = forward + backward
        normalized_score = total_score / 10

        status, _ = TestStatus.objects.get_or_create(user=request.user)
        status.digit_span_done = True
        status.digit_span_score = normalized_score
        status.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


@csrf_exempt
@login_required
def submit_trail_b_score(request):
    if request.method == "POST":
        data = json.loads(request.body)

        time_taken = float(data.get("time_taken", 0))
        mistakes = int(data.get("mistakes", 0))

        EXPECTED_TIME = 128
        MAX_TIME = 300
        MAX_MISTAKES = 15

        if time_taken <= EXPECTED_TIME:
            time_score = 1.0
        elif time_taken >= MAX_TIME:
            time_score = 0.0
        else:
            time_score = 1 - (
                (time_taken - EXPECTED_TIME) /
                (MAX_TIME - EXPECTED_TIME)
            )

        mistake_penalty = mistakes / MAX_MISTAKES
        score = max(0, min(1, time_score - mistake_penalty))

        status, _ = TestStatus.objects.get_or_create(user=request.user)
        status.trail_done = True
        status.trail_score = score

        status.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


@csrf_exempt
@login_required
def submit_voice_score(request):
    if request.method == "POST":
        data = json.loads(request.body)
        score = float(data.get("score", 0))
        print("VOICE SCORE RECEIVED IN DJANGO:", score)
        status, _ = TestStatus.objects.get_or_create(user=request.user)
        status.voice_done = True
        status.voice_score = score
        status.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


@csrf_exempt
@login_required
def submit_questionnaire_score(request):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=400)

    data = json.loads(request.body)
    answers = data.get("answers", {})

    total_questions = len(answers)
    max_score_per_question = 4

    raw_score = sum(int(v) for v in answers.values())
    max_total = total_questions * max_score_per_question

    normalized_score = (
        (max_total - raw_score + total_questions) / max_total
        if total_questions > 0 else 0
    )

    normalized_score = max(0.0, min(1.0, normalized_score))

    status, _ = TestStatus.objects.get_or_create(user=request.user)
    status.questionnaire_done = True
    status.questionnaire_score = normalized_score
    status.save()

    return JsonResponse({"success": True})

# views_voice.py
import os
import uuid
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .predict_voice import predict_voice

# Directory to save uploaded audio files
AUDIO_UPLOAD = getattr(settings, "AUDIO_UPLOAD", "uploads")

@csrf_exempt
def analyze_voice(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=400)
    
    path = None

    try:
        os.makedirs(AUDIO_UPLOAD, exist_ok=True)

        if "audio" not in request.FILES:
            return JsonResponse({"success": False, "error": "No audio file provided"}, status=400)

        file = request.FILES["audio"]

        if file.name == "":
            return JsonResponse({"success": False, "error": "Empty filename"}, status=400)

        # Save file with unique name
        filename = f"{uuid.uuid4()}.wav"
        path = os.path.join(AUDIO_UPLOAD, filename)

        with open(path, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)

        # Run model prediction
        label, prob = predict_voice(path)

        prob = float(prob)
        voice_score = prob
        dementia_risk = 1.0 - prob
        prediction = "no_dementia" if prob >= 0.5 else "dementia"

        return JsonResponse({
            "success": True,
            "prediction": prediction,
            "voice_score": round(voice_score, 4),
            "dementia_risk": round(dementia_risk, 4),
            "raw_probability_no_dementia": round(prob, 4)
        }, status=200)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)

    finally:
        # Remove file after processing
        if path and os.path.exists(path):
            os.remove(path)
# =====================================================
# FINAL RESULT
# =====================================================

@login_required
def final_result(request):
    status = TestStatus.objects.filter(user=request.user).order_by("-id").first()
    if not status:
        return redirect("take_test")

    # Get raw scores or 0
    memory = float(status.memory_score or 0)
    attention = float(status.attention_score or 0)
    trail_b = float(status.trail_score or 0)
    digit_span = float(status.digit_span_score or 0)
    voice = float(status.voice_score or 0)
    questionnaire = float(status.questionnaire_score or 0)

    # Compute final risk score
    cognitive_score = (memory + attention + trail_b + digit_span) / 4
    final_score = cognitive_score * 0.4 + voice * 0.4 + questionnaire * 0.2

    # Risk label
    if final_score >= 0.75:
        risk = "Low Risk"
    elif final_score >= 0.6:
        risk = "Mild Cognitive Impairment"
    elif final_score >= 0.4:
        risk = "Moderate Risk"
    else:
        risk = "High Risk"

    # Create assessment record
    DementiaAssessment.objects.create(
        user=request.user,
        final_score=round(final_score, 3),
        risk_level=risk
    )

    # Pass **percentages** to template
    context = {
        "final_score": round(final_score*100, 1),
        "risk": risk,
        "status": status,
        "memory_pct": round(memory*100, 1),
        "attention_pct": round(attention*100, 1),
        "trail_b_pct": round(trail_b*100, 1),
        "digit_span_pct": round(digit_span*100, 1),
        "voice_pct": round(voice*100, 1),
        "questionnaire_pct": round(questionnaire*100, 1),
    }

    return render(request, "pages/final_result.html", context)


@login_required
def reset_tests(request):
    status = TestStatus.objects.get(user=request.user)

    status.memory_done = False
    status.attention_done = False
    status.trail_done = False
    status.voice_done = False
    status.questionnaire_done = False

    status.memory_score = None
    status.attention_score = None
    status.trail_score = None
    status.voice_score = None
    status.questionnaire_score = None

    status.save()

    return redirect("take_test")
