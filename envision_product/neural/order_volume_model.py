#!/usr/bin/env python3
# Order Volume Neural Network Model
# This script processes order volume data, trains a neural network model,
# and generates predictions for future months.

import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from datetime import datetime
import pickle

# Set random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

class OrderVolumeModel:
    def __init__(self, data_path=None, model_path=None):
        """Initialize the Order Volume prediction model.
        
        Args:
            data_path: Path to the CSV data file
            model_path: Path to load a pre-trained model
        """
        self.data_path = data_path
        self.model_path = model_path
        self.model = None
        self.source_encoder = None
        self.dest_encoder = None
        self.type_encoder = None
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
        print(f"Loading data from {self.data_path}...")
        self.raw_data = pd.read_csv(self.data_path)
        
        # Check data integrity
        if self.raw_data.isnull().sum().sum() > 0:
            print("Warning: Data contains missing values. Filling with appropriate values.")
            self.raw_data.fillna(0, inplace=True)
        
        print(f"Data loaded successfully. Shape: {self.raw_data.shape}")
    
    def preprocess_data(self):
        """Preprocess the data for training the neural network."""
        print("Preprocessing data...")
        
        # Create a copy of the raw data
        data = self.raw_data.copy()
        
        # Convert ORDER MONTH to a proper datetime format
        data['ORDER_MONTH_DATE'] = pd.to_datetime(data['ORDER MONTH'].str.replace(' ', '-') + '-01')
        
        # Extract year and month as separate features
        data['YEAR'] = data['ORDER_MONTH_DATE'].dt.year
        data['MONTH'] = data['ORDER_MONTH_DATE'].dt.month
        
        # Convert categorical variables to one-hot encoding
        print("Encoding categorical variables...")
        
        # Source city encoding
        self.source_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        source_encoded = self.source_encoder.fit_transform(data[['SOURCE CITY']])
        source_columns = [f'SOURCE_{i}' for i in range(source_encoded.shape[1])]
        source_df = pd.DataFrame(source_encoded, columns=source_columns)
        
        # Destination city encoding
        self.dest_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        dest_encoded = self.dest_encoder.fit_transform(data[['DESTINATION CITY']])
        
        # Since there are many destination cities, we'll use dimensionality reduction
        # by only keeping the top 50 most frequent destinations, the rest will be handled as 'unknown'
        dest_counts = data['DESTINATION CITY'].value_counts()
        top_dests = dest_counts.nlargest(50).index.tolist()
        
        # Re-fit encoder with only top destinations
        data['DEST_CITY_GROUPED'] = data['DESTINATION CITY'].apply(lambda x: x if x in top_dests else 'OTHER')
        self.dest_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        dest_encoded = self.dest_encoder.fit_transform(data[['DEST_CITY_GROUPED']])
        dest_columns = [f'DEST_{i}' for i in range(dest_encoded.shape[1])]
        dest_df = pd.DataFrame(dest_encoded, columns=dest_columns)
        
        # Order type encoding
        self.type_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        type_encoded = self.type_encoder.fit_transform(data[['ORDER TYPE']])
        type_columns = [f'TYPE_{i}' for i in range(type_encoded.shape[1])]
        type_df = pd.DataFrame(type_encoded, columns=type_columns)
        
        # Combine all encoded features
        print("Combining features...")
        
        # Reset the index of data to ensure proper concatenation
        data.reset_index(drop=True, inplace=True)
        source_df.reset_index(drop=True, inplace=True)
        dest_df.reset_index(drop=True, inplace=True)
        type_df.reset_index(drop=True, inplace=True)
        
        # Create final dataset with all features
        processed_data = pd.concat([
            data[['YEAR', 'MONTH', 'ORDER VOLUME']],
            source_df,
            dest_df,
            type_df
        ], axis=1)
        
        # Scale numerical features (except the target variable)
        self.scaler = StandardScaler()
        numerical_cols = ['YEAR', 'MONTH']
        processed_data[numerical_cols] = self.scaler.fit_transform(processed_data[numerical_cols])
        
        print(f"Data preprocessing complete. Processed shape: {processed_data.shape}")
        self.preprocessed_data = processed_data
        
        # Create lane identifier (combination of source, destination, and order type)
        self.raw_data['LANE_ID'] = (
            self.raw_data['SOURCE CITY'] + '_' + 
            self.raw_data['DESTINATION CITY'] + '_' + 
            self.raw_data['ORDER TYPE']
        )
        
        return processed_data
    
    def prepare_train_test_split(self, test_size=0.2):
        """Split the preprocessed data into training and testing sets."""
        print(f"Splitting data with test_size={test_size}...")
        
        if self.preprocessed_data is None:
            self.preprocess_data()
        
        # Separate features and target
        X = self.preprocessed_data.drop('ORDER VOLUME', axis=1)
        y = self.preprocessed_data['ORDER VOLUME']
        
        # Split the data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        print(f"Train set: {self.X_train.shape[0]} samples")
        print(f"Test set: {self.X_test.shape[0]} samples")
    
    def build_model(self):
        """Build the neural network model architecture."""
        print("Building neural network model...")
        
        # Get input shape from training data
        input_dim = self.X_train.shape[1]
        
        # Create a sequential model
        model = models.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1)  # Output layer - regression task
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
    
    def train(self, epochs=100, batch_size=32, validation_split=0.2):
        """Train the neural network model."""
        print(f"Training model with {epochs} epochs and batch_size={batch_size}...")
        
        if self.X_train is None or self.y_train is None:
            self.prepare_train_test_split()
        
        if self.model is None:
            self.build_model()
        
        # Create model checkpoint to save best model
        checkpoint_path = "best_model.keras"
        checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
            checkpoint_path,
            monitor='val_loss',
            save_best_only=True,
            mode='min',
            verbose=1
        )
        
        # Early stopping to prevent overfitting
        early_stop = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        )
        
        # Train the model
        history = self.model.fit(
            self.X_train, self.y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[checkpoint_callback, early_stop],
            verbose=1
        )
        
        # Load the best model weights
        self.model.load_weights(checkpoint_path)
        
        return history
    
    def evaluate(self):
        """Evaluate the model on the test set."""
        print("Evaluating model on test set...")
        
        if self.model is None:
            raise ValueError("Model has not been trained yet. Call train() first.")
        
        # Make predictions on the test set
        y_pred = self.model.predict(self.X_test)
        
        # Calculate evaluation metrics
        mae = mean_absolute_error(self.y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
        r2 = r2_score(self.y_test, y_pred)
        
        print(f"Mean Absolute Error: {mae:.2f}")
        print(f"Root Mean Squared Error: {rmse:.2f}")
        print(f"R² Score: {r2:.4f}")
        
        # Plot actual vs predicted values
        plt.figure(figsize=(10, 6))
        plt.scatter(self.y_test, y_pred, alpha=0.5)
        plt.plot([0, self.y_test.max()], [0, self.y_test.max()], 'r--')
        plt.xlabel('Actual Order Volume')
        plt.ylabel('Predicted Order Volume')
        plt.title('Actual vs Predicted Order Volume')
        plt.savefig('prediction_evaluation.png')
        plt.close()
        
        return {'mae': mae, 'rmse': rmse, 'r2': r2}
    
    def predict_future(self, months=6):
        """Generate predictions for future months for each unique lane.
        
        Args:
            months: Number of future months to predict
        
        Returns:
            DataFrame with predictions for each lane and future month
        """
        print(f"Generating predictions for the next {months} months...")
        
        if self.model is None:
            raise ValueError("Model has not been trained yet. Call train() first.")
        
        # Get unique lanes (source, destination, order type combinations)
        unique_lanes = self.raw_data['LANE_ID'].unique()
        
        # Get the latest month in the data
        latest_month_str = self.raw_data['ORDER MONTH'].max()
        latest_date = pd.to_datetime(latest_month_str.replace(' ', '-') + '-01')
        
        # Create a dataframe to store predictions
        future_predictions = []
        
        for lane in unique_lanes:
            # Split the lane ID back into its components
            source, destination, order_type = lane.split('_', 2)
            
            # For each future month, prepare input data and make prediction
            for i in range(1, months+1):
                # Calculate future date
                future_date = pd.DateOffset(months=i)
                prediction_date = latest_date + future_date
                
                # Create input features for prediction
                prediction_input = pd.DataFrame({
                    'SOURCE CITY': [source],
                    'DESTINATION CITY': [destination],
                    'ORDER TYPE': [order_type],
                    'YEAR': [prediction_date.year],
                    'MONTH': [prediction_date.month]
                })
                
                # Handle destination city grouping
                top_dests = self.raw_data['DESTINATION CITY'].value_counts().nlargest(50).index.tolist()
                prediction_input['DEST_CITY_GROUPED'] = prediction_input['DESTINATION CITY'].apply(
                    lambda x: x if x in top_dests else 'OTHER'
                )
                
                # Encode categorical variables
                source_encoded = self.source_encoder.transform(prediction_input[['SOURCE CITY']])
                dest_encoded = self.dest_encoder.transform(prediction_input[['DEST_CITY_GROUPED']])
                type_encoded = self.type_encoder.transform(prediction_input[['ORDER TYPE']])
                
                # Create column names
                source_columns = [f'SOURCE_{i}' for i in range(source_encoded.shape[1])]
                dest_columns = [f'DEST_{i}' for i in range(dest_encoded.shape[1])]
                type_columns = [f'TYPE_{i}' for i in range(type_encoded.shape[1])]
                
                # Create DataFrames for each encoded feature
                source_df = pd.DataFrame(source_encoded, columns=source_columns)
                dest_df = pd.DataFrame(dest_encoded, columns=dest_columns)
                type_df = pd.DataFrame(type_encoded, columns=type_columns)
                
                # Scale numerical features
                numerical_data = prediction_input[['YEAR', 'MONTH']]
                scaled_numerical = self.scaler.transform(numerical_data)
                numerical_df = pd.DataFrame(
                    scaled_numerical, 
                    columns=['YEAR', 'MONTH']
                )
                
                # Combine all features
                X_pred = pd.concat([
                    numerical_df,
                    source_df,
                    dest_df,
                    type_df
                ], axis=1)
                
                # Make prediction
                prediction = self.model.predict(X_pred)[0][0]
                
                # Round prediction and handle negative values
                prediction = max(round(prediction), 0)
                
                # Add prediction to results
                future_predictions.append({
                    'SOURCE CITY': source,
                    'DESTINATION CITY': destination,
                    'ORDER TYPE': order_type,
                    'PREDICTION YEAR': prediction_date.year,
                    'PREDICTION MONTH': prediction_date.month,
                    'PREDICTION DATE': prediction_date.strftime('%Y-%m'),
                    'PREDICTED ORDER VOLUME': prediction
                })
        
        # Convert to DataFrame
        predictions_df = pd.DataFrame(future_predictions)
        
        # Save predictions to CSV
        predictions_df.to_csv('future_predictions.csv', index=False)
        print(f"Predictions saved to 'future_predictions.csv'")
        
        return predictions_df
    
    def save_model(self, path="order_volume_model"):
        """Save the trained model and preprocessing components."""
        print(f"Saving model to {path}...")
        
        if self.model is None:
            raise ValueError("Model has not been trained yet. Call train() first.")
        
        # Create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        
        # Save the model
        self.model.save(os.path.join(path, "model.keras"))
        
        # Save preprocessors
        with open(os.path.join(path, "preprocessors.pkl"), "wb") as f:
            pickle.dump({
                'source_encoder': self.source_encoder,
                'dest_encoder': self.dest_encoder,
                'type_encoder': self.type_encoder,
                'scaler': self.scaler
            }, f)
        
        print(f"Model and preprocessors saved successfully to {path}")
    
    def load_model(self, path):
        """Load a trained model and preprocessors."""
        print(f"Loading model from {path}...")
        
        # Load the model
        model_path = os.path.join(path, "model.keras")
        self.model = models.load_model(model_path)
        
        # Load preprocessors
        preprocessors_path = os.path.join(path, "preprocessors.pkl")
        with open(preprocessors_path, "rb") as f:
            preprocessors = pickle.load(f)
            self.source_encoder = preprocessors['source_encoder']
            self.dest_encoder = preprocessors['dest_encoder']
            self.type_encoder = preprocessors['type_encoder']
            self.scaler = preprocessors['scaler']
        
        print("Model and preprocessors loaded successfully")


def main():
    """Main function to execute model training and prediction."""
    # Define paths
    data_path = "data/OrderVolume_ByMonth_v2.csv"
    
    # Initialize model
    model = OrderVolumeModel(data_path=data_path)
    
    # Preprocess data
    model.preprocess_data()
    
    # Prepare train/test split
    model.prepare_train_test_split(test_size=0.2)
    
    # Build and train model
    model.build_model()
    history = model.train(epochs=100, batch_size=32)
    
    # Evaluate model
    metrics = model.evaluate()
    
    # Generate future predictions
    predictions = model.predict_future(months=6)
    
    # Save model
    model.save_model("order_volume_model")
    
    print("Model training and prediction complete!")


if __name__ == "__main__":
    main() 