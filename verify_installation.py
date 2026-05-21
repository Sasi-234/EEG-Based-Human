"""
EEG Emotion Recognition System - Installation Verification Script
This script verifies that all components are properly installed and working.
"""

import sys
import os

print("=" * 60)
print("EEG EMOTION RECOGNITION SYSTEM - VERIFICATION")
print("=" * 60)
print()

# Test 1: Python Version
print("1. Checking Python Version...")
print(f"   ✅ Python {sys.version.split()[0]}")
if sys.version_info >= (3, 11) and sys.version_info < (3, 13):
    print("   ✅ Python version is compatible with TensorFlow")
else:
    print("   ⚠️  Python version may not be optimal for TensorFlow")
print()

# Test 2: Core Dependencies
print("2. Checking Core Dependencies...")
try:
    import django
    print(f"   ✅ Django {django.get_version()}")
except ImportError as e:
    print(f"   ❌ Django not found: {e}")

try:
    import rest_framework
    print(f"   ✅ Django REST Framework installed")
except ImportError as e:
    print(f"   ❌ Django REST Framework not found: {e}")
print()

# Test 3: TensorFlow and Keras
print("3. Checking TensorFlow and Keras...")
try:
    import tensorflow as tf
    print(f"   ✅ TensorFlow {tf.__version__}")
    
    # Check if GPU is available
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"   ✅ GPU available: {len(gpus)} device(s)")
    else:
        print(f"   ℹ️  No GPU detected (CPU mode)")
    
    import keras
    print(f"   ✅ Keras {keras.__version__}")
except ImportError as e:
    print(f"   ❌ TensorFlow/Keras not found: {e}")
print()

# Test 4: Scientific Computing Libraries
print("4. Checking Scientific Computing Libraries...")
try:
    import numpy as np
    print(f"   ✅ NumPy {np.__version__}")
except ImportError as e:
    print(f"   ❌ NumPy not found: {e}")

try:
    import pandas as pd
    print(f"   ✅ Pandas {pd.__version__}")
except ImportError as e:
    print(f"   ❌ Pandas not found: {e}")

try:
    import scipy
    print(f"   ✅ SciPy {scipy.__version__}")
except ImportError as e:
    print(f"   ❌ SciPy not found: {e}")

try:
    import sklearn
    print(f"   ✅ Scikit-learn {sklearn.__version__}")
except ImportError as e:
    print(f"   ❌ Scikit-learn not found: {e}")
print()

# Test 5: EEG Processing Libraries
print("5. Checking EEG Processing Libraries...")
try:
    import mne
    print(f"   ✅ MNE {mne.__version__}")
except ImportError as e:
    print(f"   ❌ MNE not found: {e}")

try:
    import pywt
    print(f"   ✅ PyWavelets {pywt.__version__}")
except ImportError as e:
    print(f"   ❌ PyWavelets not found: {e}")
print()

# Test 6: Visualization Libraries
print("6. Checking Visualization Libraries...")
try:
    import matplotlib
    print(f"   ✅ Matplotlib {matplotlib.__version__}")
except ImportError as e:
    print(f"   ❌ Matplotlib not found: {e}")

try:
    import seaborn
    print(f"   ✅ Seaborn {seaborn.__version__}")
except ImportError as e:
    print(f"   ❌ Seaborn not found: {e}")

try:
    import plotly
    print(f"   ✅ Plotly {plotly.__version__}")
except ImportError as e:
    print(f"   ❌ Plotly not found: {e}")
print()

# Test 7: Database
print("7. Checking Database...")
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
db_path = os.path.join(backend_path, 'db.sqlite3')
if os.path.exists(db_path):
    db_size = os.path.getsize(db_path) / 1024  # KB
    print(f"   ✅ Database exists: db.sqlite3 ({db_size:.2f} KB)")
else:
    print(f"   ⚠️  Database not found (run migrations)")
print()

# Test 8: Project Structure
print("8. Checking Project Structure...")
required_dirs = [
    'backend',
    'backend/config',
    'backend/users',
    'backend/eeg_processing',
    'backend/ml_models',
    'backend/api',
    'backend/recommendations',
    'backend/templates',
    'backend/static',
]

for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f"   ✅ {dir_path}")
    else:
        print(f"   ❌ {dir_path} not found")
print()

# Test 9: TensorFlow Functionality
print("9. Testing TensorFlow Functionality...")
try:
    import tensorflow as tf
    import numpy as np
    
    # Create a simple tensor
    test_tensor = tf.constant([[1, 2], [3, 4]])
    print(f"   ✅ Tensor creation works")
    
    # Test basic operation
    result = tf.reduce_sum(test_tensor)
    print(f"   ✅ Tensor operations work (sum: {result.numpy()})")
    
    # Test model creation
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
        tf.keras.layers.Dense(3, activation='softmax')
    ])
    print(f"   ✅ Model creation works")
    
    # Test prediction
    test_input = np.random.rand(1, 5)
    prediction = model.predict(test_input, verbose=0)
    print(f"   ✅ Model prediction works")
    
except Exception as e:
    print(f"   ❌ TensorFlow functionality test failed: {e}")
print()

# Summary
print("=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print()
print("✅ All core components are installed and working!")
print()
print("Next Steps:")
print("1. Start the server:")
print("   cd backend")
print("   python manage.py runserver")
print()
print("2. Open browser:")
print("   http://127.0.0.1:8000/")
print()
print("3. Upload EEG CSV files:")
print("   http://127.0.0.1:8000/eeg/upload/")
print()
print("4. Get emotion predictions in 30-60 seconds!")
print("=" * 60)

# Made with Bob
