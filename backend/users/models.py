from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Extended User model with additional fields for EEG Emotion Recognition System
    """
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="User profile picture"
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="User biography"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="Contact phone number"
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Date of birth"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def total_uploads(self):
        """Return total number of EEG uploads"""
        return self.eeg_uploads.count()
    
    @property
    def total_predictions(self):
        """Return total number of predictions"""
        return self.predictions.count()


class UserActivityLog(models.Model):
    """
    Model for tracking user activities in the system
    """
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('upload', 'File Upload'),
        ('prediction', 'Emotion Prediction'),
        ('download', 'Report Download'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text="User who performed the activity"
    )
    activity_type = models.CharField(
        max_length=100,
        choices=ACTIVITY_TYPES,
        help_text="Type of activity"
    )
    description = models.TextField(
        help_text="Detailed description of the activity"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the activity occurred"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text="Browser user agent"
    )
    
    class Meta:
        db_table = 'user_activity_logs'
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

# Made with Bob
