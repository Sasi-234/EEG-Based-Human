"""
API Views for EEG Emotion Recognition
Provides REST API endpoints for emotion prediction and data management
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
import numpy as np
import logging
import os
import json

from eeg_processing.models import EEGUpload, EmotionPrediction, PreprocessingLog
from ml_models.models import ModelVersion
from eeg_processing.preprocessing import EEGPreprocessor
from users.models import UserActivityLog

logger = logging.getLogger(__name__)


def log_activity(user, activity_type, description, request):
    """Log user activity"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    UserActivityLog.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=ip,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
    )


@api_view(['POST'])
def predict_emotion(request):
    """
    API endpoint for real-time emotion prediction
    
    POST /api/predict/
    Body: {
        "upload_id": int,
        "model_type": "cnn" or "lstm" (optional)
    }
    """
    try:
        # Check authentication
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get upload ID
        upload_id = request.data.get('upload_id')
        if not upload_id:
            return Response(
                {'error': 'upload_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get upload object
        upload = get_object_or_404(EEGUpload, id=upload_id, user=request.user)
        
        # Update upload status
        upload.status = 'processing'
        upload.save()
        
        try:
            # Preprocess EEG data
            preprocessor = EEGPreprocessor(sampling_rate=128)
            file_path = upload.file_path.path
            
            # Log preprocessing start
            PreprocessingLog.objects.create(
                upload=upload,
                step='preprocessing_start',
                status='processing',
                details={'message': 'Starting EEG signal preprocessing'}
            )
            
            # Run preprocessing pipeline
            preprocessed_data = preprocessor.preprocess_pipeline(file_path)
            
            # Log preprocessing completion
            PreprocessingLog.objects.create(
                upload=upload,
                step='preprocessing_complete',
                status='completed',
                details={
                    'shape': str(preprocessed_data['shape']),
                    'num_segments': preprocessed_data['num_segments']
                }
            )
            
            # Get model type
            model_type = request.data.get('model_type', 'cnn')
            
            # Get active model version
            try:
                model_version = ModelVersion.objects.filter(
                    model_type=model_type,
                    status='active'
                ).latest('created_at')
            except ModelVersion.DoesNotExist:
                return Response(
                    {'error': f'No active {model_type} model found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Load and use model for prediction
            # This is a placeholder - actual model loading would happen here
            # For now, we'll simulate a prediction
            
            # Simulate prediction (replace with actual model prediction)
            emotions = ['happy', 'sad', 'angry', 'relaxed', 'excited', 'stressed']
            predicted_emotion = np.random.choice(emotions)
            confidence_score = np.random.uniform(70, 99)
            
            # Create prediction record
            prediction = EmotionPrediction.objects.create(
                user=request.user,
                upload=upload,
                model_version=model_version,
                predicted_emotion=predicted_emotion,
                confidence_score=confidence_score,
                valence=np.random.uniform(0, 100),
                arousal=np.random.uniform(0, 100),
                processing_time=2.5,
                raw_output=json.dumps({
                    'probabilities': {emotion: float(np.random.uniform(0, 100)) for emotion in emotions}
                })
            )
            
            # Update upload status
            upload.status = 'completed'
            upload.save()
            
            # Log activity
            log_activity(
                request.user,
                'prediction',
                f'Emotion predicted: {predicted_emotion}',
                request
            )
            
            # Return prediction result
            return Response({
                'success': True,
                'prediction_id': prediction.id,
                'emotion': predicted_emotion,
                'confidence': confidence_score,
                'valence': prediction.valence,
                'arousal': prediction.arousal,
                'processing_time': prediction.processing_time,
                'model_type': model_type,
                'model_version': model_version.version
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Update upload status to failed
            upload.status = 'failed'
            upload.error_message = str(e)
            upload.save()
            
            logger.error(f"Prediction error: {str(e)}")
            return Response(
                {'error': f'Prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_prediction(request, prediction_id):
    """
    Get prediction details
    
    GET /api/prediction/<id>/
    """
    try:
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        prediction = get_object_or_404(EmotionPrediction, id=prediction_id, user=request.user)
        
        return Response({
            'id': prediction.id,
            'emotion': prediction.predicted_emotion,
            'confidence': prediction.confidence_score,
            'valence': prediction.valence,
            'arousal': prediction.arousal,
            'prediction_date': prediction.prediction_date.isoformat(),
            'processing_time': prediction.processing_time,
            'upload_id': prediction.upload.id,
            'upload_filename': prediction.upload.file_name,
            'model_type': prediction.model_version.model_type if prediction.model_version else None,
            'model_version': prediction.model_version.version if prediction.model_version else None
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_user_predictions(request):
    """
    Get all predictions for the authenticated user
    
    GET /api/predictions/
    Query params: emotion, limit, offset
    """
    try:
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        predictions = EmotionPrediction.objects.filter(user=request.user).order_by('-prediction_date')
        
        # Filter by emotion if provided
        emotion = request.GET.get('emotion')
        if emotion:
            predictions = predictions.filter(predicted_emotion=emotion)
        
        # Pagination
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        total_count = predictions.count()
        predictions = predictions[offset:offset + limit]
        
        results = [{
            'id': p.id,
            'emotion': p.predicted_emotion,
            'confidence': p.confidence_score,
            'prediction_date': p.prediction_date.isoformat(),
            'upload_id': p.upload.id,
            'upload_filename': p.upload.file_name
        } for p in predictions]
        
        return Response({
            'count': total_count,
            'results': results,
            'limit': limit,
            'offset': offset
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_emotion_statistics(request):
    """
    Get emotion statistics for the authenticated user
    
    GET /api/statistics/
    """
    try:
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        predictions = EmotionPrediction.objects.filter(user=request.user)
        
        # Count by emotion
        emotion_counts = {}
        for emotion_code, emotion_name in EmotionPrediction.EMOTION_CHOICES:
            count = predictions.filter(predicted_emotion=emotion_code).count()
            emotion_counts[emotion_name] = count
        
        # Calculate average confidence
        avg_confidence = predictions.aggregate(
            avg=models.Avg('confidence_score')
        )['avg'] or 0
        
        # Get most common emotion
        most_common = max(emotion_counts.items(), key=lambda x: x[1]) if emotion_counts else ('None', 0)
        
        return Response({
            'total_predictions': predictions.count(),
            'emotion_distribution': emotion_counts,
            'average_confidence': round(avg_confidence, 2),
            'most_common_emotion': most_common[0],
            'most_common_count': most_common[1]
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def batch_predict(request):
    """
    Batch prediction for multiple uploads
    
    POST /api/batch-predict/
    Body: {
        "upload_ids": [1, 2, 3],
        "model_type": "cnn" or "lstm" (optional)
    }
    """
    try:
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        upload_ids = request.data.get('upload_ids', [])
        if not upload_ids:
            return Response(
                {'error': 'upload_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        for upload_id in upload_ids:
            # Call predict_emotion for each upload
            # This is a simplified version - in production, use Celery for async processing
            try:
                upload = EEGUpload.objects.get(id=upload_id, user=request.user)
                # Simulate prediction
                results.append({
                    'upload_id': upload_id,
                    'status': 'success',
                    'message': 'Prediction queued'
                })
            except EEGUpload.DoesNotExist:
                results.append({
                    'upload_id': upload_id,
                    'status': 'error',
                    'message': 'Upload not found'
                })
        
        return Response({
            'success': True,
            'results': results
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Import models for statistics
from django.db import models

# Made with Bob
