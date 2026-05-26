from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
import os


# ---------------- EEG UPLOAD ----------------
class EEGUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eeg_uploads'
    )

    file_name = models.CharField(max_length=255)

    file_path = models.FileField(
        upload_to='eeg_uploads/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'dat', 'edf', 'bdf'])]
    )

    file_size = models.IntegerField()

    upload_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    description = models.TextField(blank=True)

    error_message = models.TextField(blank=True)

    processing_time = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'eeg_uploads'
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.file_name} - {self.user.username}"

    def get_file_extension(self):
        return os.path.splitext(self.file_name)[1]

    @property
    def is_processed(self):
        return self.status == 'completed'

    def delete(self, *args, **kwargs):
        if self.file_path and os.path.isfile(self.file_path.path):
            os.remove(self.file_path.path)
        super().delete(*args, **kwargs)


# ---------------- EMOTION PREDICTION ----------------
class EmotionPrediction(models.Model):
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('relaxed', 'Relaxed'),
        ('stressed', 'Stressed'),
        ('excited', 'Excited'),
        ('neutral', 'Neutral'),
    ]

    MODEL_CHOICES = [
        ('cnn', 'CNN'),
        ('lstm', 'LSTM'),
        ('hybrid', 'Hybrid'),
    ]

    upload = models.ForeignKey(
        EEGUpload,
        on_delete=models.CASCADE,
        related_name='predictions'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eeg_predictions'
    )

    predicted_emotion = models.CharField(max_length=50, choices=EMOTION_CHOICES)

    confidence_score = models.FloatField()

    model_used = models.CharField(max_length=50, choices=MODEL_CHOICES)

    prediction_date = models.DateTimeField(auto_now_add=True)

    valence = models.FloatField(null=True, blank=True)
    arousal = models.FloatField(null=True, blank=True)
    dominance = models.FloatField(null=True, blank=True)

    raw_predictions = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'emotion_predictions'
        ordering = ['-prediction_date']

    def __str__(self):
        return f"{self.predicted_emotion} ({self.confidence_score:.2f})"


# ---------------- PREPROCESSING LOG ----------------
class PreprocessingLog(models.Model):
    upload = models.ForeignKey(
        EEGUpload,
        on_delete=models.CASCADE,
        related_name='preprocessing_logs'
    )

    step_name = models.CharField(max_length=100)

    step_description = models.TextField()

    parameters = models.JSONField(null=True, blank=True)

    execution_time = models.FloatField()

    timestamp = models.DateTimeField(auto_now_add=True)

    success = models.BooleanField(default=True)

    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'preprocessing_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.step_name} - {self.upload.file_name}"