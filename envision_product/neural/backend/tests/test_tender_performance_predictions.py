#!/usr/bin/env python3
"""
Test script for tender performance prediction API endpoints.
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

def test_get_predictions(model_id):
    """Test getting tender performance predictions."""
    endpoint = f"{API_BASE_URL}/predictions/tender-performance/{model_id}"
    
    logger.info(f"Testing GET {endpoint}")
    
    response = requests.get(endpoint)
    
    if response.status_code == 200:
        data = response.json()
        prediction_count = data.get('prediction_count', 0)
        
        logger.info(f"Successfully retrieved {prediction_count} predictions")
        
        # Show metrics if available
        if 'metrics' in data:
            metrics = data.get('metrics', {})
            logger.info(f"Prediction metrics:")
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

def test_create_predictions(model_id):
    """Test creating tender performance predictions."""
    endpoint = f"{API_BASE_URL}/predictions/tender-performance"
    payload = {"model_id": model_id}
    
    logger.info(f"Testing POST {endpoint} with payload {payload}")
    
    response = requests.post(endpoint, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        prediction_id = data.get('prediction_id')
        prediction_count = data.get('prediction_count', 0)
        
        logger.info(f"Successfully created predictions with ID: {prediction_id}")
        logger.info(f"Generated {prediction_count} predictions")
        
        # Show metrics if available
        if 'metrics' in data:
            metrics = data.get('metrics', {})
            logger.info(f"Prediction metrics:")
            logger.info(f"  - MAE: {metrics.get('mae', 'N/A')}")
            logger.info(f"  - MAPE: {metrics.get('mape', 'N/A')}%")
            logger.info(f"  - Count: {metrics.get('count', 'N/A')} predictions")
        
        # Show sample predictions if available in the response
        if 'data' in data and 'predictions' in data['data']:
            predictions = data['data']['predictions'][:3]  # Take first 3 as samples
            logger.info("Sample predictions (first 3):")
            for i, pred in enumerate(predictions):
                logger.info(f"  Prediction {i+1}:")
                logger.info(f"    - Carrier: {pred.get('carrier', 'N/A')}")
                logger.info(f"    - Lane: {pred.get('source_city', 'N/A')} to {pred.get('dest_city', 'N/A')}")
                logger.info(f"    - Predicted: {pred.get('predicted_performance', 'N/A')}%")
                logger.info(f"    - Actual: {pred.get('actual_performance', 'N/A')}%")
                logger.info(f"    - Error: {pred.get('absolute_error', 'N/A')}%")
        
        return prediction_id
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def test_get_predictions_by_lane(model_id, source_city, dest_city, carrier=None):
    """Test getting tender performance predictions for a specific lane."""
    endpoint = f"{API_BASE_URL}/predictions/tender-performance/{model_id}/by-lane"
    params = {
        "source_city": source_city,
        "dest_city": dest_city
    }
    if carrier:
        params["carrier"] = carrier
    
    logger.info(f"Testing GET {endpoint} with params {params}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        prediction_count = data.get('prediction_count', 0)
        
        logger.info(f"Successfully retrieved {prediction_count} predictions for lane")
        
        # Show lane info
        lane = data.get('lane', {})
        logger.info(f"Lane info:")
        logger.info(f"  - Source city: {lane.get('source_city')}")
        logger.info(f"  - Destination city: {lane.get('dest_city')}")
        if lane.get('carrier'):
            logger.info(f"  - Carrier: {lane.get('carrier')}")
        
        # Show lane-specific metrics
        if 'metrics' in data:
            metrics = data.get('metrics', {})
            logger.info(f"Lane metrics:")
            logger.info(f"  - MAE: {metrics.get('mae', 'N/A')}")
            logger.info(f"  - MAPE: {metrics.get('mape', 'N/A')}%")
        
        return True
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return False

def test_download_predictions(model_id, format="csv", source_city=None, dest_city=None, carrier=None):
    """Test downloading tender performance predictions in the specified format."""
    endpoint = f"{API_BASE_URL}/predictions/tender-performance/{model_id}/download"
    params = {"format": format}
    
    # Add filter parameters if provided
    if source_city:
        params["source_city"] = source_city
    if dest_city:
        params["dest_city"] = dest_city
    if carrier:
        params["carrier"] = carrier
    
    filter_desc = ""
    if source_city or dest_city or carrier:
        filter_desc = " with filters"
        if source_city:
            filter_desc += f" source_city={source_city}"
        if dest_city:
            filter_desc += f" dest_city={dest_city}"
        if carrier:
            filter_desc += f" carrier={carrier}"
    
    logger.info(f"Testing GET {endpoint} with format={format}{filter_desc}")
    
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
        filename_base = f"tender_performance_predictions_{model_id}"
        if source_city or dest_city or carrier:
            filename_base += "_filtered"
        filename = f"{filename_base}.{extension}"
        
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
    """Run tests for tender performance prediction API endpoints."""
    if len(sys.argv) < 2:
        print("Usage: python test_tender_performance_predictions.py <model_id> [source_city] [dest_city] [carrier] [format]")
        return
    
    model_id = sys.argv[1]
    source_city = sys.argv[2] if len(sys.argv) > 2 else None
    dest_city = sys.argv[3] if len(sys.argv) > 3 else None
    carrier = sys.argv[4] if len(sys.argv) > 4 else None
    format = sys.argv[5] if len(sys.argv) > 5 else "csv"
    
    logger.info(f"Testing tender performance prediction API with model_id: {model_id}")
    
    # Test creating new predictions
    new_prediction_id = test_create_predictions(model_id)
    
    # Test getting predictions
    if test_get_predictions(model_id):
        # Test by-lane if source and destination are provided
        if source_city and dest_city:
            test_get_predictions_by_lane(model_id, source_city, dest_city, carrier)
        
        # Test downloading predictions
        test_download_predictions(model_id, format, source_city, dest_city, carrier)
    
    logger.info("Tests completed")

if __name__ == "__main__":
    main() 