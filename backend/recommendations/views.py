"""
Recommendation System Views
Provides personalized recommendations based on detected emotions
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from .models import Recommendation, RecommendationTemplate, UserRecommendationFeedback
from eeg_processing.models import EmotionPrediction
from users.models import UserActivityLog
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(user, activity_type, description, request):
    """Log user activity"""
    UserActivityLog.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
    )


@login_required
def recommendations_dashboard(request):
    """Main recommendations dashboard"""
    # Get user's recent predictions
    recent_predictions = EmotionPrediction.objects.filter(
        user=request.user
    ).order_by('-prediction_date')[:10]
    
    # Get active recommendations for user
    active_recommendations = Recommendation.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Get emotion distribution
    emotion_stats = EmotionPrediction.objects.filter(
        user=request.user
    ).values('predicted_emotion').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'recent_predictions': recent_predictions,
        'active_recommendations': active_recommendations,
        'emotion_stats': emotion_stats,
    }
    return render(request, 'recommendations/dashboard.html', context)


@login_required
def get_recommendations(request, prediction_id):
    """Get recommendations for a specific prediction"""
    prediction = get_object_or_404(EmotionPrediction, id=prediction_id, user=request.user)
    
    # Get or create recommendations based on emotion
    recommendations = Recommendation.objects.filter(
        user=request.user,
        prediction=prediction
    )
    
    if not recommendations.exists():
        # Generate recommendations based on emotion
        recommendations = generate_recommendations_for_emotion(
            request.user,
            prediction
        )
    
    context = {
        'prediction': prediction,
        'recommendations': recommendations,
    }
    return render(request, 'recommendations/list.html', context)


def generate_recommendations_for_emotion(user, prediction):
    """Generate recommendations based on detected emotion"""
    emotion = prediction.predicted_emotion
    
    # Get recommendation templates for this emotion
    templates = RecommendationTemplate.objects.filter(
        emotion=emotion,
        is_active=True
    ).order_by('-priority')
    
    recommendations = []
    for template in templates:
        recommendation = Recommendation.objects.create(
            user=user,
            prediction=prediction,
            recommendation_type=template.recommendation_type,
            title=template.title,
            description=template.description,
            priority=template.priority,
            is_active=True
        )
        recommendations.append(recommendation)
    
    logger.info(f"Generated {len(recommendations)} recommendations for {emotion}")
    return recommendations


@login_required
def recommendation_detail(request, recommendation_id):
    """View recommendation details"""
    recommendation = get_object_or_404(
        Recommendation,
        id=recommendation_id,
        user=request.user
    )
    
    # Mark as viewed
    if not recommendation.viewed_at:
        recommendation.mark_as_viewed()
    
    context = {
        'recommendation': recommendation,
    }
    return render(request, 'recommendations/detail.html', context)


@login_required
def submit_feedback(request, recommendation_id):
    """Submit feedback for a recommendation"""
    if request.method == 'POST':
        recommendation = get_object_or_404(
            Recommendation,
            id=recommendation_id,
            user=request.user
        )
        
        rating = request.POST.get('rating')
        helpful = request.POST.get('helpful') == 'yes'
        comments = request.POST.get('comments', '')
        
        # Create or update feedback
        feedback, created = UserRecommendationFeedback.objects.get_or_create(
            user=request.user,
            recommendation=recommendation,
            defaults={
                'rating': int(rating) if rating else None,
                'helpful': helpful,
                'comments': comments
            }
        )
        
        if not created:
            feedback.rating = int(rating) if rating else None
            feedback.helpful = helpful
            feedback.comments = comments
            feedback.save()
        
        # Log activity
        log_activity(
            request.user,
            'feedback',
            f'Submitted feedback for recommendation: {recommendation.title}',
            request
        )
        
        messages.success(request, 'Thank you for your feedback!')
        return redirect('recommendation_detail', recommendation_id=recommendation_id)
    
    return redirect('recommendations_dashboard')


@login_required
def dismiss_recommendation(request, recommendation_id):
    """Dismiss a recommendation"""
    if request.method == 'POST':
        recommendation = get_object_or_404(
            Recommendation,
            id=recommendation_id,
            user=request.user
        )
        
        recommendation.is_active = False
        recommendation.save()
        
        messages.success(request, 'Recommendation dismissed')
        
    return redirect('recommendations_dashboard')


@login_required
def recommendation_history(request):
    """View all recommendations history"""
    recommendations = Recommendation.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Filter by type if provided
    rec_type = request.GET.get('type')
    if rec_type:
        recommendations = recommendations.filter(recommendation_type=rec_type)
    
    # Pagination
    paginator = Paginator(recommendations, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'rec_type': rec_type,
        'recommendation_types': Recommendation.RECOMMENDATION_TYPES,
    }
    return render(request, 'recommendations/history.html', context)


@login_required
def emotion_insights(request):
    """View emotion insights and patterns"""
    # Get emotion distribution
    emotion_distribution = EmotionPrediction.objects.filter(
        user=request.user
    ).values('predicted_emotion').annotate(
        count=Count('id'),
        avg_confidence=Avg('confidence_score')
    ).order_by('-count')
    
    # Get recent trends
    recent_emotions = EmotionPrediction.objects.filter(
        user=request.user
    ).order_by('-prediction_date')[:20]
    
    # Calculate dominant emotion
    if emotion_distribution:
        dominant_emotion = emotion_distribution[0]
    else:
        dominant_emotion = None
    
    context = {
        'emotion_distribution': emotion_distribution,
        'recent_emotions': recent_emotions,
        'dominant_emotion': dominant_emotion,
        'total_predictions': EmotionPrediction.objects.filter(user=request.user).count(),
    }
    return render(request, 'recommendations/insights.html', context)

# Made with Bob
