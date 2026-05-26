"""
Views for Face Emotion Recognition Module
Handles webcam capture, image upload, and real-time detection
"""

import os
import json
import time
import base64
from io import BytesIO
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.conf import settings

from .models import FaceEmotionPrediction, FaceDetectionSession
from .forms import FaceImageUploadForm, WebcamCaptureForm, FaceEmotionFilterForm
from .face_detector import FaceDetector, load_image_from_base64
from .emotion_model import load_pretrained_model
from .preprocessing import preprocess_for_model, load_image_from_upload

import cv2
import numpy as np


# Initialize face detector and emotion model (singleton pattern)
face_detector = None
emotion_model = None


def get_face_detector():
    """Get or create face detector instance"""
    global face_detector
    if face_detector is None:
        face_detector = FaceDetector(method='haar')
    return face_detector


def get_emotion_model():
    """Get or create emotion model instance"""
    global emotion_model
    if emotion_model is None:
        try:
            emotion_model = load_pretrained_model()
        except Exception as e:
            print(f"Error loading emotion model: {e}")
            return None
    return emotion_model


@login_required
def webcam_capture_view(request):
    """
    View for webcam capture interface
    """
    context = {
        'page_title': 'Webcam Emotion Detection',
        'active_page': 'face_emotion_webcam',
    }
    return render(request, 'face_emotion/webcam_capture.html', context)


@login_required
def image_upload_view(request):
    """
    View for image upload interface
    """
    if request.method == 'POST':
        form = FaceImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process uploaded image
            image_file = request.FILES['image']
            notes = form.cleaned_data.get('notes', '')
            
            # Redirect to processing
            return redirect('face_emotion:process_upload', image_id=image_file.name)
    else:
        form = FaceImageUploadForm()
    
    context = {
        'form': form,
        'page_title': 'Upload Face Image',
        'active_page': 'face_emotion_upload',
    }
    return render(request, 'face_emotion/image_upload.html', context)


@login_required
def realtime_detection_view(request):
    """
    View for real-time continuous detection
    """
    context = {
        'page_title': 'Real-time Emotion Detection',
        'active_page': 'face_emotion_realtime',
    }
    return render(request, 'face_emotion/realtime_detection.html', context)


@login_required
def prediction_history_view(request):
    """
    View for prediction history with filtering
    """
    # Get filter form
    filter_form = FaceEmotionFilterForm(request.GET)
    
    # Base queryset
    predictions = FaceEmotionPrediction.objects.filter(user=request.user)
    
    # Apply filters
    if filter_form.is_valid():
        emotion = filter_form.cleaned_data.get('emotion')
        method = filter_form.cleaned_data.get('method')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        min_confidence = filter_form.cleaned_data.get('min_confidence')
        
        if emotion:
            predictions = predictions.filter(predicted_emotion=emotion)
        if method:
            predictions = predictions.filter(detection_method=method)
        if date_from:
            predictions = predictions.filter(prediction_date__gte=date_from)
        if date_to:
            predictions = predictions.filter(prediction_date__lte=date_to)
        if min_confidence:
            predictions = predictions.filter(confidence_score__gte=min_confidence)
    
    # Pagination
    paginator = Paginator(predictions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = predictions.aggregate(
        total=Count('id'),
        avg_confidence=Avg('confidence_score'),
    )
    
    # Emotion distribution
    emotion_dist = predictions.values('predicted_emotion').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Calculate additional statistics
    total_predictions = stats['total'] or 0
    avg_confidence = stats['avg_confidence'] or 0
    most_common_emotion = emotion_dist[0]['predicted_emotion'] if emotion_dist else None
    today_count = predictions.filter(prediction_date__date=datetime.now().date()).count()
    
    context = {
        'predictions': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'filter_form': filter_form,
        'total_predictions': total_predictions,
        'avg_confidence': avg_confidence,
        'most_common_emotion': most_common_emotion,
        'today_count': today_count,
        'page_title': 'Prediction History',
        'active_page': 'face_emotion_history',
    }
    return render(request, 'face_emotion/prediction_history.html', context)


@login_required
def prediction_detail_view(request, prediction_id):
    """
    View for individual prediction details
    """
    prediction = get_object_or_404(
        FaceEmotionPrediction,
        id=prediction_id,
        user=request.user
    )
    
    context = {
        'prediction': prediction,
        'page_title': f'Prediction #{prediction.id}',
        'active_page': 'face_emotion_history',
    }
    return render(request, 'face_emotion/prediction_detail.html', context)


@login_required
def session_list_view(request):
    """
    View for detection sessions list
    """
    sessions = FaceDetectionSession.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'sessions': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': 'Detection Sessions',
        'active_page': 'face_emotion_sessions',
    }
    return render(request, 'face_emotion/session_list.html', context)


