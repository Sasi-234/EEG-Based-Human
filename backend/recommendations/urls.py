from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommendations_dashboard, name='recommendations_dashboard'),
    path('prediction/<int:prediction_id>/', views.get_recommendations, name='get_recommendations'),
    path('<int:recommendation_id>/', views.recommendation_detail, name='recommendation_detail'),
    path('<int:recommendation_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('<int:recommendation_id>/dismiss/', views.dismiss_recommendation, name='dismiss_recommendation'),
    path('history/', views.recommendation_history, name='recommendation_history'),
    path('insights/', views.emotion_insights, name='emotion_insights'),
]

# Made with Bob
