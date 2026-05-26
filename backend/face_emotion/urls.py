"""
URL Configuration for Face Emotion Recognition Module
"""

from django.urls import path
from . import views

app_name = 'face_emotion'

urlpatterns = [
    # Main views
    path('webcam/', views.webcam_capture_view, name='webcam_capture'),
    path('upload/', views.image_upload_view, name='image_upload'),
    path('realtime/', views.realtime_detection_view, name='realtime_detection'),
    path('history/', views.prediction_history_view, name='prediction_history'),
    path('prediction/<int:prediction_id>/', views.prediction_detail_view, name='prediction_detail'),
    path('sessions/', views.session_list_view, name='session_list'),
    path('session/<int:session_id>/', views.session_detail_view, name='session_detail'),
    
    # API endpoints
    path('api/predict-webcam/', views.api_predict_webcam, name='api_predict_webcam'),
    path('api/predict-upload/', views.api_predict_upload, name='api_predict_upload'),
    path('api/start-session/', views.api_start_session, name='api_start_session'),
    path('api/end-session/', views.api_end_session, name='api_end_session'),
    path('api/update-session/', views.api_update_session, name='api_update_session'),
    path('api/statistics/', views.api_get_statistics, name='api_statistics'),
]

# Made with Bob
