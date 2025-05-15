#!/usr/bin/env python3
"""
Test script for tender performance training data prediction API endpoints.
"""

import requests
import json
import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = "http://localhost:8000/api"

def test_generate_training_predictions(model_id):
    """Test generating predictions on training data for a tender performance model."""
    endpoint = f"{API_BASE_URL}/predictions/tender-performance/{model_id}/full-predictions"
    
    logger.info(f"Testing GET {endpoint}")
    
    response = requests.get(endpoint)
    
    if response.status_code == 200:
        data = response.json()
        prediction_count = data.get('prediction_count', 0)
        
        logger.info(f"Successfully generated {prediction_count} predictions on training data")
        
        # Show metrics if available
        if 'metrics' in data:
            metrics = data.get('metrics', {})
            logger.info(f"Training data metrics:")
            logger.info(f"  - MAE: {metrics.get('mae', 'N/A')}")
            logger.info(f"  - MAPE: {metrics.get('mape', 'N/A')}%")
            logger.info(f"  - Count: {metrics.get('count', 'N/A')} predictions")
        
        # Show sample predictions
        predictions = data.get('predictions', [])
        if predictions:
            logger.info("Sample predictions (first 3):")
            for i, pred in enumerate(predictions[:3]):
                logger.info(f"  Prediction {i+1}:")
                logger.info(f"    - Carrier: {pred.get('carrier', 'N/A')}")
                logger.info(f"    - Lane: {pred.get('source_city', 'N/A')} to {pred.get('dest_city', 'N/A')}")
                logger.info(f"    - Predicted: {pred.get('predicted_performance', 'N/A')}%")
                logger.info(f"    - Actual: {pred.get('actual_performance', 'N/A')}%")
                logger.info(f"    - Error: {pred.get('absolute_error', 'N/A')}%")
        
        return True
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return False

def test_download_predictions(model_id, format="csv"):
    """Test downloading training data predictions in the specified format."""
    endpoint = f"{API_BASE_URL}/predictions/tender-performance/{model_id}/full-predictions/download"
    params = {"format": format}
    
    logger.info(f"Testing GET {endpoint} with format={format}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        is_fallback = response.headers.get('X-File-Format-Fallback') == 'true'
        
        if 'text/csv' in content_type:
            extension = "csv"
            format_type = "CSV"
        elif 'application/json' in content_type:
            extension = "json"
            format_type = "JSON"
        else:
            logger.error(f"Unexpected content type: {content_type}")
            return False
        
        # Save the file
        filename = f"tender_performance_training_predictions_{model_id}.{extension}"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        if is_fallback:
            logger.warning(f"Requested {format.upper()} format, but received {format_type} due to fallback mechanism")
        
        logger.info(f"Successfully downloaded {format_type} data to {filename}")
        
        # Check file size
        file_size = os.path.getsize(filename) / 1024  # KB
        logger.info(f"File size: {file_size:.2f} KB")
        
        return True
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return False

def main():
    """Run tests for tender performance training data prediction API endpoints."""
    if len(sys.argv) < 2:
        print("Usage: python test_tender_performance_training_predictions.py <model_id> [format]")
        return
    
    model_id = sys.argv[1]
    format = sys.argv[2] if len(sys.argv) > 2 else "csv"
    
    logger.info(f"Testing tender performance training data prediction API with model_id: {model_id}")
    
    # Test generating training predictions
    if test_generate_training_predictions(model_id):
        # Test downloading predictions
        test_download_predictions(model_id, format)
    
    logger.info("Tests completed")

if __name__ == "__main__":
    main() 