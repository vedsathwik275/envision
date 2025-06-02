#!/usr/bin/env python3
"""
Test script for Tender Performance Model Migration
This script validates the migration from legacy format to new format with state/country information
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import tempfile
import shutil

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.tender_performance_model import TenderPerformanceModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_legacy_test_data(num_rows: int = 100) -> pd.DataFrame:
    """Create sample legacy format test data."""
    logger.info(f"Creating legacy test data with {num_rows} rows...")
    
    carriers = ['ODFL', 'RBTW', 'AFXN', 'FDEG', 'LRGR', 'AEQC']
    source_cities = ['ELWOOD', 'RICHMOND', 'PHARR', 'REDLANDS', 'SUMNER', 'GRAND RAPIDS']
    dest_cities = ['VILLA RICA', 'BUCKEYE', 'HAUPPAUGE', 'PATTERSON', 'LOVELAND', 'STOCKTON']
    
    data = []
    np.random.seed(42)  # For reproducible results
    
    for i in range(num_rows):
        carrier = np.random.choice(carriers)
        source_city = np.random.choice(source_cities)
        dest_city = np.random.choice(dest_cities)
        
        # Generate realistic tender performance values (50-100%)
        performance = np.random.normal(85, 15)
        performance = max(50, min(100, performance))  # Clamp between 50-100
        
        data.append({
            'TENDER_PERF_PERCENTAGE': round(performance, 1),
            'CARRIER': carrier,
            'SOURCE_CITY': source_city,
            'DEST_CITY': dest_city
        })
    
    df = pd.DataFrame(data)
    logger.info("Legacy test data created successfully")
    return df

def create_new_format_test_data(num_rows: int = 100) -> pd.DataFrame:
    """Create sample new format test data with state/country information."""
    logger.info(f"Creating new format test data with {num_rows} rows...")
    
    carriers = ['ODFL', 'RBTW', 'AFXN', 'FDEG', 'LRGR', 'AEQC']
    
    # Define location data with state/country
    locations = [
        {'city': 'RICHMOND', 'state': 'VA', 'country': 'US'},
        {'city': 'CHICAGO', 'state': 'IL', 'country': 'US'},
        {'city': 'DALLAS', 'state': 'TX', 'country': 'US'},
        {'city': 'LOSANGELES', 'state': 'CA', 'country': 'US'},
        {'city': 'SEATTLE', 'state': 'WA', 'country': 'US'},
        {'city': 'MILTON', 'state': 'ON', 'country': 'CA'},
        {'city': 'LANCASTER', 'state': 'TX', 'country': 'US'},
        {'city': 'GRAND RAPIDS', 'state': 'MI', 'country': 'US'}
    ]
    
    data = []
    np.random.seed(42)  # For reproducible results
    
    for i in range(num_rows):
        carrier = np.random.choice(carriers)
        source_loc = np.random.choice(locations)
        dest_loc = np.random.choice(locations)
        
        # Generate realistic tender performance values (50-100%)
        performance = np.random.normal(85, 15)
        performance = max(50, min(100, performance))  # Clamp between 50-100
        
        data.append({
            'TENDER_PERFORMANCE': round(performance, 1),
            'CARRIER': carrier,
            'SOURCE_CITY': source_loc['city'],
            'SOURCE_STATE': source_loc['state'],
            'SOURCE_COUNTRY': source_loc['country'],
            'DEST_CITY': dest_loc['city'],
            'DEST_STATE': dest_loc['state'],
            'DEST_COUNTRY': dest_loc['country']
        })
    
    df = pd.DataFrame(data)
    logger.info("New format test data created successfully")
    return df

def test_legacy_format_processing():
    """Test legacy format data processing."""
    logger.info("=== Testing Legacy Format Processing ===")
    
    try:
        # Create legacy test data
        legacy_data = create_legacy_test_data(50)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            legacy_data.to_csv(f.name, index=False)
            legacy_file = f.name
        
        try:
            # Initialize model with legacy data
            model = TenderPerformanceModel(data_path=legacy_file)
            
            # Verify format detection
            assert model.data_format == 'legacy', f"Expected 'legacy' format, got '{model.data_format}'"
            logger.info("✓ Legacy format correctly detected")
            
            # Test preprocessing
            processed_data = model.preprocess_data()
            assert processed_data is not None, "Preprocessing failed"
            assert len(processed_data) == len(legacy_data), "Data length mismatch after preprocessing"
            logger.info("✓ Legacy data preprocessing successful")
            
            # Test train/test split
            model.prepare_train_test_split(test_size=0.3)
            assert model.X_train is not None, "X_train not created"
            assert model.y_train is not None, "y_train not created"
            assert model.feature_columns is not None, "Feature columns not stored"
            logger.info("✓ Legacy data train/test split successful")
            
            logger.info("Legacy format processing test PASSED")
            return True
            
        finally:
            os.unlink(legacy_file)
            
    except Exception as e:
        logger.error(f"Legacy format processing test FAILED: {str(e)}")
        return False

def test_new_format_processing():
    """Test new format data processing."""
    logger.info("=== Testing New Format Processing ===")
    
    try:
        # Create new format test data
        new_data = create_new_format_test_data(50)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            new_data.to_csv(f.name, index=False)
            new_file = f.name
        
        try:
            # Initialize model with new format data
            model = TenderPerformanceModel(data_path=new_file)
            
            # Verify format detection
            assert model.data_format == 'new', f"Expected 'new' format, got '{model.data_format}'"
            logger.info("✓ New format correctly detected")
            
            # Test preprocessing
            processed_data = model.preprocess_data()
            assert processed_data is not None, "Preprocessing failed"
            assert len(processed_data) == len(new_data), "Data length mismatch after preprocessing"
            logger.info("✓ New format data preprocessing successful")
            
            # Test train/test split
            model.prepare_train_test_split(test_size=0.3)
            assert model.X_train is not None, "X_train not created"
            assert model.y_train is not None, "y_train not created"
            assert model.feature_columns is not None, "Feature columns not stored"
            logger.info("✓ New format data train/test split successful")
            
            # Verify that new format has more features than legacy
            feature_count = len(model.feature_columns)
            logger.info(f"New format feature count: {feature_count}")
            assert feature_count > 25, f"Expected more features for new format, got {feature_count}"
            logger.info("✓ New format has enhanced features")
            
            logger.info("New format processing test PASSED")
            return True
            
        finally:
            os.unlink(new_file)
            
    except Exception as e:
        logger.error(f"New format processing test FAILED: {str(e)}")
        return False

def test_model_training_and_prediction():
    """Test model training and prediction for both formats."""
    logger.info("=== Testing Model Training and Prediction ===")
    
    legacy_success = False
    new_success = False
    
    # Test legacy format
    try:
        logger.info("Testing legacy format training...")
        legacy_data = create_legacy_test_data(100)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            legacy_data.to_csv(f.name, index=False)
            legacy_file = f.name
        
        try:
            model = TenderPerformanceModel(data_path=legacy_file)
            model.train(epochs=10, batch_size=16)  # Quick training for testing
            
            # Test prediction
            prediction = model.predict(
                carrier='ODFL',
                source_city='ELWOOD',
                dest_city='VILLA RICA'
            )
            
            assert prediction is not None, "Legacy prediction failed"
            assert 'predicted_performance' in prediction, "Prediction missing performance value"
            assert 0 <= prediction['predicted_performance'] <= 100, "Invalid prediction value"
            
            logger.info("✓ Legacy format training and prediction successful")
            legacy_success = True
            
        finally:
            os.unlink(legacy_file)
            
    except Exception as e:
        logger.error(f"Legacy format training test FAILED: {str(e)}")
    
    # Test new format
    try:
        logger.info("Testing new format training...")
        new_data = create_new_format_test_data(100)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            new_data.to_csv(f.name, index=False)
            new_file = f.name
        
        try:
            model = TenderPerformanceModel(data_path=new_file)
            model.train(epochs=10, batch_size=16)  # Quick training for testing
            
            # Test prediction with new format
            prediction = model.predict(
                carrier='AFXN',
                source_city='RICHMOND',
                source_state='VA',
                source_country='US',
                dest_city='CHICAGO',
                dest_state='IL',
                dest_country='US'
            )
            
            assert prediction is not None, "New format prediction failed"
            assert 'predicted_performance' in prediction, "Prediction missing performance value"
            assert 0 <= prediction['predicted_performance'] <= 100, "Invalid prediction value"
            assert 'source_state' in prediction, "New format prediction missing state info"
            
            logger.info("✓ New format training and prediction successful")
            new_success = True
            
        finally:
            os.unlink(new_file)
            
    except Exception as e:
        logger.error(f"New format training test FAILED: {str(e)}")
    
    if legacy_success and new_success:
        logger.info("Model training and prediction test PASSED")
        return True
    else:
        logger.error("Model training and prediction test FAILED")
        return False

def test_model_persistence():
    """Test model saving and loading for both formats."""
    logger.info("=== Testing Model Persistence ===")
    
    temp_dirs = []
    legacy_success = False
    new_success = False
    
    try:
        # Test legacy format persistence
        logger.info("Testing legacy format model persistence...")
        legacy_data = create_legacy_test_data(50)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            legacy_data.to_csv(f.name, index=False)
            legacy_file = f.name
        
        legacy_model_dir = tempfile.mkdtemp(prefix='legacy_model_')
        temp_dirs.append(legacy_model_dir)
        
        try:
            # Train and save legacy model
            model = TenderPerformanceModel(data_path=legacy_file)
            model.train(epochs=5, batch_size=16)
            
            save_success = model.save_model(legacy_model_dir)
            assert save_success, "Legacy model save failed"
            
            # Load and test legacy model
            loaded_model = TenderPerformanceModel(model_path=legacy_model_dir)
            assert loaded_model.data_format == 'legacy', "Wrong data format after loading"
            
            # Test prediction with loaded model
            prediction = loaded_model.predict(
                carrier='ODFL',
                source_city='ELWOOD',
                dest_city='VILLA RICA'
            )
            
            assert prediction is not None, "Loaded legacy model prediction failed"
            logger.info("✓ Legacy model persistence successful")
            legacy_success = True
            
        finally:
            os.unlink(legacy_file)
        
        # Test new format persistence
        logger.info("Testing new format model persistence...")
        new_data = create_new_format_test_data(50)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            new_data.to_csv(f.name, index=False)
            new_file = f.name
        
        new_model_dir = tempfile.mkdtemp(prefix='new_model_')
        temp_dirs.append(new_model_dir)
        
        try:
            # Train and save new format model
            model = TenderPerformanceModel(data_path=new_file)
            model.train(epochs=5, batch_size=16)
            
            save_success = model.save_model(new_model_dir)
            assert save_success, "New format model save failed"
            
            # Load and test new format model
            loaded_model = TenderPerformanceModel(model_path=new_model_dir)
            assert loaded_model.data_format == 'new', "Wrong data format after loading"
            
            # Test prediction with loaded model
            prediction = loaded_model.predict(
                carrier='AFXN',
                source_city='RICHMOND',
                source_state='VA',
                source_country='US',
                dest_city='CHICAGO',
                dest_state='IL',
                dest_country='US'
            )
            
            assert prediction is not None, "Loaded new format model prediction failed"
            assert 'source_state' in prediction, "New format prediction missing state info"
            logger.info("✓ New format model persistence successful")
            new_success = True
            
        finally:
            os.unlink(new_file)
    
    finally:
        # Clean up temporary directories
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    if legacy_success and new_success:
        logger.info("Model persistence test PASSED")
        return True
    else:
        logger.error("Model persistence test FAILED")
        return False

def test_prediction_on_training_data():
    """Test prediction generation on training data for both formats."""
    logger.info("=== Testing Prediction on Training Data ===")
    
    temp_dirs = []
    legacy_success = False
    new_success = False
    
    try:
        # Test legacy format
        logger.info("Testing legacy format prediction on training data...")
        legacy_data = create_legacy_test_data(30)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            legacy_data.to_csv(f.name, index=False)
            legacy_file = f.name
        
        try:
            model = TenderPerformanceModel(data_path=legacy_file)
            model.train(epochs=5, batch_size=16)
            
            result = model.predict_on_training_data()
            assert result is not None, "Legacy training data prediction failed"
            assert 'predictions' in result, "No predictions in result"
            assert 'metrics' in result, "No metrics in result"
            assert len(result['predictions']) > 0, "No predictions generated"
            
            # Check that legacy format also includes geographic columns (even if None)
            first_prediction = result['predictions'][0]
            assert 'source_state' in first_prediction, "Legacy format prediction missing source_state column"
            assert 'source_country' in first_prediction, "Legacy format prediction missing source_country column"
            assert 'dest_state' in first_prediction, "Legacy format prediction missing dest_state column"
            assert 'dest_country' in first_prediction, "Legacy format prediction missing dest_country column"
            
            # For legacy format, these values should be None
            assert first_prediction['source_state'] is None, "Legacy format source_state should be None"
            assert first_prediction['source_country'] is None, "Legacy format source_country should be None"
            assert first_prediction['dest_state'] is None, "Legacy format dest_state should be None"
            assert first_prediction['dest_country'] is None, "Legacy format dest_country should be None"
            
            logger.info("✓ Legacy format training data prediction successful")
            logger.info("✓ Legacy format includes consistent geographic column structure")
            legacy_success = True
            
        finally:
            os.unlink(legacy_file)
        
        # Test new format
        logger.info("Testing new format prediction on training data...")
        new_data = create_new_format_test_data(30)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            new_data.to_csv(f.name, index=False)
            new_file = f.name
        
        try:
            model = TenderPerformanceModel(data_path=new_file)
            model.train(epochs=5, batch_size=16)
            
            result = model.predict_on_training_data()
            assert result is not None, "New format training data prediction failed"
            assert 'predictions' in result, "No predictions in result"
            assert 'metrics' in result, "No metrics in result"
            assert len(result['predictions']) > 0, "No predictions generated"
            
            # Check that new format includes complete state/country info
            first_prediction = result['predictions'][0]
            assert 'source_state' in first_prediction, "New format prediction missing source_state column"
            assert 'source_country' in first_prediction, "New format prediction missing source_country column"
            assert 'dest_state' in first_prediction, "New format prediction missing dest_state column"
            assert 'dest_country' in first_prediction, "New format prediction missing dest_country column"
            
            # For new format, these values should have actual data
            assert first_prediction['source_state'] is not None, "New format source_state should have data"
            assert first_prediction['source_country'] is not None, "New format source_country should have data"
            assert first_prediction['dest_state'] is not None, "New format dest_state should have data"
            assert first_prediction['dest_country'] is not None, "New format dest_country should have data"
            
            logger.info("✓ New format training data prediction successful")
            logger.info("✓ New format includes complete geographic information")
            new_success = True
            
        finally:
            os.unlink(new_file)
    
    finally:
        # Clean up any temporary directories
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    if legacy_success and new_success:
        logger.info("Prediction on training data test PASSED")
        return True
    else:
        logger.error("Prediction on training data test FAILED")
        return False

def run_all_tests():
    """Run all migration tests."""
    logger.info("Starting Tender Performance Model Migration Tests")
    logger.info("=" * 60)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Legacy Format Processing", test_legacy_format_processing),
        ("New Format Processing", test_new_format_processing),
        ("Model Training and Prediction", test_model_training_and_prediction),
        ("Model Persistence", test_model_persistence),
        ("Prediction on Training Data", test_prediction_on_training_data)
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name}...")
        try:
            success = test_func()
            test_results.append((test_name, success))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {str(e)}")
            test_results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, success in test_results:
        status = "PASSED" if success else "FAILED"
        logger.info(f"{test_name}: {status}")
        if success:
            passed_tests += 1
    
    logger.info(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests PASSED! Tender Performance migration is successful.")
        return True
    else:
        logger.error(f"❌ {total_tests - passed_tests} test(s) FAILED. Migration needs attention.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 