# Real-time Face Detection with OpenCV - Complete Guide

## Overview
This guide explains how to use the real-time face detection and emotion recognition system using OpenCV and your webcam.

---

## 📋 What Was Created

### Python Script: `realtime_detector.py`
A comprehensive 632-line Python script that provides:
- ✅ Real-time webcam access using OpenCV
- ✅ Face detection using Haar Cascade
- ✅ Emotion recognition using CNN model
- ✅ Live statistics overlay
- ✅ Emotion history visualization
- ✅ Screenshot capture
- ✅ Video recording
- ✅ Django integration support

---

## 🚀 Quick Start

### Method 1: Standalone Mode (Face Detection Only)

```powershell
# Navigate to backend directory
cd backend

# Run the detector
python face_emotion/realtime_detector.py
```

This will:
1. Open your webcam
2. Detect faces in real-time
3. Draw green boxes around detected faces
4. Show FPS and statistics

### Method 2: Django Integration Mode (With Emotion Recognition)

```powershell
# Navigate to backend directory
cd backend

# Run with Django integration
python face_emotion/realtime_detector.py --django
```

This will:
1. Load the emotion recognition model
2. Detect faces AND predict emotions
3. Show emotion labels with confidence scores
4. Track emotion distribution over time

---

## 🎮 Controls

While the detector is running, use these keyboard shortcuts:

| Key | Action |
|-----|--------|
| **SPACE** | Capture screenshot |
| **S** | Toggle statistics overlay |
| **H** | Toggle emotion history graph |
| **R** | Reset statistics |
| **Q** or **ESC** | Quit application |

---

## 🔧 Command Line Options

### Basic Usage
```powershell
python face_emotion/realtime_detector.py [OPTIONS]
```

### Available Options

#### `--camera INDEX`
Select camera device (default: 0)
```powershell
# Use external webcam (camera 1)
python face_emotion/realtime_detector.py --camera 1
```

#### `--django`
Enable Django integration for emotion prediction
```powershell
python face_emotion/realtime_detector.py --django
```

#### `--no-stats`
Hide statistics overlay
```powershell
python face_emotion/realtime_detector.py --no-stats
```

#### `--no-history`
Hide emotion history graph
```powershell
python face_emotion/realtime_detector.py --no-history
```

#### `--save`
Save output video to file
```powershell
python face_emotion/realtime_detector.py --save
```

### Combined Options
```powershell
# Full featured mode with video recording
python face_emotion/realtime_detector.py --django --save

# Minimal mode (no overlays)
python face_emotion/realtime_detector.py --no-stats --no-history

# External camera with Django
python face_emotion/realtime_detector.py --camera 1 --django
```

---

## 📊 Features Explained

### 1. Face Detection
```python
# Uses OpenCV Haar Cascade
faces = detector.detect_faces(frame)

# Parameters:
# - scaleFactor: 1.1 (image pyramid scale)
# - minNeighbors: 5 (detection quality)
# - minSize: (30, 30) (minimum face size)
```

**What it does**:
- Converts frame to grayscale
- Applies Haar Cascade classifier
- Returns bounding boxes for all detected faces
- Draws colored rectangles around faces

### 2. Emotion Recognition
```python
# Predicts emotion from face region
result = detector.predict_emotion(face_gray)

# Returns:
# {
#     'emotion': 'happy',
#     'confidence': 0.87,
#     'all_probabilities': {...}
# }
```

**What it does**:
- Extracts face region from frame
- Resizes to 48x48 pixels
- Normalizes pixel values
- Passes through CNN model
- Returns emotion with confidence

### 3. Statistics Overlay
Shows real-time metrics:
- **FPS**: Frames per second
- **Frames**: Total frames processed
- **Faces Detected**: Total faces found
- **Detection Rate**: Percentage of frames with faces

### 4. Emotion History Graph
Displays:
- Top 5 emotions detected
- Count for each emotion
- Visual bar chart
- Real-time updates

### 5. Screenshot Capture
Press **SPACE** to save current frame:
```
screenshot_20260522_134530.jpg
```

### 6. Video Recording
Use `--save` flag to record session:
```
face_emotion_output_20260522_134530.avi
```

---

## 💻 Code Examples

### Example 1: Basic Face Detection
```python
from face_emotion.realtime_detector import RealtimeFaceEmotionDetector

# Create detector
detector = RealtimeFaceEmotionDetector(camera_index=0)

# Run detection
detector.run(show_stats=True, show_history=False)
```

