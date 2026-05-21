from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
import os

class EEGUpload(models.Model):
    """
    Model for storing EEG file uploads
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eeg_uploads',
        help_text="User who uploaded the file"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    file_path = models.FileField(
        upload_to='eeg_uploads/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'dat', 'edf', 'bdf'])],
        help_text="Path to the uploaded EEG file"
    )
    file_size = models.IntegerField(
        help_text="File size in bytes"
    )
    upload_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of upload"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Processing status"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the EEG data"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if processing failed"
    )
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken to process in seconds"
    )
    
    class Meta:
        db_table = 'eeg_uploads'
        verbose_name = 'EEG Upload'
        verbose_name_plural = 'EEG Uploads'
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['user', '-upload_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.file_name} - {self.user.username}"
    
    def get_file_extension(self):
        """Return the file extension"""
        return os.path.splitext(self.file_name)[1]
    
    @property
    def is_processed(self):
        """Check if file has been processed"""
        return self.status == 'completed'
    
    def delete(self, *args, **kwargs):
        """Override delete to remove file from storage"""
        if self.file_path:
            if os.path.isfile(self.file_path.path):
                os.remove(self.file_path.path)
        super().delete(*args, **kwargs)


class EmotionPrediction(models.Model):
    """
    Model for storing emotion predictions from EEG data
    """
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('relaxed', 'Relaxed'),
        ('stressed', 'Stressed'),
        ('excited', 'Excited'),
    ]
    
    MODEL_CHOICES = [
        ('cnn', 'CNN'),
        ('lstm', 'LSTM'),
        ('hybrid', 'Hybrid'),
    ]
    
    upload = models.ForeignKey(
        EEGUpload,
        on_delete=models.CASCADE,
        related_name='predictions',
        help_text="Associated EEG upload"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='predictions',
        help_text="User who requested the prediction"
    )
    predicted_emotion = models.CharField(
        max_length=50,
        choices=EMOTION_CHOICES,
        help_text="Predicted emotion"
    )
    confidence_score = models.FloatField(
        help_text="Confidence score of the prediction (0-1)"
    )
    model_used = models.CharField(
        max_length=50,
        choices=MODEL_CHOICES,
        help_text="ML model used for prediction"
    )
    prediction_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of prediction"
    )
    valence = models.FloatField(
        null=True,
        blank=True,
        help_text="Valence score (1-9 scale)"
    )
    arousal = models.FloatField(
        null=True,
        blank=True,
        help_text="Arousal score (1-9 scale)"
    )
    dominance = models.FloatField(
        null=True,
        blank=True,
        help_text="Dominance score (1-9 scale)"
    )
    raw_predictions = models.JSONField(
        null=True,
        blank=True,
        help_text="Raw prediction probabilities for all emotions"
    )
    
    class Meta:
        db_table = 'emotion_predictions'
        verbose_name = 'Emotion Prediction'
        verbose_name_plural = 'Emotion Predictions'
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['user', '-prediction_date']),
            models.Index(fields=['predicted_emotion']),
            models.Index(fields=['upload']),
        ]
    
    def __str__(self):
        return f"{self.predicted_emotion} ({self.confidence_score:.2%}) - {self.user.username}"
    
    @property
    def confidence_percentage(self):
        """Return confidence as percentage"""
        return self.confidence_score * 100
    
    def get_emotion_display_color(self):
        """Return color code for emotion visualization"""
        emotion_colors = {
            'happy': '#FFD700',      # Gold
            'sad': '#4169E1',        # Royal Blue
            'angry': '#DC143C',      # Crimson
            'relaxed': '#90EE90',    # Light Green
            'stressed': '#FF6347',   # Tomato
            'excited': '#FF69B4',    # Hot Pink
        }
        return emotion_colors.get(self.predicted_emotion, '#808080')


class PreprocessingLog(models.Model):
    """
    Model for logging EEG preprocessing steps
    """
    upload = models.ForeignKey(
        EEGUpload,
        on_delete=models.CASCADE,
        related_name='preprocessing_logs',
        help_text="Associated EEG upload"
    )
    step_name = models.CharField(
        max_length=100,
        help_text="Name of preprocessing step"
    )
    step_description = models.TextField(
        help_text="Description of what was done"
    )
    parameters = models.JSONField(
        null=True,
        blank=True,
        help_text="Parameters used in this step"
    )
    execution_time = models.FloatField(
        help_text="Time taken for this step in seconds"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When this step was executed"
    )
    success = models.BooleanField(
        default=True,
        help_text="Whether the step completed successfully"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if step failed"
    )
    
    class Meta:
        db_table = 'preprocessing_logs'
        verbose_name = 'Preprocessing Log'
        verbose_name_plural = 'Preprocessing Logs'
        ordering = ['upload', 'timestamp']
    
    def __str__(self):
        return f"{self.step_name} - {self.upload.file_name}"

# Made with Bob
