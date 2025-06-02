#!/usr/bin/env python3
# Tender Performance Neural Network Model
# This script processes tender performance data, trains a neural network model,
# and generates predictions for tender performance by carrier and lane.

import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from datetime import datetime
import pickle
import logging
import json
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)

# Set random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

class TenderPerformanceModel:
    """
    Tender Performance Neural Network Model for predicting tender performance.
    
    This model handles both legacy city-only data and new data with expanded 
    geographic features including state and country information.
    """
    
    def __init__(self, data_path: Optional[str] = None, model_path: Optional[str] = None) -> None:
        """Initialize the Tender Performance prediction model.
        
        Args:
            data_path: Path to the CSV data file
            model_path: Path to load a pre-trained model
        """
        self.data_path = data_path
        self.model_path = model_path
        self.model = None
        self.carrier_encoder = None
        self.source_city_encoder = None
        self.source_state_encoder = None
        self.source_country_encoder = None
        self.dest_city_encoder = None
        self.dest_state_encoder = None
        self.dest_country_encoder = None
        self.scaler = None
        self.preprocessed_data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_columns = None
        self.data_format = None  # 'legacy' or 'new'
        
        # If data path is provided, load and preprocess the data
        if data_path:
            self.load_data()
        
        # If model path is provided, load the pre-trained model
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def _detect_data_format(self, data: pd.DataFrame) -> str:
        """Detect whether the data is in legacy or new format.
        
        Args:
            data: The loaded DataFrame
            
        Returns:
            'legacy' for city-only data, 'new' for data with state/country information
        """
        # Check for new format indicators
        has_state_columns = 'SOURCE_STATE' in data.columns and 'DEST_STATE' in data.columns
        has_country_columns = 'SOURCE_COUNTRY' in data.columns and 'DEST_COUNTRY' in data.columns
        
        # Check for legacy format indicator (could be either column name)
        has_legacy_target = 'TENDER_PERF_PERCENTAGE' in data.columns
        has_new_target = 'TENDER_PERFORMANCE' in data.columns
        
        if has_state_columns and has_country_columns and (has_new_target or has_legacy_target):
            return 'new'
        elif (has_legacy_target or has_new_target):
            return 'legacy'
        else:
            # Default to legacy if ambiguous
            logger.warning("Data format ambiguous, defaulting to legacy format")
            return 'legacy'
    
    def load_data(self) -> pd.DataFrame:
        """Load and perform initial preprocessing of the data."""
        logger.info(f"Loading data from {self.data_path}...")
        self.raw_data = pd.read_csv(self.data_path)
        
        # Detect data format
        self.data_format = self._detect_data_format(self.raw_data)
        logger.info(f"Detected data format: {self.data_format}")
        
        # Check data integrity
        if self.raw_data.isnull().sum().sum() > 0:
            logger.warning("Data contains missing values. Filling with appropriate values.")
            self.raw_data.fillna(0, inplace=True)
        
        # Standardize target column name
        if 'TENDER_PERF_PERCENTAGE' in self.raw_data.columns:
            self.target_column = 'TENDER_PERF_PERCENTAGE'
        elif 'TENDER_PERFORMANCE' in self.raw_data.columns:
            self.target_column = 'TENDER_PERFORMANCE'
        else:
            # Try to identify the performance column
            potential_columns = [col for col in self.raw_data.columns if 'perf' in col.lower() or 'rate' in col.lower()]
            if potential_columns:
                self.target_column = potential_columns[0]
                logger.info(f"Using {self.target_column} as the target column")
            else:
                raise ValueError("Could not identify the tender performance column in the data")
        
        logger.info(f"Data loaded successfully. Shape: {self.raw_data.shape}")
        return self.raw_data
    
    def preprocess_data(self) -> pd.DataFrame:
        """Preprocess the data for training the neural network."""
        logger.info("Preprocessing data...")
        
        # Create a copy of the raw data
        data = self.raw_data.copy()
        
        if self.data_format == 'new':
            return self._preprocess_new_format(data)
        else:
            return self._preprocess_legacy_format(data)
    
    def _preprocess_new_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data in the new format with expanded location data."""
        logger.info("Preprocessing new format data with expanded location features...")
        
        # Create comprehensive lane identifier
        data['LANE_ID'] = (data['SOURCE_CITY'] + '_' + data['SOURCE_STATE'] + '_' + 
                          data['SOURCE_COUNTRY'] + '_TO_' + data['DEST_CITY'] + '_' + 
                          data['DEST_STATE'] + '_' + data['DEST_COUNTRY'])
        
        # One-hot encoding for categorical variables
        logger.info("Encoding categorical variables for new format...")
        
        # Carrier encoding
        self.carrier_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        carrier_encoded = self.carrier_encoder.fit_transform(data[['CARRIER']])
        carrier_columns = [f'CARRIER_{i}' for i in range(carrier_encoded.shape[1])]
        carrier_df = pd.DataFrame(carrier_encoded, columns=carrier_columns)
        
        # Source location encoding
        self.source_city_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        source_city_encoded = self.source_city_encoder.fit_transform(data[['SOURCE_CITY']])
        source_city_columns = [f'SOURCE_CITY_{i}' for i in range(source_city_encoded.shape[1])]
        source_city_df = pd.DataFrame(source_city_encoded, columns=source_city_columns)
        
        self.source_state_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        source_state_encoded = self.source_state_encoder.fit_transform(data[['SOURCE_STATE']])
        source_state_columns = [f'SOURCE_STATE_{i}' for i in range(source_state_encoded.shape[1])]
        source_state_df = pd.DataFrame(source_state_encoded, columns=source_state_columns)
        
        self.source_country_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        source_country_encoded = self.source_country_encoder.fit_transform(data[['SOURCE_COUNTRY']])
        source_country_columns = [f'SOURCE_COUNTRY_{i}' for i in range(source_country_encoded.shape[1])]
        source_country_df = pd.DataFrame(source_country_encoded, columns=source_country_columns)
        
        # Destination location encoding - handle high cardinality for cities
        dest_city_counts = data['DEST_CITY'].value_counts()
        top_dest_cities = dest_city_counts.nlargest(50).index.tolist()  # Use top 50 destination cities
        data['DEST_CITY_GROUPED'] = data['DEST_CITY'].apply(lambda x: x if x in top_dest_cities else 'OTHER')
        
        self.dest_city_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        dest_city_encoded = self.dest_city_encoder.fit_transform(data[['DEST_CITY_GROUPED']])
        dest_city_columns = [f'DEST_CITY_{i}' for i in range(dest_city_encoded.shape[1])]
        dest_city_df = pd.DataFrame(dest_city_encoded, columns=dest_city_columns)
        
        self.dest_state_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        dest_state_encoded = self.dest_state_encoder.fit_transform(data[['DEST_STATE']])
        dest_state_columns = [f'DEST_STATE_{i}' for i in range(dest_state_encoded.shape[1])]
        dest_state_df = pd.DataFrame(dest_state_encoded, columns=dest_state_columns)
        
        self.dest_country_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        dest_country_encoded = self.dest_country_encoder.fit_transform(data[['DEST_COUNTRY']])
        dest_country_columns = [f'DEST_COUNTRY_{i}' for i in range(dest_country_encoded.shape[1])]
        dest_country_df = pd.DataFrame(dest_country_encoded, columns=dest_country_columns)
        
        # Reset indices to ensure proper concatenation
        data.reset_index(drop=True, inplace=True)
        carrier_df.reset_index(drop=True, inplace=True)
        source_city_df.reset_index(drop=True, inplace=True)
        source_state_df.reset_index(drop=True, inplace=True)
        source_country_df.reset_index(drop=True, inplace=True)
        dest_city_df.reset_index(drop=True, inplace=True)
        dest_state_df.reset_index(drop=True, inplace=True)
        dest_country_df.reset_index(drop=True, inplace=True)
        
        # Create the final processed dataset
        processed_data = pd.concat([
            data[[self.target_column]],
            carrier_df,
            source_city_df,
            source_state_df,
            source_country_df,
            dest_city_df,
            dest_state_df,
            dest_country_df
        ], axis=1)
        
        logger.info(f"New format data preprocessing complete. Processed shape: {processed_data.shape}")
        self.preprocessed_data = processed_data
        
        return processed_data
    
    def _preprocess_legacy_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data in the legacy format with city-only location data."""
        logger.info("Preprocessing legacy format data with city-only location features...")
        
        # Create lane identifier (combination of source and destination)
        data['LANE_ID'] = data['SOURCE_CITY'] + '_' + data['DEST_CITY']
        
        # One-hot encoding for categorical variables
        logger.info("Encoding categorical variables for legacy format...")
        
        # Carrier encoding
        self.carrier_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        carrier_encoded = self.carrier_encoder.fit_transform(data[['CARRIER']])
        carrier_columns = [f'CARRIER_{i}' for i in range(carrier_encoded.shape[1])]
        carrier_df = pd.DataFrame(carrier_encoded, columns=carrier_columns)
        
        # Source city encoding
        self.source_city_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        source_encoded = self.source_city_encoder.fit_transform(data[['SOURCE_CITY']])
        source_columns = [f'SOURCE_{i}' for i in range(source_encoded.shape[1])]
        source_df = pd.DataFrame(source_encoded, columns=source_columns)
        
        # Destination city encoding - handle high cardinality
        # Get top N destination cities
        dest_counts = data['DEST_CITY'].value_counts()
        top_dests = dest_counts.nlargest(50).index.tolist()  # Use top 50 destinations
        
        # Group less frequent destinations as 'OTHER'
        data['DEST_CITY_GROUPED'] = data['DEST_CITY'].apply(lambda x: x if x in top_dests else 'OTHER')
        
        # One-hot encode the grouped destinations
        self.dest_city_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        dest_encoded = self.dest_city_encoder.fit_transform(data[['DEST_CITY_GROUPED']])
        dest_columns = [f'DEST_{i}' for i in range(dest_encoded.shape[1])]
        dest_df = pd.DataFrame(dest_encoded, columns=dest_columns)
        
        # Reset indices to ensure proper concatenation
        data.reset_index(drop=True, inplace=True)
        carrier_df.reset_index(drop=True, inplace=True)
        source_df.reset_index(drop=True, inplace=True)
        dest_df.reset_index(drop=True, inplace=True)
        
        # Create the final processed dataset
        processed_data = pd.concat([
            data[[self.target_column]],
            carrier_df,
            source_df,
            dest_df
        ], axis=1)
        
        logger.info(f"Legacy format data preprocessing complete. Processed shape: {processed_data.shape}")
        self.preprocessed_data = processed_data
        
        return processed_data
    
    def prepare_train_test_split(self, test_size: float = 0.2) -> None:
        """Split the preprocessed data into training and testing sets."""
        logger.info(f"Splitting data with test_size={test_size}...")
        
        if self.preprocessed_data is None:
            self.preprocess_data()
        
        # Separate features and target
        X = self.preprocessed_data.drop(self.target_column, axis=1)
        y = self.preprocessed_data[self.target_column]
        
        # Store feature columns for prediction compatibility
        self.feature_columns = list(X.columns)
        
        # Normalize the target value to [0, 1] range
        y = y / 100.0
        
        # Split the data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        logger.info(f"Train set: {self.X_train.shape[0]} samples")
        logger.info(f"Test set: {self.X_test.shape[0]} samples")
        logger.info(f"Feature columns stored: {len(self.feature_columns)} features")
    
    def build_model(self):
        """Build the neural network model architecture."""
        logger.info("Building neural network model...")
        
        # Get input shape from training data
        input_dim = self.X_train.shape[1]
        
        # Create a sequential model with appropriate architecture for this data
        model = models.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # Sigmoid for [0,1] output
        ])
        
        # Compile the model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mean_squared_error',
            metrics=['mean_absolute_error']
        )
        
        self.model = model
        model.summary()
        return model
    
    def train(self, epochs=100, batch_size=32, validation_split=0.2, callbacks=None):
        """Train the neural network model."""
        logger.info(f"Training model with {epochs} epochs and batch_size={batch_size}...")
        
        if self.X_train is None or self.y_train is None:
            self.prepare_train_test_split()
        
        if self.model is None:
            self.build_model()
        
        # Add early stopping if no callbacks provided
        if callbacks is None:
            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    patience=10,
                    monitor='val_loss',
                    restore_best_weights=True
                )
            ]
        
        # Train the model
        history = self.model.fit(
            self.X_train, self.y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def evaluate(self, plot_path=None):
        """Evaluate the model on the test data and generate metrics."""
        logger.info("Evaluating model performance...")
        
        if self.model is None:
            logger.error("Model not trained yet. Call train() first.")
            return None
        
        # Make predictions on test data
        y_pred = self.model.predict(self.X_test)
        
        # Convert predictions back to original scale
        y_pred_scaled = y_pred * 100.0
        y_test_scaled = self.y_test * 100.0
        
        # Calculate metrics
        mae = mean_absolute_error(y_test_scaled, y_pred_scaled)
        mse = mean_squared_error(y_test_scaled, y_pred_scaled)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test_scaled, y_pred_scaled)
        
        logger.info(f"Mean Absolute Error: {mae:.2f}")
        logger.info(f"Root Mean Squared Error: {rmse:.2f}")
        logger.info(f"R² Score: {r2:.4f}")
        
        # Create an evaluation plot if path provided
        if plot_path:
            plt.figure(figsize=(10, 6))
            plt.scatter(y_test_scaled, y_pred_scaled, alpha=0.5)
            plt.plot([0, 100], [0, 100], 'r--')
            plt.xlabel('Actual Tender Performance (%)')
            plt.ylabel('Predicted Tender Performance (%)')
            plt.title('Tender Performance Prediction Model Evaluation')
            plt.savefig(plot_path)
            plt.close()
            logger.info(f"Evaluation plot saved to {plot_path}")
        
        # Return metrics as a dictionary
        return {
            "mae": mae,
            "mse": mse,
            "rmse": rmse,
            "r2": r2
        }
    
    def predict(self, carrier: str, source_city: str, dest_city: str, 
                source_state: Optional[str] = None, source_country: Optional[str] = None,
                dest_state: Optional[str] = None, dest_country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Predict tender performance for a specific carrier and lane.
        
        This method supports both legacy (city-only) and new (state/country) formats.
        The format is automatically detected based on available parameters and model training.
        
        Args:
            carrier: Carrier code
            source_city: Source city name
            dest_city: Destination city name
            source_state: Source state (optional, for new format)
            source_country: Source country (optional, for new format)
            dest_state: Destination state (optional, for new format)
            dest_country: Destination country (optional, for new format)
            
        Returns:
            Dictionary with prediction results or None if prediction fails
        """
        # Determine which format to use
        has_location_params = all([source_state, source_country, dest_state, dest_country])
        
        if self.data_format == 'new' or has_location_params:
            return self._predict_new_format(
                carrier, source_city, dest_city, 
                source_state, source_country, dest_state, dest_country
            )
        else:
            return self._predict_legacy_format(carrier, source_city, dest_city)
    
    def _predict_new_format(self, carrier: str, source_city: str, dest_city: str,
                           source_state: str, source_country: str, dest_state: str, 
                           dest_country: str) -> Optional[Dict[str, Any]]:
        """Predict tender performance using the new format with state/country information."""
        logger.info(f"Predicting performance (new format) for {carrier} from {source_city}, {source_state}, {source_country} to {dest_city}, {dest_state}, {dest_country}...")
        
        if self.model is None:
            logger.error("Model not loaded or trained. Cannot make predictions.")
            return None
            
        # Ensure required encoders are available
        required_encoders = [
            self.carrier_encoder, self.source_city_encoder, self.source_state_encoder,
            self.source_country_encoder, self.dest_city_encoder, self.dest_state_encoder,
            self.dest_country_encoder
        ]
        
        if any(encoder is None for encoder in required_encoders):
            logger.error("One or more required encoders not initialized for new format")
            return None
        
        try:
            # Create a sample dataframe
            sample = pd.DataFrame({
                'CARRIER': [carrier],
                'SOURCE_CITY': [source_city],
                'SOURCE_STATE': [source_state],
                'SOURCE_COUNTRY': [source_country],
                'DEST_CITY': [dest_city],
                'DEST_STATE': [dest_state],
                'DEST_COUNTRY': [dest_country]
            })
            
            # Handle destination cities not in the training data
            dest_city_categories = self.dest_city_encoder.categories_[0]
            if dest_city not in dest_city_categories:
                logger.warning(f"Destination city {dest_city} not found in training data. Using 'OTHER'.")
                sample['DEST_CITY_GROUPED'] = ['OTHER']
            else:
                sample['DEST_CITY_GROUPED'] = [dest_city]
            
            # Transform all categorical features
            carrier_encoded = self.carrier_encoder.transform(sample[['CARRIER']])
            source_city_encoded = self.source_city_encoder.transform(sample[['SOURCE_CITY']])
            source_state_encoded = self.source_state_encoder.transform(sample[['SOURCE_STATE']])
            source_country_encoded = self.source_country_encoder.transform(sample[['SOURCE_COUNTRY']])
            dest_city_encoded = self.dest_city_encoder.transform(sample[['DEST_CITY_GROUPED']])
            dest_state_encoded = self.dest_state_encoder.transform(sample[['DEST_STATE']])
            dest_country_encoded = self.dest_country_encoder.transform(sample[['DEST_COUNTRY']])
            
            # Create feature dataframes
            carrier_df = pd.DataFrame(carrier_encoded, columns=[f'CARRIER_{i}' for i in range(carrier_encoded.shape[1])])
            source_city_df = pd.DataFrame(source_city_encoded, columns=[f'SOURCE_CITY_{i}' for i in range(source_city_encoded.shape[1])])
            source_state_df = pd.DataFrame(source_state_encoded, columns=[f'SOURCE_STATE_{i}' for i in range(source_state_encoded.shape[1])])
            source_country_df = pd.DataFrame(source_country_encoded, columns=[f'SOURCE_COUNTRY_{i}' for i in range(source_country_encoded.shape[1])])
            dest_city_df = pd.DataFrame(dest_city_encoded, columns=[f'DEST_CITY_{i}' for i in range(dest_city_encoded.shape[1])])
            dest_state_df = pd.DataFrame(dest_state_encoded, columns=[f'DEST_STATE_{i}' for i in range(dest_state_encoded.shape[1])])
            dest_country_df = pd.DataFrame(dest_country_encoded, columns=[f'DEST_COUNTRY_{i}' for i in range(dest_country_encoded.shape[1])])
            
            # Combine all features
            features = pd.concat([
                carrier_df, source_city_df, source_state_df, source_country_df,
                dest_city_df, dest_state_df, dest_country_df
            ], axis=1)
            
            # Ensure feature order matches training data
            if hasattr(self, 'feature_columns') and self.feature_columns is not None:
                features = features.reindex(columns=self.feature_columns, fill_value=0)
            
            # Make prediction
            prediction = self.model.predict(features, verbose=0)[0][0]
            
            # Scale prediction back to percentage
            prediction_percent = prediction * 100.0
            
            logger.info(f"Predicted tender performance: {prediction_percent:.2f}%")
            
            result = {
                "carrier": carrier,
                "source_city": source_city,
                "source_state": source_state,
                "source_country": source_country,
                "dest_city": dest_city,
                "dest_state": dest_state,
                "dest_country": dest_country,
                "predicted_performance": float(prediction_percent)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting tender performance (new format): {str(e)}")
            return None
    
    def _predict_legacy_format(self, carrier: str, source_city: str, dest_city: str) -> Optional[Dict[str, Any]]:
        """Predict tender performance using the legacy format with city-only information."""
        logger.info(f"Predicting performance (legacy format) for {carrier} from {source_city} to {dest_city}...")
        
        if self.model is None:
            logger.error("Model not loaded or trained. Cannot make predictions.")
            return None
            
        # Ensure required encoders are available
        if any(encoder is None for encoder in [self.carrier_encoder, self.source_city_encoder, self.dest_city_encoder]):
            logger.error("One or more required encoders not initialized for legacy format")
            return None
        
        try:
            # Create a sample dataframe
            sample = pd.DataFrame({
                'CARRIER': [carrier],
                'SOURCE_CITY': [source_city],
                'DEST_CITY': [dest_city]
            })
            
            # Handle destination cities not in the training data
            dest_city_categories = self.dest_city_encoder.categories_[0]
            if dest_city not in dest_city_categories:
                logger.warning(f"Destination city {dest_city} not found in training data. Using 'OTHER'.")
                sample['DEST_CITY_GROUPED'] = ['OTHER']
            else:
                sample['DEST_CITY_GROUPED'] = [dest_city]
            
            # Transform the categorical features
            carrier_encoded = self.carrier_encoder.transform(sample[['CARRIER']])
            source_encoded = self.source_city_encoder.transform(sample[['SOURCE_CITY']])
            dest_encoded = self.dest_city_encoder.transform(sample[['DEST_CITY_GROUPED']])
            
            # Create feature dataframes
            carrier_df = pd.DataFrame(carrier_encoded, columns=[f'CARRIER_{i}' for i in range(carrier_encoded.shape[1])])
            source_df = pd.DataFrame(source_encoded, columns=[f'SOURCE_{i}' for i in range(source_encoded.shape[1])])
            dest_df = pd.DataFrame(dest_encoded, columns=[f'DEST_{i}' for i in range(dest_encoded.shape[1])])
            
            # Combine features
            features = pd.concat([carrier_df, source_df, dest_df], axis=1)
            
            # Ensure feature order matches training data
            if hasattr(self, 'feature_columns') and self.feature_columns is not None:
                features = features.reindex(columns=self.feature_columns, fill_value=0)
            
            # Make prediction
            prediction = self.model.predict(features, verbose=0)[0][0]
            
            # Scale prediction back to percentage
            prediction_percent = prediction * 100.0
            
            logger.info(f"Predicted tender performance: {prediction_percent:.2f}%")
            
            result = {
                "carrier": carrier,
                "source_city": source_city,
                "dest_city": dest_city,
                "predicted_performance": float(prediction_percent)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting tender performance (legacy format): {str(e)}")
            return None
    
    def predict_batch(self, carriers: List[str], source_cities: List[str], dest_cities: List[str],
                     source_states: Optional[List[str]] = None, source_countries: Optional[List[str]] = None,
                     dest_states: Optional[List[str]] = None, dest_countries: Optional[List[str]] = None) -> List[Optional[Dict[str, Any]]]:
        """Predict tender performance for multiple combinations.
        
        Args:
            carriers: List of carrier codes
            source_cities: List of source city names
            dest_cities: List of destination city names
            source_states: List of source states (optional, for new format)
            source_countries: List of source countries (optional, for new format)
            dest_states: List of destination states (optional, for new format)
            dest_countries: List of destination countries (optional, for new format)
            
        Returns:
            List of prediction results
        """
        if len(carriers) != len(source_cities) or len(carriers) != len(dest_cities):
            raise ValueError("Input lists must have the same length")
        
        # Check if we have location parameters
        has_location_params = all([
            source_states is not None, source_countries is not None,
            dest_states is not None, dest_countries is not None
        ])
        
        if has_location_params:
            if (len(carriers) != len(source_states) or len(carriers) != len(source_countries) or
                len(carriers) != len(dest_states) or len(carriers) != len(dest_countries)):
                raise ValueError("All input lists must have the same length when using location parameters")
        
        results = []
        for i in range(len(carriers)):
            if has_location_params:
                prediction = self.predict(
                    carriers[i], source_cities[i], dest_cities[i],
                    source_states[i], source_countries[i], dest_states[i], dest_countries[i]
                )
            else:
                prediction = self.predict(carriers[i], source_cities[i], dest_cities[i])
            results.append(prediction)
        
        return results
    
    def predict_on_training_data(self, output_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Predict tender performance on the training data.
        
        This method uses the trained model to make predictions on the same data
        that was used for training, which can help evaluate model performance.
        
        Args:
            output_dir: Directory to save the prediction files. If None,
                       a default directory will be created in the model path.
                       
        Returns:
            Dictionary with prediction results including input features and predictions
        """
        logger.info("Generating predictions on training data...")
        
        if self.model is None:
            logger.error("Model not trained or loaded. Cannot make predictions.")
            return None
        
        if self.raw_data is None:
            logger.error("No training data available for prediction.")
            return None
        
        try:
            # Make predictions for each row in the raw data
            predictions = []
            actual_values = []
            
            for index, row in self.raw_data.iterrows():
                # Extract parameters based on data format
                carrier = row['CARRIER']
                source_city = row['SOURCE_CITY']
                dest_city = row['DEST_CITY']
                actual_performance = row[self.target_column]
                
                # Initialize location variables with default values
                source_state = None
                source_country = None
                dest_state = None
                dest_country = None
                
                if self.data_format == 'new':
                    # Use new format with state/country information
                    source_state = row['SOURCE_STATE']
                    source_country = row['SOURCE_COUNTRY']
                    dest_state = row['DEST_STATE']
                    dest_country = row['DEST_COUNTRY']
                    
                    prediction_result = self.predict(
                        carrier, source_city, dest_city,
                        source_state, source_country, dest_state, dest_country
                    )
                else:
                    # Use legacy format
                    prediction_result = self.predict(carrier, source_city, dest_city)
                
                if prediction_result:
                    predicted_performance = prediction_result['predicted_performance']
                    
                    # Calculate errors
                    absolute_error = abs(actual_performance - predicted_performance)
                    percent_error = (absolute_error / actual_performance) * 100 if actual_performance != 0 else 0
                    
                    # Create detailed prediction record with consistent structure
                    prediction_record = {
                        'carrier': carrier,
                        'source_city': source_city,
                        'source_state': source_state,  # Always include, even if None for legacy
                        'source_country': source_country,  # Always include, even if None for legacy
                        'dest_city': dest_city,
                        'dest_state': dest_state,  # Always include, even if None for legacy
                        'dest_country': dest_country,  # Always include, even if None for legacy
                        'actual_performance': actual_performance,
                        'predicted_performance': predicted_performance,
                        'absolute_error': absolute_error,
                        'percent_error': percent_error
                    }
                    
                    predictions.append(prediction_record)
                    actual_values.append(actual_performance)
                else:
                    logger.warning(f"Failed to predict for row {index}")
            
            if not predictions:
                logger.error("No predictions were generated successfully")
                return None
            
            # Calculate overall metrics
            predicted_values = [p['predicted_performance'] for p in predictions]
            mae = np.mean([p['absolute_error'] for p in predictions])
            mape = np.mean([p['percent_error'] for p in predictions])
            
            logger.info(f"Generated {len(predictions)} predictions")
            logger.info(f"Overall MAE: {mae:.2f}")
            logger.info(f"Overall MAPE: {mape:.2f}%")
            
            # Create output directory if needed
            if output_dir is None:
                if self.model_path:
                    base_dir = os.path.dirname(self.model_path)
                else:
                    base_dir = "."
                output_dir = os.path.join(base_dir, "training_predictions")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Save predictions to JSON
            result = {
                "model_info": {
                    "data_format": self.data_format,
                    "target_column": self.target_column,
                    "prediction_count": len(predictions)
                },
                "metrics": {
                    "mae": float(mae),
                    "mape": float(mape),
                    "count": len(predictions)
                },
                "predictions": predictions
            }
            
            # Save to JSON file
            json_path = os.path.join(output_dir, "prediction_data.json")
            with open(json_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Predictions saved to {json_path}")
            
            # Save to CSV file with consistent column structure
            csv_path = os.path.join(output_dir, "prediction_data.csv")
            predictions_df = pd.DataFrame(predictions)
            
            # Ensure consistent column order regardless of data format
            if self.data_format == 'new':
                # New format CSV columns
                csv_columns = ['carrier', 'source_city', 'source_state', 'source_country', 
                              'dest_city', 'dest_state', 'dest_country', 'actual_performance', 
                              'predicted_performance', 'absolute_error', 'percent_error']
            else:
                # Legacy format CSV columns (still include state/country columns but they'll be None/empty)
                csv_columns = ['carrier', 'source_city', 'source_state', 'source_country', 
                              'dest_city', 'dest_state', 'dest_country', 'actual_performance', 
                              'predicted_performance', 'absolute_error', 'percent_error']
            
            # Reorder columns and save
            predictions_df = predictions_df.reindex(columns=csv_columns)
            predictions_df.to_csv(csv_path, index=False)
            
            logger.info(f"Predictions also saved to {csv_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating predictions on training data: {str(e)}")
            return None
    
    def save_model(self, path: str = "tender_performance_model") -> bool:
        """Save the trained model and associated encoders.
        
        Args:
            path: Base path for saving the model files
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Saving model to {path}...")
        
        try:
            if self.model is None:
                logger.error("No model to save. Train a model first.")
                return False
            
            # Create the directory if it doesn't exist
            os.makedirs(path, exist_ok=True)
            
            # Save the neural network model
            model_file = os.path.join(path, "model.keras")
            self.model.save(model_file)
            logger.info(f"Model saved to {model_file}")
            
            # Ensure all required encoders are available based on data format
            if self.data_format == 'new':
                required_encoders = [
                    self.carrier_encoder, self.source_city_encoder, self.source_state_encoder,
                    self.source_country_encoder, self.dest_city_encoder, self.dest_state_encoder,
                    self.dest_country_encoder
                ]
                if any(encoder is None for encoder in required_encoders):
                    logger.error("One or more encoders are not initialized for new format. Cannot save model.")
                    return False
            else:
                # Legacy format
                if any(encoder is None for encoder in [self.carrier_encoder, self.source_city_encoder, self.dest_city_encoder]):
                    logger.error("One or more encoders are not initialized for legacy format. Cannot save model.")
                    return False
            
            # Save encoders based on data format
            encoders_file = os.path.join(path, "encoders.pkl")
            encoders = {
                "carrier_encoder": self.carrier_encoder,
                "source_city_encoder": self.source_city_encoder,
                "dest_city_encoder": self.dest_city_encoder,
                "target_column": self.target_column,
                "data_format": self.data_format,
                "feature_columns": getattr(self, 'feature_columns', None)
            }
            
            # Add new format encoders if available
            if self.data_format == 'new':
                encoders.update({
                    "source_state_encoder": self.source_state_encoder,
                    "source_country_encoder": self.source_country_encoder,
                    "dest_state_encoder": self.dest_state_encoder,
                    "dest_country_encoder": self.dest_country_encoder
                })
            
            with open(encoders_file, "wb") as f:
                pickle.dump(encoders, f)
            logger.info(f"Encoders saved to {encoders_file}")
            
            # Save model metadata
            metadata = {
                "model_type": "tender_performance",
                "data_format": self.data_format,
                "target_column": self.target_column,
                "feature_count": len(self.feature_columns) if self.feature_columns else None,
                "save_time": datetime.now().isoformat(),
                "training_data_shape": self.raw_data.shape if self.raw_data is not None else None
            }
            
            metadata_file = os.path.join(path, "model_metadata.json")
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Model metadata saved to {metadata_file}")
            
            # Save the full training data for feature extraction and training data prediction
            if self.raw_data is not None:
                training_data_file = os.path.join(path, "training_data.csv")
                self.raw_data.to_csv(training_data_file, index=False)
                logger.info(f"Full training data saved to {training_data_file}")
                
                # Also save a sample for quick reference
                sample_data_file = os.path.join(path, "sample_data.csv")
                sample_size = min(10, len(self.raw_data))
                self.raw_data.head(sample_size).to_csv(sample_data_file, index=False)
                logger.info(f"Sample training data saved to {sample_data_file}")
            
            logger.info("Model saved successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, path: str) -> bool:
        """Load a pre-trained model and its encoders.
        
        Args:
            path: Path to the model directory
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Loading model from {path}...")
        
        try:
            # Load the neural network model
            model_file = os.path.join(path, "model.keras")
            if not os.path.exists(model_file):
                logger.error(f"Model file not found: {model_file}")
                return False
            
            self.model = tf.keras.models.load_model(model_file)
            logger.info("Model loaded successfully")
            
            # Load encoders
            encoders_file = os.path.join(path, "encoders.pkl")
            if os.path.exists(encoders_file):
                with open(encoders_file, "rb") as f:
                    encoders = pickle.load(f)
                
                self.carrier_encoder = encoders.get("carrier_encoder")
                self.source_city_encoder = encoders.get("source_city_encoder")
                self.dest_city_encoder = encoders.get("dest_city_encoder")
                self.target_column = encoders.get("target_column", "TENDER_PERF_PERCENTAGE")
                self.data_format = encoders.get("data_format", "legacy")
                self.feature_columns = encoders.get("feature_columns", None)
                
                # Load new format encoders if available
                if self.data_format == 'new':
                    self.source_state_encoder = encoders.get("source_state_encoder")
                    self.source_country_encoder = encoders.get("source_country_encoder")
                    self.dest_state_encoder = encoders.get("dest_state_encoder")
                    self.dest_country_encoder = encoders.get("dest_country_encoder")
                
                logger.info(f"Encoders loaded successfully for {self.data_format} format")
            else:
                logger.warning(f"Encoders file not found: {encoders_file}")
                return False
            
            # Load model metadata if available
            metadata_file = os.path.join(path, "model_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                logger.info(f"Model metadata loaded: {metadata.get('model_type', 'unknown')} model")
                logger.info(f"Data format: {metadata.get('data_format', 'unknown')}")
                logger.info(f"Feature count: {metadata.get('feature_count', 'unknown')}")
            
            # Try to load full training data for training data predictions
            training_data_file = os.path.join(path, "training_data.csv")
            if os.path.exists(training_data_file):
                self.raw_data = pd.read_csv(training_data_file)
                logger.info(f"Full training data loaded for training data prediction: {len(self.raw_data)} rows")
            else:
                # Fallback to sample data for feature compatibility
                sample_data_file = os.path.join(path, "sample_data.csv")
                if os.path.exists(sample_data_file):
                    self.raw_data = pd.read_csv(sample_data_file)
                    logger.warning("Only sample training data available - predictions will be limited to sample data")
                else:
                    logger.warning("No training data available - predict_on_training_data will not work")
            
            logger.info("Model loading completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False 