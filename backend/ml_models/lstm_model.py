"""
LSTM Model for EEG Emotion Recognition
Implements a Long Short-Term Memory network for classifying emotions from EEG signals
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import logging

logger = logging.getLogger(__name__)


class EEGEmotionLSTM:
    """
    LSTM model for EEG-based emotion recognition
    Architecture designed for temporal analysis of EEG signals
    """
    
    def __init__(self, input_shape=(256, 32), num_classes=6, learning_rate=0.001):
        """
        Initialize the LSTM model
        
        Args:
            input_shape (tuple): Shape of input data (timesteps, features)
            num_classes (int): Number of emotion classes (default: 6)
            learning_rate (float): Learning rate for optimizer
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.model = None
        self.history = None
        
        # Emotion labels
        self.emotion_labels = ['happy', 'sad', 'angry', 'relaxed', 'excited', 'stressed']
        
    def build_model(self):
        """
        Build the LSTM architecture
        
        Returns:
            keras.Model: Compiled LSTM model
        """
        try:
            model = models.Sequential([
                # First LSTM Layer
                layers.LSTM(128, return_sequences=True, input_shape=self.input_shape),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                
                # Second LSTM Layer
                layers.LSTM(128, return_sequences=True),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                
                # Third LSTM Layer
                layers.LSTM(64, return_sequences=True),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                
                # Fourth LSTM Layer
                layers.LSTM(64, return_sequences=False),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                
                # Dense Layers
                layers.Dense(128, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(0.5),
                
                layers.Dense(64, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(0.5),
                
                # Output Layer
                layers.Dense(self.num_classes, activation='softmax')
            ])
            
            # Compile the model
            model.compile(
                optimizer=Adam(learning_rate=self.learning_rate),
                loss='categorical_crossentropy',
                metrics=['accuracy', 'precision', 'recall']
            )
            
            self.model = model
            logger.info("LSTM model built successfully")
            logger.info(f"Model parameters: {model.count_params()}")
            
            return model
            
        except Exception as e:
            logger.error(f"Error building LSTM model: {str(e)}")
            raise
    
    def build_bidirectional_model(self):
        """
        Build a Bidirectional LSTM architecture for better temporal understanding
        
        Returns:
            keras.Model: Compiled Bidirectional LSTM model
        """
        try:
            model = models.Sequential([
                # First Bidirectional LSTM Layer
                layers.Bidirectional(
                    layers.LSTM(128, return_sequences=True),
                    input_shape=self.input_shape
                ),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                
                # Second Bidirectional LSTM Layer
                layers.Bidirectional(layers.LSTM(128, return_sequences=True)),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                
                # Third Bidirectional LSTM Layer
                layers.Bidirectional(layers.LSTM(64, return_sequences=False)),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                
                # Dense Layers
                layers.Dense(128, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(0.5),
                
                layers.Dense(64, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(0.5),
                
                # Output Layer
                layers.Dense(self.num_classes, activation='softmax')
            ])
            
            # Compile the model
            model.compile(
                optimizer=Adam(learning_rate=self.learning_rate),
                loss='categorical_crossentropy',
                metrics=['accuracy', 'precision', 'recall']
            )
            
            self.model = model
            logger.info("Bidirectional LSTM model built successfully")
            logger.info(f"Model parameters: {model.count_params()}")
            
            return model
            
        except Exception as e:
            logger.error(f"Error building Bidirectional LSTM model: {str(e)}")
            raise
    
    def get_model_summary(self):
        """Get model architecture summary"""
        if self.model is None:
            self.build_model()
        return self.model.summary()
    
    def train(self, X_train, y_train, X_val=None, y_val=None, 
              epochs=50, batch_size=32, verbose=1):
        """
        Train the LSTM model
        
        Args:
            X_train (np.ndarray): Training data
            y_train (np.ndarray): Training labels
            X_val (np.ndarray): Validation data (optional)
            y_val (np.ndarray): Validation labels (optional)
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            verbose (int): Verbosity level
            
        Returns:
            dict: Training history
        """
        try:
            if self.model is None:
                self.build_model()
            
            # Convert labels to categorical if needed
            if len(y_train.shape) == 1:
                y_train = to_categorical(y_train, self.num_classes)
            if y_val is not None and len(y_val.shape) == 1:
                y_val = to_categorical(y_val, self.num_classes)
            
            # Prepare callbacks
            callback_list = [
                callbacks.EarlyStopping(
                    monitor='val_loss' if X_val is not None else 'loss',
                    patience=15,
                    restore_best_weights=True,
                    verbose=1
                ),
                callbacks.ReduceLROnPlateau(
                    monitor='val_loss' if X_val is not None else 'loss',
                    factor=0.5,
                    patience=7,
                    min_lr=1e-7,
                    verbose=1
                ),
                callbacks.ModelCheckpoint(
                    'best_lstm_model.h5',
                    monitor='val_accuracy' if X_val is not None else 'accuracy',
                    save_best_only=True,
                    verbose=1
                )
            ]
            
            # Train the model
            validation_data = (X_val, y_val) if X_val is not None else None
            
            history = self.model.fit(
                X_train, y_train,
                validation_data=validation_data,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callback_list,
                verbose=verbose
            )
            
            self.history = history.history
            logger.info("Model training completed")
            
            return self.history
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {str(e)}")
            raise
    
    def predict(self, X, return_probabilities=False):
        """
        Make predictions on new data
        
        Args:
            X (np.ndarray): Input data
            return_probabilities (bool): Whether to return class probabilities
            
        Returns:
            np.ndarray: Predictions (class indices or probabilities)
        """
        try:
            if self.model is None:
                raise ValueError("Model not built or loaded")
            
            predictions = self.model.predict(X)
            
            if return_probabilities:
                return predictions
            else:
                return np.argmax(predictions, axis=1)
                
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise
    
    def predict_single(self, X):
        """
        Predict emotion for a single EEG sample
        
        Args:
            X (np.ndarray): Single EEG sample
            
        Returns:
            dict: Prediction results with emotion and confidence
        """
        try:
            if len(X.shape) == 2:
                X = np.expand_dims(X, axis=0)
            
            probabilities = self.predict(X, return_probabilities=True)[0]
            predicted_class = np.argmax(probabilities)
            confidence = probabilities[predicted_class] * 100
            
            result = {
                'emotion': self.emotion_labels[predicted_class],
                'emotion_code': predicted_class,
                'confidence': float(confidence),
                'probabilities': {
                    emotion: float(prob * 100) 
                    for emotion, prob in zip(self.emotion_labels, probabilities)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in single prediction: {str(e)}")
            raise
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        
        Args:
            X_test (np.ndarray): Test data
            y_test (np.ndarray): Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        try:
            if self.model is None:
                raise ValueError("Model not built or loaded")
            
            # Convert labels to categorical if needed
            if len(y_test.shape) == 1:
                y_test_cat = to_categorical(y_test, self.num_classes)
            else:
                y_test_cat = y_test
            
            # Evaluate
            results = self.model.evaluate(X_test, y_test_cat, verbose=0)
            
            # Get predictions for confusion matrix
            predictions = self.predict(X_test)
            y_true = np.argmax(y_test_cat, axis=1) if len(y_test.shape) > 1 else y_test
            
            # Calculate confusion matrix
            from sklearn.metrics import confusion_matrix, classification_report
            cm = confusion_matrix(y_true, predictions)
            report = classification_report(
                y_true, predictions, 
                target_names=self.emotion_labels,
                output_dict=True
            )
            
            evaluation = {
                'loss': float(results[0]),
                'accuracy': float(results[1]),
                'precision': float(results[2]) if len(results) > 2 else None,
                'recall': float(results[3]) if len(results) > 3 else None,
                'confusion_matrix': cm.tolist(),
                'classification_report': report
            }
            
            logger.info(f"Model evaluation - Accuracy: {evaluation['accuracy']:.4f}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise
    
    def save_model(self, filepath):
        """
        Save the trained model
        
        Args:
            filepath (str): Path to save the model
        """
        try:
            if self.model is None:
                raise ValueError("No model to save")
            
            self.model.save(filepath)
            logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load_model(self, filepath):
        """
        Load a trained model
        
        Args:
            filepath (str): Path to the saved model
        """
        try:
            self.model = keras.models.load_model(filepath)
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def get_training_history(self):
        """Get training history"""
        return self.history


def create_lstm_model(input_shape=(256, 32), num_classes=6, bidirectional=False):
    """
    Convenience function to create and build an LSTM model
    
    Args:
        input_shape (tuple): Shape of input data
        num_classes (int): Number of emotion classes
        bidirectional (bool): Whether to use bidirectional LSTM
        
    Returns:
        EEGEmotionLSTM: Built LSTM model instance
    """
    lstm = EEGEmotionLSTM(input_shape=input_shape, num_classes=num_classes)
    if bidirectional:
        lstm.build_bidirectional_model()
    else:
        lstm.build_model()
    return lstm


def train_lstm_model(X_train, y_train, X_val=None, y_val=None, 
                    epochs=50, batch_size=32, bidirectional=False):
    """
    Convenience function to train an LSTM model
    
    Args:
        X_train (np.ndarray): Training data
        y_train (np.ndarray): Training labels
        X_val (np.ndarray): Validation data
        y_val (np.ndarray): Validation labels
        epochs (int): Number of epochs
        batch_size (int): Batch size
        bidirectional (bool): Whether to use bidirectional LSTM
        
    Returns:
        EEGEmotionLSTM: Trained LSTM model
    """
    lstm = create_lstm_model(input_shape=X_train.shape[1:], bidirectional=bidirectional)
    lstm.train(X_train, y_train, X_val, y_val, epochs, batch_size)
    return lstm

# Made with Bob
