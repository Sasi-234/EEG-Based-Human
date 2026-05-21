"""
URL configuration for EEG Emotion Recognition project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home and About
    path('', user_views.home, name='home'),
    path('about/', user_views.about, name='about'),
    
    # Users app
    path('users/', include('users.urls')),
    
    # EEG Processing
    path('eeg/', include('eeg_processing.urls')),
    
    # API
    path('api/', include('api.urls')),
    
    # Recommendations
    path('recommendations/', include('recommendations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Made with Bob
