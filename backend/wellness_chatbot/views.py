from django.shortcuts import render
from django.http import JsonResponse

from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg

from eeg_processing.models import EmotionPrediction
from .models import ChatMessage, RecommendationHistory, EmotionalWellnessLog


# ---------------- DASHBOARD PAGE ----------------
def chatbot_dashboard(request):
    return render(request, "wellness_chatbot/dashboard.html")


def chat_history_page(request):
    return render(request, "wellness_chatbot/history.html")


def wellness_tips_page(request):
    return render(request, "wellness_chatbot/tips.html")


# ---------------- BASIC API PLACEHOLDERS ----------------
def send_message(request):
    return JsonResponse({"message": "send_message working"})


def get_chat_history(request):
    return JsonResponse({"message": "chat_history working"})


def clear_chat_history(request):
    return JsonResponse({"message": "clear_history working"})


def get_latest_emotion(request):
    return JsonResponse({"message": "latest_emotion working"})


def get_recommendations(request):
    return JsonResponse({"message": "recommendations working"})


def log_wellness_activity(request):
    return JsonResponse({"message": "log_activity working"})


def get_wellness_score(request):
    return JsonResponse(calculate_wellness_score(request.user))


def get_daily_summary(request):
    return JsonResponse({"message": "daily_summary working"})


def create_emergency_alert(request):
    return JsonResponse({"message": "emergency_alert working"})


# ---------------- WELLNESS SCORE LOGIC ----------------
def calculate_wellness_score(user):

    score = 50
    factors = []

    week_ago = timezone.now() - timedelta(days=7)

    recent_emotions = EmotionPrediction.objects.filter(
        user=user,
        prediction_date__gte=week_ago
    )

    emotions = [
        str(e.predicted_emotion).strip().lower()
        for e in recent_emotions
    ]

    positive = {"happy", "excited", "relaxed", "joy"}

    positive_count = sum(e in positive for e in emotions)
    total_count = len(emotions)

    if total_count > 0:
        emotion_score = (positive_count / total_count) * 30
        score += emotion_score

        factors.append({
            "name": "Emotional Positivity",
            "score": round(emotion_score, 1),
            "max": 30
        })

    chat_count = ChatMessage.objects.filter(
        user=user,
        timestamp__gte=week_ago,
        is_user_message=True
    ).count()

    score += min((chat_count / 10) * 20, 20)

    completed = RecommendationHistory.objects.filter(
        user=user,
        created_at__gte=week_ago,
        was_completed=True
    ).count()

    score += min((completed / 5) * 20, 20)

    logs = EmotionalWellnessLog.objects.filter(
        user=user,
        log_date__gte=week_ago.date()
    )

    if logs.exists():
        avg_stress = logs.aggregate(Avg("stress_level"))["stress_level__avg"] or 3
        score += ((6 - avg_stress) / 5) * 30

    score = max(0, min(100, score))

    if score >= 80:
        level = "Excellent"
        message = "Your wellness is thriving!"
    elif score >= 60:
        level = "Good"
        message = "You're doing well!"
    elif score >= 40:
        level = "Fair"
        message = "Room for improvement."
    else:
        level = "Needs Attention"
        message = "Let's improve your wellness."

    return {
        "score": round(score, 1),
        "level": level,
        "message": message,
        "factors": factors
    }