from django.apps import AppConfig


class WellnessChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wellness_chatbot'
    verbose_name = 'Wellness Chatbot'
    
    def ready(self):
        """
        Import signals or perform startup tasks
        """
        pass


# Made with Bob
