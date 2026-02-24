from django.contrib import admin
from .models import DementiaAssessment

@admin.register(DementiaAssessment)
class DementiaAssessmentAdmin(admin.ModelAdmin):
    list_display = ("user", "risk_level", "final_score", "created_at")
    list_filter = ("risk_level", "created_at")
    search_fields = ("user__username",)
