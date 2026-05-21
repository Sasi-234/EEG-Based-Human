# Technical Specifications - EEG Emotion Recognition System

## 1. DEAP Dataset Specifications

### Dataset Overview
- **Name**: DEAP (Database for Emotion Analysis using Physiological signals)
- **Participants**: 32 subjects
- **Trials**: 40 music video trials per participant
- **Duration**: 60 seconds per trial
- **Sampling Rate**: 512 Hz (downsampled to 128 Hz)

### EEG Channels
- **Total Channels**: 32 EEG channels
- **Channel Names**: Fp1, AF3, F3, F7, FC5, FC1, C3, T7, CP5, CP1, P3, P7, PO3, O1, Oz, Pz, Fp2, AF4, Fz, F4, F8, FC6, FC2, Cz, C4, T8, CP6, CP2, P4, P8, PO4, O2
- **Reference**: Average of mastoids
- **Ground**: Common ground

### Emotion Labels
- **Valence**: 1-9 scale (1=low, 9=high)
- **Arousal**: 1-9 scale (1=low, 9=high)
- **Dominance**: 1-9 scale (1=low, 9=high)
- **Liking**: 1-9 scale (1=low, 9=high)

### Emotion Mapping
```python
EMOTION_MAPPING = {
    'happy': {'valence': (6, 9), 'arousal': (6, 9)},      # High valence, high arousal
    'excited': {'valence': (6, 9), 'arousal': (7, 9)},    # High valence, very high arousal
    'relaxed': {'valence': (6, 9), 'arousal': (1, 4)},    # High valence, low arousal
    'sad': {'valence': (1, 4), 'arousal': (1, 4)},        # Low valence, low arousal
    'angry': {'valence': (1, 4), 'arousal': (6, 9)},      # Low valence, high arousal
    'stressed': {'valence': (1, 5), 'arousal': (6, 9)}    # Low-mid valence, high arousal
}
```

---

## 2. EEG Signal Preprocessing Pipeline

### Step 1: Data Loading
```python
import mne
import numpy as np
import pandas as pd

def load_eeg_data(file_path):
    """
    Load EEG data from various formats
    Supported: .csv, .dat, .edf, .bdf
    """
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
        return data.values
    elif file_path.endswith('.dat'):
        data = np.load(file_path, allow_pickle=True)
        return data
    elif file_path.endswith(('.edf', '.bdf')):
        raw = mne.io.read_raw_edf(file_path, preload=True)
        return raw.get_data()
```

### Step 2: Bandpass Filtering
```python
from scipy.signal import butter, filtfilt

def bandpass_filter(data, lowcut=0.5, highcut=45.0, fs=128, order=5):
    """
    Apply bandpass filter to remove noise
    - Delta: 0.5-4 Hz
    - Theta: 4-8 Hz
    - Alpha: 8-13 Hz
    - Beta: 13-30 Hz
    - Gamma: 30-45 Hz
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    filtered_data = filtfilt(b, a, data, axis=-1)
    return filtered_data
```

### Step 3: Artifact Removal
```python
from sklearn.decomposition import FastICA

def remove_artifacts(data, n_components=None):
    """
    Remove artifacts using Independent Component Analysis (ICA)
    """
    ica = FastICA(n_components=n_components, random_state=42)
    # Reshape data for ICA
    n_channels, n_samples = data.shape
    ica_data = ica.fit_transform(data.T)
    # Remove components with high variance (likely artifacts)
    threshold = np.std(ica_data) * 3
    artifact_components = np.where(np.std(ica_data, axis=0) > threshold)[0]
    ica_data[:, artifact_components] = 0
    # Reconstruct signal
    cleaned_data = ica.inverse_transform(ica_data).T
    return cleaned_data
```

### Step 4: Normalization
```python
from sklearn.preprocessing import StandardScaler

def normalize_eeg(data):
    """
    Z-score normalization per channel
    """
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(data.T).T
    return normalized_data
```

### Step 5: Segmentation
```python
def segment_eeg(data, window_size=128, overlap=64):
    """
    Segment EEG into overlapping windows
    window_size: samples per window (1 second at 128 Hz)
    overlap: samples overlap between windows
    """
    n_channels, n_samples = data.shape
    step = window_size - overlap
    segments = []
    
    for start in range(0, n_samples - window_size + 1, step):
        segment = data[:, start:start + window_size]
        segments.append(segment)
    
    return np.array(segments)
```

