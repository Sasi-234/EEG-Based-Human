# Face Emotion Recognition Module - Architecture Plan

## 📋 Module Overview

**Module Name**: Face Emotion Recognition (FER)
**Integration**: Additional feature to existing EEG Emotion Recognition System
**Status**: New Module (Non-intrusive to existing system)

---

## 🎯 Objectives

1. Add real-time facial emotion recognition via webcam
2. Support image upload for emotion detection
3. Detect 8 emotions from facial expressions
4. Integrate seamlessly with existing dashboard
5. Store predictions in database
6. Provide visualization and analytics

---

## 🏗️ Module Architecture

### **1. Module Structure**

```
backend/
├── face_emotion/              # NEW MODULE
│   ├── __init__.py
│   ├── models.py             # Database models
│   ├── views.py              # API endpoints
│   ├── urls.py               # URL routing
│   ├── admin.py              # Admin interface
│   ├── forms.py              # Upload forms
│   ├── face_detector.py      # Face detection logic
│   ├── emotion_model.py      # CNN emotion model
│   ├── preprocessing.py      # Image preprocessing
│   ├── training.py           # Model training
│   └── migrations/
│       └── __init__.py
│
├── templates/
│   └── face_emotion/         # NEW TEMPLATES
│       ├── webcam_capture.html
│       ├── image_upload.html
│       ├── prediction_result.html
│       ├── prediction_list.html
│       └── realtime_detection.html
│
└── static/
    ├── js/
    │   └── face_emotion/     # NEW JS FILES
    │       ├── webcam.js
    │       ├── face_capture.js
    │       └── emotion_display.js
    └── css/
        └── face_emotion.css  # NEW STYLES
```

---

## 📊 Database Schema

### **FaceEmotionPrediction Model**

```python
class FaceEmotionPrediction(models.Model):
    user = ForeignKey(User)
    image = ImageField()
    predicted_emotion = CharField(choices=EMOTION_CHOICES)
    confidence_score = FloatField()
    detection_method = CharField(choices=['webcam', 'upload'])
    face_detected = BooleanField()
    face_coordinates = JSONField()  # x, y, width, height
    all_probabilities = JSONField()  # All 8 emotion probabilities
    processing_time = FloatField()
    prediction_date = DateTimeField(auto_now_add=True)
    
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('fear', 'Fear'),
        ('neutral', 'Neutral'),
        ('surprise', 'Surprise'),
        ('stress', 'Stress'),
        ('relaxed', 'Relaxed'),
    ]
```

---

## 🔧 Technical Components

### **1. Face Detection**

**Technology**: OpenCV with Haar Cascade or DNN

```python
# face_detector.py
- detect_face(image) -> face_coordinates
- extract_face_roi(image, coordinates) -> face_image
- preprocess_face(face_image) -> normalized_face
```

**Features**:
- Real-time face detection
- Multiple face handling
- Face alignment
- Quality validation

### **2. Emotion Recognition Model**

**Architecture**: CNN (Convolutional Neural Network)

```python
# emotion_model.py
Model Architecture:
- Input: 48x48 grayscale face image
- Conv2D(32) -> ReLU -> MaxPool
- Conv2D(64) -> ReLU -> MaxPool
- Conv2D(128) -> ReLU -> MaxPool
- Flatten
- Dense(512) -> Dropout(0.5)
- Dense(8) -> Softmax
- Output: 8 emotion probabilities
```

**Training**:
- Dataset: FER2013 or custom dataset
- Augmentation: Rotation, flip, zoom
- Optimizer: Adam
- Loss: Categorical crossentropy

### **3. Preprocessing Pipeline**

```python
# preprocessing.py
1. Load image (webcam frame or uploaded file)
2. Convert to grayscale
3. Detect face using Haar Cascade
4. Extract face ROI
5. Resize to 48x48
6. Normalize pixel values (0-1)
7. Reshape for model input
```

---

## 🌐 API Endpoints

### **REST API Routes**

```python
# face_emotion/urls.py

urlpatterns = [
    # Webcam capture
    path('webcam/', webcam_capture, name='webcam_capture'),
    path('api/predict-webcam/', predict_from_webcam, name='predict_webcam'),
    
    # Image upload
    path('upload/', image_upload, name='image_upload'),
    path('api/predict-upload/', predict_from_upload, name='predict_upload'),
    
    # Real-time detection
    path('realtime/', realtime_detection, name='realtime_detection'),
    path('api/detect-realtime/', detect_realtime, name='detect_realtime'),
    
    # Results
    path('predictions/', prediction_list, name='prediction_list'),
    path('prediction/<int:pk>/', prediction_detail, name='prediction_detail'),
    
    # Statistics
    path('api/statistics/', face_emotion_statistics, name='statistics'),
]
```

### **API Specifications**

