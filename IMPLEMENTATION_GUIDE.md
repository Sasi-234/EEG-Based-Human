# Implementation Guide - EEG Emotion Recognition System

## Quick Start Guide

This guide provides step-by-step instructions for implementing the EEG Emotion Recognition System.

---

## Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.8 or higher
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 10GB free space
- **GPU**: Optional (NVIDIA GPU with CUDA for faster training)

### Required Software
- Python 3.8+
- pip (Python package manager)
- Git
- Visual Studio Code or PyCharm (recommended)
- Web browser (Chrome, Firefox, or Edge)

---

## Phase 1: Environment Setup

### Step 1: Create Project Directory
```bash
# Create main project directory
mkdir eeg-emotion-recognition
cd eeg-emotion-recognition

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
# Create requirements.txt
cat > requirements.txt << EOF
# Django Framework
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.0
django-filter==23.3

# Database
psycopg2-binary==2.9.9

# Deep Learning
tensorflow==2.15.0
keras==2.15.0
torch==2.1.0
torchvision==0.16.0

# Data Processing
numpy==1.24.3
pandas==2.1.3
scipy==1.11.4
scikit-learn==1.3.2

# EEG Processing
mne==1.5.1
pywavelets==1.4.1

# Visualization
matplotlib==3.8.2
seaborn==0.13.0
plotly==5.18.0

# Utilities
Pillow==10.1.0
python-dotenv==1.0.0
celery==5.3.4
redis==5.0.1

# Testing
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0

# Production
gunicorn==21.2.0
whitenoise==6.6.0
EOF

# Install all dependencies
pip install -r requirements.txt
```

### Step 3: Initialize Git Repository
```bash
# Initialize git
git init

# Create .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Django
*.log
db.sqlite3
media/
staticfiles/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# ML Models
*.h5
*.pkl
*.joblib

# Dataset
dataset/DEAP/raw/*
!dataset/DEAP/raw/.gitkeep

# Environment
.env
EOF

# Initial commit
git add .
git commit -m "Initial project setup"
```

---

## Phase 2: Django Project Setup

### Step 1: Create Django Project
```bash
# Create Django project
django-admin startproject config .

# Create Django apps
python manage.py startapp users
python manage.py startapp eeg_processing
python manage.py startapp ml_models
python manage.py startapp api
python manage.py startapp recommendations
```

### Step 2: Configure Settings
Edit [`config/settings.py`](config/settings.py):

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    
    # Local apps
    'users',
    'eeg_processing',
    'ml_models',
    'api',
    'recommendations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB

# Custom user model (if needed)
# AUTH_USER_MODEL = 'users.CustomUser'
```

### Step 3: Create Directory Structure
```bash
# Create necessary directories
mkdir -p media/eeg_uploads
mkdir -p media/reports
mkdir -p media/models
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p templates/users
mkdir -p templates/eeg
mkdir -p templates/admin
mkdir -p dataset/DEAP/raw
mkdir -p dataset/DEAP/processed
mkdir -p notebooks
mkdir -p tests
mkdir -p docs

# Create .gitkeep files to preserve empty directories
touch media/eeg_uploads/.gitkeep
touch media/reports/.gitkeep
touch media/models/.gitkeep
touch dataset/DEAP/raw/.gitkeep
touch dataset/DEAP/processed/.gitkeep
```

---

## Phase 3: Database Models Implementation

### Step 1: Create User Models
Edit [`users/models.py`](users/models.py):

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Extended User model"""
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
```

### Step 2: Create EEG Processing Models
Edit [`eeg_processing/models.py`](eeg_processing/models.py):

