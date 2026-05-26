"""
TensorFlow CNN Model Training for Facial Emotion Recognition
Supports FER2013 dataset with 8 emotions
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau,
    TensorBoard, CSVLogger
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical


class FaceEmotionCNNTrainer:
    """
    CNN Model Trainer for Facial Emotion Recognition
    """
    
    # 8 Emotion classes
    EMOTIONS = ['angry', 'fear', 'happy', 'neutral', 'relaxed', 'sad', 'stress', 'surprise']
    NUM_CLASSES = 8
    IMG_SIZE = 48
    
    def __init__(self, data_path=None, model_save_path='saved_models'):
        """
        Initialize the trainer
        
        Args:
            data_path: Path to FER2013 dataset CSV file
            model_save_path: Directory to save trained models
        """
        self.data_path = data_path
        self.model_save_path = model_save_path
        self.model = None
        self.history = None
        
        # Create save directory
        os.makedirs(model_save_path, exist_ok=True)
        
        print("="*70)
        print("Face Emotion Recognition CNN Trainer")
        print("="*70)
        print(f"Emotions: {', '.join(self.EMOTIONS)}")
        print(f"Number of classes: {self.NUM_CLASSES}")
        print(f"Image size: {self.IMG_SIZE}x{self.IMG_SIZE}")
        print(f"Model save path: {self.model_save_path}")
        print("="*70 + "\n")
    
    def load_fer2013_data(self, csv_path):
        """
        Load FER2013 dataset from CSV file
        
        Args:
            csv_path: Path to fer2013.csv file
            
        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        print("Loading FER2013 dataset...")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"Total samples: {len(df)}")
        
        # Extract pixels and labels
        pixels = df['pixels'].tolist()
        emotions = df['emotion'].tolist()
        
        # Convert pixels to numpy arrays
        X = []
        for pixel_sequence in pixels:
            face = [int(pixel) for pixel in pixel_sequence.split(' ')]
            face = np.asarray(face).reshape(self.IMG_SIZE, self.IMG_SIZE)
            X.append(face)
        
        X = np.array(X)
        y = np.array(emotions)
        
        # Normalize pixel values
        X = X.astype('float32') / 255.0
        
        # Add channel dimension
        X = np.expand_dims(X, axis=-1)
        
        print(f"Data shape: {X.shape}")
        print(f"Labels shape: {y.shape}")
        
        # Split data
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        
        # Convert labels to categorical
        y_train = to_categorical(y_train, self.NUM_CLASSES)
        y_val = to_categorical(y_val, self.NUM_CLASSES)
        y_test = to_categorical(y_test, self.NUM_CLASSES)
        
        print(f"\nTrain set: {X_train.shape[0]} samples")
        print(f"Validation set: {X_val.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples\n")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def load_custom_data(self, data_dir):
        """
        Load custom dataset from directory structure
        
        Directory structure:
        data_dir/
            angry/
                img1.jpg
                img2.jpg
            happy/
                img1.jpg
            ...
        
        Args:
            data_dir: Path to data directory
            
        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        print(f"Loading custom dataset from {data_dir}...")
        
        X = []
        y = []
        
        for emotion_idx, emotion in enumerate(self.EMOTIONS):
            emotion_dir = os.path.join(data_dir, emotion)
            
            if not os.path.exists(emotion_dir):
                print(f"Warning: Directory not found: {emotion_dir}")
                continue
            
            image_files = [f for f in os.listdir(emotion_dir) 
                          if f.endswith(('.jpg', '.jpeg', '.png'))]
            
            print(f"Loading {emotion}: {len(image_files)} images")
            
            for img_file in image_files:
                img_path = os.path.join(emotion_dir, img_file)
                
                try:
                    # Read and preprocess image
                    img = tf.keras.preprocessing.image.load_img(
                        img_path,
                        color_mode='grayscale',
                        target_size=(self.IMG_SIZE, self.IMG_SIZE)
                    )
                    img_array = tf.keras.preprocessing.image.img_to_array(img)
                    img_array = img_array / 255.0
                    
                    X.append(img_array)
                    y.append(emotion_idx)
                    
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"\nTotal samples loaded: {len(X)}")
        print(f"Data shape: {X.shape}")
        
        # Split data
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        
        # Convert labels to categorical
        y_train = to_categorical(y_train, self.NUM_CLASSES)
        y_val = to_categorical(y_val, self.NUM_CLASSES)
        y_test = to_categorical(y_test, self.NUM_CLASSES)
        
        print(f"\nTrain set: {X_train.shape[0]} samples")
        print(f"Validation set: {X_val.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples\n")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def build_cnn_model(self, model_type='standard'):
        """
        Build CNN model architecture
        
        Args:
            model_type: 'standard', 'deep', or 'lightweight'
            
        Returns:
            Compiled Keras model
        """
        print(f"Building {model_type} CNN model...")
        
        if model_type == 'standard':
            model = self._build_standard_model()
        elif model_type == 'deep':
            model = self._build_deep_model()
        elif model_type == 'lightweight':
            model = self._build_lightweight_model()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Print model summary
        model.summary()
        
        self.model = model
        return model
    
    def _build_standard_model(self):
        """Build standard CNN architecture"""
        model = models.Sequential([
            # Block 1
            layers.Conv2D(32, (3, 3), activation='relu', 
                         input_shape=(self.IMG_SIZE, self.IMG_SIZE, 1), 
                         padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 2
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 3
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 4
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
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
            
            # Output layer
            layers.Dense(self.NUM_CLASSES, activation='softmax')
        ])
        
        return model
    
    def _build_deep_model(self):
        """Build deeper CNN architecture for better accuracy"""
        model = models.Sequential([
            # Block 1
            layers.Conv2D(64, (3, 3), activation='relu', 
                         input_shape=(self.IMG_SIZE, self.IMG_SIZE, 1), 
                         padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 2
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 3
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 4
            layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Dense layers
            layers.Flatten(),
            layers.Dense(1024, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            # Output layer
            layers.Dense(self.NUM_CLASSES, activation='softmax')
        ])
        
        return model
    
    def _build_lightweight_model(self):
        """Build lightweight CNN for faster inference"""
        model = models.Sequential([
            # Block 1
            layers.Conv2D(32, (3, 3), activation='relu', 
                         input_shape=(self.IMG_SIZE, self.IMG_SIZE, 1)),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 2
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 3
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Dense layers
            layers.Flatten(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            
            # Output layer
            layers.Dense(self.NUM_CLASSES, activation='softmax')
        ])
        
        return model
    
    def train(self, X_train, y_train, X_val, y_val, 
              epochs=50, batch_size=32, use_augmentation=True):
        """
        Train the CNN model
        
        Args:
            X_train: Training images
            y_train: Training labels
            X_val: Validation images
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size
            use_augmentation: Whether to use data augmentation
            
        Returns:
            Training history
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_cnn_model() first.")
        
        print("\n" + "="*70)
        print("Starting Model Training")
        print("="*70)
        print(f"Epochs: {epochs}")
        print(f"Batch size: {batch_size}")
        print(f"Data augmentation: {use_augmentation}")
        print("="*70 + "\n")
        
        # Data augmentation
        if use_augmentation:
            datagen = ImageDataGenerator(
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                horizontal_flip=True,
                zoom_range=0.2,
                shear_range=0.2,
                fill_mode='nearest'
            )
            train_generator = datagen.flow(X_train, y_train, batch_size=batch_size)
        else:
            train_generator = None
        
        # Callbacks
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        checkpoint = ModelCheckpoint(
            os.path.join(self.model_save_path, f'best_model_{timestamp}.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
        
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=15,
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
        
        tensorboard = TensorBoard(
            log_dir=os.path.join(self.model_save_path, 'logs', timestamp),
            histogram_freq=1
        )
        
        csv_logger = CSVLogger(
            os.path.join(self.model_save_path, f'training_log_{timestamp}.csv')
        )
        
        callbacks = [checkpoint, early_stop, reduce_lr, tensorboard, csv_logger]
        
        # Train model
        if use_augmentation:
            self.history = self.model.fit(
                train_generator,
                steps_per_epoch=len(X_train) // batch_size,
                validation_data=(X_val, y_val),
                epochs=epochs,
                callbacks=callbacks,
                verbose=1
            )
        else:
            self.history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
        
        print("\n" + "="*70)
        print("Training Completed!")
        print("="*70 + "\n")
        
        return self.history
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model on test set
        
        Args:
            X_test: Test images
            y_test: Test labels
            
        Returns:
            Test loss and accuracy
        """
        print("\n" + "="*70)
        print("Evaluating Model on Test Set")
        print("="*70)
        
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=1)
        
        print(f"\nTest Loss: {test_loss:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
        print("="*70 + "\n")
        
        return test_loss, test_accuracy
    
    def plot_training_history(self, save_path=None):
        """
        Plot training history
        
        Args:
            save_path: Path to save plot (optional)
        """
        if self.history is None:
            print("No training history available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot accuracy
        ax1.plot(self.history.history['accuracy'], label='Train Accuracy')
        ax1.plot(self.history.history['val_accuracy'], label='Val Accuracy')
        ax1.set_title('Model Accuracy')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Accuracy')
        ax1.legend()
        ax1.grid(True)
        
        # Plot loss
        ax2.plot(self.history.history['loss'], label='Train Loss')
        ax2.plot(self.history.history['val_loss'], label='Val Loss')
        ax2.set_title('Model Loss')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Loss')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def save_model(self, filename='face_emotion_model.h5'):
        """
        Save trained model
        
        Args:
            filename: Model filename
        """
        if self.model is None:
            print("No model to save")
            return
        
        filepath = os.path.join(self.model_save_path, filename)
        self.model.save(filepath)
        print(f"Model saved to: {filepath}")


def main():
    """Main training function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Face Emotion Recognition CNN')
    parser.add_argument('--data', type=str, required=True, 
                       help='Path to FER2013 CSV or custom data directory')
    parser.add_argument('--type', type=str, choices=['csv', 'dir'], default='csv',
                       help='Data type: csv (FER2013) or dir (custom directory)')
    parser.add_argument('--model', type=str, choices=['standard', 'deep', 'lightweight'],
                       default='standard', help='Model architecture')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--no-augmentation', action='store_true', 
                       help='Disable data augmentation')
    parser.add_argument('--save-path', type=str, default='saved_models',
                       help='Directory to save models')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = FaceEmotionCNNTrainer(model_save_path=args.save_path)
    
    # Load data
    if args.type == 'csv':
        X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_fer2013_data(args.data)
    else:
        X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_custom_data(args.data)
    
    # Build model
    trainer.build_cnn_model(model_type=args.model)
    
    # Train model
    trainer.train(
        X_train, y_train, X_val, y_val,
        epochs=args.epochs,
        batch_size=args.batch_size,
        use_augmentation=not args.no_augmentation
    )
    
    # Evaluate model
    trainer.evaluate(X_test, y_test)
    
    # Plot training history
    plot_path = os.path.join(args.save_path, 'training_history.png')
    trainer.plot_training_history(save_path=plot_path)
    
    # Save final model
    trainer.save_model('face_emotion_model_final.h5')
    
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print(f"Model saved to: {args.save_path}")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()

# Made with Bob
