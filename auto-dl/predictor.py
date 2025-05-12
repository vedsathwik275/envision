"""
Terminal-Based Neural Network Trainer
Prediction Component
"""

import tensorflow as tf
import pickle
import numpy as np
import json
import os

class Predictor:
    """
    Loads trained models and makes predictions on new data.
    """
    
    def __init__(self):
        """Initialize the Predictor."""
        self.model = None
        self.preprocessing_pipeline = None
        self.label_encoder = None
        self.model_info = None
    
    def load_model(self, model_path):
        """
        Load a trained model and preprocessing pipeline.
        
        Args:
            model_path (str): Path to the trained model
            
        Returns:
            bool or tuple: True if successful, (False, error_message) if failed
        """
        try:
            # Load the Keras model
            self.model = tf.keras.models.load_model(model_path)
            
            # Check for preprocessing pipeline
            pipeline_path = f"{model_path}_pipeline.pkl"
            if os.path.exists(pipeline_path):
                with open(pipeline_path, 'rb') as f:
                    self.preprocessing_pipeline = pickle.load(f)
            
            # Check for label encoder
            label_encoder_path = f"{model_path}_label_encoder.pkl"
            if os.path.exists(label_encoder_path):
                with open(label_encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
            
            # Load model info if available
            info_path = f"{model_path}_info.json"
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    self.model_info = json.load(f)
            
            return True
        except Exception as e:
            return False, str(e)
    
    def predict(self, data):
        """
        Make predictions using the loaded model.
        
        Args:
            data (pandas.DataFrame): Input data for prediction
            
        Returns:
            numpy.ndarray or tuple: Predictions if successful, (False, error_message) if failed
        """
        if self.model is None:
            return False, "Model not loaded."
        
        try:
            # Preprocess the data using the pipeline if available
            if self.preprocessing_pipeline is not None:
                processed_data = self.preprocessing_pipeline.transform(data)
                
                # Convert to numpy array if needed
                if not isinstance(processed_data, np.ndarray):
                    processed_data = processed_data.toarray()
            else:
                # If no preprocessing pipeline, assume data is already in correct format
                processed_data = data.values
            
            # Make predictions
            predictions = self.model.predict(processed_data)
            
            # For multi-class classification, return probabilities for all classes
            # For binary classification, return probability of positive class
            # For regression, return predicted values
            
            return True, predictions
        except Exception as e:
            return False, str(e)
    
    def get_model_info(self):
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model information or None if not available
        """
        return self.model_info
    
    def decode_predictions(self, predictions):
        """
        Decode numerical predictions to original labels for classification problems.
        
        Args:
            predictions (numpy.ndarray): Model predictions
            
        Returns:
            numpy.ndarray: Decoded predictions or original predictions if not classification
        """
        if self.model_info is None or self.label_encoder is None:
            return predictions
        
        if self.model_info.get('problem_type', '').endswith('classification'):
            # For multi-class, get the class with highest probability
            if len(predictions.shape) > 1 and predictions.shape[1] > 1:
                class_indices = np.argmax(predictions, axis=1)
                return self.label_encoder.inverse_transform(class_indices)
            # For binary, threshold at 0.5
            elif len(predictions.shape) <= 1 or predictions.shape[1] == 1:
                class_indices = (predictions > 0.5).astype(int)
                return self.label_encoder.inverse_transform(class_indices.flatten())
        
        return predictions