```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EEGUpload(models.Model):
    """Model for EEG file uploads"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eeg_uploads')
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='eeg_uploads/')
    file_size = models.IntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'eeg_uploads'
        ordering = ['-upload_date']
        verbose_name = 'EEG Upload'
        verbose_name_plural = 'EEG Uploads'
    
    def __str__(self):
        return f"{self.file_name} - {self.user.username}"

class EmotionPrediction(models.Model):
    """Model for emotion predictions"""
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('relaxed', 'Relaxed'),
        ('stressed', 'Stressed'),
        ('excited', 'Excited'),
    ]
    
    upload = models.ForeignKey(EEGUpload, on_delete=models.CASCADE, related_name='predictions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    predicted_emotion = models.CharField(max_length=50, choices=EMOTION_CHOICES)
    confidence_score = models.FloatField()
    model_used = models.CharField(max_length=50)
    prediction_date = models.DateTimeField(auto_now_add=True)
    valence = models.FloatField(null=True, blank=True)
    arousal = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'emotion_predictions'
        ordering = ['-prediction_date']
        verbose_name = 'Emotion Prediction'
        verbose_name_plural = 'Emotion Predictions'
    
    def __str__(self):
        return f"{self.predicted_emotion} - {self.confidence_score:.2f}"
```

### Step 3: Create ML Models
Edit [`ml_models/models.py`](ml_models/models.py):

```python
from django.db import models

class ModelTrainingLog(models.Model):
    """Model for tracking training sessions"""
    MODEL_TYPE_CHOICES = [
        ('cnn', 'CNN'),
        ('lstm', 'LSTM'),
        ('hybrid', 'Hybrid'),
    ]
    
    model_name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES)
    accuracy = models.FloatField()
    loss = models.FloatField()
    epochs = models.IntegerField()
    training_date = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField()
    model_path = models.CharField(max_length=500)
    
    class Meta:
        db_table = 'model_training_logs'
        ordering = ['-training_date']
        verbose_name = 'Model Training Log'
        verbose_name_plural = 'Model Training Logs'
    
    def __str__(self):
        return f"{self.model_name} - {self.accuracy:.2f}%"
```

### Step 4: Create Recommendation Models
Edit [`recommendations/models.py`](recommendations/models.py):

```python
from django.db import models
from django.contrib.auth import get_user_model
from eeg_processing.models import EmotionPrediction

User = get_user_model()

class Recommendation(models.Model):
    """Model for emotion-based recommendations"""
    RECOMMENDATION_TYPES = [
        ('activity', 'Activity'),
        ('meditation', 'Meditation'),
        ('music', 'Music'),
        ('exercise', 'Exercise'),
        ('therapy', 'Therapy'),
    ]
    
    prediction = models.ForeignKey(
        EmotionPrediction,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_text = models.TextField()
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendations'
        ordering = ['-created_date']
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'
    
    def __str__(self):
        return f"{self.recommendation_type} for {self.user.username}"
```

### Step 5: Create Activity Log Model
Edit [`users/models.py`](users/models.py) (add to existing file):

```python
class UserActivityLog(models.Model):
    """Model for tracking user activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=100)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_activity_logs'
        ordering = ['-timestamp']
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"
```

### Step 6: Run Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

## Phase 4: EEG Preprocessing Implementation

### Step 1: Create Preprocessing Module
Create [`eeg_processing/preprocessing.py`](eeg_processing/preprocessing.py):

```python
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FastICA
import mne

class EEGPreprocessor:
    """Class for EEG signal preprocessing"""
    
    def __init__(self, sampling_rate=128):
        self.sampling_rate = sampling_rate
        self.scaler = StandardScaler()
    
    def load_data(self, file_path):
        """Load EEG data from file"""
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path).values
        elif file_path.endswith('.dat'):
            data = np.load(file_path, allow_pickle=True)
        else:
            raise ValueError("Unsupported file format")
        return data
    
    def bandpass_filter(self, data, lowcut=0.5, highcut=45.0, order=5):
        """Apply bandpass filter"""
        nyquist = 0.5 * self.sampling_rate
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        filtered_data = filtfilt(b, a, data, axis=-1)
        return filtered_data
    
    def remove_artifacts(self, data, n_components=None):
        """Remove artifacts using ICA"""
        ica = FastICA(n_components=n_components, random_state=42)
        n_channels, n_samples = data.shape
        ica_data = ica.fit_transform(data.T)
        
        # Remove high-variance components
        threshold = np.std(ica_data) * 3
        artifact_components = np.where(np.std(ica_data, axis=0) > threshold)[0]
        ica_data[:, artifact_components] = 0
        
        cleaned_data = ica.inverse_transform(ica_data).T
        return cleaned_data
    
    def normalize(self, data):
        """Normalize data using z-score"""
        normalized_data = self.scaler.fit_transform(data.T).T
        return normalized_data
    
    def segment(self, data, window_size=128, overlap=64):
        """Segment data into windows"""
        n_channels, n_samples = data.shape
        step = window_size - overlap
        segments = []
        
        for start in range(0, n_samples - window_size + 1, step):
            segment = data[:, start:start + window_size]
            segments.append(segment)
        
        return np.array(segments)
    
    def preprocess(self, file_path):
        """Complete preprocessing pipeline"""
        # Load data
        data = self.load_data(file_path)
        
        # Apply bandpass filter
        filtered_data = self.bandpass_filter(data)
        
        # Remove artifacts
        cleaned_data = self.remove_artifacts(filtered_data)
        
        # Normalize
        normalized_data = self.normalize(cleaned_data)
        
        # Segment
        segments = self.segment(normalized_data)
        
        return segments
```

