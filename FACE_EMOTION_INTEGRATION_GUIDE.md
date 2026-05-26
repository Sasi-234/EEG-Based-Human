# Face Emotion Recognition Module - Integration Guide

## Overview
This guide provides step-by-step instructions to integrate the Face Emotion Recognition module into your existing EEG-based emotion recognition system.

---

## 📋 Prerequisites

### System Requirements
- Python 3.11.9 (already installed)
- Django 4.2.7 (already installed)
- TensorFlow 2.15.0 (already installed)
- Virtual environment: `venv311`

### New Dependencies Required
```bash
opencv-python==4.8.1.78
opencv-contrib-python==4.8.1.78
Pillow==10.1.0
```

---

## 🚀 Integration Steps

### Step 1: Install OpenCV Dependencies

Open PowerShell in your project directory and activate the virtual environment:

```powershell
# Activate virtual environment
.\venv311\Scripts\Activate.ps1

# Install OpenCV
pip install opencv-python==4.8.1.78
pip install opencv-contrib-python==4.8.1.78
pip install Pillow==10.1.0

# Verify installation
python -c "import cv2; print(cv2.__version__)"
```

**Expected Output**: `4.8.1`

---

### Step 2: Update Django Settings

Edit `backend/config/settings.py` and add the face_emotion app to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Existing apps
    'users',
    'eeg_processing',
    'ml_models',
    'recommendations',
    
    # NEW: Face Emotion Recognition
    'face_emotion',
]
```

**Location**: Line 40-50 in `backend/config/settings.py`

---

### Step 3: Update URL Configuration

Edit `backend/config/urls.py` and include the face_emotion URLs:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('eeg/', include('eeg_processing.urls')),
    path('ml/', include('ml_models.urls')),
    path('recommendations/', include('recommendations.urls')),
    
    # NEW: Face Emotion Recognition
    path('face-emotion/', include('face_emotion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Location**: Around line 20-35 in `backend/config/urls.py`

---

### Step 4: Run Database Migrations

Create and apply migrations for the new face_emotion models:

```powershell
# Navigate to backend directory
cd backend

# Create migrations
python manage.py makemigrations face_emotion

# Apply migrations
python manage.py migrate

# Verify tables created
python manage.py dbshell
.tables
.exit
```

**Expected Output**:
```
Migrations for 'face_emotion':
  face_emotion\migrations\0001_initial.py
    - Create model FaceEmotionPrediction
    - Create model FaceDetectionSession
Operations to perform:
  Apply all migrations: face_emotion
Running migrations:
  Applying face_emotion.0001_initial... OK
```

---

### Step 5: Update Navigation Menu

Edit `backend/templates/base.html` to add Face Emotion links to the navigation:

Find the navigation section (around line 50-100) and add:

```html
<!-- Existing navigation items -->
<li class="nav-item">
    <a class="nav-link" href="{% url 'eeg:upload' %}">
        <i class="fas fa-brain"></i> EEG Upload
    </a>
</li>

<!-- NEW: Face Emotion Navigation -->
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="faceEmotionDropdown" 
       role="button" data-bs-toggle="dropdown" aria-expanded="false">
        <i class="fas fa-smile"></i> Face Emotion
    </a>
    <ul class="dropdown-menu" aria-labelledby="faceEmotionDropdown">
        <li>
            <a class="dropdown-item" href="{% url 'face_emotion:webcam_capture' %}">
                <i class="fas fa-video"></i> Webcam Detection
            </a>
        </li>
        <li>
            <a class="dropdown-item" href="{% url 'face_emotion:image_upload' %}">
                <i class="fas fa-upload"></i> Upload Image
            </a>
        </li>
        <li>
            <a class="dropdown-item" href="{% url 'face_emotion:realtime_detection' %}">
                <i class="fas fa-play-circle"></i> Real-time Detection
            </a>
        </li>
        <li><hr class="dropdown-divider"></li>
        <li>
            <a class="dropdown-item" href="{% url 'face_emotion:prediction_history' %}">
                <i class="fas fa-history"></i> History
            </a>
        </li>
        <li>
            <a class="dropdown-item" href="{% url 'face_emotion:session_list' %}">
                <i class="fas fa-list"></i> Sessions
            </a>
        </li>
    </ul>
