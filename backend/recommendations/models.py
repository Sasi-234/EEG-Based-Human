from django.db import models
from django.conf import settings
from eeg_processing.models import EmotionPrediction

class Recommendation(models.Model):
    """
    Model for storing emotion-based recommendations
    """
    RECOMMENDATION_TYPES = [
        ('activity', 'Activity'),
        ('meditation', 'Meditation'),
        ('music', 'Music'),
        ('exercise', 'Exercise'),
        ('therapy', 'Therapy'),
        ('breathing', 'Breathing Exercise'),
        ('social', 'Social Activity'),
        ('relaxation', 'Relaxation Technique'),
    ]
    
    prediction = models.ForeignKey(
        EmotionPrediction,
        on_delete=models.CASCADE,
        related_name='recommendations',
        help_text="Associated emotion prediction"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations',
        help_text="User receiving the recommendation"
    )
    recommendation_text = models.TextField(
        help_text="Detailed recommendation text"
    )
    recommendation_type = models.CharField(
        max_length=50,
        choices=RECOMMENDATION_TYPES,
        help_text="Type of recommendation"
    )
    priority = models.IntegerField(
        default=1,
        help_text="Priority level (1=low, 5=high)"
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When recommendation was created"
    )
    is_viewed = models.BooleanField(
        default=False,
        help_text="Whether user has viewed this recommendation"
    )
    is_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="User feedback on helpfulness"
    )
    
    class Meta:
        db_table = 'recommendations'
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'
        ordering = ['-priority', '-created_date']
        indexes = [
            models.Index(fields=['user', '-created_date']),
            models.Index(fields=['prediction']),
        ]
    
    def __str__(self):
        return f"{self.recommendation_type} for {self.user.username}"
    
    def mark_as_viewed(self):
        """Mark recommendation as viewed"""
        self.is_viewed = True
        self.save()


class RecommendationTemplate(models.Model):
    """
    Model for storing recommendation templates for different emotions
    """
    emotion = models.CharField(
        max_length=50,
        choices=EmotionPrediction.EMOTION_CHOICES,
        help_text="Target emotion"
    )
    recommendation_type = models.CharField(
        max_length=50,
        choices=Recommendation.RECOMMENDATION_TYPES,
        help_text="Type of recommendation"
    )
    title = models.CharField(
        max_length=200,
        help_text="Recommendation title"
    )
    content = models.TextField(
        help_text="Recommendation content template"
    )
    priority = models.IntegerField(
        default=1,
        help_text="Default priority level"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active"
    )
    created_date = models.DateTimeField(
        auto_now_add=True
    )
    updated_date = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        db_table = 'recommendation_templates'
        verbose_name = 'Recommendation Template'
        verbose_name_plural = 'Recommendation Templates'
        ordering = ['emotion', '-priority']
    
    def __str__(self):
        return f"{self.emotion} - {self.title}"


class UserRecommendationFeedback(models.Model):
    """
    Model for tracking user feedback on recommendations
    """
    RATING_CHOICES = [
        (1, 'Not Helpful'),
        (2, 'Slightly Helpful'),
        (3, 'Moderately Helpful'),
        (4, 'Very Helpful'),
        (5, 'Extremely Helpful'),
    ]
    
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name='feedback',
        help_text="Associated recommendation"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendation_feedback',
        help_text="User providing feedback"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="User rating"
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional feedback comment"
    )
    followed = models.BooleanField(
        default=False,
        help_text="Whether user followed the recommendation"
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When feedback was provided"
    )
    
    class Meta:
        db_table = 'user_recommendation_feedback'
        verbose_name = 'User Recommendation Feedback'
        verbose_name_plural = 'User Recommendation Feedback'
        ordering = ['-created_date']
        unique_together = ['recommendation', 'user']
    
    def __str__(self):
        return f"Feedback from {self.user.username} - Rating: {self.rating}"

# Made with Bob
