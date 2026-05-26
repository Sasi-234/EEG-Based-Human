from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import FaceEmotionPrediction, FaceDetectionSession


@admin.register(FaceEmotionPrediction)
class FaceEmotionPredictionAdmin(admin.ModelAdmin):
    """
    Admin interface for Face Emotion Predictions
    """
    list_display = [
        'id',
        'user_link',
        'emotion_badge',
        'confidence_display',
        'detection_method',
        'face_detected',
        'prediction_date',
        'image_preview',
    ]
    list_filter = [
        'predicted_emotion',
        'detection_method',
        'face_detected',
        'prediction_date',
    ]
    search_fields = [
        'user__username',
        'user__email',
        'predicted_emotion',
        'notes',
    ]
    readonly_fields = [
        'prediction_date',
        'image_preview_large',
        'emotion_badge',
        'confidence_display',
        'processing_time',
        'face_coordinates',
        'all_probabilities',
    ]
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Prediction Details', {
            'fields': (
                'emotion_badge',
                'predicted_emotion',
                'confidence_display',
                'confidence_score',
                'detection_method',
            )
        }),
        ('Image Information', {
            'fields': (
                'image',
                'image_preview_large',
                'face_detected',
                'face_coordinates',
            )
        }),
        ('Technical Details', {
            'fields': (
                'all_probabilities',
                'processing_time',
                'prediction_date',
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'prediction_date'
    ordering = ['-prediction_date']
    list_per_page = 25
    
    def user_link(self, obj):
        """Display user as clickable link"""
        return format_html(
            '<a href="/admin/users/customuser/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = 'User'
    
    def emotion_badge(self, obj):
        """Display emotion with emoji and color"""
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 5px; font-weight: bold;">{} {}</span>',
            obj.get_emotion_color(),
            obj.get_emotion_emoji(),
            obj.predicted_emotion.upper()
        )
    emotion_badge.short_description = 'Emotion'
    
    def confidence_display(self, obj):
        """Display confidence as progress bar"""
        percentage = obj.confidence_percentage
        color = '#28a745' if percentage >= 80 else '#ffc107' if percentage >= 60 else '#dc3545'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 5px;">'
            '<div style="width: {}%; background-color: {}; color: white; text-align: center; '
            'padding: 2px; border-radius: 5px; font-size: 11px;">{:.1f}%</div></div>',
            percentage,
            color,
            percentage
        )
    confidence_display.short_description = 'Confidence'
    
    def image_preview(self, obj):
        """Display small image preview in list"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; '
                'border-radius: 5px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        """Display large image preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; '
                'border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return '-'
    image_preview_large.short_description = 'Image Preview'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to changelist view"""
        extra_context = extra_context or {}
        
        # Calculate statistics
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_predictions=Count('id'),
            avg_confidence=Avg('confidence_score'),
            faces_detected=Count('id', filter=models.Q(face_detected=True)),
        )
        
        # Emotion distribution
        emotion_dist = queryset.values('predicted_emotion').annotate(
            count=Count('id')
        ).order_by('-count')
        
        extra_context['stats'] = stats
        extra_context['emotion_distribution'] = emotion_dist
        
        return super().changelist_view(request, extra_context)


@admin.register(FaceDetectionSession)
class FaceDetectionSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for Face Detection Sessions
    """
    list_display = [
        'id',
        'user_link',
        'session_start',
        'session_end',
        'status_badge',
        'total_frames',
        'faces_detected',
        'dominant_emotion_badge',
        'duration_display',
    ]
    list_filter = [
        'session_start',
        'dominant_emotion',
    ]
    search_fields = [
        'user__username',
        'user__email',
        'dominant_emotion',
    ]
    readonly_fields = [
        'session_start',
        'session_end',
        'duration_seconds',
        'emotion_distribution',
        'average_confidence',
    ]
    fieldsets = (
        ('Session Information', {
            'fields': (
                'user',
                'session_start',
                'session_end',
                'duration_seconds',
            )
        }),
        ('Detection Statistics', {
            'fields': (
                'total_frames',
                'faces_detected',
                'dominant_emotion',
                'average_confidence',
            )
        }),
        ('Emotion Analysis', {
            'fields': ('emotion_distribution',),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'session_start'
    ordering = ['-session_start']
    list_per_page = 25
    
    def user_link(self, obj):
        """Display user as clickable link"""
        return format_html(
            '<a href="/admin/users/customuser/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = 'User'
    
    def status_badge(self, obj):
        """Display session status"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">● ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">● ENDED</span>'
            )
    status_badge.short_description = 'Status'
    
    def dominant_emotion_badge(self, obj):
        """Display dominant emotion with color"""
        if obj.dominant_emotion:
            # Get color for emotion
            emotion_colors = {
                'happy': '#FFD700',
                'sad': '#4169E1',
                'angry': '#DC143C',
                'fear': '#9370DB',
                'neutral': '#808080',
                'surprise': '#FF69B4',
                'stress': '#FF4500',
                'relaxed': '#32CD32',
            }
            color = emotion_colors.get(obj.dominant_emotion, '#808080')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">{}</span>',
                color,
                obj.dominant_emotion.upper()
            )
        return '-'
    dominant_emotion_badge.short_description = 'Dominant Emotion'
    
    def duration_display(self, obj):
        """Display session duration in readable format"""
        if obj.duration_seconds:
            minutes = int(obj.duration_seconds // 60)
            seconds = int(obj.duration_seconds % 60)
            return f"{minutes}m {seconds}s"
        return '-'
    duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related('user')


# Import models for Q object
from django.db import models

# Made with Bob
