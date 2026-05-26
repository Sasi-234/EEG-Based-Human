# CNN Model Training Guide for Facial Emotion Recognition

## Overview
Complete guide for training a TensorFlow CNN model to recognize 8 facial emotions using the FER2013 dataset or custom images.

---

## 🎯 Emotions Supported

The model recognizes **8 emotions**:
1. **Angry** 😠
2. **Fear** 😨
3. **Happy** 😊
4. **Neutral** 😐
5. **Relaxed** 😌
6. **Sad** 😢
7. **Stress** 😰
8. **Surprise** 😲

---

## 📋 Prerequisites

### System Requirements
- Python 3.11+
- TensorFlow 2.15.0
- 8GB+ RAM (16GB recommended)
- GPU (optional, but recommended for faster training)

### Install Dependencies
```powershell
pip install tensorflow==2.15.0
pip install numpy pandas matplotlib scikit-learn
```

---

## 📊 Dataset Options

### Option 1: FER2013 Dataset (Recommended)

#### Download FER2013
1. Visit Kaggle: https://www.kaggle.com/datasets/msambare/fer2013
2. Download `fer2013.csv` (308 MB)
3. Place in project directory

#### FER2013 Format
```csv
emotion,pixels,Usage
0,70 80 82 72 58 58 60 63 54 58 60 48 89 115 121...,Training
1,151 150 147 155 148 133 111 140 170 174 182...,Training
...
```

**Emotion Mapping**:
- 0 = Angry
- 1 = Fear  
- 2 = Happy
- 3 = Sad
- 4 = Surprise
- 5 = Neutral
- 6 = Disgust (map to Stress)
- 7 = Contempt (map to Relaxed)

### Option 2: Custom Dataset

#### Directory Structure
```
dataset/
├── angry/
│   ├── img001.jpg
│   ├── img002.jpg
│   └── ...
├── fear/
│   ├── img001.jpg
│   └── ...
├── happy/
├── neutral/
├── relaxed/
├── sad/
├── stress/
└── surprise/
```

#### Image Requirements
- Format: JPG, JPEG, or PNG
- Size: Any (will be resized to 48x48)
- Color: Grayscale or RGB (will be converted)
- Minimum: 100 images per emotion
- Recommended: 1000+ images per emotion

---

## 🏗️ Model Architectures

### 1. Standard Model (Recommended)
**Best balance of accuracy and speed**

```
Input: 48x48x1 grayscale image
↓
Conv2D(32) → BatchNorm → Conv2D(32) → BatchNorm → MaxPool → Dropout(0.25)
↓
Conv2D(64) → BatchNorm → Conv2D(64) → BatchNorm → MaxPool → Dropout(0.25)
↓
Conv2D(128) → BatchNorm → Conv2D(128) → BatchNorm → MaxPool → Dropout(0.25)
↓
Conv2D(256) → BatchNorm → Conv2D(256) → BatchNorm → MaxPool → Dropout(0.25)
↓
Flatten → Dense(512) → BatchNorm → Dropout(0.5)
↓
Dense(256) → BatchNorm → Dropout(0.5)
↓
Dense(8, softmax) → Output: 8 emotion probabilities
```

**Parameters**: ~2.5M  
**Training Time**: 2-4 hours (GPU)  
**Expected Accuracy**: 70-75%

### 2. Deep Model
**Higher accuracy, slower training**

```
Input: 48x48x1
↓
4 Conv Blocks (64, 128, 256, 512 filters)
↓
Dense(1024) → Dense(512) → Dense(8)
```

**Parameters**: ~8M  
**Training Time**: 4-8 hours (GPU)  
**Expected Accuracy**: 75-80%

### 3. Lightweight Model
**Faster inference, lower accuracy**

```
Input: 48x48x1
↓
3 Conv Blocks (32, 64, 128 filters)
↓
Dense(256) → Dense(8)
```

**Parameters**: ~500K  
**Training Time**: 1-2 hours (GPU)  
**Expected Accuracy**: 65-70%

---

## 🚀 Training Commands

### Quick Start (FER2013 CSV)
```powershell
cd backend

# Train with default settings
python face_emotion/train_model.py --data path/to/fer2013.csv --type csv

# Train with custom settings
python face_emotion/train_model.py \
    --data path/to/fer2013.csv \
    --type csv \
    --model standard \
    --epochs 50 \
    --batch-size 32
```

### Custom Dataset
```powershell
# Train with custom images
python face_emotion/train_model.py \
    --data path/to/dataset \
    --type dir \
    --model standard \
    --epochs 50
```

### Advanced Options
```powershell
# Deep model with more epochs
python face_emotion/train_model.py \
    --data fer2013.csv \
    --type csv \
    --model deep \
    --epochs 100 \
    --batch-size 64

# Lightweight model without augmentation
python face_emotion/train_model.py \
    --data fer2013.csv \
    --type csv \
    --model lightweight \
    --epochs 30 \
    --no-augmentation

# Custom save path
python face_emotion/train_model.py \
    --data fer2013.csv \
    --type csv \
    --save-path my_models
```

---

## 📝 Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--data` | str | Required | Path to CSV file or data directory |
| `--type` | str | `csv` | Data type: `csv` or `dir` |
| `--model` | str | `standard` | Model: `standard`, `deep`, or `lightweight` |
| `--epochs` | int | `50` | Number of training epochs |
| `--batch-size` | int | `32` | Batch size for training |
| `--no-augmentation` | flag | False | Disable data augmentation |
| `--save-path` | str | `saved_models` | Directory to save models |

---

## 📈 Training Process

### Step 1: Data Loading
```
Loading FER2013 dataset...
Total samples: 35887
Data shape: (35887, 48, 48, 1)
Labels shape: (35887,)

Train set: 28709 samples
Validation set: 3589 samples
Test set: 3589 samples
```

### Step 2: Model Building
```
Building standard CNN model...
Model: "sequential"
_________________________________________________________________
Layer (type)                Output Shape              Param #   
=================================================================
conv2d (Conv2D)            (None, 48, 48, 32)        320       
batch_normalization        (None, 48, 48, 32)        128       
...
=================================================================
Total params: 2,547,848
Trainable params: 2,545,544
Non-trainable params: 2,304
```

### Step 3: Training
```
Epoch 1/50
897/897 [==============================] - 45s 50ms/step
loss: 1.8234 - accuracy: 0.2456 - val_loss: 1.7123 - val_accuracy: 0.3012

Epoch 2/50
897/897 [==============================] - 42s 47ms/step
loss: 1.6234 - accuracy: 0.3567 - val_loss: 1.5234 - val_accuracy: 0.4123
...

Epoch 50/50
897/897 [==============================] - 42s 47ms/step
loss: 0.8234 - accuracy: 0.7234 - val_loss: 0.9123 - val_accuracy: 0.7012
```

### Step 4: Evaluation
```
Evaluating Model on Test Set
3589/3589 [==============================] - 12s 3ms/step
loss: 0.9234 - accuracy: 0.7123

Test Loss: 0.9234
Test Accuracy: 0.7123 (71.23%)
```

---

## 📊 Output Files

### Saved Models
```
saved_models/
├── best_model_20260522_143530.h5          # Best model during training
├── face_emotion_model_final.h5            # Final trained model
├── training_history.png                   # Training plots
├── training_log_20260522_143530.csv       # Training metrics
└── logs/                                  # TensorBoard logs
    └── 20260522_143530/
```

### Training Log CSV
```csv
epoch,accuracy,loss,val_accuracy,val_loss,lr
0,0.2456,1.8234,0.3012,1.7123,0.0001
1,0.3567,1.6234,0.4123,1.5234,0.0001
...
```

---

## 📉 Monitoring Training

### TensorBoard
```powershell
# Start TensorBoard
tensorboard --logdir=saved_models/logs

# Open browser
http://localhost:6006
```

**TensorBoard Features**:
- Real-time training metrics
- Loss and accuracy curves
- Model graph visualization
- Histogram of weights

### Training Plots
Automatically generated `training_history.png`:
- Left: Accuracy over epochs
- Right: Loss over epochs
- Blue: Training metrics
- Orange: Validation metrics

---

## 🎯 Data Augmentation

### Enabled by Default
```python
ImageDataGenerator(
    rotation_range=20,        # Rotate ±20 degrees
    width_shift_range=0.2,    # Shift horizontally ±20%
    height_shift_range=0.2,   # Shift vertically ±20%
    horizontal_flip=True,     # Random horizontal flip
    zoom_range=0.2,           # Zoom ±20%
    shear_range=0.2,          # Shear transformation
    fill_mode='nearest'       # Fill empty pixels
)
```

### Disable Augmentation
```powershell
python face_emotion/train_model.py --data fer2013.csv --type csv --no-augmentation
```

**When to disable**:
- Small dataset (augmentation may not help)
- Testing baseline performance
- Faster training needed

---

## 🔧 Callbacks & Features

### 1. ModelCheckpoint
Saves best model based on validation accuracy
```python
ModelCheckpoint(
    'best_model.h5',
    monitor='val_accuracy',
    save_best_only=True
)
```

### 2. EarlyStopping
Stops training if no improvement
```python
EarlyStopping(
    monitor='val_loss',
    patience=15,              # Wait 15 epochs
    restore_best_weights=True
)
```

