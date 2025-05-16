#!/usr/bin/env python3
"""
Test script for the Carrier Performance Model

This script demonstrates training and evaluating the carrier performance
neural network model using the Carrier_Performance_New.csv dataset.
"""

import os
import sys
import logging
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

# Add the parent directory to the path so we can import the models package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.models.carrier_performance_model import CarrierPerformanceModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('carrier_performance_model_test.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to test the carrier performance model."""
    data_file = "../../data/Carrier_Performance_New.csv"
    
    if not os.path.exists(data_file):
        logger.error(f"Data file {data_file} not found!")
        return
    
    logger.info(f"Starting test with data file: {data_file}")
    
    # Create a timestamp for model output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_output_dir = f"model_output_{timestamp}"
    os.makedirs(model_output_dir, exist_ok=True)
    
    # Initialize the model
    model = CarrierPerformanceModel(data_path=data_file)
    
    # Preprocess data
    logger.info("Preprocessing data...")
    model.preprocess_data()
    
    # Prepare train/test split
    logger.info("Preparing train/test split...")
    model.prepare_train_test_split(test_size=0.2)
    
    # Build and train the model
    logger.info("Building and training the model...")
    model.build_model()
    history = model.train(epochs=100, batch_size=16, validation_split=0.2)
    
    # Plot training history
    logger.info("Plotting training history...")
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['mean_absolute_error'], label='Training MAE')
    plt.plot(history.history['val_mean_absolute_error'], label='Validation MAE')
    plt.xlabel('Epoch')
    plt.ylabel('Mean Absolute Error')
    plt.title('Training and Validation MAE')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(model_output_dir, "training_history.png"))
    
    # Evaluate the model
    logger.info("Evaluating the model...")
    evaluation = model.evaluate(plot_path=os.path.join(model_output_dir, "evaluation_plot.png"))
    
    # Print evaluation metrics
    logger.info(f"Evaluation metrics: {evaluation}")
    
    # Save the model
    logger.info("Saving the model...")
    model_path = os.path.join(model_output_dir, "carrier_performance_model")
    model.save_model(model_path)
    
    # Test predictions on a few examples
    logger.info("Testing predictions on a few examples...")
    
    # Get some carrier-lane combinations from the test set
    data = pd.read_csv(data_file)
    test_samples = data.sample(5)
    
    for _, row in test_samples.iterrows():
        carrier = row['CARRIER']
        source_city = row['SOURCE_CITY']
        dest_city = row['DEST_CITY']
        quarter = row['QTR']
        order_count = row['ORDER_COUNT']
        avg_transit_days = row['AVG_TRANSIT_DAYS']
        actual_transit_days = row['ACTUAL_TRANSIT_DAYS']
        actual_performance = row['ONTIME_PERFORMANCE']
        
        # Make prediction
        prediction = model.predict(
            carrier=carrier,
            source_city=source_city,
            dest_city=dest_city,
            quarter=quarter,
            order_count=order_count,
            avg_transit_days=avg_transit_days,
            actual_transit_days=actual_transit_days
        )
        
        if prediction:
            logger.info(f"Carrier: {carrier}, Lane: {source_city} to {dest_city}")
            logger.info(f"Actual On-Time Performance: {actual_performance:.2f}%")
            logger.info(f"Predicted On-Time Performance: {prediction['ontime_performance']:.2f}%")
            logger.info(f"Difference: {abs(actual_performance - prediction['ontime_performance']):.2f}%")
            logger.info("-" * 40)
    
    # Generate predictions on all training data
    logger.info("Generating predictions on all training data...")
    predictions_output_dir = os.path.join(model_output_dir, "training_predictions")
    results = model.predict_on_training_data(output_dir=predictions_output_dir)
    
    if results:
        metrics = results.get('metrics', {})
        logger.info(f"Overall MAE on training data: {metrics.get('mae', 'N/A')}")
        logger.info(f"Overall MAPE on training data: {metrics.get('mape', 'N/A')}")
        logger.info(f"Overall RMSE on training data: {metrics.get('rmse', 'N/A')}")
    
    logger.info("Test completed successfully!")
    logger.info(f"Model and outputs saved to: {model_output_dir}")

if __name__ == "__main__":
    main() 