@login_required
def session_detail_view(request, session_id):
    """
    View for individual session details
    """
    session = get_object_or_404(
        FaceDetectionSession,
        id=session_id,
        user=request.user
    )
    
    context = {
        'session': session,
        'page_title': f'Session #{session.id}',
        'active_page': 'face_emotion_sessions',
    }
    return render(request, 'face_emotion/session_detail.html', context)


# API Endpoints

@login_required
@require_http_methods(["POST"])
def api_predict_webcam(request):
    """
    API endpoint for webcam capture prediction
    Accepts base64 encoded image from webcam
    """
    try:
        # Parse request data
        data = json.loads(request.body)
        image_data = data.get('image')
        notes = data.get('notes', '')
        
        if not image_data:
            return JsonResponse({
                'success': False,
                'error': 'No image data provided'
            }, status=400)
        
        # Start timing
        start_time = time.time()
        
        # Load image from base64
        image = load_image_from_base64(image_data)
        
        if image is None:
            return JsonResponse({
                'success': False,
                'error': 'Invalid image data'
            }, status=400)
        
        # Detect face
        detector = get_face_detector()
        faces = detector.detect_faces(image)
        
        if not faces:
            return JsonResponse({
                'success': False,
                'error': 'No face detected in image',
                'face_detected': False
            })
        
        # Get largest face
        face_box = detector.get_largest_face(faces)
        x, y, w, h = face_box
        
        # Extract and preprocess face
        face_image = detector.extract_face(image, face_box, target_size=(48, 48))
        face_preprocessed = detector.preprocess_for_model(face_image)
        
        # Predict emotion
        model = get_emotion_model()
        if model is None:
            return JsonResponse({
                'success': False,
                'error': 'Emotion model not available'
            }, status=500)
        
        prediction = model.predict(face_preprocessed)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Save image to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'webcam_{timestamp}.jpg'
        filepath = os.path.join('face_emotions', datetime.now().strftime('%Y/%m/%d'), filename)
        
        # Create directory if needed
        full_path = os.path.join(settings.MEDIA_ROOT, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Save image
        cv2.imwrite(full_path, image)
        
        # Save to database
        face_prediction = FaceEmotionPrediction.objects.create(
            user=request.user,
            image=filepath,
            predicted_emotion=prediction['emotion'],
            confidence_score=prediction['confidence'],
            detection_method='webcam',
            face_detected=True,
            face_coordinates={'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
            all_probabilities=prediction['all_probabilities'],
            processing_time=processing_time,
            notes=notes
        )
        
        return JsonResponse({
            'success': True,
            'prediction_id': face_prediction.id,
            'emotion': prediction['emotion'],
            'confidence': prediction['confidence'],
            'all_probabilities': prediction['all_probabilities'],
            'face_coordinates': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
            'processing_time': processing_time,
            'emoji': face_prediction.get_emotion_emoji(),
            'color': face_prediction.get_emotion_color(),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_predict_upload(request):
    """
    API endpoint for uploaded image prediction
    """
    try:
        # Check if file was uploaded
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)
        
        image_file = request.FILES['image']
        notes = request.POST.get('notes', '')
        
        # Start timing
        start_time = time.time()
        
        # Load image
        image = load_image_from_upload(image_file)
        
        if image is None:
            return JsonResponse({
                'success': False,
                'error': 'Invalid image file'
            }, status=400)
        
        # Detect face
        detector = get_face_detector()
        faces = detector.detect_faces(image)
        
        if not faces:
            return JsonResponse({
                'success': False,
                'error': 'No face detected in image',
                'face_detected': False
            })
        
        # Get largest face
        face_box = detector.get_largest_face(faces)
        x, y, w, h = face_box
        
        # Extract and preprocess face
        face_image = detector.extract_face(image, face_box, target_size=(48, 48))
        face_preprocessed = detector.preprocess_for_model(face_image)
        
        # Predict emotion
        model = get_emotion_model()
        if model is None:
            return JsonResponse({
                'success': False,
                'error': 'Emotion model not available'
            }, status=500)
        
        prediction = model.predict(face_preprocessed)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Save to database
        face_prediction = FaceEmotionPrediction.objects.create(
            user=request.user,
            image=image_file,
            predicted_emotion=prediction['emotion'],
            confidence_score=prediction['confidence'],
            detection_method='upload',
            face_detected=True,
            face_coordinates={'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
            all_probabilities=prediction['all_probabilities'],
            processing_time=processing_time,
            notes=notes
        )
        
        return JsonResponse({
            'success': True,
            'prediction_id': face_prediction.id,
            'emotion': prediction['emotion'],
            'confidence': prediction['confidence'],
            'all_probabilities': prediction['all_probabilities'],
            'face_coordinates': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
            'processing_time': processing_time,
            'emoji': face_prediction.get_emotion_emoji(),
            'color': face_prediction.get_emotion_color(),
            'image_url': face_prediction.image.url,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_start_session(request):
    """
    API endpoint to start a new detection session
    """
    try:
        session = FaceDetectionSession.objects.create(
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'session_start': session.session_start.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_end_session(request):
    """
    API endpoint to end a detection session
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'No session_id provided'
            }, status=400)
        
        session = get_object_or_404(
            FaceDetectionSession,
            id=session_id,
            user=request.user
        )
        
        # Update session end time
        session.session_end = datetime.now()
        session.calculate_duration()
        session.save()
        
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'duration_seconds': session.duration_seconds
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_update_session(request):
    """
    API endpoint to update session statistics
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        emotion = data.get('emotion')
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'No session_id provided'
            }, status=400)
        
        session = get_object_or_404(
            FaceDetectionSession,
            id=session_id,
            user=request.user
        )
        
        # Update statistics
        session.total_frames += 1
        if emotion:
            session.faces_detected += 1
            
            # Update emotion distribution
            if session.emotion_distribution is None:
                session.emotion_distribution = {}
            
            emotion_dist = session.emotion_distribution
            emotion_dist[emotion] = emotion_dist.get(emotion, 0) + 1
            session.emotion_distribution = emotion_dist
            
            # Update dominant emotion
            dominant = max(emotion_dist, key=emotion_dist.get)
            session.dominant_emotion = dominant
        
        session.save()
        
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'total_frames': session.total_frames,
            'faces_detected': session.faces_detected
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_get_statistics(request):
    """
    API endpoint to get user's emotion statistics
    """
    try:
        predictions = FaceEmotionPrediction.objects.filter(user=request.user)
        
        # Overall statistics
        total_predictions = predictions.count()
        avg_confidence = predictions.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0
        
        # Emotion distribution
        emotion_dist = {}
        for emotion in ['happy', 'sad', 'angry', 'fear', 'neutral', 'surprise', 'stress', 'relaxed']:
            count = predictions.filter(predicted_emotion=emotion).count()
            emotion_dist[emotion] = count
        
        # Method distribution
        method_dist = {}
        for method in ['webcam', 'upload', 'realtime']:
            count = predictions.filter(detection_method=method).count()
            method_dist[method] = count
        
        return JsonResponse({
            'success': True,
            'total_predictions': total_predictions,
            'average_confidence': float(avg_confidence),
            'emotion_distribution': emotion_dist,
            'method_distribution': method_dist,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Made with Bob
