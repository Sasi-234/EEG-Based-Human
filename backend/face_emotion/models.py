from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
import os


class FaceEmotionPrediction(models.Model):
    """
    Model for storing facial emotion predictions
    """
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('fear', 'Fear'),
        ('neutral', 'Neutral'),
        ('surprise', 'Surprise'),
        ('stress', 'Stress'),
        ('relaxed', 'Relaxed'),
    ]
    
    METHOD_CHOICES = [
        ('webcam', 'Webcam Capture'),
        ('upload', 'Image Upload'),
        ('realtime', 'Real-time Detection'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='face_predictions',
        help_text="User who made the prediction"
    )
    image = models.ImageField(
        upload_to='face_emotions/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp'])],
        help_text="Captured or uploaded face image"
    )
    predicted_emotion = models.CharField(
        max_length=20,
        choices=EMOTION_CHOICES,
        help_text="Predicted emotion from facial expression"
    )
    confidence_score = models.FloatField(
        help_text="Confidence score of the prediction (0-1)"
    )
    detection_method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default='upload',
        help_text="Method used for detection"
    )
    face_detected = models.BooleanField(
        default=True,
        help_text="Whether a face was detected in the image"
    )
    face_coordinates = models.JSONField(
        null=True,
        blank=True,
        help_text="Face bounding box coordinates (x, y, width, height)"
    )
    all_probabilities = models.JSONField(
        null=True,
        blank=True,
        help_text="Probability scores for all emotions"
    )
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken to process in seconds"
    )
    prediction_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of prediction"
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional notes about the prediction"
    )
    
    class Meta:
        db_table = 'face_emotion_predictions'
        verbose_name = 'Face Emotion Prediction'
        verbose_name_plural = 'Face Emotion Predictions'
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['user', '-prediction_date']),
            models.Index(fields=['predicted_emotion']),
            models.Index(fields=['detection_method']),
        ]
    
    def __str__(self):
        return f"{self.predicted_emotion} ({self.confidence_score:.2%}) - {self.user.username}"
    
    @property
    def confidence_percentage(self):
        """Return confidence as percentage"""
        return self.confidence_score * 100
    
    def get_emotion_emoji(self):
        """Return emoji for the emotion"""
        emotion_emojis = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'fear': '😨',
            'neutral': '😐',
            'surprise': '😲',
            'stress': '😰',
            'relaxed': '😌',
        }
        return emotion_emojis.get(self.predicted_emotion, '😐')
    
    def get_emotion_color(self):
        """Return color code for emotion visualization"""
        emotion_colors = {
            'happy': '#FFD700',      # Gold
            'sad': '#4169E1',        # Royal Blue
            'angry': '#DC143C',      # Crimson
            'fear': '#9370DB',       # Medium Purple
            'neutral': '#808080',    # Gray
            'surprise': '#FF69B4',   # Hot Pink
            'stress': '#FF4500',     # Orange Red
            'relaxed': '#32CD32',    # Lime Green
        }
        return emotion_colors.get(self.predicted_emotion, '#808080')
    
    def delete(self, *args, **kwargs):
        """Override delete to remove image from storage"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


class FaceDetectionSession(models.Model):
    """
    Model for tracking real-time face detection sessions
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='face_sessions',
        help_text="User who started the session"
    )
    session_start = models.DateTimeField(
        auto_now_add=True,
        help_text="Session start time"
    )
    session_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Session end time"
    )
    total_frames = models.IntegerField(
        default=0,
        help_text="Total frames processed"
    )
    faces_detected = models.IntegerField(
        default=0,
        help_text="Number of frames with faces detected"
    )
    dominant_emotion = models.CharField(
        max_length=20,
        blank=True,
        help_text="Most frequent emotion in session"
    )
    emotion_distribution = models.JSONField(
        null=True,
        blank=True,
        help_text="Distribution of emotions throughout session"
    )
    average_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Average confidence score"
    )
    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Session duration in seconds"
    )
    
    class Meta:
        db_table = 'face_detection_sessions'
        verbose_name = 'Face Detection Session'
        verbose_name_plural = 'Face Detection Sessions'
        ordering = ['-session_start']
        indexes = [
            models.Index(fields=['user', '-session_start']),
        ]
    
    def __str__(self):
        return f"Session {self.id} - {self.user.username} ({self.session_start.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def is_active(self):
        """Check if session is still active"""
        return self.session_end is None
    
    def calculate_duration(self):
        """Calculate session duration"""
        if self.session_end and self.session_start:
            delta = self.session_end - self.session_start
            self.duration_seconds = delta.total_seconds()
            self.save()

# Made with Bob
