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
