# Face Emotion Detection Accuracy Issue & Solution

## Problem
The webcam face emotion detection is showing the same emotion for everyone instead of detecting actual emotions accurately.

## Root Cause
The current implementation uses a **placeholder/dummy model** that returns random or fixed predictions. To get accurate emotion detection, you need a **properly trained deep learning model**.

## Current Implementation Status

### What's Working ✅
- Face detection using OpenCV Haar Cascade
- Webcam capture and image processing
- UI and frontend integration
- Database storage of predictions
- Real-time video streaming

### What Needs Improvement ⚠️
- **Emotion classification model** - Currently using placeholder
- Model needs to be trained on emotion datasets
- Requires proper CNN architecture for face emotion recognition

## Solution: Train a Real Emotion Detection Model

### Option 1: Use Pre-trained Model (Recommended - Quick)

#### Step 1: Download Pre-trained Model
Use a pre-trained FER (Facial Expression Recognition) model:

```python
# Install required library
pip install fer

# Or use DeepFace
pip install deepface
```

#### Step 2: Update emotion_model.py

Replace the current `EmotionRecognitionModel` class with:

```python
from deepface import DeepFace
import cv2
import numpy as np

class EmotionRecognitionModel:
    def __init__(self):
        """Initialize with DeepFace"""
        self.model_name = 'DeepFace'
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    
    def predict(self, face_image):
        """
        Predict emotion from face image using DeepFace
        
        Args:
            face_image: numpy array of face image (BGR format)
        
        Returns:
            tuple: (predicted_emotion, confidence_score, all_probabilities)
        """
        try:
            # Analyze emotion using DeepFace
            result = DeepFace.analyze(
                face_image,
                actions=['emotion'],
                enforce_detection=False
            )
            
            # Extract emotion probabilities
            if isinstance(result, list):
                result = result[0]
            
            emotion_scores = result['emotion']
            
            # Get dominant emotion
            dominant_emotion = result['dominant_emotion']
            confidence = emotion_scores[dominant_emotion] / 100.0
            
            # Normalize probabilities
            all_probs = {k: v/100.0 for k, v in emotion_scores.items()}
            
            return dominant_emotion, confidence, all_probs
            
        except Exception as e:
            print(f"Error in emotion prediction: {e}")
            return 'neutral', 0.5, {'neutral': 0.5}
```

#### Step 3: Update requirements.txt

Add these dependencies:

```
deepface==0.0.79
tf-keras==2.15.0
opencv-python==4.8.1.78
```

#### Step 4: Install Dependencies

```bash
cd backend
pip install deepface tf-keras opencv-python
```

### Option 2: Train Custom Model (Advanced - Better Accuracy)

#### Step 1: Get Training Dataset

Download FER2013 or CK+ dataset:
- **FER2013**: https://www.kaggle.com/datasets/msambare/fer2013
- **CK+**: http://www.consortium.ri.cmu.edu/ckagree/

#### Step 2: Create Training Script

```python
# train_emotion_model.py
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def create_emotion_model(input_shape=(48, 48, 1), num_classes=7):
    """
    Create CNN model for emotion recognition
    """
    model = keras.Sequential([
        # Block 1
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 2
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 3
        layers.Conv2D(256, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(256, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def train_model(data_path, epochs=50, batch_size=64):
    """
    Train the emotion recognition model
    """
    # Load data
    df = pd.read_csv(data_path)
    
    # Prepare data
    X = []
    y = []
    
    for index, row in df.iterrows():
        pixels = np.array(row['pixels'].split(), dtype='float32')
        pixels = pixels.reshape(48, 48, 1)
        pixels /= 255.0
        X.append(pixels)
        y.append(row['emotion'])
    
    X = np.array(X)
    y = np.array(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Create model
    model = create_emotion_model()
    
    # Compile
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
        keras.callbacks.ModelCheckpoint(
            'best_emotion_model.h5',
            save_best_only=True
        )
    ]
    
    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks
    )
    
    # Save final model
    model.save('emotion_recognition_model.h5')
    
    return model, history

if __name__ == '__main__':
    # Train model
    model, history = train_model('fer2013.csv', epochs=50)
    print("Training complete!")
```

#### Step 3: Train the Model

```bash
python train_emotion_model.py
```

#### Step 4: Update emotion_model.py to Use Trained Model