---

## 3. Feature Extraction Methods

### Time Domain Features
```python
def extract_time_features(segment):
    """
    Extract statistical features from time domain
    """
    features = {
        'mean': np.mean(segment, axis=1),
        'std': np.std(segment, axis=1),
        'variance': np.var(segment, axis=1),
        'skewness': scipy.stats.skew(segment, axis=1),
        'kurtosis': scipy.stats.kurtosis(segment, axis=1),
        'min': np.min(segment, axis=1),
        'max': np.max(segment, axis=1),
        'range': np.ptp(segment, axis=1),
        'rms': np.sqrt(np.mean(segment**2, axis=1))
    }
    return np.concatenate([features[k] for k in features])
```

### Frequency Domain Features
```python
from scipy.signal import welch

def extract_frequency_features(segment, fs=128):
    """
    Extract power spectral density features
    """
    freqs, psd = welch(segment, fs=fs, nperseg=min(256, segment.shape[1]))
    
    # Define frequency bands
    bands = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 45)
    }
    
    band_powers = {}
    for band_name, (low, high) in bands.items():
        idx = np.logical_and(freqs >= low, freqs <= high)
        band_powers[band_name] = np.mean(psd[:, idx], axis=1)
    
    return np.concatenate([band_powers[k] for k in band_powers])
```

### Wavelet Features
```python
import pywt

def extract_wavelet_features(segment):
    """
    Extract wavelet decomposition features
    """
    wavelet = 'db4'
    level = 4
    features = []
    
    for channel in segment:
        coeffs = pywt.wavedec(channel, wavelet, level=level)
        for coeff in coeffs:
            features.extend([
                np.mean(coeff),
                np.std(coeff),
                np.max(np.abs(coeff))
            ])
    
    return np.array(features)
```

---

## 4. CNN Model Architecture Details

### Model Configuration
```python
import tensorflow as tf
from tensorflow.keras import layers, models

def build_cnn_model(input_shape=(32, 128, 1), num_classes=6):
    """
    Build CNN model for EEG emotion recognition
    Input: (channels, time_points, 1)
    Output: (num_classes,)
    """
    model = models.Sequential([
        # First Convolutional Block
        layers.Conv1D(64, kernel_size=3, activation='relu', 
                     input_shape=input_shape[:-1], padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.3),
        
        # Second Convolutional Block
        layers.Conv1D(128, kernel_size=3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.3),
        
        # Third Convolutional Block
        layers.Conv1D(256, kernel_size=3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling1D(),
        
        # Fully Connected Layers
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        
        # Output Layer
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model
```

### Training Configuration
```python
TRAINING_CONFIG = {
    'optimizer': 'adam',
    'learning_rate': 0.001,
    'loss': 'categorical_crossentropy',
    'metrics': ['accuracy', 'precision', 'recall'],
    'batch_size': 32,
    'epochs': 100,
    'validation_split': 0.2,
    'early_stopping_patience': 15,
    'reduce_lr_patience': 10,
    'reduce_lr_factor': 0.5
}
```

---

## 5. LSTM Model Architecture Details

### Model Configuration
```python
def build_lstm_model(input_shape=(32, 128), num_classes=6):
    """
    Build LSTM model for EEG emotion recognition
    """
    model = models.Sequential([
        # First LSTM Layer
        layers.LSTM(128, return_sequences=True, input_shape=input_shape),
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
        
        # Fully Connected Layers
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),
        
        # Output Layer
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model
```

---

## 6. API Endpoint Specifications

### Authentication Endpoints

#### POST /api/auth/register/
```json
Request:
{
    "username": "string",
    "email": "string",
    "password": "string",
    "first_name": "string",
    "last_name": "string"
}

Response (201):
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "message": "Registration successful"
}
```

#### POST /api/auth/login/
```json
Request:
{
    "username": "string",
    "password": "string"
}

Response (200):
{
    "token": "string",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string"
    }
}
```

### EEG Processing Endpoints

