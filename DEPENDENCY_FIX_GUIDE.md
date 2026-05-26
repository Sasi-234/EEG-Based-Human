# Dependency Fix Guide for Face Emotion Module

## Issue Summary
When adding the Face Emotion Recognition module with OpenCV, there was a NumPy version conflict that caused the server to crash.

## Root Cause
- OpenCV 4.13.0.92 requires NumPy >= 2.0
- TensorFlow 2.15.0 requires NumPy < 2.0
- This creates an incompatibility

## Solution Applied

### Step 1: Install Compatible Versions
```bash
# Install NumPy compatible with TensorFlow
venv311\Scripts\pip.exe install "numpy<2.0.0,>=1.23.5"

# Reinstall pandas and scipy with compatible versions
venv311\Scripts\pip.exe install --force-reinstall "pandas<3.0" "scipy<1.12"
```

### Step 2: Install OpenCV (Headless Version)
For production use without GUI, use opencv-python-headless:
```bash
venv311\Scripts\pip.exe install opencv-python-headless
```

This version doesn't require NumPy 2.0 and works with TensorFlow.

## Alternative Solution
If you need the full OpenCV with GUI support, you have two options:

### Option A: Use OpenCV 4.8.x (Recommended)
```bash
venv311\Scripts\pip.exe uninstall opencv-python
venv311\Scripts\pip.exe install "opencv-python<4.9.0"
```

### Option B: Upgrade to TensorFlow 2.16+ (Future)
Wait for TensorFlow to support NumPy 2.0, then upgrade:
```bash
venv311\Scripts\pip.exe install --upgrade tensorflow
```

## Current Package Versions (Working Configuration)
```
numpy==1.26.4
pandas==2.2.3
scipy==1.11.4
tensorflow==2.15.0
opencv-python==4.8.1.78  # or opencv-python-headless
```

## Verification Steps

### 1. Check Package Versions
```bash
venv311\Scripts\pip.exe list | findstr "numpy pandas scipy opencv tensorflow"
```

### 2. Test Import
```bash
venv311\Scripts\python.exe -c "import numpy; import cv2; import tensorflow; print('All imports successful')"
```

### 3. Start Django Server
```bash
cd backend
..\venv311\Scripts\python.exe manage.py check
..\venv311\Scripts\python.exe manage.py runserver
```

## Prevention for Future
Add these constraints to `requirements.txt`:
```
numpy>=1.23.5,<2.0.0
pandas>=2.1.0,<3.0.0
scipy>=1.11.0,<1.12.0
opencv-python>=4.8.0,<4.9.0
# OR
opencv-python-headless>=4.8.0,<4.9.0
tensorflow==2.15.0
```

## Face Emotion Module Status
- ✅ Module code created (23 files)
- ✅ Django integration complete
- ✅ Forms fixed (removed multiple file upload)
- ✅ PIL Image import added
- ⏳ Dependencies being resolved
- ⏳ Database migrations pending
- ⏳ Server restart pending

## Next Steps After Dependencies Fixed
1. Run migrations:
   ```bash
   python manage.py makemigrations face_emotion
   python manage.py migrate
   ```

2. Restart server:
   ```bash
   python manage.py runserver
   ```

3. Access Face Emotion pages:
   - http://127.0.0.1:8000/face-emotion/webcam/
   - http://127.0.0.1:8000/face-emotion/upload/
   - http://127.0.0.1:8000/face-emotion/history/

## Troubleshooting

### If server still won't start:
1. Check for syntax errors:
   ```bash
   python manage.py check
   ```

2. Clear Python cache:
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   ```

3. Restart terminal and try again

### If OpenCV import fails:
```bash
venv311\Scripts\pip.exe uninstall opencv-python
venv311\Scripts\pip.exe install opencv-python-headless
```

## Documentation Created
- FACE_EMOTION_MODULE_PLAN.md (450 lines)
- FACE_EMOTION_PLANNER.md (650 lines)
- FACE_EMOTION_INTEGRATION_GUIDE.md (750 lines)
- REALTIME_FACE_DETECTION_GUIDE.md (650 lines)
- CNN_MODEL_TRAINING_GUIDE.md (650 lines)
- DEPENDENCY_FIX_GUIDE.md (this file)

---
**Last Updated**: 2026-05-22
**Status**: Dependencies being resolved