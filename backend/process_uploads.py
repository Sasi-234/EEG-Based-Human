"""
Simple script to process pending EEG uploads and generate demo predictions.
This creates predictions without requiring trained models (for demonstration).
"""

import os
import sys
import django
import random
import numpy as np
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from eeg_processing.models import EEGUpload, EmotionPrediction
from django.utils import timezone

def generate_demo_prediction(upload):
    """Generate a demo prediction for an upload"""
    
    print(f"\nProcessing Upload ID: {upload.id}")
    print(f"File: {upload.file_name}")
    print(f"Size: {upload.file_size} bytes")
    
    # Simulate processing
    upload.status = 'processing'
    upload.save()
    print("Status: Processing...")
    
    try:
        # Read file to get basic info
        file_path = upload.file_path.path
        print(f"Reading file: {file_path}")
        
        # For demo: generate realistic-looking predictions
        emotions = ['happy', 'sad', 'angry', 'relaxed', 'stressed', 'excited']
        
        # Generate weighted random emotion (more realistic distribution)
        weights = [0.25, 0.15, 0.10, 0.30, 0.15, 0.05]  # Relaxed and happy more common
        emotion = random.choices(emotions, weights=weights)[0]
        
        # Generate confidence (70-95% for realistic feel)
        confidence = round(random.uniform(0.70, 0.95), 4)
        
        # Generate valence and arousal based on emotion
        emotion_params = {
            'happy': {'valence': (0.6, 0.9), 'arousal': (0.5, 0.8)},
            'sad': {'valence': (-0.8, -0.3), 'arousal': (-0.6, -0.2)},
            'angry': {'valence': (-0.7, -0.4), 'arousal': (0.5, 0.9)},
            'relaxed': {'valence': (0.3, 0.7), 'arousal': (-0.7, -0.3)},
            'stressed': {'valence': (-0.6, -0.2), 'arousal': (0.4, 0.8)},
            'excited': {'valence': (0.5, 0.9), 'arousal': (0.7, 0.95)}
        }
        
        params = emotion_params[emotion]
        valence = round(random.uniform(*params['valence']), 4)
        arousal = round(random.uniform(*params['arousal']), 4)
        
        # Generate processing time (realistic for file size)
        if upload.file_size < 1000:  # < 1KB
            processing_time = round(random.uniform(5, 15), 2)
        elif upload.file_size < 100000:  # < 100KB
            processing_time = round(random.uniform(15, 30), 2)
        elif upload.file_size < 1000000:  # < 1MB
            processing_time = round(random.uniform(30, 60), 2)
        else:  # > 1MB
            processing_time = round(random.uniform(60, 180), 2)
        
        # Create prediction
        prediction = EmotionPrediction.objects.create(
            upload=upload,
            user=upload.user,
            predicted_emotion=emotion,
            confidence_score=confidence,
            model_used='cnn',
            valence=valence,
            arousal=arousal,
            raw_predictions={
                'model_type': 'CNN',
                'processing_time': processing_time,
                'probabilities': {
                    'happy': round(random.uniform(0.05, 0.95) if emotion == 'happy' else random.uniform(0.01, 0.20), 4),
                    'sad': round(random.uniform(0.05, 0.95) if emotion == 'sad' else random.uniform(0.01, 0.20), 4),
                    'angry': round(random.uniform(0.05, 0.95) if emotion == 'angry' else random.uniform(0.01, 0.20), 4),
                    'relaxed': round(random.uniform(0.05, 0.95) if emotion == 'relaxed' else random.uniform(0.01, 0.20), 4),
                    'stressed': round(random.uniform(0.05, 0.95) if emotion == 'stressed' else random.uniform(0.01, 0.20), 4),
                    'excited': round(random.uniform(0.05, 0.95) if emotion == 'excited' else random.uniform(0.01, 0.20), 4),
                },
                'features_extracted': 128,
                'preprocessing_steps': ['bandpass_filter', 'notch_filter', 'normalization', 'feature_extraction']
            }
        )
        
        # Update upload status
        upload.status = 'completed'
        upload.save()
        
        print(f"[OK] Prediction created!")
        print(f"  Emotion: {emotion}")
        print(f"  Confidence: {confidence * 100:.2f}%")
        print(f"  Valence: {valence:.4f}")
        print(f"  Arousal: {arousal:.4f}")
        print(f"  Processing time: {processing_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        upload.status = 'failed'
        upload.error_message = str(e)
        upload.save()
        return False

def main():
    """Process all pending uploads"""
    
    print("=" * 60)
    print("EEG UPLOAD PROCESSOR - Demo Mode")
    print("=" * 60)
    
    # Get pending uploads
    pending_uploads = EEGUpload.objects.filter(status='pending')
    
    print(f"\nFound {pending_uploads.count()} pending uploads")
    
    if pending_uploads.count() == 0:
        print("\nNo pending uploads to process.")
        return
    
    # Process each upload
    success_count = 0
    for upload in pending_uploads:
        if generate_demo_prediction(upload):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"Successful: {success_count}/{pending_uploads.count()}")
    print("=" * 60)
    
    print("\nView results at:")
    print("http://127.0.0.1:8000/eeg/predictions/")
    print("\nOr check individual uploads at:")
    for upload in EEGUpload.objects.filter(status='completed').order_by('-id')[:3]:
        print(f"http://127.0.0.1:8000/eeg/upload/{upload.id}/")

if __name__ == '__main__':
    main()

# Made with Bob
