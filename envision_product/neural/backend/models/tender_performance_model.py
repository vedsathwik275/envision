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

logger = logging.getLogger(__name__)

# Set random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

class TenderPerformanceModel:
    def __init__(self, data_path=None, model_path=None):
        """Initialize the Tender Performance prediction model.
        
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
        self.scaler = None
        self.preprocessed_data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
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
        
        # Ensure column names are standardized
        if 'TENDER_PERF_PERCENTAGE' in self.raw_data.columns:
            self.target_column = 'TENDER_PERF_PERCENTAGE'
        else:
            # Try to identify the performance column
            potential_columns = [col for col in self.raw_data.columns if 'perf' in col.lower() or 'rate' in col.lower()]
            if potential_columns:
                self.target_column = potential_columns[0]
                logger.info(f"Using {self.target_column} as the target column")
            else:
                raise ValueError("Could not identify the tender performance column in the data")
        
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
        # Get top N destination cities
        dest_counts = data['DEST_CITY'].value_counts()
        top_dests = dest_counts.nlargest(50).index.tolist()  # Use top 50 destinations
        
        # Group less frequent destinations as 'OTHER'
        data['DEST_CITY_GROUPED'] = data['DEST_CITY'].apply(lambda x: x if x in top_dests else 'OTHER')
        
        # One-hot encode the grouped destinations
        self.dest_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        dest_encoded = self.dest_encoder.fit_transform(data[['DEST_CITY_GROUPED']])
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
        
        logger.info(f"Data preprocessing complete. Processed shape: {processed_data.shape}")
        self.preprocessed_data = processed_data
        
        return processed_data
    
    def prepare_train_test_split(self, test_size=0.2):
        """Split the preprocessed data into training and testing sets."""
        logger.info(f"Splitting data with test_size={test_size}...")
        
        if self.preprocessed_data is None:
            self.preprocess_data()
        
        # Separate features and target
        X = self.preprocessed_data.drop(self.target_column, axis=1)
        y = self.preprocessed_data[self.target_column]
        
        # Normalize the target value to [0, 1] range
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
    
    def predict(self, carrier, source_city, dest_city):
        """Predict tender performance for a specific carrier and lane."""
        logger.info(f"Predicting performance for {carrier} from {source_city} to {dest_city}...")
        
        if self.model is None:
            logger.error("Model not loaded or trained. Cannot make predictions.")
            return None
            
        # Ensure X_train is loaded - this is what's causing the error
        if self.X_train is None:
            logger.info("X_train not initialized. Loading and preprocessing data...")
            # Check if we need to load the raw data first
            if not hasattr(self, 'raw_data') or self.raw_data is None:
                # Try to load sample data if available
                sample_data_path = os.path.join(os.path.dirname(self.model_path), "sample_data.csv")
                if os.path.exists(sample_data_path):
                    logger.info(f"Loading sample data from {sample_data_path}")
                    self.raw_data = pd.read_csv(sample_data_path)
                else:
                    logger.error("No raw data available for feature extraction")
                    return None
            
            # Process the data
            self.preprocess_data()
            # Create a dummy split to initialize X_train
            self.prepare_train_test_split(test_size=0.2)
        
        # Create a sample dataframe
        sample = pd.DataFrame({
            'CARRIER': [carrier],
            'SOURCE_CITY': [source_city],
            'DEST_CITY': [dest_city]
        })
        
        # Handle destination cities not in the training data
        if self.dest_encoder is None:
            logger.error("Destination encoder not initialized")
            return None
            
        try:
            # Check if destination city is in the encoder's categories
            dest_categories = self.dest_encoder.categories_[0]
            if dest_city not in dest_categories:
                logger.warning(f"Destination city {dest_city} not found in training data. Using 'OTHER'.")
                sample['DEST_CITY_GROUPED'] = ['OTHER']
            else:
                sample['DEST_CITY_GROUPED'] = [dest_city]
            
            # Transform the categorical features
            carrier_encoded = self.carrier_encoder.transform(sample[['CARRIER']])
            source_encoded = self.source_encoder.transform(sample[['SOURCE_CITY']])
            dest_encoded = self.dest_encoder.transform(sample[['DEST_CITY_GROUPED']])
            
            # Create column names
            carrier_cols = [f'CARRIER_{i}' for i in range(carrier_encoded.shape[1])]
            source_cols = [f'SOURCE_{i}' for i in range(source_encoded.shape[1])]
            dest_cols = [f'DEST_{i}' for i in range(dest_encoded.shape[1])]
            
            # Create feature dataframes
            carrier_df = pd.DataFrame(carrier_encoded, columns=carrier_cols)
            source_df = pd.DataFrame(source_encoded, columns=source_cols)
            dest_df = pd.DataFrame(dest_encoded, columns=dest_cols)
            
            # Combine features
            features = pd.concat([carrier_df, source_df, dest_df], axis=1)
            
            # Ensure all expected features are present (fill missing with zeros)
            expected_features = set(self.X_train.columns)
            actual_features = set(features.columns)
            
            missing_features = expected_features - actual_features
            for feature in missing_features:
                features[feature] = 0
                
            # Ensure features are in the same order as during training
            features = features[self.X_train.columns]
            
            # Make prediction
            prediction = self.model.predict(features)[0][0]
            
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
            logger.error(f"Error predicting tender performance: {str(e)}")
            return None
    
    def predict_batch(self, carriers, source_cities, dest_cities):
        """Predict tender performance for multiple combinations."""
        if len(carriers) != len(source_cities) or len(carriers) != len(dest_cities):
            raise ValueError("Input lists must have the same length")
        
        results = []
        for i in range(len(carriers)):
            prediction = self.predict(carriers[i], source_cities[i], dest_cities[i])
            results.append(prediction)
        
        return results
    
    def predict_on_training_data(self, output_dir=None):
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
            # Create output directory if not provided
            if output_dir is None and self.model_path:
                output_dir = os.path.join(self.model_path, "training_predictions")
            elif output_dir is None:
                output_dir = "training_predictions"
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Get the relevant columns for prediction
            carrier_col = 'CARRIER'
            source_col = 'SOURCE_CITY'
            dest_col = 'DEST_CITY'
            
            # Ensure we have the necessary columns
            if not all(col in self.raw_data.columns for col in [carrier_col, source_col, dest_col, self.target_column]):
                logger.error("Training data missing required columns for prediction.")
                return None
            
            # Get unique combinations to predict on
            predictions = []
            total_rows = len(self.raw_data)
            
            logger.info(f"Processing {total_rows} training data rows for prediction")
            
            # Iterate through each row in the training data
            for index, row in self.raw_data.iterrows():
                try:
                    carrier = row[carrier_col]
                    source_city = row[source_col]
                    dest_city = row[dest_col]
                    actual_performance = row[self.target_column]
                    
                    # Make the prediction
                    prediction = self.predict(carrier, source_city, dest_city)
                    
                    if prediction:
                        # Add the actual performance value for comparison
                        prediction['actual_performance'] = float(actual_performance)
                        
                        # Calculate error metrics
                        predicted = prediction['predicted_performance']
                        actual = prediction['actual_performance']
                        prediction['absolute_error'] = abs(predicted - actual)
                        prediction['percent_error'] = (abs(predicted - actual) / max(1, actual)) * 100
                        
                        predictions.append(prediction)
                    
                    # Log progress for large datasets
                    if (index + 1) % 100 == 0 or (index + 1) == total_rows:
                        logger.info(f"Processed {index + 1}/{total_rows} training data rows")
                    
                except Exception as e:
                    logger.warning(f"Error predicting row {index}: {str(e)}")
                    continue
            
            # Calculate summary metrics
            if predictions:
                mae = sum(p['absolute_error'] for p in predictions) / len(predictions)
                mape = sum(p['percent_error'] for p in predictions) / len(predictions)
                
                # Create the prediction result
                result = {
                    "prediction_time": datetime.now().isoformat(),
                    "predictions": predictions,
                    "metrics": {
                        "count": len(predictions),
                        "mae": float(mae),
                        "mape": float(mape)
                    }
                }
                
                # Save as JSON
                json_path = os.path.join(output_dir, "prediction_data.json")
                with open(json_path, "w") as f:
                    json.dump(result, f, indent=2)
                logger.info(f"Training predictions saved to {json_path}")
                
                # Save as CSV
                csv_path = os.path.join(output_dir, "prediction_data.csv")
                
                # Convert to DataFrame for CSV export
                df = pd.DataFrame(predictions)
                df.to_csv(csv_path, index=False)
                logger.info(f"Training predictions saved to {csv_path}")
                
                return result
            else:
                logger.warning("No valid predictions generated from training data")
                return {
                    "prediction_time": datetime.now().isoformat(),
                    "predictions": [],
                    "warning": "No valid predictions could be generated from training data."
                }
        
        except Exception as e:
            logger.error(f"Error generating predictions on training data: {str(e)}")
            return None
    
    def save_model(self, path="tender_performance_model"):
        """Save the model, encoders, and preprocessing info."""
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
            logger.info(f"Model saved to {model_path}")
            
            # Ensure all encoders are available
            if self.carrier_encoder is None or self.source_encoder is None or self.dest_encoder is None:
                logger.error("One or more encoders are not initialized. Cannot save model.")
                return False
            
            # Save encoders and preprocessing info
            encoders = {
                "carrier_encoder": self.carrier_encoder,
                "source_encoder": self.source_encoder,
                "dest_encoder": self.dest_encoder,
                "target_column": self.target_column
            }
            
            encoders_path = os.path.join(path, "encoders.pkl")
            with open(encoders_path, "wb") as f:
                pickle.dump(encoders, f)
            logger.info(f"Encoders saved to {encoders_path}")
            
            # Ensure raw_data is available and save a sample
            if hasattr(self, 'raw_data') and self.raw_data is not None:
                sample_data = self.raw_data.head(100)  # Save first 100 records
                sample_data_path = os.path.join(path, "sample_data.csv")
                sample_data.to_csv(sample_data_path, index=False)
                logger.info(f"Sample data saved to {sample_data_path}")
            else:
                logger.warning("No raw data available. Predictions may fail without sample data.")
            
            # Save feature column information
            if self.X_train is not None:
                feature_info = {
                    "columns": list(self.X_train.columns)
                }
                feature_info_path = os.path.join(path, "feature_info.json")
                with open(feature_info_path, "w") as f:
                    json.dump(feature_info, f)
                logger.info(f"Feature information saved to {feature_info_path}")
            else:
                logger.warning("X_train not available. Feature column information couldn't be saved.")
            
            logger.info(f"Model and preprocessing artifacts saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, path):
        """Load the model, encoders, and preprocessing info."""
        logger.info(f"Loading model from {path}...")
        self.model_path = path
        
        if not os.path.exists(path):
            logger.error(f"Model path {path} does not exist")
            return False
        
        try:
            # Load the Keras model
            model_path = os.path.join(path, "model.keras")
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                logger.info(f"Keras model loaded from {model_path}")
            else:
                logger.error(f"Model file not found at {model_path}")
                return False
            
            # Load encoders and preprocessing info
            encoders_path = os.path.join(path, "encoders.pkl")
            if os.path.exists(encoders_path):
                with open(encoders_path, "rb") as f:
                    encoders = pickle.load(f)
                    
                self.carrier_encoder = encoders.get("carrier_encoder")
                self.source_encoder = encoders.get("source_encoder")
                self.dest_encoder = encoders.get("dest_encoder")
                self.target_column = encoders.get("target_column", "TENDER_PERF_PERCENTAGE")
                logger.info("Encoders loaded successfully")
            else:
                logger.error(f"Encoders file not found at {encoders_path}")
                return False
            
            # Load feature information if available
            feature_info_path = os.path.join(path, "feature_info.json")
            feature_columns = None
            if os.path.exists(feature_info_path):
                try:
                    with open(feature_info_path, "r") as f:
                        feature_info = json.load(f)
                        feature_columns = feature_info.get("columns")
                        logger.info(f"Feature columns loaded from feature_info.json: {len(feature_columns)} columns")
                except Exception as e:
                    logger.warning(f"Error loading feature info: {str(e)}")
            
            # Load sample data
            sample_data_path = os.path.join(path, "sample_data.csv")
            if os.path.exists(sample_data_path):
                self.raw_data = pd.read_csv(sample_data_path)
                logger.info(f"Sample data loaded: {len(self.raw_data)} rows, {len(self.raw_data.columns)} columns")
                
                # Initialize the preprocessing pipeline to ensure prediction works
                self.preprocess_data()
                self.prepare_train_test_split(test_size=0.2)
                
                # If we have feature columns and X_train doesn't match, recreate it
                if feature_columns and set(self.X_train.columns) != set(feature_columns):
                    logger.warning("X_train columns don't match saved feature columns. Adjusting...")
                    
                    # Create a dummy X_train with the correct columns
                    dummy_data = {col: [0] for col in feature_columns}
                    self.X_train = pd.DataFrame(dummy_data)
                
                logger.info("Data preprocessing initialized from sample data")
            else:
                logger.warning(f"Sample data file not found at {sample_data_path}. Some model features may be missing.")
                
                # If we have feature columns but no sample data, create a dummy X_train
                if feature_columns:
                    logger.info("Creating dummy X_train from feature information")
                    dummy_data = {col: [0] for col in feature_columns}
                    self.X_train = pd.DataFrame(dummy_data)
            
            logger.info(f"Model successfully loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model from {path}: {str(e)}")
            return False 