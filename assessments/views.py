from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from .models import DementiaAssessment


# ===================== DASHBOARD DATA =====================
@login_required
def dashboard_data(request):
    user = request.user

    assessments = DementiaAssessment.objects.filter(
        user=user
    ).order_by('-created_at')

    # If no assessments yet
    if not assessments.exists():
        return JsonResponse({
            "current_risk": None,
            "risk_score": None,
            "last_assessment_type": None,
            "last_assessment_date": None,
            "total_assessments": 0,
            "completed_this_month": 0,
            "trend": None,
            "trend_change": None,
            "assessment_history": []
        })

    latest = assessments.first()

    # Build history
    history = []
    for a in assessments:
        history.append({
            "date": a.created_at.strftime("%Y-%m-%d"),
            "type": "Assessment",
            "risk": a.risk_level or "N/A",
            "score": a.final_score if a.final_score is not None else "--"
        })

    current_month = timezone.now().month
    completed_this_month = assessments.filter(
        created_at__month=current_month
    ).count()

    return JsonResponse({
        "current_risk": latest.risk_level,
        "risk_score": latest.final_score,
        "last_assessment_type": "Assessment",
        "last_assessment_date": latest.created_at.strftime("%Y-%m-%d"),
        "total_assessments": assessments.count(),
        "completed_this_month": completed_this_month,
        "trend": None,
        "trend_change": None,
        "assessment_history": history
    })


# ===================== SAVE FINAL SCORE =====================
@csrf_exempt
@login_required
def save_final_score(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"})

    try:
        data = json.loads(request.body)

        final_score = data.get("final_score")
        risk_level = data.get("risk_level")

        assessment = DementiaAssessment.objects.create(
            user=request.user,   # 🔐 SECURE
            final_score=final_score,
            risk_level=risk_level
        )

        return JsonResponse({
            "success": True,
            "assessment_id": assessment.id
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })
