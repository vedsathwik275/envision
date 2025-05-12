"""
Terminal-Based Neural Network Trainer
Model Training Component
"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np
import pickle
import os
import json

class ModelTrainer:
    """
    Manages neural network model generation, training, and saving.
    """
    
    def __init__(self):
        """Initialize the ModelTrainer."""
        self.model = None
        self.model_info = {}
        
    def generate_model(self, input_shape, output_shape):
        """
        Generate a simple neural network model.
        
        Args:
            input_shape (int): Number of input features
            output_shape (int): Number of output classes or 1 for regression/binary classification
            
        Returns:
            tensorflow.keras.Model: The generated model
        """
        self.model = Sequential()
        
        # Add layers to the model
        # Input layer with more neurons for complex problems
        self.model.add(Dense(128, activation='relu', input_shape=(input_shape,)))
        self.model.add(Dropout(0.2))
        
        # Hidden layers
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dropout(0.2))
        
        # Output layer
        if output_shape == 1:  # Binary classification or regression
            self.model.add(Dense(1, activation='sigmoid'))
            self.model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
            self.model_info['problem_type'] = 'binary_classification'
        else:  # Multi-class classification
            self.model.add(Dense(output_shape, activation='softmax'))
            self.model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
            self.model_info['problem_type'] = 'multi_class_classification'
        
        # Store model architecture info
        self.model_info['input_shape'] = input_shape
        self.model_info['output_shape'] = output_shape
        self.model_info['architecture'] = 'sequential'
        self.model_info['layers'] = [
            {'type': 'dense', 'units': 128, 'activation': 'relu'},
            {'type': 'dropout', 'rate': 0.2},
            {'type': 'dense', 'units': 64, 'activation': 'relu'},
            {'type': 'dropout', 'rate': 0.2},
            {'type': 'dense', 'units': 32, 'activation': 'relu'},
            {'type': 'dropout', 'rate': 0.2},
            {'type': 'dense', 'units': output_shape if output_shape > 1 else 1, 
             'activation': 'softmax' if output_shape > 1 else 'sigmoid'}
        ]
        
        return self.model
    
    def train_model(self, X, y, epochs=100, batch_size=32, validation_split=0.2):
        """
        Train the neural network model.
        
        Args:
            X (numpy.ndarray): Input features
            y (numpy.ndarray): Target values
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            validation_split (float): Fraction of data to use for validation
            
        Returns:
            tensorflow.keras.callbacks.History: Training history
        """
        # Convert to numpy arrays if needed
        if not isinstance(X, np.ndarray):
            X = X.toarray()  # In case of sparse matrix
            
        # Handle output shape
        if len(np.unique(y)) == 2:  # Binary classification
            output_shape = 1
        else:  # Multi-class classification
            output_shape = len(np.unique(y))
            # One-hot encode the target
            y = tf.keras.utils.to_categorical(y)
        
        # Generate model if not already done
        if self.model is None:
            self.generate_model(X.shape[1], output_shape)
        
        # Add early stopping to prevent overfitting
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train the model
        history = self.model.fit(
            X, y, 
            epochs=epochs, 
            batch_size=batch_size, 
            validation_split=validation_split, 
            verbose=1,
            callbacks=[early_stopping]
        )
        
        # Store training info
        self.model_info['training'] = {
            'epochs': epochs,
            'batch_size': batch_size,
            'validation_split': validation_split,
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1])
        }
        
        if 'accuracy' in history.history:
            self.model_info['training']['final_accuracy'] = float(history.history['accuracy'][-1])
            self.model_info['training']['final_val_accuracy'] = float(history.history['val_accuracy'][-1])
        
        return history
    
    def save_model(self, model_path, preprocessing_pipeline=None, label_encoder=None):
        """
        Save the trained model and preprocessing pipeline.
        
        Args:
            model_path (str): Path to save the model
            preprocessing_pipeline: Sklearn preprocessing pipeline
            label_encoder: Label encoder for classification
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(model_path) if os.path.dirname(model_path) else '.', exist_ok=True)
            
            # Add timestamp to model info
            import datetime
            self.model_info['timestamp'] = datetime.datetime.now().isoformat()
            
            # Save the Keras model
            self.model.save(model_path)
            
            # Save the preprocessing pipeline if provided
            if preprocessing_pipeline is not None:
                with open(f"{model_path}_pipeline.pkl", 'wb') as f:
                    pickle.dump(preprocessing_pipeline, f)
                self.model_info['has_preprocessing_pipeline'] = True
            
            # Save the label encoder if provided
            if label_encoder is not None:
                with open(f"{model_path}_label_encoder.pkl", 'wb') as f:
                    pickle.dump(label_encoder, f)
                self.model_info['has_label_encoder'] = True
            
            # Save model info as JSON
            with open(f"{model_path}_info.json", 'w') as f:
                json.dump(self.model_info, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving model: {str(e)}")
            return False
    
    def evaluate_model(self, X, y):
        """
        Evaluate the model on test data.
        
        Args:
            X (numpy.ndarray): Test features
            y (numpy.ndarray): Test targets
            
        Returns:
            dict: Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model must be trained before evaluation.")
        
        # Convert to numpy arrays if needed
        if not isinstance(X, np.ndarray):
            X = X.toarray()  # In case of sparse matrix
        
        # Handle classification vs regression
        if self.model_info.get('problem_type', '').endswith('classification'):
            # For classification, check if y needs to be one-hot encoded
            if len(y.shape) == 1 and self.model_info.get('output_shape', 0) > 1:
                y = tf.keras.utils.to_categorical(y)
        
        # Evaluate the model
        metrics = self.model.evaluate(X, y, verbose=0)
        
        # Create metrics dictionary
        metric_names = self.model.metrics_names
        evaluation = {metric_names[i]: float(metrics[i]) for i in range(len(metric_names))}
        
        return evaluation