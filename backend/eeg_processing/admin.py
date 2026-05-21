from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import EEGUpload, EmotionPrediction, PreprocessingLog


@admin.register(EEGUpload)
class EEGUploadAdmin(admin.ModelAdmin):
    """
    Admin interface for EEG Upload model
    """
    list_display = ['file_name', 'user', 'status_badge', 'file_size_display', 'upload_date', 'processing_time_display', 'predictions_count']
    list_filter = ['status', 'upload_date']
    search_fields = ['file_name', 'user__username', 'user__email', 'description']
    readonly_fields = ['file_name', 'file_size', 'upload_date', 'processing_time']
    ordering = ['-upload_date']
    date_hierarchy = 'upload_date'
    
    fieldsets = (
        ('File Information', {
            'fields': ('user', 'file_name', 'file_path', 'file_size', 'upload_date')
        }),
        ('Processing', {
            'fields': ('status', 'processing_time', 'error_message')
        }),
        ('Additional Info', {
            'fields': ('description',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    file_size_display.short_description = 'File Size'
    
    def processing_time_display(self, obj):
        """Display processing time"""
        if obj.processing_time:
            return f"{obj.processing_time:.2f}s"
        return '-'
    processing_time_display.short_description = 'Processing Time'
    
    def predictions_count(self, obj):
        """Display number of predictions"""
        count = obj.predictions.count()
        if count > 0:
            url = reverse('admin:eeg_processing_emotionprediction_changelist') + f'?upload__id__exact={obj.id}'
            return format_html('<a href="{}">{} predictions</a>', url, count)
        return '0'
    predictions_count.short_description = 'Predictions'


@admin.register(EmotionPrediction)
class EmotionPredictionAdmin(admin.ModelAdmin):
    """
    Admin interface for Emotion Prediction model
    """
    list_display = ['id', 'user', 'predicted_emotion_badge', 'confidence_display', 'model_used', 'prediction_date', 'upload_link']
    list_filter = ['predicted_emotion', 'model_used', 'prediction_date']
    search_fields = ['user__username', 'user__email', 'upload__file_name']
    readonly_fields = ['upload', 'user', 'predicted_emotion', 'confidence_score', 'model_used', 'prediction_date', 'valence', 'arousal', 'dominance', 'raw_predictions']
    ordering = ['-prediction_date']
    date_hierarchy = 'prediction_date'
    
    fieldsets = (
        ('Prediction Information', {
            'fields': ('upload', 'user', 'predicted_emotion', 'confidence_score', 'model_used', 'prediction_date')
        }),
        ('Emotion Metrics', {
            'fields': ('valence', 'arousal', 'dominance')
        }),
        ('Raw Data', {
            'fields': ('raw_predictions',),
            'classes': ('collapse',)
        }),
    )
    
    def predicted_emotion_badge(self, obj):
        """Display emotion with color badge"""
        color = obj.get_emotion_display_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_predicted_emotion_display()
        )
    predicted_emotion_badge.short_description = 'Emotion'
    
    def confidence_display(self, obj):
        """Display confidence as percentage with progress bar"""
        percentage = obj.confidence_percentage
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 60 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; color: white; text-align: center; border-radius: 3px; padding: 2px;">{:.1f}%</div>'
            '</div>',
            percentage, color, percentage
        )
    confidence_display.short_description = 'Confidence'
    
    def upload_link(self, obj):
        """Link to associated upload"""
        url = reverse('admin:eeg_processing_eegupload_change', args=[obj.upload.id])
        return format_html('<a href="{}">{}</a>', url, obj.upload.file_name)
    upload_link.short_description = 'Upload'
    
    def has_add_permission(self, request):
        """Disable manual addition"""
        return False


@admin.register(PreprocessingLog)
class PreprocessingLogAdmin(admin.ModelAdmin):
    """
    Admin interface for Preprocessing Log model
    """
    list_display = ['upload', 'step_name', 'success_badge', 'execution_time_display', 'timestamp']
    list_filter = ['success', 'timestamp', 'step_name']
    search_fields = ['upload__file_name', 'step_name', 'step_description']
    readonly_fields = ['upload', 'step_name', 'step_description', 'parameters', 'execution_time', 'timestamp', 'success', 'error_message']
    ordering = ['upload', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def success_badge(self, obj):
        """Display success status with badge"""
        if obj.success:
            return format_html('<span style="color: green; font-weight: bold;">✓ Success</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Failed</span>')
    success_badge.short_description = 'Status'
    
    def execution_time_display(self, obj):
        """Display execution time"""
        return f"{obj.execution_time:.3f}s"
    execution_time_display.short_description = 'Execution Time'
    
    def has_add_permission(self, request):
        """Disable manual addition"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing"""
        return False

# Made with Bob