</li>
```

---

### Step 6: Update Main Dashboard

Edit `backend/templates/dashboard.html` to add a Face Emotion card:

Find the dashboard cards section and add:

```html
<!-- Existing EEG card -->
<div class="col-md-6 col-lg-4 mb-4">
    <div class="card dashboard-card">
        <div class="card-body">
            <h5 class="card-title">
                <i class="fas fa-brain text-primary"></i> EEG Analysis
            </h5>
            <p class="card-text">Upload and analyze EEG signals</p>
            <a href="{% url 'eeg:upload' %}" class="btn btn-primary">
                Go to EEG Module
            </a>
        </div>
    </div>
</div>

<!-- NEW: Face Emotion card -->
<div class="col-md-6 col-lg-4 mb-4">
    <div class="card dashboard-card">
        <div class="card-body">
            <h5 class="card-title">
                <i class="fas fa-smile text-success"></i> Face Emotion
            </h5>
            <p class="card-text">Detect emotions from facial expressions</p>
            <div class="d-grid gap-2">
                <a href="{% url 'face_emotion:webcam_capture' %}" class="btn btn-success">
                    <i class="fas fa-video"></i> Webcam
                </a>
                <a href="{% url 'face_emotion:image_upload' %}" class="btn btn-outline-success">
                    <i class="fas fa-upload"></i> Upload
                </a>
            </div>
        </div>
    </div>
</div>
```

---

### Step 7: Create Model Directory and Download Pre-trained Model

```powershell
# Create models directory
New-Item -ItemType Directory -Force -Path backend\face_emotion\saved_models

# Download Haar Cascade (for face detection)
# This file is included with OpenCV, but we'll copy it to our models directory
python -c "import cv2; import shutil; shutil.copy(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml', 'backend/face_emotion/saved_models/')"
```

**Note**: For the emotion recognition model, you have two options:

**Option A: Use Pre-trained Model** (Recommended for quick start)
- Download a pre-trained FER2013 model
- Place it in `backend/face_emotion/saved_models/face_emotion_model.h5`

**Option B: Train Your Own Model**
- Use the training script (to be created)
- Requires FER2013 dataset
- Takes 2-4 hours on GPU

---

### Step 8: Update Requirements.txt

Add the new dependencies to `requirements.txt`:

```txt
# Existing dependencies
Django==4.2.7
tensorflow==2.15.0
numpy==1.24.3
pandas==2.1.3
scikit-learn==1.3.2
mne==1.5.1

