from django.db import models
from django.contrib.auth.models import User

class DementiaAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    final_score = models.FloatField()
    risk_level = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.final_score}"


class TestStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Existing tests
    memory_done = models.BooleanField(default=False)
    attention_done = models.BooleanField(default=False)
    voice_done = models.BooleanField(default=False)
    questionnaire_done = models.BooleanField(default=False)

    memory_score = models.FloatField(null=True, blank=True)
    attention_score = models.FloatField(null=True, blank=True)
    voice_score = models.FloatField(null=True, blank=True)
    questionnaire_score = models.FloatField(null=True, blank=True)

    # New tests
    digit_span_done = models.BooleanField(default=False)
    trail_done = models.BooleanField(default=False)

    digit_span_score = models.FloatField(null=True, blank=True)
    trail_score = models.FloatField(null=True, blank=True)

    def all_completed(self):
        return (
            self.memory_done and
            self.attention_done and
            self.voice_done and
            self.questionnaire_done and
            self.digit_span_done and
            self.trail_done
        )

    @property
    def completed_count(self):
        return sum([
            self.memory_done,
            self.attention_done,
            self.voice_done,
            self.questionnaire_done,
            self.digit_span_done,
            self.trail_done
        ])

    def __str__(self):
        return self.user.username
