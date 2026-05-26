from django.contrib import admin
from .models import (
    ChatMessage, WellnessSession, EmotionalWellnessLog,
    RecommendationHistory, EmergencyAlert, WellnessTip
)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_preview', 'is_user_message', 'emotion_context', 'timestamp']
    list_filter = ['is_user_message', 'emotion_context', 'timestamp']
    search_fields = ['user__username', 'message']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'


@admin.register(WellnessSession)
class WellnessSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'session_start', 'session_end', 'dominant_emotion', 'wellness_score', 'is_active']
    list_filter = ['is_active', 'dominant_emotion', 'session_start']
    search_fields = ['user__username', 'session_id']
    date_hierarchy = 'session_start'
    readonly_fields = ['session_start', 'session_end']


@admin.register(EmotionalWellnessLog)
class EmotionalWellnessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'log_date', 'combined_emotion', 'stress_level', 'mood_rating', 'chatbot_interactions']
    list_filter = ['stress_level', 'log_date', 'combined_emotion']
    search_fields = ['user__username']
    date_hierarchy = 'log_date'


@admin.register(RecommendationHistory)
class RecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommendation_type', 'emotion_trigger', 'was_helpful', 'was_completed', 'created_at']
    list_filter = ['recommendation_type', 'emotion_trigger', 'was_helpful', 'was_completed', 'created_at']
    search_fields = ['user__username', 'recommendation_text']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'alert_level', 'trigger_emotion', 'stress_score', 'was_acknowledged', 'created_at']
    list_filter = ['alert_level', 'was_acknowledged', 'created_at']
    search_fields = ['user__username', 'alert_message']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'resolved_at']


@admin.register(WellnessTip)
class WellnessTipAdmin(admin.ModelAdmin):
    list_display = ['title', 'emotion_category', 'tip_type', 'duration_minutes', 'difficulty_level', 'is_active', 'usage_count', 'helpful_count']
    list_filter = ['emotion_category', 'tip_type', 'difficulty_level', 'is_active']
    search_fields = ['title', 'content']
    readonly_fields = ['usage_count', 'helpful_count', 'created_at']


# Made with Bob
