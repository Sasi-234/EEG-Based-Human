from django.apps import AppConfig


class FaceEmotionConfig(AppConfig):
    """
    Configuration for Face Emotion Recognition app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'face_emotion'
    verbose_name = 'Face Emotion Recognition'
    
    def ready(self):
        """
        Import signals when app is ready
        """
        pass

# Made with Bob
