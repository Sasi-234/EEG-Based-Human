from django.contrib import admin
from django.utils.html import format_html
from .models import Recommendation, RecommendationTemplate, UserRecommendationFeedback


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    """
    Admin interface for Recommendation model
    """
    list_display = ['user', 'recommendation_type', 'priority_badge', 'created_date', 'is_viewed_badge', 'is_helpful_badge']
    list_filter = ['recommendation_type', 'priority', 'is_viewed', 'is_helpful', 'created_date']
    search_fields = ['user__username', 'user__email', 'recommendation_text']
    readonly_fields = ['prediction', 'user', 'created_date']
    ordering = ['-priority', '-created_date']
    date_hierarchy = 'created_date'
    
    fieldsets = (
        ('Recommendation Info', {
            'fields': ('prediction', 'user', 'recommendation_type', 'priority')
        }),
        ('Content', {
            'fields': ('recommendation_text',)
        }),
        ('Status', {
            'fields': ('is_viewed', 'is_helpful', 'created_date')
        }),
    )
    
    def priority_badge(self, obj):
        """Display priority with color coding"""
        colors = {1: 'gray', 2: 'blue', 3: 'orange', 4: 'darkorange', 5: 'red'}
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.priority
        )
    priority_badge.short_description = 'Priority'
    
    def is_viewed_badge(self, obj):
        """Display viewed status"""
        if obj.is_viewed:
            return format_html('<span style="color: green;">✓ Viewed</span>')
        return format_html('<span style="color: gray;">Not viewed</span>')
    is_viewed_badge.short_description = 'Viewed'
    
    def is_helpful_badge(self, obj):
        """Display helpful status"""
        if obj.is_helpful is True:
            return format_html('<span style="color: green;">✓ Helpful</span>')
        elif obj.is_helpful is False:
            return format_html('<span style="color: red;">✗ Not helpful</span>')
        return format_html('<span style="color: gray;">No feedback</span>')
    is_helpful_badge.short_description = 'Helpful'


@admin.register(RecommendationTemplate)
class RecommendationTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for Recommendation Template model
    """
    list_display = ['emotion', 'recommendation_type', 'title', 'priority', 'is_active_badge', 'created_date']
    list_filter = ['emotion', 'recommendation_type', 'is_active', 'priority']
    search_fields = ['title', 'content']
    ordering = ['emotion', '-priority']
    date_hierarchy = 'created_date'
    
    fieldsets = (
        ('Template Info', {
            'fields': ('emotion', 'recommendation_type', 'title', 'priority')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_date', 'updated_date')
        }),
    )
    
    readonly_fields = ['created_date', 'updated_date']
    
    def is_active_badge(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_badge.short_description = 'Active'
    
    actions = ['activate_templates', 'deactivate_templates']
    
    def activate_templates(self, request, queryset):
        """Activate selected templates"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} template(s) activated.')
    activate_templates.short_description = 'Activate selected templates'
    
    def deactivate_templates(self, request, queryset):
        """Deactivate selected templates"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} template(s) deactivated.')
    deactivate_templates.short_description = 'Deactivate selected templates'


@admin.register(UserRecommendationFeedback)
class UserRecommendationFeedbackAdmin(admin.ModelAdmin):
    """
    Admin interface for User Recommendation Feedback model
    """
    list_display = ['user', 'recommendation_type', 'rating_display', 'followed_badge', 'created_date']
    list_filter = ['rating', 'followed', 'created_date']
    search_fields = ['user__username', 'user__email', 'comment']
    readonly_fields = ['recommendation', 'user', 'created_date']
    ordering = ['-created_date']
    date_hierarchy = 'created_date'
    
    fieldsets = (
        ('Feedback Info', {
            'fields': ('recommendation', 'user', 'rating', 'followed')
        }),
        ('Comment', {
            'fields': ('comment',)
        }),
        ('Date', {
            'fields': ('created_date',)
        }),
    )
    
    def recommendation_type(self, obj):
        """Display recommendation type"""
        return obj.recommendation.recommendation_type
    recommendation_type.short_description = 'Type'
    
    def rating_display(self, obj):
        """Display rating with stars"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        colors = {1: 'red', 2: 'orange', 3: 'gold', 4: 'lightgreen', 5: 'green'}
        color = colors.get(obj.rating, 'gray')
        return format_html(
            '<span style="color: {}; font-size: 16px;">{}</span> <span style="color: gray;">({}/5)</span>',
            color, stars, obj.rating
        )
    rating_display.short_description = 'Rating'
    
    def followed_badge(self, obj):
        """Display followed status"""
        if obj.followed:
            return format_html('<span style="color: green; font-weight: bold;">✓ Followed</span>')
        return format_html('<span style="color: gray;">Not followed</span>')
    followed_badge.short_description = 'Followed'
    
    def has_add_permission(self, request):
        """Disable manual addition"""
        return False

# Made with Bob
