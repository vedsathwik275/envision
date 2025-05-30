#!/usr/bin/env python3
# Carrier Performance Neural Network Model
# This script processes carrier performance data, trains a neural network model,
# and generates predictions for carrier on-time performance by carrier and lane.

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

class CarrierPerformanceModel:
    """
    Carrier Performance Neural Network Model for predicting on-time performance.
    
    This model handles both legacy quarter-based data and new month-based data with 
    expanded geographic features including state and country information.
    """
    
    def __init__(self, data_path: Optional[str] = None, model_path: Optional[str] = None) -> None:
        """Initialize the Carrier Performance prediction model.
        
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
        self.time_encoder = None  # For quarter or tracking_month
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
            'legacy' for quarter-based data, 'new' for month-based data, or 'hybrid' for state/country with quarters
        """
        # Check for new format indicators
        has_tracking_month = 'TRACKING_MONTH' in data.columns
        has_state_columns = 'SOURCE_STATE' in data.columns and 'DEST_STATE' in data.columns
        has_country_columns = 'SOURCE_COUNTRY' in data.columns and 'DEST_COUNTRY' in data.columns
        
        # Check for legacy format indicators
        has_qtr = 'QTR' in data.columns
        
        if has_tracking_month and has_state_columns and has_country_columns:
            return 'new'
        elif has_state_columns and has_country_columns and has_qtr:
            return 'hybrid'  # Has state/country but uses quarters
        elif has_state_columns and has_country_columns:
            return 'hybrid_no_time'  # Has state/country but no explicit time column
        elif has_qtr:
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
        
        logger.info(f"Data loaded successfully. Shape: {self.raw_data.shape}")
        return self.raw_data
    
    def preprocess_data(self) -> pd.DataFrame:
        """Preprocess the data for training the neural network."""
        logger.info("Preprocessing data...")
        
        # Create a copy of the raw data
        data = self.raw_data.copy()
        
        if self.data_format == 'new':
            return self._preprocess_new_format(data)
        elif self.data_format in ['hybrid', 'hybrid_no_time']:
            return self._preprocess_hybrid_format(data)
        else:
            return self._preprocess_legacy_format(data)
    
    def _preprocess_new_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data in the new format with tracking months and expanded location data."""
        logger.info("Preprocessing new format data with tracking months and expanded location features...")
        
        # Create comprehensive lane identifier
        data['LANE_ID'] = (data['SOURCE_CITY'] + '_' + data['SOURCE_STATE'] + '_' + 
                          data['SOURCE_COUNTRY'] + '_TO_' + data['DEST_CITY'] + '_' + 
                          data['DEST_STATE'] + '_' + data['DEST_COUNTRY'])
        
        # One-hot encoding for categorical variables
        logger.info("Encoding categorical variables for new format...")
        
        # Time encoding (tracking month)
        self.time_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        time_encoded = self.time_encoder.fit_transform(data[['TRACKING_MONTH']])
        time_columns = [f'TRACKING_MONTH_{i}' for i in range(time_encoded.shape[1])]
        time_df = pd.DataFrame(time_encoded, columns=time_columns)
        
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
        
        # Scale numerical features
        self.scaler = StandardScaler()
        numerical_cols = ['ORDER_COUNT', 'AVG_TRANSIT_DAYS', 'ACTUAL_TRANSIT_DAYS']
        if set(numerical_cols).issubset(data.columns):
            numerical_data = self.scaler.fit_transform(data[numerical_cols])
            numerical_df = pd.DataFrame(numerical_data, columns=numerical_cols)
        else:
            logger.warning(f"Not all numerical columns found in data. Available columns: {data.columns}")
            numerical_df = pd.DataFrame()
            available_num_cols = [col for col in numerical_cols if col in data.columns]
            if available_num_cols:
                numerical_data = self.scaler.fit_transform(data[available_num_cols])
                numerical_df = pd.DataFrame(numerical_data, columns=available_num_cols)
        
        # Reset indices to ensure proper concatenation
        for df in [data, time_df, carrier_df, source_city_df, source_state_df, source_country_df,
                  dest_city_df, dest_state_df, dest_country_df]:
            df.reset_index(drop=True, inplace=True)
        if not numerical_df.empty:
            numerical_df.reset_index(drop=True, inplace=True)
        
        # Create the final processed dataset
        dfs_to_concat = [
            data[['ONTIME_PERFORMANCE']],
            time_df,
            carrier_df,
            source_city_df,
            source_state_df,
            source_country_df,
            dest_city_df,
            dest_state_df,
            dest_country_df
        ]
        
        if not numerical_df.empty:
            dfs_to_concat.append(numerical_df)
        
        processed_data = pd.concat(dfs_to_concat, axis=1)
        
        # Save feature columns for prediction
        self.feature_columns = list(processed_data.columns)
        self.feature_columns.remove('ONTIME_PERFORMANCE')
        
        logger.info(f"New format data preprocessing complete. Processed shape: {processed_data.shape}")
        self.preprocessed_data = processed_data
        
        # Save information about the features for later use
        self.feature_info = {
            'data_format': 'new',
            'time_categories': self.time_encoder.categories_[0].tolist(),
            'carrier_categories': self.carrier_encoder.categories_[0].tolist(),
            'source_city_categories': self.source_city_encoder.categories_[0].tolist(),
            'source_state_categories': self.source_state_encoder.categories_[0].tolist(),
            'source_country_categories': self.source_country_encoder.categories_[0].tolist(),
            'dest_city_categories': self.dest_city_encoder.categories_[0].tolist(),
            'dest_state_categories': self.dest_state_encoder.categories_[0].tolist(),
            'dest_country_categories': self.dest_country_encoder.categories_[0].tolist(),
            'numerical_columns': numerical_cols if not numerical_df.empty else [],
            'feature_columns': self.feature_columns
        }
        
        return processed_data
    
    def _preprocess_legacy_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data in the legacy format with quarters and city-only location data."""
        logger.info("Preprocessing legacy format data with quarters...")
        
        # Create lane identifier (combination of source and destination)
        data['LANE_ID'] = data['SOURCE_CITY'] + '_' + data['DEST_CITY']
        
        # One-hot encoding for categorical variables
        logger.info("Encoding categorical variables for legacy format...")
        
        # Quarter encoding
        self.time_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        time_encoded = self.time_encoder.fit_transform(data[['QTR']])
        time_columns = [f'QTR_{i}' for i in range(time_encoded.shape[1])]
        time_df = pd.DataFrame(time_encoded, columns=time_columns)
        
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
        dest_counts = data['DEST_CITY'].value_counts()
        top_dests = dest_counts.nlargest(50).index.tolist()  # Use top 50 destinations
        
        # Group less frequent destinations as 'OTHER'
        data['DEST_CITY_GROUPED'] = data['DEST_CITY'].apply(lambda x: x if x in top_dests else 'OTHER')
        
        # One-hot encode the grouped destinations
        self.dest_city_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        dest_encoded = self.dest_city_encoder.fit_transform(data[['DEST_CITY_GROUPED']])
        dest_columns = [f'DEST_{i}' for i in range(dest_encoded.shape[1])]
        dest_df = pd.DataFrame(dest_encoded, columns=dest_columns)
        
        # Scale numerical features
        self.scaler = StandardScaler()
        numerical_cols = ['ORDER_COUNT', 'AVG_TRANSIT_DAYS', 'ACTUAL_TRANSIT_DAYS']
        if set(numerical_cols).issubset(data.columns):
            numerical_data = self.scaler.fit_transform(data[numerical_cols])
            numerical_df = pd.DataFrame(numerical_data, columns=numerical_cols)
        else:
            logger.warning(f"Not all numerical columns found in data. Available columns: {data.columns}")
            numerical_df = pd.DataFrame()
            available_num_cols = [col for col in numerical_cols if col in data.columns]
            if available_num_cols:
                numerical_data = self.scaler.fit_transform(data[available_num_cols])
                numerical_df = pd.DataFrame(numerical_data, columns=available_num_cols)
        
        # Reset indices to ensure proper concatenation
        data.reset_index(drop=True, inplace=True)
        time_df.reset_index(drop=True, inplace=True)
        carrier_df.reset_index(drop=True, inplace=True)
        source_df.reset_index(drop=True, inplace=True)
        dest_df.reset_index(drop=True, inplace=True)
        if not numerical_df.empty:
            numerical_df.reset_index(drop=True, inplace=True)
        
        # Create the final processed dataset
        dfs_to_concat = [
            data[['ONTIME_PERFORMANCE']],
            time_df,
            carrier_df,
            source_df,
            dest_df
        ]
        
        if not numerical_df.empty:
            dfs_to_concat.append(numerical_df)
        
        processed_data = pd.concat(dfs_to_concat, axis=1)
        
        # Save feature columns for prediction
        self.feature_columns = list(processed_data.columns)
        self.feature_columns.remove('ONTIME_PERFORMANCE')
        
        logger.info(f"Legacy format data preprocessing complete. Processed shape: {processed_data.shape}")
        self.preprocessed_data = processed_data
        
        # Save information about the features for later use
        self.feature_info = {
            'data_format': 'legacy',
            'quarter_categories': self.time_encoder.categories_[0].tolist(),
            'carrier_categories': self.carrier_encoder.categories_[0].tolist(),
            'source_categories': self.source_city_encoder.categories_[0].tolist(),
            'dest_categories': self.dest_city_encoder.categories_[0].tolist(),
            'numerical_columns': numerical_cols if not numerical_df.empty else [],
            'feature_columns': self.feature_columns
        }
        
        return processed_data
    
    def _preprocess_hybrid_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data in the hybrid format with state/country data but possibly using quarters or no time dimension."""
        logger.info("Preprocessing hybrid format data with expanded location features...")
        
        # Create comprehensive lane identifier
        data['LANE_ID'] = (data['SOURCE_CITY'] + '_' + data['SOURCE_STATE'] + '_' + 
                          data['SOURCE_COUNTRY'] + '_TO_' + data['DEST_CITY'] + '_' + 
                          data['DEST_STATE'] + '_' + data['DEST_COUNTRY'])
        
        # One-hot encoding for categorical variables
        logger.info("Encoding categorical variables for hybrid format...")
        
        # Time encoding (if available)
        if 'QTR' in data.columns:
            self.time_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            time_encoded = self.time_encoder.fit_transform(data[['QTR']])
            time_columns = [f'QTR_{i}' for i in range(time_encoded.shape[1])]
            time_df = pd.DataFrame(time_encoded, columns=time_columns)
        else:
            # No time dimension available, create a dummy time feature
            logger.info("No time dimension found, creating default time feature")
            time_df = pd.DataFrame({'DEFAULT_TIME': [1] * len(data)})
        
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
        
        # Scale numerical features
        self.scaler = StandardScaler()
        numerical_cols = ['ORDER_COUNT', 'AVG_TRANSIT_DAYS', 'ACTUAL_TRANSIT_DAYS']
        if set(numerical_cols).issubset(data.columns):
            numerical_data = self.scaler.fit_transform(data[numerical_cols])
            numerical_df = pd.DataFrame(numerical_data, columns=numerical_cols)
        else:
            logger.warning(f"Not all numerical columns found in data. Available columns: {data.columns}")
            numerical_df = pd.DataFrame()
            available_num_cols = [col for col in numerical_cols if col in data.columns]
            if available_num_cols:
                numerical_data = self.scaler.fit_transform(data[available_num_cols])
                numerical_df = pd.DataFrame(numerical_data, columns=available_num_cols)
        
        # Reset indices to ensure proper concatenation
        for df in [data, time_df, carrier_df, source_city_df, source_state_df, source_country_df,
                  dest_city_df, dest_state_df, dest_country_df]:
            df.reset_index(drop=True, inplace=True)
        if not numerical_df.empty:
            numerical_df.reset_index(drop=True, inplace=True)
        
        # Create the final processed dataset
        dfs_to_concat = [
            data[['ONTIME_PERFORMANCE']],
            time_df,
            carrier_df,
            source_city_df,
            source_state_df,
            source_country_df,
            dest_city_df,
            dest_state_df,
            dest_country_df
        ]
        
        if not numerical_df.empty:
            dfs_to_concat.append(numerical_df)
        
        processed_data = pd.concat(dfs_to_concat, axis=1)
        
        # Save feature columns for prediction
        self.feature_columns = list(processed_data.columns)
        self.feature_columns.remove('ONTIME_PERFORMANCE')
        
        logger.info(f"Hybrid format data preprocessing complete. Processed shape: {processed_data.shape}")
        self.preprocessed_data = processed_data
        
        # Save information about the features for later use
        self.feature_info = {
            'data_format': 'hybrid',
            'has_qtr': 'QTR' in data.columns,
            'time_categories': self.time_encoder.categories_[0].tolist() if hasattr(self.time_encoder, 'categories_') else [],
            'carrier_categories': self.carrier_encoder.categories_[0].tolist(),
            'source_city_categories': self.source_city_encoder.categories_[0].tolist(),
            'source_state_categories': self.source_state_encoder.categories_[0].tolist(),
            'source_country_categories': self.source_country_encoder.categories_[0].tolist(),
            'dest_city_categories': self.dest_city_encoder.categories_[0].tolist(),
            'dest_state_categories': self.dest_state_encoder.categories_[0].tolist(),
            'dest_country_categories': self.dest_country_encoder.categories_[0].tolist(),
            'numerical_columns': numerical_cols if not numerical_df.empty else [],
            'feature_columns': self.feature_columns
        }
        
        return processed_data
    
    def prepare_train_test_split(self, test_size=0.2):
        """Split the preprocessed data into training and testing sets."""
        logger.info(f"Splitting data with test_size={test_size}...")
        
        if self.preprocessed_data is None:
            self.preprocess_data()
        
        # Separate features and target
        X = self.preprocessed_data.drop('ONTIME_PERFORMANCE', axis=1)
        y = self.preprocessed_data['ONTIME_PERFORMANCE']
        
        # Normalize the target value to [0, 1] range for better training
        y = y / 100.0
        
        # Split the data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        logger.info(f"Train set: {self.X_train.shape[0]} samples")
        logger.info(f"Test set: {self.X_test.shape[0]} samples")
    
    def build_model(self):
        """Build the neural network model architecture."""
        logger.info("Building neural network model...")
        
        # Get input shape from training data
        input_dim = self.X_train.shape[1]
        
        # Create a sequential model with appropriate architecture for carrier performance data
        model = models.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # Sigmoid for [0,1] output
        ])
        
        # Compile the model with appropriate metrics
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mean_squared_error',
            metrics=['mean_absolute_error', 'mean_absolute_percentage_error']
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
        
        # Define default callbacks if none provided
        if callbacks is None:
            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.2,
                    patience=5,
                    min_lr=0.0001
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
        
        logger.info("Model training completed")
        return history
    
    def evaluate(self, plot_path=None):
        """Evaluate the model performance on the test set."""
        logger.info("Evaluating model performance...")
        
        if self.X_test is None or self.y_test is None:
            logger.error("No test data available for evaluation. Call prepare_train_test_split() first.")
            return None
        
        if self.model is None:
            logger.error("No model available for evaluation. Train or load a model first.")
            return None
        
        # Get predictions on test set
        y_pred = self.model.predict(self.X_test)
        
        # Convert back to original scale
        y_test_original = self.y_test * 100
        y_pred_original = y_pred.flatten() * 100
        
        # Calculate error metrics
        mae = mean_absolute_error(y_test_original, y_pred_original)
        mse = mean_squared_error(y_test_original, y_pred_original)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test_original, y_pred_original)
        
        # Print evaluation metrics
        logger.info(f"Mean Absolute Error (MAE): {mae:.2f}")
        logger.info(f"Mean Squared Error (MSE): {mse:.2f}")
        logger.info(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
        logger.info(f"R-squared (R²): {r2:.4f}")
        
        # Optionally plot actual vs predicted values
        if plot_path:
            plt.figure(figsize=(10, 6))
            plt.scatter(y_test_original, y_pred_original, alpha=0.5)
            plt.plot([0, 100], [0, 100], 'r--')
            plt.xlabel('Actual On-Time Performance (%)')
            plt.ylabel('Predicted On-Time Performance (%)')
            plt.title('Actual vs Predicted On-Time Performance')
            plt.grid(True)
            plt.savefig(plot_path)
            plt.close()
            logger.info(f"Evaluation plot saved to {plot_path}")
        
        # Return evaluation metrics as a dictionary
        evaluation = {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(rmse),
            'r2': float(r2)
        }
        
        return evaluation
    
    def predict(self, carrier: str, source_city: str, dest_city: str, 
                source_state: Optional[str] = None, source_country: Optional[str] = None,
                dest_state: Optional[str] = None, dest_country: Optional[str] = None,
                tracking_month: Optional[str] = None, quarter: Optional[str] = None,
                order_count: Optional[float] = None, avg_transit_days: Optional[float] = None, 
                actual_transit_days: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Predict the on-time performance for a specific carrier and lane.
        
        Supports both legacy format (quarter-based with city-only locations) and
        new format (month-based with state/country location data).
        
        Args:
            carrier: Carrier name
            source_city: Source city name
            dest_city: Destination city name
            source_state: Source state (required for new format)
            source_country: Source country (required for new format)
            dest_state: Destination state (required for new format)
            dest_country: Destination country (required for new format)
            tracking_month: Tracking month for new format (e.g., '2025 05')
            quarter: Quarter for legacy format (e.g., '2025 1')
            order_count: Number of orders
            avg_transit_days: Average transit days
            actual_transit_days: Actual transit days
            
        Returns:
            Dictionary with prediction results or None if prediction fails
        """
        if self.model is None:
            logger.error("No model available for prediction. Train or load a model first.")
            return None
        
        # Determine which format to use based on available data and model format
        if hasattr(self, 'feature_info') and self.feature_info:
            model_format = self.feature_info.get('data_format', 'legacy')
        else:
            # Fallback to detection based on available parameters
            model_format = 'new' if all([source_state, source_country, dest_state, dest_country]) else 'legacy'
        
        if model_format == 'new':
            return self._predict_new_format(
                carrier, source_city, dest_city, source_state, source_country,
                dest_state, dest_country, tracking_month, order_count, 
                avg_transit_days, actual_transit_days
            )
        elif model_format == 'hybrid':
            return self._predict_hybrid_format(
                carrier, source_city, dest_city, source_state, source_country,
                dest_state, dest_country, quarter, order_count, 
                avg_transit_days, actual_transit_days
            )
        else:
            return self._predict_legacy_format(
                carrier, source_city, dest_city, quarter, order_count,
                avg_transit_days, actual_transit_days
            )
    
    def _predict_new_format(self, carrier: str, source_city: str, dest_city: str,
                           source_state: str, source_country: str, dest_state: str, 
                           dest_country: str, tracking_month: Optional[str] = None,
                           order_count: Optional[float] = None, avg_transit_days: Optional[float] = None,
                           actual_transit_days: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Predict using new format with expanded location data."""
        
        # Check if all required encoders are available for new format
        required_encoders = [
            self.carrier_encoder, self.source_city_encoder, self.source_state_encoder,
            self.source_country_encoder, self.dest_city_encoder, self.dest_state_encoder,
            self.dest_country_encoder, self.time_encoder
        ]
        
        if not all(required_encoders):
            logger.error("Not all encoders available for new format prediction.")
            return None
        
        # Validate required parameters for new format
        if not all([source_state, source_country, dest_state, dest_country]):
            logger.error("Missing required location parameters for new format prediction.")
            return None
        
        try:
            # Create input dataframe
            input_data = pd.DataFrame({
                'CARRIER': [carrier],
                'SOURCE_CITY': [source_city],
                'SOURCE_STATE': [source_state],
                'SOURCE_COUNTRY': [source_country],
                'DEST_CITY': [dest_city],
                'DEST_STATE': [dest_state],
                'DEST_COUNTRY': [dest_country]
            })
            
            # Add time feature
            if tracking_month is not None:
                input_data['TRACKING_MONTH'] = [tracking_month]
            else:
                # Use the most recent tracking month from training data
                input_data['TRACKING_MONTH'] = [self.time_encoder.categories_[0][-1]]
            
            # Add numerical features with defaults
            numerical_features = {}
            if order_count is not None:
                numerical_features['ORDER_COUNT'] = [order_count]
            if avg_transit_days is not None:
                numerical_features['AVG_TRANSIT_DAYS'] = [avg_transit_days]
            if actual_transit_days is not None:
                numerical_features['ACTUAL_TRANSIT_DAYS'] = [actual_transit_days]
            
            # Apply encodings
            # Time encoding
            time_encoded = self.time_encoder.transform(input_data[['TRACKING_MONTH']])
            time_df = pd.DataFrame(time_encoded, columns=[f'TRACKING_MONTH_{i}' for i in range(time_encoded.shape[1])])
            
            # Carrier encoding
            carrier_encoded = self.carrier_encoder.transform(input_data[['CARRIER']])
            carrier_df = pd.DataFrame(carrier_encoded, columns=[f'CARRIER_{i}' for i in range(carrier_encoded.shape[1])])
            
            # Source location encodings
            source_city_encoded = self.source_city_encoder.transform(input_data[['SOURCE_CITY']])
            source_city_df = pd.DataFrame(source_city_encoded, columns=[f'SOURCE_CITY_{i}' for i in range(source_city_encoded.shape[1])])
            
            source_state_encoded = self.source_state_encoder.transform(input_data[['SOURCE_STATE']])
            source_state_df = pd.DataFrame(source_state_encoded, columns=[f'SOURCE_STATE_{i}' for i in range(source_state_encoded.shape[1])])
            
            source_country_encoded = self.source_country_encoder.transform(input_data[['SOURCE_COUNTRY']])
            source_country_df = pd.DataFrame(source_country_encoded, columns=[f'SOURCE_COUNTRY_{i}' for i in range(source_country_encoded.shape[1])])
            
            # Destination location encodings
            # Handle destination city grouping
            dest_city_categories = self.dest_city_encoder.categories_[0]
            dest_city_grouped = dest_city if dest_city in dest_city_categories else 'OTHER'
            input_data['DEST_CITY_GROUPED'] = [dest_city_grouped]
            
            dest_city_encoded = self.dest_city_encoder.transform(input_data[['DEST_CITY_GROUPED']])
            dest_city_df = pd.DataFrame(dest_city_encoded, columns=[f'DEST_CITY_{i}' for i in range(dest_city_encoded.shape[1])])
            
            dest_state_encoded = self.dest_state_encoder.transform(input_data[['DEST_STATE']])
            dest_state_df = pd.DataFrame(dest_state_encoded, columns=[f'DEST_STATE_{i}' for i in range(dest_state_encoded.shape[1])])
            
            dest_country_encoded = self.dest_country_encoder.transform(input_data[['DEST_COUNTRY']])
            dest_country_df = pd.DataFrame(dest_country_encoded, columns=[f'DEST_COUNTRY_{i}' for i in range(dest_country_encoded.shape[1])])
            
            # Combine all encoded features
            encoded_dfs = [
                time_df, carrier_df, source_city_df, source_state_df, source_country_df,
                dest_city_df, dest_state_df, dest_country_df
            ]
            
            # Add numerical features if available
            if numerical_features and self.scaler is not None:
                # Create DataFrame with all possible numerical columns, filling missing with defaults
                num_data = pd.DataFrame({
                    'ORDER_COUNT': numerical_features.get('ORDER_COUNT', [1]),
                    'AVG_TRANSIT_DAYS': numerical_features.get('AVG_TRANSIT_DAYS', [2]),
                    'ACTUAL_TRANSIT_DAYS': numerical_features.get('ACTUAL_TRANSIT_DAYS', [2])
                })
                
                # Scale the numerical features
                scaled_numerical = self.scaler.transform(num_data)
                numerical_df = pd.DataFrame(scaled_numerical, columns=num_data.columns)
                encoded_dfs.append(numerical_df)
            
            # Concatenate all features
            model_input = pd.concat(encoded_dfs, axis=1)
            
            # Ensure the input has all required features in the correct order
            model_input = model_input.reindex(columns=self.feature_columns, fill_value=0)
            
            # Make prediction
            prediction = self.model.predict(model_input)
            
            # Convert back to percentage
            ontime_performance = float(prediction[0][0] * 100)
            
            result = {
                'carrier': carrier,
                'source_city': source_city,
                'source_state': source_state,
                'source_country': source_country,
                'dest_city': dest_city,
                'dest_state': dest_state,
                'dest_country': dest_country,
                'ontime_performance': ontime_performance
            }
            
            if tracking_month is not None:
                result['tracking_month'] = tracking_month
            
            # Add any provided numerical features to the result
            for key, value in numerical_features.items():
                result[key.lower()] = value[0]
            
            return result
            
        except Exception as e:
            logger.error(f"Error during new format prediction: {str(e)}")
            return None
    
    def _predict_hybrid_format(self, carrier: str, source_city: str, dest_city: str,
                              source_state: str, source_country: str, dest_state: str, 
                              dest_country: str, quarter: Optional[str] = None,
                              order_count: Optional[float] = None, avg_transit_days: Optional[float] = None,
                              actual_transit_days: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Predict using hybrid format with expanded location data and optional quarter information."""
        
        # Check if all required encoders are available for hybrid format
        required_encoders = [
            self.carrier_encoder, self.source_city_encoder, self.source_state_encoder,
            self.source_country_encoder, self.dest_city_encoder, self.dest_state_encoder,
            self.dest_country_encoder
        ]
        
        if not all(required_encoders):
            logger.error("Not all encoders available for hybrid format prediction.")
            return None
        
        # Validate required parameters for hybrid format
        if not all([source_state, source_country, dest_state, dest_country]):
            logger.error("Missing required location parameters for hybrid format prediction.")
            return None
        
        try:
            # Create input dataframe
            input_data = pd.DataFrame({
                'CARRIER': [carrier],
                'SOURCE_CITY': [source_city],
                'SOURCE_STATE': [source_state],
                'SOURCE_COUNTRY': [source_country],
                'DEST_CITY': [dest_city],
                'DEST_STATE': [dest_state],
                'DEST_COUNTRY': [dest_country]
            })
            
            # Handle time feature
            has_qtr = self.feature_info.get('has_qtr', False) if hasattr(self, 'feature_info') else False
            
            if has_qtr and quarter is not None:
                input_data['QTR'] = [quarter]
                # Quarter encoding
                time_encoded = self.time_encoder.transform(input_data[['QTR']])
                time_df = pd.DataFrame(time_encoded, columns=[f'QTR_{i}' for i in range(time_encoded.shape[1])])
            elif has_qtr and hasattr(self.time_encoder, 'categories_'):
                # Use the most recent quarter from training data
                input_data['QTR'] = [self.time_encoder.categories_[0][-1]]
                time_encoded = self.time_encoder.transform(input_data[['QTR']])
                time_df = pd.DataFrame(time_encoded, columns=[f'QTR_{i}' for i in range(time_encoded.shape[1])])
            else:
                # Use default time feature
                time_df = pd.DataFrame({'DEFAULT_TIME': [1]})
            
            # Add numerical features with defaults
            numerical_features = {}
            if order_count is not None:
                numerical_features['ORDER_COUNT'] = [order_count]
            if avg_transit_days is not None:
                numerical_features['AVG_TRANSIT_DAYS'] = [avg_transit_days]
            if actual_transit_days is not None:
                numerical_features['ACTUAL_TRANSIT_DAYS'] = [actual_transit_days]
            
            # Apply encodings
            # Carrier encoding
            carrier_encoded = self.carrier_encoder.transform(input_data[['CARRIER']])
            carrier_df = pd.DataFrame(carrier_encoded, columns=[f'CARRIER_{i}' for i in range(carrier_encoded.shape[1])])
            
            # Source location encodings
            source_city_encoded = self.source_city_encoder.transform(input_data[['SOURCE_CITY']])
            source_city_df = pd.DataFrame(source_city_encoded, columns=[f'SOURCE_CITY_{i}' for i in range(source_city_encoded.shape[1])])
            
            source_state_encoded = self.source_state_encoder.transform(input_data[['SOURCE_STATE']])
            source_state_df = pd.DataFrame(source_state_encoded, columns=[f'SOURCE_STATE_{i}' for i in range(source_state_encoded.shape[1])])
            
            source_country_encoded = self.source_country_encoder.transform(input_data[['SOURCE_COUNTRY']])
            source_country_df = pd.DataFrame(source_country_encoded, columns=[f'SOURCE_COUNTRY_{i}' for i in range(source_country_encoded.shape[1])])
            
            # Destination location encodings
            # Handle destination city grouping
            dest_city_categories = self.dest_city_encoder.categories_[0]
            dest_city_grouped = dest_city if dest_city in dest_city_categories else 'OTHER'
            input_data['DEST_CITY_GROUPED'] = [dest_city_grouped]
            
            dest_city_encoded = self.dest_city_encoder.transform(input_data[['DEST_CITY_GROUPED']])
            dest_city_df = pd.DataFrame(dest_city_encoded, columns=[f'DEST_CITY_{i}' for i in range(dest_city_encoded.shape[1])])
            
            dest_state_encoded = self.dest_state_encoder.transform(input_data[['DEST_STATE']])
            dest_state_df = pd.DataFrame(dest_state_encoded, columns=[f'DEST_STATE_{i}' for i in range(dest_state_encoded.shape[1])])
            
            dest_country_encoded = self.dest_country_encoder.transform(input_data[['DEST_COUNTRY']])
            dest_country_df = pd.DataFrame(dest_country_encoded, columns=[f'DEST_COUNTRY_{i}' for i in range(dest_country_encoded.shape[1])])
            
            # Combine all encoded features
            encoded_dfs = [
                time_df, carrier_df, source_city_df, source_state_df, source_country_df,
                dest_city_df, dest_state_df, dest_country_df
            ]
            
            # Add numerical features if available
            if numerical_features and self.scaler is not None:
                # Create DataFrame with all possible numerical columns, filling missing with defaults
                num_data = pd.DataFrame({
                    'ORDER_COUNT': numerical_features.get('ORDER_COUNT', [1]),
                    'AVG_TRANSIT_DAYS': numerical_features.get('AVG_TRANSIT_DAYS', [2]),
                    'ACTUAL_TRANSIT_DAYS': numerical_features.get('ACTUAL_TRANSIT_DAYS', [2])
                })
                
                # Scale the numerical features
                scaled_numerical = self.scaler.transform(num_data)
                numerical_df = pd.DataFrame(scaled_numerical, columns=num_data.columns)
                encoded_dfs.append(numerical_df)
            
            # Concatenate all features
            model_input = pd.concat(encoded_dfs, axis=1)
            
            # Ensure the input has all required features in the correct order
            model_input = model_input.reindex(columns=self.feature_columns, fill_value=0)
            
            # Make prediction
            prediction = self.model.predict(model_input)
            
            # Convert back to percentage
            ontime_performance = float(prediction[0][0] * 100)
            
            result = {
                'carrier': carrier,
                'source_city': source_city,
                'source_state': source_state,
                'source_country': source_country,
                'dest_city': dest_city,
                'dest_state': dest_state,
                'dest_country': dest_country,
                'ontime_performance': ontime_performance
            }
            
            if quarter is not None:
                result['quarter'] = quarter
            
            # Add any provided numerical features to the result
            for key, value in numerical_features.items():
                result[key.lower()] = value[0]
            
            return result
            
        except Exception as e:
            logger.error(f"Error during hybrid format prediction: {str(e)}")
            return None
    
    def _predict_legacy_format(self, carrier: str, source_city: str, dest_city: str,
                              quarter: Optional[str] = None, order_count: Optional[float] = None,
                              avg_transit_days: Optional[float] = None, 
                              actual_transit_days: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Predict using legacy format with quarter and city-only location data."""
        
        # Check if all encoders are available
        if not all([self.carrier_encoder, self.source_city_encoder, self.dest_city_encoder]):
            logger.error("Encoders not available. The model needs to be trained first or loaded from a complete saved model.")
            return None
        
        try:
            # Create a dataframe with the input features
            input_data = pd.DataFrame({
                'CARRIER': [carrier],
                'SOURCE_CITY': [source_city],
                'DEST_CITY': [dest_city]
            })
            
            # Add optional features if provided
            if quarter is not None:
                input_data['QTR'] = [quarter]
            else:
                # Use the most recent quarter from training data
                input_data['QTR'] = [self.time_encoder.categories_[0][-1]]
            
            # Add optional numerical features
            numerical_features = {}
            if order_count is not None:
                numerical_features['ORDER_COUNT'] = [order_count]
            if avg_transit_days is not None:
                numerical_features['AVG_TRANSIT_DAYS'] = [avg_transit_days]
            if actual_transit_days is not None:
                numerical_features['ACTUAL_TRANSIT_DAYS'] = [actual_transit_days]
            
            # Quarter encoding
            quarter_encoded = self.time_encoder.transform(input_data[['QTR']])
            quarter_df = pd.DataFrame(
                quarter_encoded, 
                columns=[f'QTR_{i}' for i in range(quarter_encoded.shape[1])]
            )
            
            # Carrier encoding  
            carrier_encoded = self.carrier_encoder.transform(input_data[['CARRIER']])
            carrier_df = pd.DataFrame(
                carrier_encoded, 
                columns=[f'CARRIER_{i}' for i in range(carrier_encoded.shape[1])]
            )
            
            # Source city encoding
            source_encoded = self.source_city_encoder.transform(input_data[['SOURCE_CITY']])
            source_df = pd.DataFrame(
                source_encoded, 
                columns=[f'SOURCE_{i}' for i in range(source_encoded.shape[1])]
            )
            
            # Destination city encoding
            # Check if dest_city is in the top destinations, otherwise use 'OTHER'
            top_dests = self.dest_city_encoder.categories_[0]
            dest_city_grouped = dest_city if dest_city in top_dests else 'OTHER'
            input_data['DEST_CITY_GROUPED'] = [dest_city_grouped]
            
            dest_encoded = self.dest_city_encoder.transform(input_data[['DEST_CITY_GROUPED']])
            dest_df = pd.DataFrame(
                dest_encoded, 
                columns=[f'DEST_{i}' for i in range(dest_encoded.shape[1])]
            )
            
            # Combine all categorical features
            categorical_features = pd.concat([quarter_df, carrier_df, source_df, dest_df], axis=1)
            
            # Handle numerical features
            if numerical_features and self.scaler is not None:
                # Create a DataFrame with default values for missing features
                num_data = pd.DataFrame({
                    'ORDER_COUNT': numerical_features.get('ORDER_COUNT', [1]),
                    'AVG_TRANSIT_DAYS': numerical_features.get('AVG_TRANSIT_DAYS', [2]),
                    'ACTUAL_TRANSIT_DAYS': numerical_features.get('ACTUAL_TRANSIT_DAYS', [2])
                })
                
                # Scale the numerical features
                scaled_numerical = self.scaler.transform(num_data)
                numerical_df = pd.DataFrame(scaled_numerical, columns=num_data.columns)
                
                # Combine categorical and numerical features
                model_input = pd.concat([categorical_features, numerical_df], axis=1)
            else:
                model_input = categorical_features
            
            # Ensure the input has all required features in the correct order
            model_input = model_input.reindex(columns=self.feature_columns, fill_value=0)
            
            # Make prediction
            prediction = self.model.predict(model_input)
            
            # Convert back to percentage
            ontime_performance = float(prediction[0][0] * 100)
            
            result = {
                'carrier': carrier,
                'source_city': source_city,
                'dest_city': dest_city,
                'ontime_performance': ontime_performance
            }
            
            if quarter is not None:
                result['quarter'] = quarter
                
            # Add any provided numerical features to the result
            for key, value in numerical_features.items():
                result[key.lower()] = value[0]
            
            return result
            
        except Exception as e:
            logger.error(f"Error during legacy format prediction: {str(e)}")
            return None
    
    def predict_batch(self, carriers, source_cities, dest_cities, quarters=None):
        """
        Predict on-time performance for multiple carrier-lane combinations.
        
        Args:
            carriers: List of carrier names
            source_cities: List of source city names
            dest_cities: List of destination city names
            quarters: Optional list of quarters
            
        Returns:
            List of predictions, each with carrier, source_city, dest_city, and ontime_performance
        """
        if len(carriers) != len(source_cities) or len(carriers) != len(dest_cities):
            logger.error("Input lists must have the same length")
            return None
            
        if quarters is not None and len(quarters) != len(carriers):
            logger.error("If quarters are provided, the list must have the same length as other inputs")
            return None
            
        results = []
        for i in range(len(carriers)):
            quarter = quarters[i] if quarters is not None else None
            prediction = self.predict(carriers[i], source_cities[i], dest_cities[i], quarter=quarter)
            if prediction:
                results.append(prediction)
                
        return results
    
    def predict_on_training_data(self, output_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate predictions on the training data and calculate performance metrics.
        
        Args:
            output_dir: Directory to save prediction results
            
        Returns:
            Dictionary with predictions and performance metrics
        """
        logger.info("Generating predictions on training data...")
        
        # Check if raw data is available
        if not hasattr(self, 'raw_data') or self.raw_data is None:
            if hasattr(self, 'data_path') and self.data_path and os.path.exists(self.data_path):
                self.load_data()
            else:
                logger.error("No training data available for prediction")
                return None
        
        try:
            # Get unique carrier-lane combinations
            data = self.raw_data.copy()
            
            # Preprocess the data again to ensure all the same preprocessing steps
            if self.preprocessed_data is None:
                self.preprocess_data()
            
            # Get features and make predictions
            X = self.preprocessed_data.drop('ONTIME_PERFORMANCE', axis=1)
            y_actual = self.preprocessed_data['ONTIME_PERFORMANCE']
            
            # Generate predictions
            y_pred_normalized = self.model.predict(X)
            y_pred = y_pred_normalized.flatten() * 100  # Convert back to percentage
            
            # Calculate individual errors
            absolute_errors = np.abs(y_actual - y_pred)
            percentage_errors = np.abs((y_actual - y_pred) / y_actual) * 100
            
            # Add predictions and errors to the original data
            data['predicted_performance'] = y_pred
            data['absolute_error'] = absolute_errors
            data['percent_error'] = percentage_errors
            
            # Calculate overall metrics
            mae = np.mean(absolute_errors)
            mape = np.mean(percentage_errors[~np.isinf(percentage_errors)])  # Exclude inf values from zero division
            rmse = np.sqrt(np.mean(np.square(y_actual - y_pred)))
            
            # Prepare results based on data format
            predictions = []
            for i, row in data.iterrows():
                if self.data_format == 'new':
                    # New format with tracking month and expanded location data
                    prediction = {
                        'carrier': row['CARRIER'],
                        'source_city': row['SOURCE_CITY'],
                        'source_state': row['SOURCE_STATE'],
                        'source_country': row['SOURCE_COUNTRY'],
                        'dest_city': row['DEST_CITY'],
                        'dest_state': row['DEST_STATE'],
                        'dest_country': row['DEST_COUNTRY'],
                        'tracking_month': row['TRACKING_MONTH'],
                        'order_count': int(row['ORDER_COUNT']),
                        'avg_transit_days': float(row['AVG_TRANSIT_DAYS']),
                        'actual_transit_days': float(row['ACTUAL_TRANSIT_DAYS']),
                        'actual_performance': float(row['ONTIME_PERFORMANCE']),
                        'predicted_performance': float(row['predicted_performance']),
                        'absolute_error': float(row['absolute_error']),
                        'percent_error': float(row['percent_error']) if not np.isinf(row['percent_error']) else None
                    }
                elif self.data_format in ['hybrid', 'hybrid_no_time']:
                    # Hybrid format with expanded location data and optional quarter
                    prediction = {
                        'carrier': row['CARRIER'],
                        'source_city': row['SOURCE_CITY'],
                        'source_state': row['SOURCE_STATE'],
                        'source_country': row['SOURCE_COUNTRY'],
                        'dest_city': row['DEST_CITY'],
                        'dest_state': row['DEST_STATE'],
                        'dest_country': row['DEST_COUNTRY'],
                        'order_count': int(row['ORDER_COUNT']),
                        'avg_transit_days': float(row['AVG_TRANSIT_DAYS']),
                        'actual_transit_days': float(row['ACTUAL_TRANSIT_DAYS']),
                        'actual_performance': float(row['ONTIME_PERFORMANCE']),
                        'predicted_performance': float(row['predicted_performance']),
                        'absolute_error': float(row['absolute_error']),
                        'percent_error': float(row['percent_error']) if not np.isinf(row['percent_error']) else None
                    }
                    # Add quarter if available
                    if 'QTR' in data.columns and 'QTR' in row:
                        prediction['quarter'] = row['QTR']
                else:
                    # Legacy format with quarter and city-only data
                    prediction = {
                        'carrier': row['CARRIER'],
                        'source_city': row['SOURCE_CITY'],
                        'dest_city': row['DEST_CITY'],
                        'quarter': row['QTR'],
                        'order_count': int(row['ORDER_COUNT']),
                        'avg_transit_days': float(row['AVG_TRANSIT_DAYS']),
                        'actual_transit_days': float(row['ACTUAL_TRANSIT_DAYS']),
                        'actual_performance': float(row['ONTIME_PERFORMANCE']),
                        'predicted_performance': float(row['predicted_performance']),
                        'absolute_error': float(row['absolute_error']),
                        'percent_error': float(row['percent_error']) if not np.isinf(row['percent_error']) else None
                    }
                predictions.append(prediction)
            
            # Prepare metrics
            metrics = {
                'mae': float(mae),
                'mape': float(mape),
                'rmse': float(rmse),
                'records_analyzed': len(data),
                'data_format': self.data_format
            }
            
            # Save results to file if output directory is specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
                # Save as JSON
                output_json = {
                    'prediction_time': datetime.now().isoformat(),
                    'data_format': self.data_format,
                    'metrics': metrics,
                    'predictions': predictions
                }
                
                json_path = os.path.join(output_dir, "prediction_data.json")
                with open(json_path, 'w') as f:
                    json.dump(output_json, f, indent=2)
                logger.info(f"Predictions saved to JSON: {json_path}")
                
                # Also save as CSV for easier analysis (format-specific columns)
                csv_path = os.path.join(output_dir, "prediction_data.csv")
                if self.data_format == 'new':
                    # New format CSV columns
                    csv_columns = ['TRACKING_MONTH', 'CARRIER', 'SOURCE_CITY', 'SOURCE_STATE', 'SOURCE_COUNTRY',
                                  'DEST_CITY', 'DEST_STATE', 'DEST_COUNTRY', 'ORDER_COUNT', 'AVG_TRANSIT_DAYS', 
                                  'ACTUAL_TRANSIT_DAYS', 'ONTIME_PERFORMANCE', 'predicted_performance', 
                                  'absolute_error', 'percent_error']
                elif self.data_format in ['hybrid', 'hybrid_no_time']:
                    # Hybrid format CSV columns
                    csv_columns = ['CARRIER', 'SOURCE_CITY', 'SOURCE_STATE', 'SOURCE_COUNTRY',
                                  'DEST_CITY', 'DEST_STATE', 'DEST_COUNTRY', 'ORDER_COUNT', 'AVG_TRANSIT_DAYS', 
                                  'ACTUAL_TRANSIT_DAYS', 'ONTIME_PERFORMANCE', 'predicted_performance', 
                                  'absolute_error', 'percent_error']
                    # Add quarter column if it exists
                    if 'QTR' in data.columns:
                        csv_columns.insert(1, 'QTR')
                else:
                    # Legacy format CSV columns
                    csv_columns = ['QTR', 'CARRIER', 'SOURCE_CITY', 'DEST_CITY', 'ORDER_COUNT', 'AVG_TRANSIT_DAYS', 
                                  'ACTUAL_TRANSIT_DAYS', 'ONTIME_PERFORMANCE', 'predicted_performance', 
                                  'absolute_error', 'percent_error']
                
                df_to_save = data[csv_columns]
                df_to_save.to_csv(csv_path, index=False)
                logger.info(f"Predictions saved to CSV: {csv_path}")
            
            # Return the results
            return {
                'prediction_time': datetime.now().isoformat(),
                'data_format': self.data_format,
                'metrics': metrics,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Error generating predictions on training data: {str(e)}")
            return None
    
    def save_model(self, path: str = "carrier_performance_model") -> bool:
        """
        Save the trained model and all preprocessing components.
        
        Args:
            path: Directory path to save the model
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Saving model to {path}...")
        
        if self.model is None:
            logger.error("No model to save. Train a model first.")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(path, exist_ok=True)
            
            # Save the Keras model
            model_path = os.path.join(path, "model.keras")
            self.model.save(model_path)
            logger.info(f"Neural network model saved to {model_path}")
            
            # Save the preprocessors and other necessary components
            # Include all possible encoders (some may be None for legacy format)
            preprocessors = {
                'carrier_encoder': self.carrier_encoder,
                'source_city_encoder': self.source_city_encoder,
                'source_state_encoder': getattr(self, 'source_state_encoder', None),
                'source_country_encoder': getattr(self, 'source_country_encoder', None),
                'dest_city_encoder': self.dest_city_encoder,
                'dest_state_encoder': getattr(self, 'dest_state_encoder', None),
                'dest_country_encoder': getattr(self, 'dest_country_encoder', None),
                'time_encoder': self.time_encoder,
                'scaler': self.scaler,
                'data_format': getattr(self, 'data_format', 'legacy')  # Save the data format
            }
            
            with open(os.path.join(path, "preprocessors.pkl"), 'wb') as f:
                pickle.dump(preprocessors, f)
            
            # Save feature information as JSON
            if hasattr(self, 'feature_info'):
                with open(os.path.join(path, "feature_info.json"), 'w') as f:
                    # Convert numpy arrays to lists for JSON serialization
                    feature_info = self.feature_info.copy()
                    json.dump(feature_info, f, indent=2)
            
            # Save a sample of the training data for reference
            if self.X_train is not None and not self.X_train.empty:
                sample_X = self.X_train.head(5)
                sample_X.to_csv(os.path.join(path, "sample_features.csv"), index=False)
            
            logger.info(f"Model and components successfully saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, path: str) -> bool:
        """
        Load a trained model and all preprocessing components.
        
        Args:
            path: Directory path containing the saved model
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Loading model from {path}...")
        
        try:
            # Load the Keras model
            model_path = os.path.join(path, "model.keras")
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                logger.info(f"Neural network model loaded from {model_path}")
            else:
                logger.error(f"Model file not found at {model_path}")
                return False
            
            # Load the preprocessors
            preprocessor_path = os.path.join(path, "preprocessors.pkl")
            if os.path.exists(preprocessor_path):
                with open(preprocessor_path, 'rb') as f:
                    preprocessors = pickle.load(f)
                
                # Load common encoders
                self.carrier_encoder = preprocessors.get('carrier_encoder')
                self.source_city_encoder = preprocessors.get('source_city_encoder')
                self.dest_city_encoder = preprocessors.get('dest_city_encoder')
                self.time_encoder = preprocessors.get('time_encoder')
                self.scaler = preprocessors.get('scaler')
                
                # Load new format encoders (may be None for legacy models)
                self.source_state_encoder = preprocessors.get('source_state_encoder')
                self.source_country_encoder = preprocessors.get('source_country_encoder')
                self.dest_state_encoder = preprocessors.get('dest_state_encoder')
                self.dest_country_encoder = preprocessors.get('dest_country_encoder')
                
                # Get data format (default to legacy for backward compatibility)
                self.data_format = preprocessors.get('data_format', 'legacy')
                
                # Backward compatibility: handle old preprocessor structure
                if self.source_city_encoder is None and 'source_encoder' in preprocessors:
                    self.source_city_encoder = preprocessors.get('source_encoder')
                if self.dest_city_encoder is None and 'dest_encoder' in preprocessors:
                    self.dest_city_encoder = preprocessors.get('dest_encoder')
                if self.time_encoder is None and 'quarter_encoder' in preprocessors:
                    self.time_encoder = preprocessors.get('quarter_encoder')
                
                logger.info("Preprocessors loaded successfully")
            else:
                logger.warning("Preprocessors file not found, some functionality may be limited")
            
            # Load feature information
            feature_info_path = os.path.join(path, "feature_info.json")
            if os.path.exists(feature_info_path):
                with open(feature_info_path, 'r') as f:
                    self.feature_info = json.load(f)
                    
                # Get feature columns from feature_info if available
                self.feature_columns = self.feature_info.get('feature_columns', [])
                
                # Set data format from feature_info if not already set
                if not hasattr(self, 'data_format') or self.data_format is None:
                    self.data_format = self.feature_info.get('data_format', 'legacy')
                
                logger.info("Feature information loaded successfully")
            else:
                logger.warning("Feature information file not found, some functionality may be limited")
            
            # Load sample features to initialize X_train if needed for predictions
            sample_features_path = os.path.join(path, "sample_features.csv")
            if os.path.exists(sample_features_path):
                self.X_train = pd.read_csv(sample_features_path)
                logger.info("Sample features loaded successfully")
            else:
                logger.warning("Sample features file not found")
            
            logger.info(f"Model successfully loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False 