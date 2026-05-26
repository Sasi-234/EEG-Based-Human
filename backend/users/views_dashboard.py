"""
Unified Dashboard Views
Combines EEG and Face Emotion Recognition data
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta

from eeg_processing.models import EEGUpload, EmotionPrediction
from face_emotion.models import FaceEmotionPrediction, FaceDetectionSession


@login_required
def unified_dashboard(request):
    """
    Main unified dashboard view showing both EEG and Face emotions
    """
    context = {
        'page_title': 'Unified Emotion Dashboard',
        'active_page': 'unified_dashboard',
    }
    return render(request, 'unified_dashboard.html', context)


@login_required
def api_unified_statistics(request):
    """
    API endpoint for unified statistics
    Returns combined data from EEG and Face predictions
    """
    try:
        # Get user's predictions
        eeg_predictions = EmotionPrediction.objects.filter(
            upload__user=request.user
        )
        face_predictions = FaceEmotionPrediction.objects.filter(
            user=request.user
        )
        
        # Calculate statistics
        total_eeg = eeg_predictions.count()
        total_face = face_predictions.count()
        total_predictions = total_eeg + total_face
        
        # Average confidence
        eeg_avg_conf = eeg_predictions.aggregate(
            Avg('confidence_score')
        )['confidence_score__avg'] or 0
        
        face_avg_conf = face_predictions.aggregate(
            Avg('confidence_score')
        )['confidence_score__avg'] or 0
        
        overall_avg_conf = (
            (eeg_avg_conf * total_eeg + face_avg_conf * total_face) / 
            max(total_predictions, 1)
        )
        
        # Emotion distribution
        eeg_emotions = {}
        for emotion in ['happy', 'sad', 'angry', 'fear', 'neutral', 'surprise', 'stress', 'relaxed', 'excited', 'calm']:
            count = eeg_predictions.filter(predicted_emotion=emotion).count()
            if count > 0:
                eeg_emotions[emotion] = count
        
        face_emotions = {}
        for emotion in ['happy', 'sad', 'angry', 'fear', 'neutral', 'surprise', 'stress', 'relaxed']:
            count = face_predictions.filter(predicted_emotion=emotion).count()
            if count > 0:
                face_emotions[emotion] = count
        
        # Recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_eeg = eeg_predictions.filter(
            prediction_date__gte=yesterday
        ).count()
        recent_face = face_predictions.filter(
            prediction_date__gte=yesterday
        ).count()
        
        # Agreement rate (when both systems have predictions)
        # This is a simplified calculation
        agreement_count = 0
        total_comparisons = 0
        
        # Get latest predictions from each system
        latest_eeg = eeg_predictions.order_by('-prediction_date').first()
        latest_face = face_predictions.order_by('-prediction_date').first()
        
        if latest_eeg and latest_face:
            total_comparisons = 1
            if latest_eeg.predicted_emotion == latest_face.predicted_emotion:
                agreement_count = 1
        
        agreement_rate = (agreement_count / max(total_comparisons, 1)) * 100
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total_predictions': total_predictions,
                'eeg_predictions': total_eeg,
                'face_predictions': total_face,
                'average_confidence': overall_avg_conf,
                'eeg_avg_confidence': eeg_avg_conf,
                'face_avg_confidence': face_avg_conf,
                'recent_activity_24h': {
                    'eeg': recent_eeg,
                    'face': recent_face,
                    'total': recent_eeg + recent_face
                },
                'agreement_rate': agreement_rate,
                'emotion_distribution': {
                    'eeg': eeg_emotions,
                    'face': face_emotions
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_latest_predictions(request):
    """
    API endpoint to get latest predictions from both systems
    """
    try:
        # Get latest EEG prediction
        latest_eeg = EmotionPrediction.objects.filter(
            upload__user=request.user
        ).order_by('-prediction_date').first()
        
        eeg_data = None
        if latest_eeg:
            eeg_data = {
                'emotion': latest_eeg.predicted_emotion,
                'confidence': float(latest_eeg.confidence_score),
                'timestamp': latest_eeg.prediction_date.isoformat(),
                'model_type': latest_eeg.model_type
            }
        
        # Get latest Face prediction
        latest_face = FaceEmotionPrediction.objects.filter(
            user=request.user
        ).order_by('-prediction_date').first()
        
        face_data = None
        if latest_face:
            face_data = {
                'emotion': latest_face.predicted_emotion,
                'confidence': float(latest_face.confidence_score),
                'timestamp': latest_face.prediction_date.isoformat(),
                'detection_method': latest_face.detection_method
            }
        
        return JsonResponse({
            'success': True,
            'eeg': eeg_data,
            'face': face_data,
            'agreement': (
                eeg_data and face_data and 
                eeg_data['emotion'] == face_data['emotion']
            )
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_emotion_timeline(request):
    """
    API endpoint for emotion timeline data
    Returns recent predictions from both systems
    """
    try:
        # Get time range (default: last 7 days)
        days = int(request.GET.get('days', 7))
        start_date = datetime.now() - timedelta(days=days)
        
        # Get EEG predictions
        eeg_predictions = EmotionPrediction.objects.filter(
            upload__user=request.user,
            prediction_date__gte=start_date
        ).order_by('prediction_date').values(
            'predicted_emotion',
            'confidence_score',
            'prediction_date'
        )
        
        # Get Face predictions
        face_predictions = FaceEmotionPrediction.objects.filter(
            user=request.user,
            prediction_date__gte=start_date
        ).order_by('prediction_date').values(
            'predicted_emotion',
            'confidence_score',
            'prediction_date'
        )
        
        # Format data
        eeg_timeline = [{
            'emotion': p['predicted_emotion'],
            'confidence': float(p['confidence_score']),
            'timestamp': p['prediction_date'].isoformat(),
            'type': 'eeg'
        } for p in eeg_predictions]
        
        face_timeline = [{
            'emotion': p['predicted_emotion'],
            'confidence': float(p['confidence_score']),
            'timestamp': p['prediction_date'].isoformat(),
            'type': 'face'
        } for p in face_predictions]
        
        # Combine and sort
        combined_timeline = eeg_timeline + face_timeline
        combined_timeline.sort(key=lambda x: x['timestamp'])
        
        return JsonResponse({
            'success': True,
            'timeline': combined_timeline,
            'eeg_count': len(eeg_timeline),
            'face_count': len(face_timeline),
            'total_count': len(combined_timeline)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Made with Bob
