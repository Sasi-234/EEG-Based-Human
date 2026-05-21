from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_eeg, name='eeg_upload'),
    path('uploads/', views.eeg_upload_list, name='eeg_upload_list'),
    path('upload/<int:upload_id>/', views.eeg_upload_detail, name='eeg_upload_detail'),
    path('upload/<int:upload_id>/delete/', views.eeg_upload_delete, name='eeg_upload_delete'),
    path('predictions/', views.prediction_list, name='prediction_list'),
    path('prediction/<int:prediction_id>/', views.prediction_detail, name='prediction_detail'),
]

# Made with Bob