**1. POST /face-emotion/api/predict-webcam/**
```json
Request:
{
    "image": "base64_encoded_image"
}

Response:
{
    "success": true,
    "emotion": "happy",
    "confidence": 0.89,
    "all_probabilities": {
        "happy": 0.89,
        "sad": 0.03,
        "angry": 0.02,
        "fear": 0.01,
        "neutral": 0.02,
        "surprise": 0.01,
        "stress": 0.01,
        "relaxed": 0.01
    },
    "face_detected": true,
    "face_coordinates": {"x": 100, "y": 50, "w": 200, "h": 200},
    "processing_time": 0.15
}
```

**2. POST /face-emotion/api/predict-upload/**
```json
Request: multipart/form-data
- image: file

Response: Same as predict-webcam
```

---

## 🎨 Frontend Components

### **1. Webcam Capture Page**

**Features**:
- Live webcam feed
- Face detection overlay
- Capture button
- Real-time emotion display
- Confidence meter
- Emotion history

**Technologies**:
- WebRTC for camera access
- Canvas for video display
- JavaScript for capture
- AJAX for prediction

### **2. Image Upload Page**

**Features**:
- Drag-and-drop upload
- File validation
- Preview before prediction
- Batch upload support
- Result display

### **3. Real-time Detection Page**

**Features**:
- Continuous face detection
- Live emotion updates
- Emotion timeline graph
- Confidence visualization
- Recording capability

---

## 🔄 Integration with Existing System

### **1. Dashboard Integration**

```python
# Update users/views.py dashboard()
Add face emotion statistics:
- Total face predictions
- Recent face emotions
- Face vs EEG comparison chart
```

### **2. Navigation Menu**

```html
<!-- Add to base.html -->
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="emotionDropdown">
        Emotion Recognition
    </a>
    <div class="dropdown-menu">
        <a class="dropdown-item" href="{% url 'eeg_processing:upload' %}">
            EEG Analysis
        </a>
        <a class="dropdown-item" href="{% url 'face_emotion:webcam_capture' %}">
            Face Webcam
        </a>
        <a class="dropdown-item" href="{% url 'face_emotion:image_upload' %}">
            Face Upload
        </a>
    </div>
</li>
```

### **3. Unified Predictions View**

```python
# Create combined view showing both EEG and Face predictions
def all_predictions(request):
    eeg_predictions = EmotionPrediction.objects.filter(user=request.user)
    face_predictions = FaceEmotionPrediction.objects.filter(user=request.user)
    # Combine and display
```

---

## 📦 Dependencies

### **New Requirements**

```txt
# Add to requirements.txt
opencv-python==4.8.1.78
opencv-contrib-python==4.8.1.78
deepface==0.0.79
mtcnn==0.1.1
```

### **Model Files**

```
backend/face_emotion/models/
├── haarcascade_frontalface_default.xml
├── face_emotion_cnn.h5
└── face_emotion_weights.h5
```

---

## 🎯 Features Implementation

### **Phase 1: Core Functionality**
1. ✅ Database models
2. ✅ Face detection with OpenCV
3. ✅ Basic CNN model
4. ✅ Image upload prediction
5. ✅ Result display

### **Phase 2: Webcam Integration**
1. ✅ WebRTC camera access
2. ✅ Real-time face detection
3. ✅ Frame capture
4. ✅ Live prediction
5. ✅ Emotion overlay

### **Phase 3: Advanced Features**
1. ✅ Continuous detection mode
2. ✅ Emotion timeline
3. ✅ Confidence graphs
4. ✅ Prediction history
5. ✅ Statistics dashboard

### **Phase 4: Integration**
1. ✅ Dashboard integration
2. ✅ Navigation updates
3. ✅ Combined analytics
4. ✅ Admin panel
5. ✅ API documentation

---

## 🔒 Security Considerations

1. **Camera Permissions**: Request user consent
2. **Image Storage**: Secure file handling
3. **Privacy**: Option to delete images
4. **Authentication**: Login required
5. **Rate Limiting**: Prevent API abuse

---

## 📈 Performance Optimization

1. **Model Optimization**:
   - Use TensorFlow Lite for faster inference
   - Model quantization
   - Batch processing

2. **Image Processing**:
   - Resize before upload
   - Compress images
   - Cache face detection results

3. **Real-time Detection**:
   - Frame skipping (process every 3rd frame)
   - Async processing
   - WebSocket for live updates

---

## 🧪 Testing Strategy

### **Unit Tests**
```python
# tests/test_face_emotion.py
- test_face_detection()
- test_emotion_prediction()
- test_image_preprocessing()
- test_api_endpoints()
```

### **Integration Tests**
- Webcam capture flow
- Upload and predict flow
- Dashboard integration
- Database operations

---

## 📊 Success Metrics

1. **Accuracy**: > 70% on test set
2. **Speed**: < 200ms per prediction
3. **Face Detection**: > 95% success rate
4. **User Experience**: Smooth real-time detection
5. **Integration**: Seamless with existing system

---

## 🚀 Deployment Steps

1. Install OpenCV dependencies
2. Download Haar Cascade files
3. Train or download pre-trained model
4. Run migrations
5. Update settings.py
6. Collect static files
7. Test webcam access
8. Deploy to production

---

## 📝 Documentation

1. **User Guide**: How to use face emotion recognition
2. **API Documentation**: Endpoint specifications
3. **Model Documentation**: Architecture and training
4. **Integration Guide**: Adding to existing system

---

## 🎊 Expected Outcomes

### **User Benefits**
- ✅ Dual emotion recognition (EEG + Face)
- ✅ Real-time feedback
- ✅ Easy-to-use interface
- ✅ Comprehensive analytics
- ✅ Historical tracking

### **Technical Benefits**
- ✅ Modular architecture
- ✅ Non-intrusive integration
- ✅ Scalable design
- ✅ Well-documented code
- ✅ Production-ready

---

## 🔄 Future Enhancements

1. Multi-face detection
2. Age and gender detection
3. Emotion intensity measurement
4. Video file upload support
5. Mobile app integration
6. Cloud deployment
7. Real-time collaboration
8. Advanced analytics

---

**This module will provide a complete facial emotion recognition system that complements the existing EEG-based emotion recognition, giving users multiple ways to analyze emotions!**