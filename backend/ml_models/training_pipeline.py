"""
Model Training Pipeline
Handles data preparation, model training, evaluation, and comparison
"""
import numpy as np
import os
import json
import logging
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

from .cnn_model import EEGEmotionCNN
from .lstm_model import EEGEmotionLSTM

logger = logging.getLogger(__name__)


class ModelTrainingPipeline:
    """
    Complete pipeline for training and evaluating EEG emotion recognition models
    """
    
    def __init__(self, model_type='cnn', save_dir='trained_models'):
        """
        Initialize the training pipeline
        
        Args:
            model_type (str): Type of model ('cnn' or 'lstm')
            save_dir (str): Directory to save trained models
        """
        self.model_type = model_type.lower()
        self.save_dir = save_dir
        self.model = None
        self.label_encoder = LabelEncoder()
        self.training_history = None
        self.evaluation_results = None
        
        # Create save directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
    def prepare_data(self, X, y, test_size=0.2, val_size=0.1, random_state=42):
        """
        Prepare data for training
        
        Args:
            X (np.ndarray): Feature data
            y (np.ndarray): Labels
            test_size (float): Proportion of test set
            val_size (float): Proportion of validation set
            random_state (int): Random seed
            
        Returns:
            tuple: (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        try:
            # Encode labels if they are strings
            if y.dtype == object or isinstance(y[0], str):
                y = self.label_encoder.fit_transform(y)
            
            # Split into train+val and test
            X_temp, X_test, y_temp, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            # Split train+val into train and val
            val_size_adjusted = val_size / (1 - test_size)
            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp, test_size=val_size_adjusted, 
                random_state=random_state, stratify=y_temp
            )
            
            logger.info(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
            
            return X_train, X_val, X_test, y_train, y_val, y_test
            
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            raise
    
    def reshape_for_cnn(self, X):
        """
        Reshape data for CNN input (add channel dimension)
        
        Args:
            X (np.ndarray): Input data
            
        Returns:
            np.ndarray: Reshaped data
        """
        if len(X.shape) == 3:
            # Add channel dimension: (samples, height, width) -> (samples, height, width, 1)
            return np.expand_dims(X, axis=-1)
        return X
    
    def reshape_for_lstm(self, X):
        """
        Reshape data for LSTM input
        
        Args:
            X (np.ndarray): Input data
            
        Returns:
            np.ndarray: Reshaped data
        """
        if len(X.shape) == 3 and X.shape[-1] == 1:
            # Remove channel dimension: (samples, height, width, 1) -> (samples, height, width)
            return np.squeeze(X, axis=-1)
        return X
    
    def train_model(self, X_train, y_train, X_val=None, y_val=None,
                   epochs=50, batch_size=32, learning_rate=0.001):
        """
        Train the model
        
        Args:
            X_train (np.ndarray): Training data
            y_train (np.ndarray): Training labels
            X_val (np.ndarray): Validation data
            y_val (np.ndarray): Validation labels
            epochs (int): Number of epochs
            batch_size (int): Batch size
            learning_rate (float): Learning rate
            
        Returns:
            dict: Training history
        """
        try:
            # Reshape data based on model type
            if self.model_type == 'cnn':
                X_train = self.reshape_for_cnn(X_train)
                if X_val is not None:
                    X_val = self.reshape_for_cnn(X_val)
                
                # Create and train CNN model
                self.model = EEGEmotionCNN(
                    input_shape=X_train.shape[1:],
                    num_classes=len(np.unique(y_train)),
                    learning_rate=learning_rate
                )
                self.model.build_model()
                
            elif self.model_type == 'lstm':
                X_train = self.reshape_for_lstm(X_train)
                if X_val is not None:
                    X_val = self.reshape_for_lstm(X_val)
                
                # Create and train LSTM model
                self.model = EEGEmotionLSTM(
                    input_shape=X_train.shape[1:],
                    num_classes=len(np.unique(y_train)),
                    learning_rate=learning_rate
                )
                self.model.build_model()
                
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
            
            # Train the model
            logger.info(f"Training {self.model_type.upper()} model...")
            self.training_history = self.model.train(
                X_train, y_train, X_val, y_val,
                epochs=epochs, batch_size=batch_size
            )
            
            return self.training_history
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def evaluate_model(self, X_test, y_test):
        """
        Evaluate the trained model
        
        Args:
            X_test (np.ndarray): Test data
            y_test (np.ndarray): Test labels
            
        Returns:
            dict: Evaluation results
        """
        try:
            if self.model is None:
                raise ValueError("Model not trained yet")
            
            # Reshape data based on model type
            if self.model_type == 'cnn':
                X_test = self.reshape_for_cnn(X_test)
            elif self.model_type == 'lstm':
                X_test = self.reshape_for_lstm(X_test)
            
            # Evaluate
            logger.info(f"Evaluating {self.model_type.upper()} model...")
            self.evaluation_results = self.model.evaluate(X_test, y_test)
            
            return self.evaluation_results
            
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise
    
    def save_model(self, model_name=None):
        """
        Save the trained model
        
        Args:
            model_name (str): Name for the saved model
            
        Returns:
            str: Path to saved model
        """
        try:
            if self.model is None:
                raise ValueError("No model to save")
            
            if model_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                model_name = f"{self.model_type}_model_{timestamp}.h5"
            
            filepath = os.path.join(self.save_dir, model_name)
            self.model.save_model(filepath)
            
            # Save training history and evaluation results
            metadata = {
                'model_type': self.model_type,
                'training_history': self.training_history,
                'evaluation_results': self.evaluation_results,
                'timestamp': datetime.now().isoformat()
            }
            
            metadata_path = filepath.replace('.h5', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)
            
            logger.info(f"Model saved to {filepath}")
            return filepath
            
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
            if self.model_type == 'cnn':
                self.model = EEGEmotionCNN()
            elif self.model_type == 'lstm':
                self.model = EEGEmotionLSTM()
            
            self.model.load_model(filepath)
            
            # Load metadata if available
            metadata_path = filepath.replace('.h5', '_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.training_history = metadata.get('training_history')
                    self.evaluation_results = metadata.get('evaluation_results')
            
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def plot_training_history(self, save_path=None):
        """
        Plot training history
        
        Args:
            save_path (str): Path to save the plot
        """
        try:
            if self.training_history is None:
                raise ValueError("No training history available")
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # Plot accuracy
            axes[0, 0].plot(self.training_history['accuracy'], label='Train')
            if 'val_accuracy' in self.training_history:
                axes[0, 0].plot(self.training_history['val_accuracy'], label='Validation')
            axes[0, 0].set_title('Model Accuracy')
            axes[0, 0].set_xlabel('Epoch')
            axes[0, 0].set_ylabel('Accuracy')
            axes[0, 0].legend()
            axes[0, 0].grid(True)
            
            # Plot loss
            axes[0, 1].plot(self.training_history['loss'], label='Train')
            if 'val_loss' in self.training_history:
                axes[0, 1].plot(self.training_history['val_loss'], label='Validation')
            axes[0, 1].set_title('Model Loss')
            axes[0, 1].set_xlabel('Epoch')
            axes[0, 1].set_ylabel('Loss')
            axes[0, 1].legend()
            axes[0, 1].grid(True)
            
            # Plot precision
            if 'precision' in self.training_history:
                axes[1, 0].plot(self.training_history['precision'], label='Train')
                if 'val_precision' in self.training_history:
                    axes[1, 0].plot(self.training_history['val_precision'], label='Validation')
                axes[1, 0].set_title('Model Precision')
                axes[1, 0].set_xlabel('Epoch')
                axes[1, 0].set_ylabel('Precision')
                axes[1, 0].legend()
                axes[1, 0].grid(True)
            
            # Plot recall
            if 'recall' in self.training_history:
                axes[1, 1].plot(self.training_history['recall'], label='Train')
                if 'val_recall' in self.training_history:
                    axes[1, 1].plot(self.training_history['val_recall'], label='Validation')
                axes[1, 1].set_title('Model Recall')
                axes[1, 1].set_xlabel('Epoch')
                axes[1, 1].set_ylabel('Recall')
                axes[1, 1].legend()
                axes[1, 1].grid(True)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path)
                logger.info(f"Training history plot saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting training history: {str(e)}")
            raise


def compare_models(X_train, y_train, X_val, y_val, X_test, y_test,
                  epochs=50, batch_size=32):
    """
    Train and compare CNN and LSTM models
    
    Args:
        X_train, y_train: Training data
        X_val, y_val: Validation data
        X_test, y_test: Test data
        epochs (int): Number of epochs
        batch_size (int): Batch size
        
    Returns:
        dict: Comparison results
    """
    results = {}
    
    # Train CNN
    logger.info("Training CNN model...")
    cnn_pipeline = ModelTrainingPipeline(model_type='cnn')
    cnn_pipeline.train_model(X_train, y_train, X_val, y_val, epochs, batch_size)
    cnn_results = cnn_pipeline.evaluate_model(X_test, y_test)
    cnn_pipeline.save_model('best_cnn_model.h5')
    results['cnn'] = cnn_results
    
    # Train LSTM
    logger.info("Training LSTM model...")
    lstm_pipeline = ModelTrainingPipeline(model_type='lstm')
    lstm_pipeline.train_model(X_train, y_train, X_val, y_val, epochs, batch_size)
    lstm_results = lstm_pipeline.evaluate_model(X_test, y_test)
    lstm_pipeline.save_model('best_lstm_model.h5')
    results['lstm'] = lstm_results
    
    # Compare
    logger.info("\n=== Model Comparison ===")
    logger.info(f"CNN Accuracy: {cnn_results['accuracy']:.4f}")
    logger.info(f"LSTM Accuracy: {lstm_results['accuracy']:.4f}")
    
    if cnn_results['accuracy'] > lstm_results['accuracy']:
        logger.info("CNN performs better!")
        results['best_model'] = 'cnn'
    else:
        logger.info("LSTM performs better!")
        results['best_model'] = 'lstm'
    
    return results

# Made with Bob