---

## Phase 5: CNN Model Implementation

Create [`ml_models/cnn_model.py`](ml_models/cnn_model.py):

```python
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
import numpy as np

class CNNEmotionClassifier:
    """CNN model for emotion classification"""
    
    def __init__(self, input_shape=(32, 128, 1), num_classes=6):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = self.build_model()
    
    def build_model(self):
        """Build CNN architecture"""
        model = models.Sequential([
            # First Conv Block
            layers.Conv1D(64, 3, activation='relu', padding='same',
                         input_shape=self.input_shape[:-1]),
            layers.BatchNormalization(),
            layers.MaxPooling1D(2),
            layers.Dropout(0.3),
            
            # Second Conv Block
            layers.Conv1D(128, 3, activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling1D(2),
            layers.Dropout(0.3),
            
            # Third Conv Block
            layers.Conv1D(256, 3, activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.GlobalAveragePooling1D(),
            
            # Dense Layers
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            
            # Output Layer
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        return model
    
    def compile_model(self, learning_rate=0.001):
        """Compile the model"""
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
        """Train the model"""
        # Callbacks
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True
        )
        
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=10,
            min_lr=1e-7
        )
        
        # Train
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, reduce_lr],
            verbose=1
        )
        
        return history
    
    def predict(self, X):
        """Make predictions"""
        predictions = self.model.predict(X)
        return predictions
    
    def save_model(self, path):
        """Save model to file"""
        self.model.save(path)
    
    def load_model(self, path):
        """Load model from file"""
        self.model = tf.keras.models.load_model(path)
```

---

## Phase 6: LSTM Model Implementation

Create [`ml_models/lstm_model.py`](ml_models/lstm_model.py):

```python
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks

class LSTMEmotionClassifier:
    """LSTM model for emotion classification"""
    
    def __init__(self, input_shape=(32, 128), num_classes=6):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = self.build_model()
    
    def build_model(self):
        """Build LSTM architecture"""
        model = models.Sequential([
            # First LSTM Layer
            layers.LSTM(128, return_sequences=True, input_shape=self.input_shape),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Second LSTM Layer
            layers.LSTM(64, return_sequences=True),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Third LSTM Layer
            layers.LSTM(32, return_sequences=False),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Dense Layers
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.5),
            
            # Output Layer
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        return model
    
    def compile_model(self, learning_rate=0.001):
        """Compile the model"""
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
        """Train the model"""
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True
        )
        
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=10,
            min_lr=1e-7
        )
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, reduce_lr],
            verbose=1
        )
        
        return history
    
    def predict(self, X):
        """Make predictions"""
        predictions = self.model.predict(X)
        return predictions
    
    def save_model(self, path):
        """Save model"""
        self.model.save(path)
    
    def load_model(self, path):
        """Load model"""
        self.model = tf.keras.models.load_model(path)
```

---

## Next Steps

After completing these phases, you should:

1. **Test the setup**: Run the Django development server
2. **Create admin interface**: Customize Django admin
3. **Build frontend**: Create HTML templates
4. **Implement APIs**: Create REST API endpoints
5. **Train models**: Use DEAP dataset to train CNN and LSTM
6. **Integrate**: Connect all components
7. **Test**: Comprehensive testing
8. **Deploy**: Production deployment

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-21