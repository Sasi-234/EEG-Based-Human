from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserActivityLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model
    """
    list_display = ['username', 'email', 'full_name', 'is_staff', 'is_active', 'date_joined', 'total_uploads_display', 'total_predictions_display']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'bio', 'date_of_birth', 'profile_picture')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
    )
    
    def full_name(self, obj):
        """Display full name"""
        return obj.get_full_name() or '-'
    full_name.short_description = 'Full Name'
    
    def total_uploads_display(self, obj):
        """Display total uploads count"""
        count = obj.total_uploads
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return count
    total_uploads_display.short_description = 'Uploads'
    
    def total_predictions_display(self, obj):
        """Display total predictions count"""
        count = obj.total_predictions
        if count > 0:
            return format_html('<span style="color: blue; font-weight: bold;">{}</span>', count)
        return count
    total_predictions_display.short_description = 'Predictions'


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """
    Admin interface for UserActivityLog model
    """
    list_display = ['user', 'activity_type', 'description_short', 'timestamp', 'ip_address']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'user__email', 'description', 'ip_address']
    readonly_fields = ['user', 'activity_type', 'description', 'timestamp', 'ip_address', 'user_agent']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    def description_short(self, obj):
        """Display shortened description"""
        if len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description
    description_short.short_description = 'Description'
    
    def has_add_permission(self, request):
        """Disable adding activity logs manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing activity logs"""
        return False


# Customize admin site header and title
admin.site.site_header = 'EEG Emotion Recognition Admin'
admin.site.site_title = 'EEG Admin Portal'
admin.site.index_title = 'Welcome to EEG Emotion Recognition Administration'

# Made with Bob