#### POST /api/eeg/upload/
```json
Request (multipart/form-data):
{
    "file": "binary",
    "description": "string (optional)"
}

Response (201):
{
    "id": "integer",
    "file_name": "string",
    "file_size": "integer",
    "upload_date": "datetime",
    "status": "pending"
}
```

#### POST /api/predict/
```json
Request:
{
    "upload_id": "integer",
    "model_type": "cnn|lstm"
}

Response (200):
{
    "prediction_id": "integer",
    "predicted_emotion": "string",
    "confidence_score": "float",
    "valence": "float",
    "arousal": "float",
    "model_used": "string",
    "prediction_date": "datetime",
    "recommendations": [
        {
            "type": "string",
            "text": "string"
        }
    ]
}
```

#### GET /api/predictions/
```json
Response (200):
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "predicted_emotion": "string",
            "confidence_score": "float",
            "prediction_date": "datetime",
            "upload": {
                "id": "integer",
                "file_name": "string"
            }
        }
    ]
}
```

---

## 7. Database Indexes and Optimization

### Recommended Indexes
```sql
-- Users table
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- EEG Uploads table
CREATE INDEX idx_uploads_user_id ON eeg_uploads(user_id);
CREATE INDEX idx_uploads_status ON eeg_uploads(status);
CREATE INDEX idx_uploads_date ON eeg_uploads(upload_date);

-- Predictions table
CREATE INDEX idx_predictions_user_id ON emotion_predictions(user_id);
CREATE INDEX idx_predictions_upload_id ON emotion_predictions(upload_id);
CREATE INDEX idx_predictions_date ON emotion_predictions(prediction_date);
CREATE INDEX idx_predictions_emotion ON emotion_predictions(predicted_emotion);

-- Activity Logs
CREATE INDEX idx_activity_user_id ON user_activity_logs(user_id);
CREATE INDEX idx_activity_timestamp ON user_activity_logs(timestamp);
```

---

## 8. Security Specifications

### Password Requirements
- Minimum length: 8 characters
- Must contain: uppercase, lowercase, number, special character
- Password hashing: PBKDF2 with SHA256

### File Upload Security
```python
ALLOWED_EXTENSIONS = {'.csv', '.dat', '.edf', '.bdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

def validate_file(file):
    # Check extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("Invalid file type")
    
    # Check size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError("File too large")
    
    # Check content type
    if not file.content_type.startswith(('text/', 'application/')):
        raise ValidationError("Invalid content type")
```

### Rate Limiting
```python
RATE_LIMITS = {
    'login': '5/minute',
    'register': '3/hour',
    'upload': '10/hour',
    'predict': '20/hour',
    'api_default': '100/hour'
}
```

---

## 9. Performance Benchmarks

### Target Metrics
- **Model Training Time**: <2 hours for 100 epochs
- **Prediction Time**: <5 seconds per file
- **API Response Time**: <500ms (excluding prediction)
- **File Upload Time**: <10 seconds for 10MB file
- **Page Load Time**: <2 seconds
- **Concurrent Users**: Support 100+ simultaneous users

### Optimization Strategies
1. **Database**: Connection pooling, query optimization
2. **Caching**: Redis for session and query caching
3. **Static Files**: CDN delivery
4. **Model**: Model quantization, batch processing
5. **Frontend**: Code splitting, lazy loading

---

## 10. Error Handling

### Error Response Format
```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": "object (optional)"
    }
}
```

### Common Error Codes
- `AUTH_001`: Invalid credentials
- `AUTH_002`: Token expired
- `FILE_001`: Invalid file format
- `FILE_002`: File too large
- `PRED_001`: Prediction failed
- `PRED_002`: Model not found
- `DB_001`: Database error
- `VAL_001`: Validation error

---

## 11. Monitoring and Logging

### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues

### Metrics to Monitor
- Request count and response times
- Error rates
- Model prediction accuracy
- Database query performance
- Memory and CPU usage
- Disk space usage

---

## 12. Backup and Recovery

### Backup Strategy
- **Database**: Daily automated backups
- **User Files**: Real-time backup to cloud storage
- **Models**: Version-controlled model storage
- **Configuration**: Git-based configuration management

### Recovery Procedures
1. Database restoration from latest backup
2. File recovery from cloud storage
3. Model rollback to previous version
4. Configuration restoration from Git

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-21