# NEW: Face Emotion Recognition dependencies
opencv-python==4.8.1.78
opencv-contrib-python==4.8.1.78
Pillow==10.1.0
```

---

### Step 9: Test the Integration

#### 9.1 Start the Development Server

```powershell
cd backend
python manage.py runserver
```

#### 9.2 Access the Face Emotion Module

Open your browser and navigate to:
- **Webcam Detection**: http://localhost:8000/face-emotion/webcam/
- **Image Upload**: http://localhost:8000/face-emotion/upload/
- **History**: http://localhost:8000/face-emotion/history/

#### 9.3 Test Webcam Access

1. Click "Start Webcam" button
2. Grant camera permissions when prompted
3. Position your face in the frame
4. Click "Capture & Predict"
5. View the emotion prediction result

---

## 🔧 Configuration Options

### Adjust Capture Interval

Edit `backend/static/js/face_emotion/webcam.js` (line 10):

```javascript
this.captureInterval = options.captureInterval || 2000; // Change to 1000 for 1 second
```

### Change Face Detection Method

Edit `backend/face_emotion/views.py` (line 36):

```python
face_detector = FaceDetector(method='haar')  # Options: 'haar' or 'dnn'
```

**Note**: DNN method is more accurate but slower. Requires additional model files.

---

## 📊 Database Schema

### New Tables Created

#### 1. face_emotion_predictions
Stores individual emotion predictions from webcam or uploaded images.

**Fields**:
- `id`: Primary key
- `user_id`: Foreign key to users
- `image`: Path to captured/uploaded image
- `predicted_emotion`: Detected emotion (happy, sad, angry, etc.)
- `confidence_score`: Prediction confidence (0-1)
- `detection_method`: webcam, upload, or realtime
- `face_detected`: Boolean
- `face_coordinates`: JSON with face bounding box
- `all_probabilities`: JSON with all emotion probabilities
- `processing_time`: Time taken for prediction
- `prediction_date`: Timestamp
- `notes`: Optional user notes

#### 2. face_detection_sessions
Tracks real-time detection sessions.

**Fields**:
- `id`: Primary key
- `user_id`: Foreign key to users
- `session_start`: Session start time
- `session_end`: Session end time
- `total_frames`: Number of frames processed
- `faces_detected`: Number of frames with faces
- `dominant_emotion`: Most frequent emotion
- `emotion_distribution`: JSON with emotion counts
- `average_confidence`: Average confidence score
- `duration_seconds`: Session duration

---

## 🎯 API Endpoints

### Prediction Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/face-emotion/api/predict-webcam/` | POST | Predict from webcam capture |
| `/face-emotion/api/predict-upload/` | POST | Predict from uploaded image |
| `/face-emotion/api/start-session/` | POST | Start detection session |
| `/face-emotion/api/end-session/` | POST | End detection session |
| `/face-emotion/api/update-session/` | POST | Update session statistics |
| `/face-emotion/api/statistics/` | GET | Get user statistics |

### Example API Request (Webcam Prediction)

```javascript
fetch('/face-emotion/api/predict-webcam/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        image: base64ImageData,
        notes: 'Optional notes'
    })
})
.then(response => response.json())
.then(data => {
    console.log('Emotion:', data.emotion);
    console.log('Confidence:', data.confidence);
    console.log('All probabilities:', data.all_probabilities);
});
```

### Example API Response

```json
{
    "success": true,
    "prediction_id": 123,
    "emotion": "happy",
    "confidence": 0.87,
    "all_probabilities": {
        "happy": 0.87,
        "neutral": 0.08,
        "surprise": 0.03,
        "sad": 0.01,
        "angry": 0.01,
        "fear": 0.00,
        "stress": 0.00,
        "relaxed": 0.00
    },
    "face_coordinates": {
        "x": 120,
        "y": 80,
        "w": 200,
        "h": 200
    },
    "processing_time": 0.234,
    "emoji": "😊",
    "color": "#FFD700"
}
```

---

## 🐛 Troubleshooting

### Issue 1: OpenCV Import Error

**Error**: `ImportError: No module named 'cv2'`

**Solution**:
```powershell
pip install opencv-python==4.8.1.78
```

### Issue 2: Webcam Not Accessible

**Error**: "Failed to access webcam"

**Solutions**:
1. Check browser permissions (Chrome: Settings > Privacy > Camera)
2. Ensure no other application is using the webcam
3. Try a different browser (Chrome recommended)
4. Use HTTPS in production (WebRTC requirement)

### Issue 3: No Face Detected

**Error**: "No face detected in image"

**Solutions**:
1. Ensure good lighting
2. Face the camera directly
3. Move closer to the camera
4. Remove obstructions (glasses, masks)

### Issue 4: Model Not Found

**Error**: "Emotion model not available"

**Solution**:
```powershell
# Create default model
cd backend
python manage.py shell
>>> from face_emotion.emotion_model import create_default_model
>>> create_default_model()
>>> exit()
```

### Issue 5: CSRF Token Error