### Example 2: With Emotion Recognition
```python
# Create detector with Django integration
detector = RealtimeFaceEmotionDetector(
    camera_index=0,
    use_django=True
)

# Run with all features
detector.run(
    show_stats=True,
    show_history=True,
    save_video=True
)
```

### Example 3: Process Single Frame
```python
# Initialize detector
detector = RealtimeFaceEmotionDetector()
detector.start_camera()

# Read frame
ret, frame = detector.cap.read()

# Detect faces
faces = detector.detect_faces(frame)

# Process each face
for (x, y, w, h) in faces:
    face_gray = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
    result = detector.predict_emotion(face_gray)
    print(f"Emotion: {result['emotion']}, Confidence: {result['confidence']}")

# Cleanup
detector.stop_camera()
```

---

## 🎨 Visual Elements

### Face Bounding Box Colors
Each emotion has a unique color:

| Emotion | Color | RGB |
|---------|-------|-----|
| Happy | Gold | (0, 215, 255) |
| Sad | Royal Blue | (255, 105, 65) |
| Angry | Crimson | (60, 20, 220) |
| Fear | Medium Purple | (219, 112, 147) |
| Neutral | Gray | (128, 128, 128) |
| Surprise | Hot Pink | (180, 105, 255) |
| Stress | Orange Red | (0, 69, 255) |
| Relaxed | Lime Green | (50, 205, 50) |

### Display Layout
```
┌─────────────────────────────────────────────────────────┐
│  Statistics          [Video Feed]      Emotion History  │
│  ┌──────────┐       ┌──────────┐      ┌──────────┐     │
│  │ FPS: 30  │       │          │      │ happy: 15│     │
│  │ Frames:  │       │  [Face]  │      │ sad: 5   │     │
│  │ Faces:   │       │          │      │ neutral:3│     │
│  │ Rate:    │       └──────────┘      └──────────┘     │
│  └──────────┘                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 How It Works

### Step-by-Step Process

#### 1. **Initialize Camera**
```python
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

#### 2. **Read Frame**
```python
ret, frame = cap.read()
frame = cv2.flip(frame, 1)  # Mirror effect
```

#### 3. **Detect Faces**
```python
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, 1.1, 5)
```

#### 4. **Process Each Face**
```python
for (x, y, w, h) in faces:
    # Extract face region
    face_gray = gray[y:y+h, x:x+w]
    
    # Predict emotion
    result = predict_emotion(face_gray)
    
    # Draw bounding box
    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
    
    # Draw label
    cv2.putText(frame, label, (x, y-5), font, 0.6, color, 2)
```

#### 5. **Display Frame**
```python
cv2.imshow('Face Emotion Detection', frame)
key = cv2.waitKey(1)
```

#### 6. **Handle Input**
```python
if key == ord('q'):
    break
elif key == ord(' '):
    cv2.imwrite('screenshot.jpg', frame)
```

---

## 📈 Performance Metrics

### Expected Performance
- **FPS**: 20-30 frames per second
- **Detection Latency**: 30-50ms per frame
- **Emotion Prediction**: 100-150ms per face
- **Memory Usage**: ~200-300 MB

### Optimization Tips

#### 1. Reduce Frame Size
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Lower resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
```

#### 2. Skip Frames
```python
frame_skip = 2  # Process every 2nd frame
if frame_count % frame_skip == 0:
    faces = detect_faces(frame)
```

#### 3. Limit Face Processing
```python
# Process only the largest face
if len(faces) > 0:
    largest_face = max(faces, key=lambda f: f[2] * f[3])
    process_face(largest_face)
```

---

## 🐛 Troubleshooting

### Issue 1: Camera Not Opening
**Error**: `Cannot open camera 0`

**Solutions**:
```powershell
# Try different camera index
python face_emotion/realtime_detector.py --camera 1

# Check available cameras
python -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"

# Close other applications using camera
# Restart computer if needed
```

### Issue 2: Low FPS
**Problem**: FPS below 10

**Solutions**:
1. Close other applications
2. Reduce frame size
3. Disable emotion prediction (remove `--django`)
4. Use `--no-stats --no-history` flags

### Issue 3: No Faces Detected
**Problem**: Faces not being detected

**Solutions**:
1. Ensure good lighting
2. Face the camera directly
3. Move closer to camera
4. Check if Haar Cascade loaded successfully

### Issue 4: Emotion Model Not Loading
**Error**: `Error loading emotion model`

**Solutions**:
```powershell
# Ensure Django is set up
cd backend
python manage.py migrate

