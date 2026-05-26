from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


# ---------------- CHAT MESSAGES ----------------
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    is_user_message = models.BooleanField(default=True)

    emotion_context = models.CharField(max_length=50, blank=True, null=True)

    sentiment_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)]
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{'User' if self.is_user_message else 'Bot'}: {self.message[:30]}"


# ---------------- WELLNESS SESSION ----------------
class WellnessSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wellness_sessions')
    session_id = models.CharField(max_length=100, unique=True)

    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(blank=True, null=True)

    dominant_emotion = models.CharField(max_length=50, blank=True)
    wellness_score = models.FloatField(default=50.0)

    recommendations_given = models.JSONField(default=list)
    session_summary = models.TextField(blank=True)

    message_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def end_session(self):
        self.session_end = timezone.now()
        self.is_active = False
        self.save()

    def __str__(self):
        return f"Session {self.session_id}"


# ---------------- EMOTIONAL WELLNESS LOG ----------------
class EmotionalWellnessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wellness_logs')

    log_date = models.DateField(default=timezone.now)

    eeg_emotion = models.CharField(max_length=50, blank=True, null=True)
    face_emotion = models.CharField(max_length=50, blank=True, null=True)

    combined_emotion = models.CharField(max_length=50, blank=True)

    stress_level = models.IntegerField(default=3)

    wellness_activities = models.JSONField(default=list)

    mood_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )

    notes = models.TextField(blank=True)
    chatbot_interactions = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.log_date}"


# ---------------- RECOMMENDATION HISTORY ----------------
class RecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendation_history')

    recommendation_type = models.CharField(max_length=50)
    recommendation_text = models.TextField()

    emotion_trigger = models.CharField(max_length=50)

    was_helpful = models.BooleanField(null=True, blank=True)
    was_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recommendation_type} - {self.user.username}"


# ---------------- EMERGENCY ALERT ----------------
class EmergencyAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_alerts')

    alert_level = models.CharField(max_length=20, default='medium')
    trigger_emotion = models.CharField(max_length=50)
    stress_score = models.FloatField()

    alert_message = models.TextField()

    was_acknowledged = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    resolved_at = models.DateTimeField(blank=True, null=True)

    def resolve(self):
        self.was_acknowledged = True
        self.resolved_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.alert_level} - {self.user.username}"


# ---------------- WELLNESS TIP ----------------
class WellnessTip(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    emotion_category = models.CharField(max_length=50)
    tip_type = models.CharField(max_length=50)

    duration_minutes = models.IntegerField(default=5)
    difficulty_level = models.CharField(max_length=20, default='easy')

    is_active = models.BooleanField(default=True)

    usage_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    # FIXED SAFE INCREMENT (NO TYPE ERROR)
    def increment_usage(self):
        self.usage_count = (self.usage_count or 0) + 1
        self.save()

    def mark_helpful(self):
        self.helpful_count = (self.helpful_count or 0) + 1
        self.save()

    def __str__(self):
        return self.title