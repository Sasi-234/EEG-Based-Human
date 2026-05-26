"""
CNN Model for Facial Emotion Recognition
Architecture designed for 48x48 grayscale face images
"""

import os
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from django.conf import settings


class FaceEmotionCNN:
    """
    Convolutional Neural Network for facial emotion recognition
    """
    
    # Emotion labels
    EMOTIONS = ['angry', 'fear', 'happy', 'neutral', 'relaxed', 'sad', 'stress', 'surprise']
    
    def __init__(self, input_shape=(48, 48, 1), num_classes=8):
        """
        Initialize the emotion recognition model
        
        Args:
            input_shape: Input image shape (height, width, channels)
            num_classes: Number of emotion classes
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.history = None
    
    def build_model(self):
        """
        Build CNN architecture for emotion recognition
        
        Returns:
            Compiled Keras model
        """
        model = models.Sequential([
            # First Convolutional Block
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape, padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Second Convolutional Block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Third Convolutional Block
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Fourth Convolutional Block
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Flatten and Dense Layers
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            # Output Layer
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def build_lightweight_model(self):
        """
        Build a lighter CNN model for faster inference
        
        Returns:
            Compiled Keras model
        """
        model = models.Sequential([
            # First Block
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Second Block
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Third Block
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Dense Layers
            layers.Flatten(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """
        Train the emotion recognition model
        
        Args:
            X_train: Training images
            y_train: Training labels (one-hot encoded)
            X_val: Validation images
            y_val: Validation labels (one-hot encoded)
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        # Data augmentation
        datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            shear_range=0.2,
            fill_mode='nearest'
        )
        
        # Callbacks
        model_dir = os.path.join(settings.BASE_DIR, 'face_emotion', 'saved_models')
        os.makedirs(model_dir, exist_ok=True)
        
        checkpoint = ModelCheckpoint(
            os.path.join(model_dir, 'best_model.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
        
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
        
        # Train model
        self.history = self.model.fit(
            datagen.flow(X_train, y_train, batch_size=batch_size),
            validation_data=(X_val, y_val),
            epochs=epochs,
            callbacks=[checkpoint, early_stop, reduce_lr],
            verbose=1
        )
        
        return self.history
    
    def predict(self, face_image):
        """
        Predict emotion from face image
        
        Args:
            face_image: Preprocessed face image (48x48x1)
            
        Returns:
            Dictionary with emotion and confidence
        """
        if self.model is None:
            raise ValueError("Model not loaded. Please load or train a model first.")
        
        # Ensure correct shape
        if len(face_image.shape) == 2:
            face_image = np.expand_dims(face_image, axis=-1)
        if len(face_image.shape) == 3:
            face_image = np.expand_dims(face_image, axis=0)
        
        # Predict
        predictions = self.model.predict(face_image, verbose=0)
        
        # Get emotion with highest probability
        emotion_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][emotion_idx])
        emotion = self.EMOTIONS[emotion_idx]
        
        # Get all probabilities
        all_probs = {
            self.EMOTIONS[i]: float(predictions[0][i])
            for i in range(len(self.EMOTIONS))
        }
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'all_probabilities': all_probs
        }
    
    def predict_batch(self, face_images):
        """
        Predict emotions for multiple face images
        
        Args:
            face_images: Array of preprocessed face images
            
        Returns:
            List of prediction dictionaries
        """
        if self.model is None:
            raise ValueError("Model not loaded. Please load or train a model first.")
        
        predictions = self.model.predict(face_images, verbose=0)
        
        results = []
        for pred in predictions:
            emotion_idx = np.argmax(pred)
            confidence = float(pred[emotion_idx])
            emotion = self.EMOTIONS[emotion_idx]
            
            all_probs = {
                self.EMOTIONS[i]: float(pred[i])
                for i in range(len(self.EMOTIONS))
            }
            
            results.append({
                'emotion': emotion,
                'confidence': confidence,
                'all_probabilities': all_probs
            })
        
        return results
    
    def save_model(self, filepath):
        """
        Save model to file
        
        Args:
            filepath: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        self.model.save(filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load model from file
        
        Args:
            filepath: Path to model file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        self.model = keras.models.load_model(filepath)
        print(f"Model loaded from {filepath}")
    
    def get_model_summary(self):
        """
        Get model architecture summary
        
        Returns:
            Model summary string
        """
        if self.model is None:
            return "No model built yet"
        
        from io import StringIO
        stream = StringIO()
        self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
        return stream.getvalue()


def load_pretrained_model():
    """
    Load pre-trained emotion recognition model
    
    Returns:
        FaceEmotionCNN instance with loaded model
    """
    model_path = os.path.join(
        settings.BASE_DIR,
        'face_emotion',
        'saved_models',
        'face_emotion_model.h5'
    )
    
    emotion_model = FaceEmotionCNN()
    
    if os.path.exists(model_path):
        emotion_model.load_model(model_path)
    else:
        # Build new model if no pre-trained model exists
        print("No pre-trained model found. Building new model...")
        emotion_model.build_model()
    
    return emotion_model


def create_default_model():
    """
    Create and save a default model for initial use
    
    Returns:
        Path to saved model
    """
    model_dir = os.path.join(settings.BASE_DIR, 'face_emotion', 'saved_models')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'face_emotion_model.h5')
    
    # Build and save model
    emotion_model = FaceEmotionCNN()
    emotion_model.build_model()
    emotion_model.save_model(model_path)
    
    return model_path

# Made with Bob
