#!/usr/bin/env python3
"""
Test script for order volume prediction API endpoints.
"""

import requests
import json
from pathlib import Path
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = "http://localhost:8000/api"

def test_get_order_volume_predictions(model_id):
    """Test getting order volume predictions."""
    endpoint = f"{API_BASE_URL}/predictions/order-volume/{model_id}"
    
    logger.info(f"Testing GET {endpoint}")
    
    response = requests.get(endpoint)
    
    if response.status_code == 200:
        data = response.json()
        logger.info(f"Successfully retrieved {len(data.get('predictions', []))} predictions")
        logger.info(f"Total predictions: {data.get('total_predictions', 0)}")
        logger.info(f"Filtered predictions: {data.get('filtered_predictions', 0)}")
        
        # Check if CSV export is available
        if data.get('has_csv_export'):
            logger.info(f"CSV export available at: {data.get('csv_path')}")
        else:
            logger.warning("CSV export not available")
            
        return True
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return False

def test_get_order_volume_by_lane(model_id, source_city, destination_city):
    """Test getting order volume predictions for a specific lane."""
    endpoint = f"{API_BASE_URL}/predictions/order-volume/{model_id}/by-lane"
    params = {
        "source_city": source_city,
        "destination_city": destination_city
    }
    
    logger.info(f"Testing GET {endpoint} with params {params}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        logger.info(f"Successfully retrieved {data.get('prediction_count', 0)} predictions for lane")
        logger.info(f"Lane: {data.get('lane', {})}")
        
        return True
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return False

def test_download_csv(model_id):
    """Test downloading CSV file."""
    endpoint = f"{API_BASE_URL}/predictions/order-volume/{model_id}/download"
    
    logger.info(f"Testing GET {endpoint}")
    
    response = requests.get(endpoint)
    
    if response.status_code == 200:
        # Check if the content type is CSV or JSON
        content_type = response.headers.get('Content-Type', '')
        
        if 'text/csv' in content_type:
            # Save the file
            filename = f"order_volume_predictions_{model_id}.csv"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded CSV to {filename}")
            return True
        elif 'application/json' in content_type:
            # Save the JSON file
            filename = f"order_volume_predictions_{model_id}.json"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            # Check if this was a fallback
            if response.headers.get('X-File-Format-Fallback') == 'true':
                logger.warning(f"CSV was not available, received JSON instead. Saved to {filename}")
                logger.info("You can convert this JSON to CSV manually if needed.")
            else:
                logger.info(f"Successfully downloaded JSON to {filename}")
            return True
        else:
            logger.error(f"Unexpected content type: {content_type}")
            return False
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return False

def main():
    """Run tests for order volume prediction API endpoints."""
    if len(sys.argv) < 2:
        print("Usage: python test_order_volume_api.py <model_id> [source_city] [destination_city]")
        return
    
    model_id = sys.argv[1]
    source_city = sys.argv[2] if len(sys.argv) > 2 else None
    destination_city = sys.argv[3] if len(sys.argv) > 3 else None
    
    logger.info(f"Testing order volume prediction API with model_id: {model_id}")
    
    # Test getting predictions
    test_get_order_volume_predictions(model_id)
    
    # Test getting predictions by lane if source and destination are provided
    if source_city and destination_city:
        test_get_order_volume_by_lane(model_id, source_city, destination_city)
    
    # Test downloading CSV
    test_download_csv(model_id)
    
    logger.info("Tests completed")

if __name__ == "__main__":
    main() 