### 3. ReduceLROnPlateau
Reduces learning rate when stuck
```python
ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,               # Reduce by 50%
    patience=5,               # Wait 5 epochs
    min_lr=1e-7
)
```

### 4. TensorBoard
Logs metrics for visualization

### 5. CSVLogger
Saves training history to CSV

---

## 💡 Training Tips

### 1. Start with Standard Model
```powershell
python face_emotion/train_model.py --data fer2013.csv --type csv --model standard
```

### 2. Monitor Overfitting
**Signs of overfitting**:
- Training accuracy >> Validation accuracy
- Validation loss increasing

**Solutions**:
- Increase dropout rates
- Add more data augmentation
- Use early stopping
- Reduce model complexity

### 3. Improve Accuracy
**If accuracy is low (<60%)**:
- Train for more epochs
- Use deeper model
- Increase batch size
- Check data quality

**If accuracy plateaus**:
- Reduce learning rate
- Try different optimizer
- Add more training data

### 4. Speed Up Training
- Use GPU (10-20x faster)
- Increase batch size
- Use lightweight model
- Reduce image size

---

## 🐛 Troubleshooting

### Issue 1: Out of Memory
**Error**: `ResourceExhaustedError: OOM when allocating tensor`

**Solutions**:
```powershell
# Reduce batch size
python face_emotion/train_model.py --data fer2013.csv --type csv --batch-size 16

# Use lightweight model
python face_emotion/train_model.py --data fer2013.csv --type csv --model lightweight
```

### Issue 2: Low Accuracy
**Problem**: Accuracy stuck at 30-40%

**Solutions**:
1. Check data quality
2. Increase epochs
3. Use data augmentation
4. Try different model architecture

### Issue 3: Training Too Slow
**Problem**: Each epoch takes >5 minutes

**Solutions**:
1. Use GPU
2. Reduce batch size
3. Use lightweight model
4. Disable augmentation for testing

### Issue 4: Model Not Saving
**Error**: `Permission denied` or `File not found`

**Solutions**:
```powershell
# Create save directory
New-Item -ItemType Directory -Force -Path saved_models

# Use different path
python face_emotion/train_model.py --data fer2013.csv --type csv --save-path my_models
```

---

## 📊 Expected Results

### FER2013 Dataset
| Model | Accuracy | Training Time | Parameters |
|-------|----------|---------------|------------|
| Lightweight | 65-70% | 1-2 hours | 500K |
| Standard | 70-75% | 2-4 hours | 2.5M |
| Deep | 75-80% | 4-8 hours | 8M |

### Custom Dataset
Results depend on:
- Dataset size
- Image quality
- Class balance
- Lighting conditions

**Minimum Requirements**:
- 100+ images per emotion
- Good lighting
- Clear faces
- Balanced classes

---

## 🎓 Usage After Training

### Load Trained Model
```python
from tensorflow import keras

# Load model
model = keras.models.load_model('saved_models/face_emotion_model_final.h5')

# Predict emotion
import numpy as np
face_image = np.random.rand(1, 48, 48, 1)  # Your preprocessed face
prediction = model.predict(face_image)
emotion_idx = np.argmax(prediction)
emotions = ['angry', 'fear', 'happy', 'neutral', 'relaxed', 'sad', 'stress', 'surprise']
print(f"Emotion: {emotions[emotion_idx]}")
```

### Integrate with Django
```python
# In face_emotion/emotion_model.py
def load_pretrained_model():
    model_path = 'saved_models/face_emotion_model_final.h5'
    emotion_model = FaceEmotionCNN()
    emotion_model.load_model(model_path)
    return emotion_model
```

---

## 📚 Additional Resources

### Datasets
- **FER2013**: https://www.kaggle.com/datasets/msambare/fer2013
- **AffectNet**: http://mohammadmahoor.com/affectnet/
- **RAF-DB**: http://www.whdeng.cn/raf/model1.html

### Papers
- "Challenges in Representation Learning: Facial Expression Recognition Challenge" (FER2013)
- "Deep Facial Expression Recognition: A Survey" (2020)

### TensorFlow Resources
- TensorFlow Guide: https://www.tensorflow.org/guide
- Keras API: https://keras.io/api/
- Image Classification: https://www.tensorflow.org/tutorials/images/classification

---

## ✅ Training Checklist

- [ ] Install TensorFlow and dependencies
- [ ] Download FER2013 dataset or prepare custom images
- [ ] Verify data format and structure
- [ ] Choose model architecture
- [ ] Set training parameters (epochs, batch size)
- [ ] Start training
- [ ] Monitor training progress
- [ ] Evaluate on test set
- [ ] Save best model
- [ ] Test model with real images
- [ ] Integrate with Django application

---

**Last Updated**: 2026-05-22  
**Version**: 1.0  
**Status**: Production Ready