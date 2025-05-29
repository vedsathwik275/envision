#!/usr/bin/env python3
"""
Test script for the updated Carrier Performance Model with new data format.
This script tests the model with tracking months and expanded location features.
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.carrier_performance_model import CarrierPerformanceModel

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('new_format_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_sample_new_format_data(filename: str = "sample_new_format.csv", num_samples: int = 100) -> str:
    """
    Create a sample dataset in the new format for testing.
    
    Args:
        filename: Name of the CSV file to create
        num_samples: Number of sample records to generate
        
    Returns:
        Path to the created sample file
    """
    logger.info(f"Creating sample new format data with {num_samples} records...")
    
    # Sample data similar to what was provided
    carriers = ['ODFL', 'HOSD', 'RBTW', 'FDEG', 'FXFC']
    source_cities = ['RICHMOND', 'ELWOOD', 'LANCASTER', 'REDLANDS', 'GRAND RAPIDS']
    source_states = ['VA', 'IN', 'PA', 'CA', 'MI']
    source_countries = ['US'] * len(source_states)
    dest_cities = ['WINDSOR', 'OMAHA', 'HOPKINS', 'MERIDIAN', 'MIAMI']
    dest_states = ['CT', 'NE', 'MN', 'MS', 'FL']
    dest_countries = ['US'] * len(dest_states)
    tracking_months = ['2025 05', '2025 04', '2025 03', '2025 02', '2025 01']
    
    # Generate random sample data
    np.random.seed(42)  # For reproducible results
    
    data = []
    for i in range(num_samples):
        source_idx = np.random.randint(0, len(source_cities))
        dest_idx = np.random.randint(0, len(dest_cities))
        
        record = {
            'TRACKING_MONTH': np.random.choice(tracking_months),
            'CARRIER': np.random.choice(carriers),
            'SOURCE_CITY': source_cities[source_idx],
            'SOURCE_STATE': source_states[source_idx],
            'SOURCE_COUNTRY': source_countries[source_idx],
            'DEST_CITY': dest_cities[dest_idx],
            'DEST_STATE': dest_states[dest_idx],
            'DEST_COUNTRY': dest_countries[dest_idx],
            'ORDER_COUNT': np.random.randint(1, 150),
            'AVG_TRANSIT_DAYS': np.random.randint(1, 5),
            'ACTUAL_TRANSIT_DAYS': np.random.randint(1, 8),
            'ONTIME_PERFORMANCE': np.random.randint(10, 100)
        }
        data.append(record)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    
    logger.info(f"Sample data created: {filename}")
    logger.info(f"Data shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    
    return filename

def test_new_format_model():
    """Test the carrier performance model with new format data."""
    logger.info("Starting new format model test...")
    
    # Create sample data
    data_file = create_sample_new_format_data("test_new_format_data.csv", 200)
    
    try:
        # Create timestamp for model output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_output_dir = f"test_new_format_output_{timestamp}"
        os.makedirs(model_output_dir, exist_ok=True)
        
        # Initialize the model with new format data
        logger.info("Initializing model with new format data...")
        model = CarrierPerformanceModel(data_path=data_file)
        
        # Verify data format detection
        logger.info(f"Detected data format: {model.data_format}")
        assert model.data_format == 'new', f"Expected 'new' format, got '{model.data_format}'"
        
        # Preprocess data
        logger.info("Preprocessing data...")
        processed_data = model.preprocess_data()
        logger.info(f"Processed data shape: {processed_data.shape}")
        
        # Prepare train/test split
        logger.info("Preparing train/test split...")
        model.prepare_train_test_split(test_size=0.2)
        
        # Build and train the model
        logger.info("Building and training the model...")
        model.build_model()
        history = model.train(epochs=50, batch_size=16, validation_split=0.2)
        
        # Evaluate the model
        logger.info("Evaluating the model...")
        evaluation_plot_path = os.path.join(model_output_dir, "evaluation_plot.png")
        evaluation = model.evaluate(plot_path=evaluation_plot_path)
        logger.info(f"Evaluation metrics: {evaluation}")
        
        # Test prediction with new format
        logger.info("Testing predictions with new format...")
        
        # Test prediction with all required parameters for new format
        prediction_result = model.predict(
            carrier='ODFL',
            source_city='RICHMOND',
            source_state='VA',
            source_country='US',
            dest_city='WINDSOR',
            dest_state='CT',
            dest_country='US',
            tracking_month='2025 05',
            order_count=73,
            avg_transit_days=2,
            actual_transit_days=4
        )
        
        if prediction_result:
            logger.info("New format prediction successful!")
            logger.info(f"Prediction result: {prediction_result}")
        else:
            logger.error("New format prediction failed!")
        
        # Test prediction without optional parameters
        prediction_minimal = model.predict(
            carrier='HOSD',
            source_city='GRAND RAPIDS',
            source_state='MI',
            source_country='US',
            dest_city='ELWOOD',
            dest_state='IN',
            dest_country='US'
        )
        
        if prediction_minimal:
            logger.info("Minimal new format prediction successful!")
            logger.info(f"Minimal prediction result: {prediction_minimal}")
        
        # Save the model
        logger.info("Saving the model...")
        model_path = os.path.join(model_output_dir, "new_format_carrier_performance_model")
        model.save_model(model_path)
        
        # Test loading the model
        logger.info("Testing model loading...")
        loaded_model = CarrierPerformanceModel()
        load_success = loaded_model.load_model(model_path)
        
        if load_success:
            logger.info("Model loaded successfully!")
            logger.info(f"Loaded model data format: {loaded_model.data_format}")
            
            # Test prediction with loaded model
            loaded_prediction = loaded_model.predict(
                carrier='ODFL',
                source_city='RICHMOND',
                source_state='VA',
                source_country='US',
                dest_city='WINDSOR',
                dest_state='CT',
                dest_country='US',
                tracking_month='2025 05'
            )
            
            if loaded_prediction:
                logger.info("Loaded model prediction successful!")
                logger.info(f"Loaded model prediction: {loaded_prediction}")
            else:
                logger.error("Loaded model prediction failed!")
        
        # Generate predictions on training data
        logger.info("Generating predictions on training data...")
        training_predictions = model.predict_on_training_data(output_dir=model_output_dir)
        
        if training_predictions:
            logger.info("Training data predictions generated successfully!")
            logger.info(f"Training predictions metrics: {training_predictions['metrics']}")
        
        logger.info(f"Test completed successfully! Output saved to: {model_output_dir}")
        
        # Cleanup
        if os.path.exists(data_file):
            os.remove(data_file)
            logger.info(f"Cleaned up test data file: {data_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_backward_compatibility():
    """Test that the model can still handle legacy format data."""
    logger.info("Testing backward compatibility with legacy format...")
    
    # Create sample legacy format data
    legacy_data = {
        'QTR': ['2025 2', '2025 2', '2025 1', '2024 4', '2024 3'],
        'CARRIER': ['HOSD', 'ODFL', 'ODFL', 'RBTW', 'FDEG'],
        'SOURCE_CITY': ['GRAND RAPIDS', 'ELWOOD', 'RICHMOND', 'LANCASTER', 'REDLANDS'],
        'DEST_CITY': ['ELWOOD', 'OMAHA', 'WINDSOR', 'SEARCY', 'MERIDIAN'],
        'ORDER_COUNT': [114, 8, 34, 19, 44],
        'AVG_TRANSIT_DAYS': [4, 1, 1, 0, 3],
        'ACTUAL_TRANSIT_DAYS': [2, 4, 2, 2, 2],
        'ONTIME_PERFORMANCE': [61, 86, 95, 79, 100]
    }
    
    legacy_df = pd.DataFrame(legacy_data)
    legacy_file = "test_legacy_format.csv"
    legacy_df.to_csv(legacy_file, index=False)
    
    try:
        # Test with legacy format
        legacy_model = CarrierPerformanceModel(data_path=legacy_file)
        
        # Verify format detection
        logger.info(f"Legacy data format detected: {legacy_model.data_format}")
        assert legacy_model.data_format == 'legacy', f"Expected 'legacy' format, got '{legacy_model.data_format}'"
        
        # Test legacy prediction
        legacy_prediction = legacy_model.predict(
            carrier='ODFL',
            source_city='ELWOOD',
            dest_city='OMAHA',
            quarter='2025 2',
            order_count=8,
            avg_transit_days=1,
            actual_transit_days=4
        )
        
        if legacy_prediction:
            logger.info("Legacy format backward compatibility test passed!")
            logger.info(f"Legacy prediction result: {legacy_prediction}")
        else:
            logger.error("Legacy format prediction failed!")
        
        # Cleanup
        if os.path.exists(legacy_file):
            os.remove(legacy_file)
        
        return True
        
    except Exception as e:
        logger.error(f"Backward compatibility test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("CARRIER PERFORMANCE MODEL - NEW FORMAT TESTING")
    logger.info("=" * 60)
    
    # Test new format
    new_format_success = test_new_format_model()
    
    # Test backward compatibility
    backward_compat_success = test_backward_compatibility()
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"New format test: {'PASSED' if new_format_success else 'FAILED'}")
    logger.info(f"Backward compatibility test: {'PASSED' if backward_compat_success else 'FAILED'}")
    
    if new_format_success and backward_compat_success:
        logger.info("All tests PASSED! ✅")
        return 0
    else:
        logger.error("Some tests FAILED! ❌")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 