# Create default model
python manage.py shell
>>> from face_emotion.emotion_model import create_default_model
>>> create_default_model()
>>> exit()
```

### Issue 5: Import Errors
**Error**: `ModuleNotFoundError: No module named 'cv2'`

**Solution**:
```powershell
# Install OpenCV
pip install opencv-python==4.8.1.78

# Verify installation
python -c "import cv2; print(cv2.__version__)"
```

---

## 🔒 Privacy & Security

### Data Handling
- ✅ All processing done locally
- ✅ No data sent to external servers
- ✅ Screenshots saved locally only
- ✅ Video recordings stored on your machine

### Camera Access
- Camera is only active when script is running
- Camera light indicator shows when active
- Press Q or ESC to immediately stop camera

### Saved Files
- Screenshots: `screenshot_YYYYMMDD_HHMMSS.jpg`
- Videos: `face_emotion_output_YYYYMMDD_HHMMSS.avi`
- Location: Current working directory

---

## 📱 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.14+, Linux
- **Python**: 3.11+
- **RAM**: 4 GB
- **Camera**: Any USB or built-in webcam
- **CPU**: Dual-core 2.0 GHz

### Recommended Requirements
- **RAM**: 8 GB
- **CPU**: Quad-core 2.5 GHz
- **GPU**: Optional (for faster emotion prediction)
- **Camera**: 720p or higher

---

## 🎓 Usage Scenarios

### Scenario 1: Testing Face Detection
```powershell
# Quick test without emotion recognition
python face_emotion/realtime_detector.py
```
**Use case**: Verify camera works and faces are detected

### Scenario 2: Emotion Analysis Session
```powershell
# Full featured session with recording
python face_emotion/realtime_detector.py --django --save
```
**Use case**: Record and analyze emotions over time

### Scenario 3: Demo/Presentation
```powershell
# Clean interface for demonstrations
python face_emotion/realtime_detector.py --django --no-stats
```
**Use case**: Show emotion detection without technical details

### Scenario 4: Development/Debugging
```powershell
# All features enabled
python face_emotion/realtime_detector.py --django --save
```
**Use case**: Test and debug the system

---

## 📊 Output Examples

### Console Output
```
✓ Face cascade loaded successfully
✓ Emotion model loaded successfully
✓ Camera 0 opened successfully
  Resolution: 640x480
  FPS: 30

============================================================
Real-time Face Emotion Detection Started
============================================================
Controls:
  SPACE - Capture screenshot
  S     - Toggle statistics
  H     - Toggle history graph
  R     - Reset statistics
  Q/ESC - Quit
============================================================

✓ Screenshot saved: screenshot_20260522_134530.jpg

============================================================
Session Statistics
============================================================
Total Frames: 1250
Faces Detected: 987
Detection Rate: 78.9%
Average FPS: 28.5

Emotion Distribution:
  Happy     :  45 (45.6%)
  Neutral   :  30 (30.4%)
  Surprise  :  12 (12.2%)
  Sad       :   8 ( 8.1%)
  Angry     :   4 ( 4.1%)
============================================================
```

---

## 🔗 Integration with Django

### Using in Django Views
```python
from face_emotion.realtime_detector import RealtimeFaceEmotionDetector

def start_realtime_detection(request):
    detector = RealtimeFaceEmotionDetector(use_django=True)
    detector.run()
    return JsonResponse({'status': 'completed'})
```

### Accessing Emotion History
```python
# Get emotion history
history = detector.emotion_history

# Convert to list
emotions = list(history)

# Count emotions
from collections import Counter
emotion_counts = Counter(emotions)
```

---

## 📚 Additional Resources

### OpenCV Documentation
- Face Detection: https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html
- Video Capture: https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html

### Python Libraries
- OpenCV: https://opencv.org/
- NumPy: https://numpy.org/
- Django: https://www.djangoproject.com/

---

## ✅ Quick Reference

### Installation
```powershell
pip install opencv-python==4.8.1.78
```

### Basic Run
```powershell
python face_emotion/realtime_detector.py
```

### Full Featured Run
```powershell
python face_emotion/realtime_detector.py --django --save
```

### Keyboard Controls
- **SPACE**: Screenshot
- **S**: Toggle stats
- **H**: Toggle history
- **R**: Reset
- **Q/ESC**: Quit

---

**Last Updated**: 2026-05-22  
**Version**: 1.0  
**Status**: Production Ready