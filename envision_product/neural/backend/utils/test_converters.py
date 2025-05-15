#!/usr/bin/env python3
"""
Test script for file conversion utilities.
"""

import os
import json
import tempfile
from pathlib import Path
from file_converters import json_to_csv, convert_order_volume_predictions, convert_tender_performance_predictions

def test_json_to_csv():
    """Test the basic JSON to CSV conversion."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a sample prediction JSON file
        sample_data = {
            "model_id": "test_model",
            "prediction_time": "2025-05-14T09:00:00",
            "predictions": [
                {
                    "source_city": "CHICAGO",
                    "destination_city": "NEW YORK",
                    "order_type": "LTL",
                    "month": "2025-06",
                    "predicted_volume": 125.5,
                    "confidence": 0.95
                },
                {
                    "source_city": "DALLAS",
                    "destination_city": "ATLANTA",
                    "order_type": "FTL",
                    "month": "2025-06",
                    "predicted_volume": 87.3,
                    "confidence": 0.92
                }
            ]
        }
        
        json_file = temp_path / "prediction_data.json"
        with open(json_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        
        # Test the conversion
        csv_file = json_to_csv(json_file)
        
        # Verify the CSV file was created
        if not csv_file.exists():
            print("❌ CSV file was not created")
            return False
        
        # Read the CSV file and verify contents
        with open(csv_file, "r") as f:
            csv_content = f.read()
            
        # Check if the headers and data are in the CSV file
        if "source_city" not in csv_content or "CHICAGO" not in csv_content:
            print("❌ CSV content is incorrect")
            return False
        
        print("✅ JSON to CSV conversion test passed")
        return True

def test_order_volume_conversions():
    """Test order volume prediction conversion."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a sample prediction JSON file
        sample_data = {
            "model_id": "order_volume_test",
            "prediction_time": "2025-05-14T09:00:00",
            "predictions": [
                {
                    "source_city": "CHICAGO",
                    "destination_city": "NEW YORK",
                    "order_type": "LTL",
                    "month": "2025-06",
                    "predicted_volume": 125.5,
                    "confidence": 0.95
                },
                {
                    "source_city": "DALLAS",
                    "destination_city": "ATLANTA",
                    "order_type": "FTL",
                    "month": "2025-06",
                    "predicted_volume": 87.3,
                    "confidence": 0.92
                }
            ]
        }
        
        # Create the prediction directory
        pred_dir = temp_path
        json_file = pred_dir / "prediction_data.json"
        with open(json_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        
        # Test the conversion
        csv_file = convert_order_volume_predictions(pred_dir)
        
        # Verify the CSV file was created
        if not csv_file.exists():
            print("❌ Order volume CSV file was not created")
            return False
        
        # Read the CSV file and verify contents
        with open(csv_file, "r") as f:
            csv_content = f.read()
            
        # Check if the columns are correct
        expected_columns = ["source_city", "destination_city", "order_type", "month", "predicted_volume", "confidence"]
        for col in expected_columns:
            if col not in csv_content:
                print(f"❌ Missing column in order volume CSV: {col}")
                return False
        
        print("✅ Order volume conversion test passed")
        return True

def test_tender_performance_conversions():
    """Test tender performance prediction conversion."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a sample prediction JSON file
        sample_data = {
            "model_id": "tender_performance_test",
            "prediction_time": "2025-05-14T09:00:00",
            "predictions": [
                {
                    "carrier": "CARRIER1",
                    "source_city": "CHICAGO",
                    "dest_city": "NEW YORK",
                    "predicted_performance": 92.5
                },
                {
                    "carrier": "CARRIER2",
                    "source_city": "DALLAS",
                    "dest_city": "ATLANTA",
                    "predicted_performance": 87.3
                }
            ]
        }
        
        # Create the prediction directory
        pred_dir = temp_path
        json_file = pred_dir / "prediction_data.json"
        with open(json_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        
        # Test the conversion
        csv_file = convert_tender_performance_predictions(pred_dir)
        
        # Verify the CSV file was created
        if not csv_file.exists():
            print("❌ Tender performance CSV file was not created")
            return False
        
        # Read the CSV file and verify contents
        with open(csv_file, "r") as f:
            csv_content = f.read()
            
        # Check if the columns are correct
        expected_columns = ["carrier", "source_city", "dest_city", "predicted_performance"]
        for col in expected_columns:
            if col not in csv_content:
                print(f"❌ Missing column in tender performance CSV: {col}")
                return False
        
        print("✅ Tender performance conversion test passed")
        return True

if __name__ == "__main__":
    print("Running converter tests...")
    test_json_to_csv()
    test_order_volume_conversions()
    test_tender_performance_conversions()
    print("All tests completed.") 