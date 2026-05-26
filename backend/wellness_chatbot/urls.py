from django.urls import path
from . import views

app_name = 'wellness_chatbot'

urlpatterns = [

    # Dashboard
    path('', views.chatbot_dashboard, name='dashboard'),

    # Chat API endpoints
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/chat-history/', views.get_chat_history, name='chat_history'),
    path('api/clear-history/', views.clear_chat_history, name='clear_history'),

    # Emotion API endpoints
    path('api/latest-emotion/', views.get_latest_emotion, name='latest_emotion'),
    path('api/recommendations/', views.get_recommendations, name='recommendations'),
    path('api/log-activity/', views.log_wellness_activity, name='log_activity'),

    # Wellness API endpoints
    path('api/wellness-score/', views.get_wellness_score, name='wellness_score'),
    path('api/daily-summary/', views.get_daily_summary, name='daily_summary'),
    path('api/emergency-alert/', views.create_emergency_alert, name='emergency_alert'),

    # Pages
    path('history/', views.chat_history_page, name='history'),
    path('tips/', views.wellness_tips_page, name='tips'),
]