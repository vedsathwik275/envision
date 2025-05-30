#!/usr/bin/env python3
"""
Test script for the updated Carrier Performance Model with hybrid format support.

This script tests the model's ability to handle data with state and country information
but without explicit time dimensions (hybrid format).
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from models.carrier_performance_model import CarrierPerformanceModel

def create_test_data():
    """Create test data in hybrid format with state/country information."""
    print("Creating test data in hybrid format...")
    
    # Sample data similar to your new format
    test_data = [
        ['ODFL', 'ELWOOD', 'IL', 'US', 'ABINGDON', 'VA', 'US', 5, 1, 4, 40],
        ['ODFL', 'ELWOOD', 'IL', 'US', 'ATLANTA', 'GA', 'US', 8, 2, 3, 75],
        ['FDX', 'CHICAGO', 'IL', 'US', 'DALLAS', 'TX', 'US', 12, 3, 2, 90],
        ['UPS', 'NEW YORK', 'NY', 'US', 'LOS ANGELES', 'CA', 'US', 15, 4, 5, 65],
        ['ODFL', 'RICHMOND', 'VA', 'US', 'WINDSOR', 'CT', 'US', 73, 2, 4, 16],
        ['FDX', 'MIAMI', 'FL', 'US', 'SEATTLE', 'WA', 'US', 20, 5, 4, 85],
        ['UPS', 'DENVER', 'CO', 'US', 'PHOENIX', 'AZ', 'US', 25, 3, 3, 95],
        ['ODFL', 'BOSTON', 'MA', 'US', 'PORTLAND', 'OR', 'US', 10, 6, 7, 55],
    ]
    
    columns = [
        'CARRIER', 'SOURCE_CITY', 'SOURCE_STATE', 'SOURCE_COUNTRY',
        'DEST_CITY', 'DEST_STATE', 'DEST_COUNTRY', 'ORDER_COUNT',
        'AVG_TRANSIT_DAYS', 'ACTUAL_TRANSIT_DAYS', 'ONTIME_PERFORMANCE'
    ]
    
    df = pd.DataFrame(test_data, columns=columns)
    
    # Save to CSV
    test_data_path = backend_dir / 'test_data' / 'carrier_performance_hybrid_test.csv'
    test_data_path.parent.mkdir(exist_ok=True)
    df.to_csv(test_data_path, index=False)
    
    print(f"Test data saved to: {test_data_path}")
    print(f"Data shape: {df.shape}")
    print("\nFirst few rows:")
    print(df.head())
    
    return str(test_data_path)

def test_model_training(data_path):
    """Test model training with hybrid format data."""
    print("\n" + "="*50)
    print("TESTING MODEL TRAINING")
    print("="*50)
    
    try:
        # Initialize the model with data
        model = CarrierPerformanceModel(data_path=data_path)
        
        print(f"Detected data format: {model.data_format}")
        print(f"Raw data shape: {model.raw_data.shape}")
        
        # Preprocess the data
        processed_data = model.preprocess_data()
        print(f"Processed data shape: {processed_data.shape}")
        print(f"Feature columns: {len(model.feature_columns)}")
        
        # Prepare train/test split
        model.prepare_train_test_split(test_size=0.2)
        print(f"Training set shape: {model.X_train.shape}")
        print(f"Test set shape: {model.X_test.shape}")
        
        # Build and train the model
        model.build_model()
        print("Model architecture built successfully")
        
        # Train with fewer epochs for testing
        history = model.train(epochs=10, batch_size=2, validation_split=0.2)
        print("Model training completed successfully")
        
        # Evaluate the model
        train_loss, train_mae, train_mape = model.model.evaluate(model.X_train, model.y_train, verbose=0)
        test_loss, test_mae, test_mape = model.model.evaluate(model.X_test, model.y_test, verbose=0)
        
        print(f"\nTraining Metrics:")
        print(f"  Loss: {train_loss:.4f}")
        print(f"  MAE: {train_mae:.4f}")
        print(f"  MAPE: {train_mape:.4f}")
        
        print(f"\nTest Metrics:")
        print(f"  Loss: {test_loss:.4f}")
        print(f"  MAE: {test_mae:.4f}")
        print(f"  MAPE: {test_mape:.4f}")
        
        return model
        
    except Exception as e:
        print(f"Error during model training: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_predictions(model):
    """Test individual predictions with the trained model."""
    print("\n" + "="*50)
    print("TESTING INDIVIDUAL PREDICTIONS")
    print("="*50)
    
    if model is None:
        print("No model available for testing predictions")
        return
    
    # Test cases for hybrid format
    test_cases = [
        {
            'carrier': 'ODFL',
            'source_city': 'ELWOOD',
            'source_state': 'IL',
            'source_country': 'US',
            'dest_city': 'ABINGDON',
            'dest_state': 'VA',
            'dest_country': 'US',
            'order_count': 5,
            'avg_transit_days': 1,
            'actual_transit_days': 4
        },
        {
            'carrier': 'FDX',
            'source_city': 'CHICAGO',
            'source_state': 'IL',
            'source_country': 'US',
            'dest_city': 'DALLAS',
            'dest_state': 'TX',
            'dest_country': 'US',
            'order_count': 12,
            'avg_transit_days': 3,
            'actual_transit_days': 2
        },
        {
            'carrier': 'UPS',
            'source_city': 'NEW YORK',
            'source_state': 'NY',
            'source_country': 'US',
            'dest_city': 'LOS ANGELES',
            'dest_state': 'CA',
            'dest_country': 'US'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Route: {test_case['source_city']}, {test_case['source_state']} → {test_case['dest_city']}, {test_case['dest_state']}")
        print(f"  Carrier: {test_case['carrier']}")
        
        try:
            prediction = model.predict(**test_case)
            
            if prediction:
                print(f"  Predicted On-Time Performance: {prediction['ontime_performance']:.2f}%")
                print("  ✓ Prediction successful")
            else:
                print("  ✗ Prediction failed")
                
        except Exception as e:
            print(f"  ✗ Error during prediction: {str(e)}")

def test_batch_predictions(model):
    """Test batch predictions on training data."""
    print("\n" + "="*50)
    print("TESTING BATCH PREDICTIONS ON TRAINING DATA")
    print("="*50)
    
    if model is None:
        print("No model available for testing batch predictions")
        return
    
    try:
        # Generate predictions on training data
        results = model.predict_on_training_data()
        
        if results:
            print(f"Prediction time: {results['prediction_time']}")
            print(f"Data format: {results['data_format']}")
            print(f"Records analyzed: {results['metrics']['records_analyzed']}")
            
            print(f"\nPerformance Metrics:")
            print(f"  MAE: {results['metrics']['mae']:.4f}")
            print(f"  MAPE: {results['metrics']['mape']:.4f}%")
            print(f"  RMSE: {results['metrics']['rmse']:.4f}")
            
            print(f"\nFirst 3 predictions:")
            for i, pred in enumerate(results['predictions'][:3]):
                print(f"  Prediction {i+1}:")
                print(f"    Route: {pred['source_city']}, {pred.get('source_state', 'N/A')} → {pred['dest_city']}, {pred.get('dest_state', 'N/A')}")
                print(f"    Carrier: {pred['carrier']}")
                print(f"    Actual: {pred['actual_performance']:.2f}%")
                print(f"    Predicted: {pred['predicted_performance']:.2f}%")
                print(f"    Error: {pred['absolute_error']:.2f}")
            
            print("  ✓ Batch predictions successful")
        else:
            print("  ✗ Batch predictions failed")
            
    except Exception as e:
        print(f"  ✗ Error during batch predictions: {str(e)}")
        import traceback
        traceback.print_exc()

def test_model_save_load(model):
    """Test saving and loading the model."""
    print("\n" + "="*50)
    print("TESTING MODEL SAVE/LOAD")
    print("="*50)
    
    if model is None:
        print("No model available for testing save/load")
        return
    
    try:
        # Save the model
        save_path = backend_dir / 'test_models' / 'hybrid_carrier_performance_test'
        save_path.parent.mkdir(exist_ok=True)
        
        success = model.save_model(str(save_path))
        if success:
            print(f"✓ Model saved successfully to {save_path}")
        else:
            print("✗ Failed to save model")
            return
        
        # Load the model
        new_model = CarrierPerformanceModel()
        load_success = new_model.load_model(str(save_path))
        
        if load_success:
            print("✓ Model loaded successfully")
            
            # Test a prediction with the loaded model
            test_prediction = new_model.predict(
                carrier='ODFL',
                source_city='ELWOOD',
                source_state='IL',
                source_country='US',
                dest_city='ABINGDON',
                dest_state='VA',
                dest_country='US'
            )
            
            if test_prediction:
                print(f"✓ Loaded model prediction successful: {test_prediction['ontime_performance']:.2f}%")
            else:
                print("✗ Loaded model prediction failed")
        else:
            print("✗ Failed to load model")
            
    except Exception as e:
        print(f"✗ Error during save/load test: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    print("Testing Updated Carrier Performance Model with Hybrid Format")
    print("="*60)
    
    # Create test data
    data_path = create_test_data()
    
    # Test model training
    model = test_model_training(data_path)
    
    # Test individual predictions
    test_predictions(model)
    
    # Test batch predictions
    test_batch_predictions(model)
    
    # Test save/load functionality
    test_model_save_load(model)
    
    print("\n" + "="*60)
    print("TESTING COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main() 