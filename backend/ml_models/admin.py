from django.contrib import admin
from django.utils.html import format_html
from .models import ModelTrainingLog, ModelEvaluationMetrics, ModelVersion


@admin.register(ModelTrainingLog)
class ModelTrainingLogAdmin(admin.ModelAdmin):
    """
    Admin interface for Model Training Log
    """
    list_display = ['model_name', 'model_type', 'accuracy_display', 'loss_display', 'epochs', 'training_date', 'duration_display', 'is_best_badge']
    list_filter = ['model_type', 'training_date']
    search_fields = ['model_name', 'model_path']
    readonly_fields = ['training_date', 'training_duration']
    ordering = ['-training_date']
    date_hierarchy = 'training_date'
    
    fieldsets = (
        ('Model Information', {
            'fields': ('model_name', 'model_type', 'model_path')
        }),
        ('Training Metrics', {
            'fields': ('accuracy', 'loss', 'val_accuracy', 'val_loss', 'epochs', 'batch_size', 'learning_rate')
        }),
        ('Training Details', {
            'fields': ('training_date', 'training_duration', 'parameters', 'dataset_info')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def accuracy_display(self, obj):
        """Display accuracy with color coding"""
        color = 'green' if obj.accuracy >= 85 else 'orange' if obj.accuracy >= 70 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, obj.accuracy
        )
    accuracy_display.short_description = 'Accuracy'
    
    def loss_display(self, obj):
        """Display loss value"""
        return f"{obj.loss:.4f}"
    loss_display.short_description = 'Loss'
    
    def duration_display(self, obj):
        """Display training duration"""
        if obj.training_duration:
            hours = int(obj.training_duration // 3600)
            minutes = int((obj.training_duration % 3600) // 60)
            seconds = int(obj.training_duration % 60)
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            return f"{seconds}s"
        return '-'
    duration_display.short_description = 'Duration'
    
    def is_best_badge(self, obj):
        """Display if this is the best model"""
        if obj.is_best_model:
            return format_html('<span style="color: gold; font-weight: bold;">★ Best</span>')
        return '-'
    is_best_badge.short_description = 'Best Model'


@admin.register(ModelEvaluationMetrics)
class ModelEvaluationMetricsAdmin(admin.ModelAdmin):
    """
    Admin interface for Model Evaluation Metrics
    """
    list_display = ['training_log', 'precision_display', 'recall_display', 'f1_score_display', 'roc_auc_display']
    search_fields = ['training_log__model_name']
    readonly_fields = ['training_log', 'precision', 'recall', 'f1_score', 'confusion_matrix', 'classification_report', 'roc_auc_score', 'per_class_accuracy']
    
    fieldsets = (
        ('Associated Training', {
            'fields': ('training_log',)
        }),
        ('Metrics', {
            'fields': ('precision', 'recall', 'f1_score', 'roc_auc_score')
        }),
        ('Detailed Reports', {
            'fields': ('confusion_matrix', 'classification_report', 'per_class_accuracy'),
            'classes': ('collapse',)
        }),
    )
    
    def precision_display(self, obj):
        """Display precision as percentage"""
        return format_html('<span style="font-weight: bold;">{:.2f}%</span>', obj.precision * 100)
    precision_display.short_description = 'Precision'
    
    def recall_display(self, obj):
        """Display recall as percentage"""
        return format_html('<span style="font-weight: bold;">{:.2f}%</span>', obj.recall * 100)
    recall_display.short_description = 'Recall'
    
    def f1_score_display(self, obj):
        """Display F1 score as percentage"""
        return format_html('<span style="font-weight: bold;">{:.2f}%</span>', obj.f1_score * 100)
    f1_score_display.short_description = 'F1 Score'
    
    def roc_auc_display(self, obj):
        """Display ROC AUC score"""
        if obj.roc_auc_score:
            return format_html('<span style="font-weight: bold;">{:.4f}</span>', obj.roc_auc_score)
        return '-'
    roc_auc_display.short_description = 'ROC AUC'
    
    def has_add_permission(self, request):
        """Disable manual addition"""
        return False


@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    """
    Admin interface for Model Version
    """
    list_display = ['model_type', 'version', 'status_badge', 'is_active_badge', 'created_date', 'deployed_date']
    list_filter = ['model_type', 'status', 'is_active', 'created_date']
    search_fields = ['version', 'description']
    ordering = ['-created_date']
    date_hierarchy = 'created_date'
    
    fieldsets = (
        ('Version Information', {
            'fields': ('model_type', 'version', 'training_log')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Dates', {
            'fields': ('created_date', 'deployed_date')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )
    
    readonly_fields = ['created_date']
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'development': 'gray',
            'testing': 'blue',
            'production': 'green',
            'deprecated': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def is_active_badge(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: gray;">Inactive</span>')
    is_active_badge.short_description = 'Active'
    
    actions = ['activate_version']
    
    def activate_version(self, request, queryset):
        """Action to activate selected version"""
        if queryset.count() != 1:
            self.message_user(request, 'Please select exactly one version to activate.', level='error')
            return
        
        version = queryset.first()
        version.activate()
        self.message_user(request, f'Version {version.version} has been activated.', level='success')
    activate_version.short_description = 'Activate selected version'

# Made with Bob
