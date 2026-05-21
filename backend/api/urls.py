from django.urls import path
from . import views

urlpatterns = [
    # Prediction endpoints
    path('predict/', views.predict_emotion, name='api_predict'),
    path('batch-predict/', views.batch_predict, name='api_batch_predict'),
    path('prediction/<int:prediction_id>/', views.get_prediction, name='api_get_prediction'),
    path('predictions/', views.get_user_predictions, name='api_user_predictions'),
    
    # Statistics endpoint
    path('statistics/', views.get_emotion_statistics, name='api_statistics'),
]

# Made with Bob
