from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),

    # API
    path("assessments/", include("assessments.urls")),

    # Public Pages
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),


    # Authentication
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard & Flow
    path("dashboard/", views.dashboard, name="dashboard"),
    path("take-test/", views.take_test, name="take_test"),
    path("final-result/", views.final_result, name="final_result"),

    # Tests
    path("memory-select/", views.memory_select, name="memory_select"),
    path("memory-test/", views.memory_test, name="memory_test"),
    path("attention-test/", views.attention_test, name="attention_test"),
    path("voice-test/", views.voice_test, name="voice_test"),
    path("questions/", views.questions, name="questions"),

    # ✅ NEW — Digit Span Test
    path("digit-span-test/", views.digit_span_test, name="digit_span_test"),

    # ✅ NEW — Trail Making Test
    path("trail-test/", views.trail_test, name="trail_test"),

    # Score Submissions
    path("submit-memory-score/", views.submit_memory_score, name="submit_memory_score"),
    path("submit-voice-score/", views.submit_voice_score, name="submit_voice_score"),
    path("submit-attention-score/", views.submit_attention_score, name="submit_attention_score"),
    path("submit-questionnaire-score/", views.submit_questionnaire_score, name="submit_questionnaire_score"),

    # Reset
    path("reset-tests/", views.reset_tests, name="reset_tests"),

    # Trail B score submission
path("submit-trail-b-score/", views.submit_trail_b_score, name="submit_trail_b_score"),
path("submit-digit-span-score/", views.submit_digit_span_score, name="submit_digit_span_score"),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATICFILES_DIRS[0]
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
