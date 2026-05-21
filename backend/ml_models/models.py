from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class ModelTrainingLog(models.Model):
    """
    Model for tracking ML model training sessions
    """
    MODEL_TYPE_CHOICES = [
        ('cnn', 'CNN'),
        ('lstm', 'LSTM'),
        ('hybrid', 'Hybrid'),
    ]
    
    model_name = models.CharField(
        max_length=100,
        help_text="Name of the trained model"
    )
    model_type = models.CharField(
        max_length=50,
        choices=MODEL_TYPE_CHOICES,
        help_text="Type of ML model"
    )
    accuracy = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Model accuracy percentage"
    )
    loss = models.FloatField(
        help_text="Training loss value"
    )
    val_accuracy = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Validation accuracy percentage"
    )
    val_loss = models.FloatField(
        null=True,
        blank=True,
        help_text="Validation loss value"
    )
    epochs = models.IntegerField(
        help_text="Number of training epochs"
    )
    batch_size = models.IntegerField(
        default=32,
        help_text="Batch size used during training"
    )
    learning_rate = models.FloatField(
        default=0.001,
        help_text="Learning rate used"
    )
    training_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of training"
    )
    training_duration = models.FloatField(
        null=True,
        blank=True,
        help_text="Training duration in seconds"
    )
    parameters = models.JSONField(
        help_text="Model hyperparameters and configuration"
    )
    model_path = models.CharField(
        max_length=500,
        help_text="Path to saved model file"
    )
    dataset_info = models.JSONField(
        null=True,
        blank=True,
        help_text="Information about training dataset"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about training"
    )
    
    class Meta:
        db_table = 'model_training_logs'
        verbose_name = 'Model Training Log'
        verbose_name_plural = 'Model Training Logs'
        ordering = ['-training_date']
        indexes = [
            models.Index(fields=['model_type', '-training_date']),
            models.Index(fields=['-accuracy']),
        ]
    
    def __str__(self):
        return f"{self.model_name} - {self.accuracy:.2f}%"
    
    @property
    def is_best_model(self):
        """Check if this is the best model of its type"""
        best = ModelTrainingLog.objects.filter(
            model_type=self.model_type
        ).order_by('-accuracy').first()
        return best and best.id == self.id


class ModelEvaluationMetrics(models.Model):
    """
    Model for storing detailed evaluation metrics
    """
    training_log = models.OneToOneField(
        ModelTrainingLog,
        on_delete=models.CASCADE,
        related_name='evaluation_metrics',
        help_text="Associated training log"
    )
    precision = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Precision score"
    )
    recall = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Recall score"
    )
    f1_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="F1 score"
    )
    confusion_matrix = models.JSONField(
        help_text="Confusion matrix data"
    )
    classification_report = models.JSONField(
        help_text="Detailed classification report"
    )
    roc_auc_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="ROC AUC score"
    )
    per_class_accuracy = models.JSONField(
        null=True,
        blank=True,
        help_text="Accuracy per emotion class"
    )
    
    class Meta:
        db_table = 'model_evaluation_metrics'
        verbose_name = 'Model Evaluation Metrics'
        verbose_name_plural = 'Model Evaluation Metrics'
    
    def __str__(self):
        return f"Metrics for {self.training_log.model_name}"


class ModelVersion(models.Model):
    """
    Model for tracking different versions of ML models
    """
    STATUS_CHOICES = [
        ('development', 'Development'),
        ('testing', 'Testing'),
        ('production', 'Production'),
        ('deprecated', 'Deprecated'),
    ]
    
    model_type = models.CharField(
        max_length=50,
        choices=ModelTrainingLog.MODEL_TYPE_CHOICES,
        help_text="Type of ML model"
    )
    version = models.CharField(
        max_length=20,
        help_text="Version number (e.g., 1.0.0)"
    )
    training_log = models.ForeignKey(
        ModelTrainingLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions',
        help_text="Associated training log"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='development',
        help_text="Current status of this version"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Whether this version is currently active"
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When this version was created"
    )
    deployed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this version was deployed to production"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of changes in this version"
    )
    
    class Meta:
        db_table = 'model_versions'
        verbose_name = 'Model Version'
        verbose_name_plural = 'Model Versions'
        ordering = ['-created_date']
        unique_together = ['model_type', 'version']
    
    def __str__(self):
        return f"{self.model_type} v{self.version}"
    
    def activate(self):
        """Set this version as active and deactivate others"""
        ModelVersion.objects.filter(
            model_type=self.model_type,
            is_active=True
        ).update(is_active=False)
        self.is_active = True
        self.save()

# Made with Bob
