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

logger = logging.getLogger(__name__)

# Set random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

class CarrierPerformanceModel:
    def __init__(self, data_path=None, model_path=None):
        """Initialize the Carrier Performance prediction model.
        
        Args:
            data_path: Path to the CSV data file
            model_path: Path to load a pre-trained model
        """
        self.data_path = data_path
        self.model_path = model_path
        self.model = None
        self.carrier_encoder = None
        self.source_encoder = None
        self.dest_encoder = None
        self.quarter_encoder = None
        self.scaler = None
        self.preprocessed_data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_columns = None
        
        # If data path is provided, load and preprocess the data
        if data_path:
            self.load_data()
        
        # If model path is provided, load the pre-trained model
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_data(self):
        """Load and perform initial preprocessing of the data."""
        logger.info(f"Loading data from {self.data_path}...")
        self.raw_data = pd.read_csv(self.data_path)
        
        # Check data integrity
        if self.raw_data.isnull().sum().sum() > 0:
            logger.warning("Data contains missing values. Filling with appropriate values.")
            self.raw_data.fillna(0, inplace=True)
        
        logger.info(f"Data loaded successfully. Shape: {self.raw_data.shape}")
        return self.raw_data
    
    def preprocess_data(self):
        """Preprocess the data for training the neural network."""
        logger.info("Preprocessing data...")
        
        # Create a copy of the raw data
        data = self.raw_data.copy()
        
        # Create lane identifier (combination of source and destination)
        data['LANE_ID'] = data['SOURCE_CITY'] + '_' + data['DEST_CITY']
        
        # One-hot encoding for categorical variables
        logger.info("Encoding categorical variables...")
        
        # Quarter encoding
        self.quarter_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        quarter_encoded = self.quarter_encoder.fit_transform(data[['QTR']])
        quarter_columns = [f'QTR_{i}' for i in range(quarter_encoded.shape[1])]
        quarter_df = pd.DataFrame(quarter_encoded, columns=quarter_columns)
        
        # Carrier encoding
        self.carrier_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        carrier_encoded = self.carrier_encoder.fit_transform(data[['CARRIER']])
        carrier_columns = [f'CARRIER_{i}' for i in range(carrier_encoded.shape[1])]
        carrier_df = pd.DataFrame(carrier_encoded, columns=carrier_columns)
        
        # Source city encoding
        self.source_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        source_encoded = self.source_encoder.fit_transform(data[['SOURCE_CITY']])
        source_columns = [f'SOURCE_{i}' for i in range(source_encoded.shape[1])]
        source_df = pd.DataFrame(source_encoded, columns=source_columns)
        
        # Destination city encoding - handle high cardinality
        dest_counts = data['DEST_CITY'].value_counts()
        top_dests = dest_counts.nlargest(50).index.tolist()  # Use top 50 destinations
        
        # Group less frequent destinations as 'OTHER'
        data['DEST_CITY_GROUPED'] = data['DEST_CITY'].apply(lambda x: x if x in top_dests else 'OTHER')
        
        # One-hot encode the grouped destinations
        self.dest_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        dest_encoded = self.dest_encoder.fit_transform(data[['DEST_CITY_GROUPED']])
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
            # Filter down to available columns
            available_num_cols = [col for col in numerical_cols if col in data.columns]
            if available_num_cols:
                numerical_data = self.scaler.fit_transform(data[available_num_cols])
                numerical_df = pd.DataFrame(numerical_data, columns=available_num_cols)
        
        # Reset indices to ensure proper concatenation
        data.reset_index(drop=True, inplace=True)
        quarter_df.reset_index(drop=True, inplace=True)
        carrier_df.reset_index(drop=True, inplace=True)
        source_df.reset_index(drop=True, inplace=True)
        dest_df.reset_index(drop=True, inplace=True)
        if not numerical_df.empty:
            numerical_df.reset_index(drop=True, inplace=True)
        
        # Create the final processed dataset
        dfs_to_concat = [
            data[['ONTIME_PERFORMANCE']],
            quarter_df,
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
        
        logger.info(f"Data preprocessing complete. Processed shape: {processed_data.shape}")
        self.preprocessed_data = processed_data
        
        # Save information about the features for later use
        self.feature_info = {
            'quarter_categories': self.quarter_encoder.categories_[0].tolist(),
            'carrier_categories': self.carrier_encoder.categories_[0].tolist(),
            'source_categories': self.source_encoder.categories_[0].tolist(),
            'dest_categories': self.dest_encoder.categories_[0].tolist(),
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
    
    def predict(self, carrier, source_city, dest_city, quarter=None, order_count=None, avg_transit_days=None, actual_transit_days=None):
        """Predict the on-time performance for a specific carrier and lane.
        
        Args:
            carrier: Carrier name
            source_city: Source city name
            dest_city: Destination city name
            quarter: Quarter (e.g., '2025 1')
            order_count: Number of orders
            avg_transit_days: Average transit days
            actual_transit_days: Actual transit days
            
        Returns:
            Predicted on-time performance percentage
        """
        if self.model is None:
            logger.error("No model available for prediction. Train or load a model first.")
            return None
        
        # Check if all encoders are available
        if not all([self.carrier_encoder, self.source_encoder, self.dest_encoder]):
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
                input_data['QTR'] = [self.quarter_encoder.categories_[0][-1]]
            
            # Add optional numerical features
            numerical_features = {}
            if order_count is not None:
                numerical_features['ORDER_COUNT'] = [order_count]
            if avg_transit_days is not None:
                numerical_features['AVG_TRANSIT_DAYS'] = [avg_transit_days]
            if actual_transit_days is not None:
                numerical_features['ACTUAL_TRANSIT_DAYS'] = [actual_transit_days]
            
            # Apply preprocessing steps
            
            # Quarter encoding
            quarter_encoded = self.quarter_encoder.transform(input_data[['QTR']])
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
            source_encoded = self.source_encoder.transform(input_data[['SOURCE_CITY']])
            source_df = pd.DataFrame(
                source_encoded, 
                columns=[f'SOURCE_{i}' for i in range(source_encoded.shape[1])]
            )
            
            # Destination city encoding
            # Check if dest_city is in the top destinations, otherwise use 'OTHER'
            top_dests = self.dest_encoder.categories_[0]
            dest_city_grouped = dest_city if dest_city in top_dests else 'OTHER'
            input_data['DEST_CITY_GROUPED'] = [dest_city_grouped]
            
            dest_encoded = self.dest_encoder.transform(input_data[['DEST_CITY_GROUPED']])
            dest_df = pd.DataFrame(
                dest_encoded, 
                columns=[f'DEST_{i}' for i in range(dest_encoded.shape[1])]
            )
            
            # Scale numerical features if provided
            numerical_df = pd.DataFrame()
            if numerical_features and self.scaler is not None:
                available_num_cols = [col for col in numerical_features.keys() if col in self.feature_info.get('numerical_columns', [])]
                if available_num_cols:
                    num_input = pd.DataFrame({col: numerical_features[col] for col in available_num_cols})
                    scaled_numerical = self.scaler.transform(num_input)
                    numerical_df = pd.DataFrame(
                        scaled_numerical,
                        columns=available_num_cols
                    )
            
            # Combine all features
            dfs_to_concat = [quarter_df, carrier_df, source_df, dest_df]
            if not numerical_df.empty:
                dfs_to_concat.append(numerical_df)
            
            # Create the input feature vector
            features = pd.concat(dfs_to_concat, axis=1)
            
            # Align feature columns with model's expected input
            # Make sure we have all required columns in the correct order
            model_input = pd.DataFrame(0, index=[0], columns=self.feature_columns)
            for col in features.columns:
                if col in model_input.columns:
                    model_input[col] = features[col].values[0]
            
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
            logger.error(f"Error during prediction: {str(e)}")
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
    
    def predict_on_training_data(self, output_dir=None):
        """
        Generate predictions on the training data and calculate performance metrics.
        
        Args:
            output_dir: Directory to save prediction results
            
        Returns:
            Dictionary with predictions and performance metrics
        """
        logger.info("Generating predictions on training data...")
        
        if self.raw_data is None:
            logger.error("No training data available. Load data first.")
            return None
        
        if self.model is None:
            logger.error("No model available for prediction. Train or load a model first.")
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
            
            # Prepare results
            predictions = []
            for i, row in data.iterrows():
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
                'records_analyzed': len(data)
            }
            
            # Save results to file if output directory is specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
                # Save as JSON
                output_json = {
                    'prediction_time': datetime.now().isoformat(),
                    'metrics': metrics,
                    'predictions': predictions
                }
                
                json_path = os.path.join(output_dir, "prediction_data.json")
                with open(json_path, 'w') as f:
                    json.dump(output_json, f, indent=2)
                logger.info(f"Predictions saved to JSON: {json_path}")
                
                # Also save as CSV for easier analysis
                csv_path = os.path.join(output_dir, "prediction_data.csv")
                df_to_save = data[['QTR', 'CARRIER', 'SOURCE_CITY', 'DEST_CITY', 
                                  'ORDER_COUNT', 'AVG_TRANSIT_DAYS', 'ACTUAL_TRANSIT_DAYS',
                                  'ONTIME_PERFORMANCE', 'predicted_performance', 
                                  'absolute_error', 'percent_error']]
                df_to_save.to_csv(csv_path, index=False)
                logger.info(f"Predictions saved to CSV: {csv_path}")
            
            # Return the results
            return {
                'prediction_time': datetime.now().isoformat(),
                'metrics': metrics,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Error generating predictions on training data: {str(e)}")
            return None
    
    def save_model(self, path="carrier_performance_model"):
        """
        Save the trained model and all preprocessing components.
        
        Args:
            path: Directory path to save the model
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
            preprocessors = {
                'carrier_encoder': self.carrier_encoder,
                'source_encoder': self.source_encoder,
                'dest_encoder': self.dest_encoder,
                'quarter_encoder': self.quarter_encoder,
                'scaler': self.scaler
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
    
    def load_model(self, path):
        """
        Load a trained model and all preprocessing components.
        
        Args:
            path: Directory path containing the saved model
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
                
                self.carrier_encoder = preprocessors.get('carrier_encoder')
                self.source_encoder = preprocessors.get('source_encoder')
                self.dest_encoder = preprocessors.get('dest_encoder')
                self.quarter_encoder = preprocessors.get('quarter_encoder')
                self.scaler = preprocessors.get('scaler')
                
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
                logger.info("Feature information loaded successfully")
            else:
                logger.warning("Feature information file not found, some functionality may be limited")
            
            # Load sample features to initialize X_train if needed for predictions
            sample_features_path = os.path.join(path, "sample_features.csv")
            if os.path.exists(sample_features_path):
                self.X_train = pd.read_csv(sample_features_path)
                logger.info("Sample features loaded successfully")
            else:
                logger.warning("Sample features file not found, creating dummy X_train")
                # Create a dummy X_train with the right columns if we have feature_columns
                if self.feature_columns:
                    self.X_train = pd.DataFrame(columns=self.feature_columns)
                    self.X_train.loc[0] = 0  # Add one row with zeros
            
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False 