**Error**: "CSRF verification failed"

**Solution**: Ensure CSRF token is included in AJAX requests:
```javascript
const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
```

---

## 📈 Performance Optimization

### 1. Reduce Image Size
Edit `backend/face_emotion/preprocessing.py`:
```python
target_size = (48, 48)  # Smaller = faster
```

### 2. Adjust Capture Interval
Edit `backend/static/js/face_emotion/webcam.js`:
```javascript
this.captureInterval = 3000;  // Increase for slower capture
```

### 3. Use Haar Cascade Instead of DNN
Edit `backend/face_emotion/views.py`:
```python
face_detector = FaceDetector(method='haar')  # Faster than 'dnn'
```

### 4. Enable Model Caching
Models are cached in memory after first load (already implemented).

---

## 🔒 Security Considerations

### 1. Camera Permissions
- Users must explicitly grant camera access
- Permissions are browser-specific
- HTTPS required in production

### 2. Image Storage
- Images are stored in `MEDIA_ROOT/face_emotions/`
- Organized by date: `YYYY/MM/DD/`
- Implement cleanup policy for old images

### 3. API Rate Limiting
Consider adding rate limiting to prevent abuse:
```python
# In settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/hour'
    }
}
```

---

## 📱 Browser Compatibility

### Supported Browsers
- ✅ Chrome 80+ (Recommended)
- ✅ Firefox 75+
- ✅ Edge 80+
- ✅ Safari 13+ (macOS/iOS)
- ❌ Internet Explorer (Not supported)

### WebRTC Requirements
- HTTPS in production
- Camera permissions granted
- Modern browser with WebRTC support

---

## 🎓 Usage Examples

### Example 1: Basic Webcam Detection
```javascript
// Start webcam
await webcamDetector.startWebcam();

// Capture and predict
await webcamDetector.captureAndPredict();

// Stop webcam
webcamDetector.stopWebcam();
```

### Example 2: Auto-Capture Mode
```javascript
// Enable auto-capture
document.getElementById('autoCapture').checked = true;
webcamDetector.autoCapture = true;
webcamDetector.startAutoCapture();
```

### Example 3: Export History
```javascript
// Export emotion history as JSON
webcamDetector.exportHistory();
```

---

## 📚 Additional Resources

### Documentation
- OpenCV Python: https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- WebRTC API: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API
- TensorFlow Keras: https://www.tensorflow.org/guide/keras

### Datasets for Training
- FER2013: https://www.kaggle.com/datasets/msambare/fer2013
- AffectNet: http://mohammadmahoor.com/affectnet/
- RAF-DB: http://www.whdeng.cn/raf/model1.html

---

## ✅ Integration Checklist

Use this checklist to verify successful integration:

- [ ] OpenCV installed and working
- [ ] face_emotion app added to INSTALLED_APPS
- [ ] URLs configured in config/urls.py
- [ ] Database migrations applied
- [ ] Navigation menu updated
- [ ] Dashboard card added
- [ ] Models directory created
- [ ] Haar Cascade file present
- [ ] Development server running
- [ ] Webcam page accessible
- [ ] Camera permissions granted
- [ ] Face detection working
- [ ] Emotion prediction working
- [ ] Results displaying correctly
- [ ] History page working
- [ ] Admin interface accessible

---

## 🎉 Success Indicators

Your integration is successful when:

1. ✅ Webcam page loads without errors
2. ✅ Camera access granted and video displays
3. ✅ Face detection works (green box around face)
4. ✅ Emotion prediction returns results
5. ✅ Confidence scores displayed
6. ✅ Predictions saved to database
7. ✅ History page shows past predictions
8. ✅ Admin interface shows face_emotion models

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review browser console for JavaScript errors
3. Check Django logs for backend errors
4. Verify all dependencies are installed
5. Ensure database migrations are applied

---

**Last Updated**: 2026-05-22  
**Version**: 1.0  
**Status**: Ready for Integration