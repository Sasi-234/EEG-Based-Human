from django.urls import path
from . import views
from . import views_dashboard

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('activity-log/', views.activity_log, name='activity_log'),
    
    # Unified Dashboard
    path('unified-dashboard/', views_dashboard.unified_dashboard, name='unified_dashboard'),
    path('api/unified-statistics/', views_dashboard.api_unified_statistics, name='api_unified_statistics'),
    path('api/latest-predictions/', views_dashboard.api_latest_predictions, name='api_latest_predictions'),
    path('api/emotion-timeline/', views_dashboard.api_emotion_timeline, name='api_emotion_timeline'),
]

# Made with Bob