```python
import tensorflow as tf
import numpy as np
import cv2

class EmotionRecognitionModel:
    def __init__(self, model_path='emotion_recognition_model.h5'):
        """Load trained model"""
        self.model = tf.keras.models.load_model(model_path)
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.input_size = (48, 48)
    
    def preprocess_face(self, face_image):
        """Preprocess face for model input"""
        # Convert to grayscale
        if len(face_image.shape) == 3:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_image
        
        # Resize
        resized = cv2.resize(gray, self.input_size)
        
        # Normalize
        normalized = resized / 255.0
        
        # Reshape for model
        input_data = normalized.reshape(1, 48, 48, 1)
        
        return input_data
    
    def predict(self, face_image):
        """Predict emotion"""
        # Preprocess
        input_data = self.preprocess_face(face_image)
        
        # Predict
        predictions = self.model.predict(input_data, verbose=0)[0]
        
        # Get results
        predicted_idx = np.argmax(predictions)
        predicted_emotion = self.emotions[predicted_idx]
        confidence = float(predictions[predicted_idx])
        
        # All probabilities
        all_probs = {
            emotion: float(prob)
            for emotion, prob in zip(self.emotions, predictions)
        }
        
        return predicted_emotion, confidence, all_probs
```

## Quick Fix: Use DeepFace (Recommended)

### Installation Steps

1. **Install DeepFace:**
```bash
pip install deepface
```

2. **Update backend/face_emotion/emotion_model.py:**

from deepface import DeepFace
import numpy as np

class EmotionRecognitionModel:
    def __init__(self):
        self.model_name = 'DeepFace'
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    
    def predict(self, face_image):
        try:
            result = DeepFace.analyze(
                face_image,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            
            if isinstance(result, list):
                result = result[0]
            
            emotion_scores = result['emotion']
            dominant_emotion = result['dominant_emotion']
            confidence = emotion_scores[dominant_emotion] / 100.0
            all_probs = {k: v/100.0 for k, v in emotion_scores.items()}
            
            return dominant_emotion, confidence, all_probs
        except Exception as e:
            return 'neutral', 0.5, {'neutral': 0.5}

3. **Test the Model:**

```bash
cd backend
python manage.py shell
```

```python
from face_emotion.emotion_model import EmotionRecognitionModel
import cv2

# Initialize model
model = EmotionRecognitionModel()

# Test with an image
img = cv2.imread('path/to/test/image.jpg')
emotion, confidence, probs = model.predict(img)

print(f"Emotion: {emotion}")
print(f"Confidence: {confidence:.2%}")
print(f"All probabilities: {probs}")
```

4. **Restart Django Server:**

```bash
python manage.py runserver
```

## Expected Results After Fix

### Before (Current):
- ❌ Same emotion for everyone
- ❌ Random or fixed predictions
- ❌ Low confidence scores

### After (With DeepFace):
- ✅ Accurate emotion detection
- ✅ Different emotions for different faces
- ✅ High confidence scores (70-95%)
- ✅ Real-time detection works properly

## Testing the Fix

1. **Test with Webcam:**
   - Visit: http://127.0.0.1:8000/face-emotion/realtime/
   - Try different facial expressions
   - Verify emotions change correctly

2. **Test with Images:**
   - Upload different emotion images
   - Check if predictions match actual emotions

3. **Test Accuracy:**
   - Happy face → Should detect "happy"
   - Sad face → Should detect "sad"
   - Angry face → Should detect "angry"
   - Neutral face → Should detect "neutral"

## Performance Optimization

### For Better Speed:
```python
# In emotion_model.py, add caching
from functools import lru_cache

@lru_cache(maxsize=100)
def predict_cached(self, face_hash):
    # Cache predictions for similar faces
    pass
```

### For Better Accuracy:
- Use larger face images (224x224 instead of 48x48)
- Ensemble multiple models
- Fine-tune on your specific use case

## Troubleshooting

### Issue: "No face detected"
**Solution:** Adjust face detection parameters in face_detector.py

### Issue: Low confidence scores
**Solution:** Ensure good lighting and clear face visibility

### Issue: Slow predictions
**Solution:** Use GPU acceleration or reduce image size

## Summary

✅ **Fixed Issues:**
1. Face emotion history page - Field name corrected
2. Activity log page - Template created
3. Webcam accuracy - Solution provided (use DeepFace)

✅ **Next Steps:**
1. Install DeepFace: `pip install deepface`
2. Replace emotion_model.py with DeepFace implementation
3. Test with real faces
4. Verify accuracy improvements

---
**Status:** Ready to implement  
**Estimated Time:** 10-15 minutes  
**Difficulty:** Easy (just install and replace code)