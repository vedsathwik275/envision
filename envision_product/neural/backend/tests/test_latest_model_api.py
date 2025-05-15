#!/usr/bin/env python3
"""
Test script for latest model API endpoint.
"""

import requests
import sys
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = "http://localhost:8000/api"

def test_get_latest_model(model_type):
    """Test the latest model retrieval API endpoint."""
    endpoint = f"{API_BASE_URL}/models/latest"
    params = {"model_type": model_type}
    
    logger.info(f"Testing GET {endpoint} with params {params}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        model = response.json()
        logger.info(f"Successfully retrieved latest {model_type} model:")
        logger.info(f"  - Model ID: {model.get('model_id')}")
        logger.info(f"  - Created at: {model.get('created_at')}")
        logger.info(f"  - Description: {model.get('description')}")
        
        # Display evaluation metrics if available
        if "evaluation" in model and model["evaluation"]:
            eval_metrics = model["evaluation"]
            logger.info("Performance metrics:")
            if "mae" in eval_metrics:
                logger.info(f"  - MAE: {eval_metrics['mae']}")
            if "rmse" in eval_metrics:
                logger.info(f"  - RMSE: {eval_metrics['rmse']}")
            if "r2" in eval_metrics:
                logger.info(f"  - R² Score: {eval_metrics['r2']}")
        
        return model
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def test_get_latest_model_with_date_filter(model_type):
    """Test the latest model retrieval API with date filtering."""
    # Get date 30 days ago
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    endpoint = f"{API_BASE_URL}/models/latest"
    params = {
        "model_type": model_type,
        "min_created_at": thirty_days_ago
    }
    
    logger.info(f"Testing GET {endpoint} with params {params}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        model = response.json()
        logger.info(f"Successfully retrieved latest {model_type} model created after {thirty_days_ago}:")
        logger.info(f"  - Model ID: {model.get('model_id')}")
        logger.info(f"  - Created at: {model.get('created_at')}")
        return model
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def test_get_latest_model_with_metrics_filter(model_type, min_accuracy=0.8, max_error=None):
    """Test the latest model retrieval API with performance metric filtering."""
    endpoint = f"{API_BASE_URL}/models/latest"
    params = {
        "model_type": model_type,
        "min_accuracy": min_accuracy
    }
    
    if max_error is not None:
        params["max_error"] = max_error
    
    logger.info(f"Testing GET {endpoint} with params {params}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        model = response.json()
        logger.info(f"Successfully retrieved latest {model_type} model with min_accuracy={min_accuracy}:")
        logger.info(f"  - Model ID: {model.get('model_id')}")
        logger.info(f"  - Created at: {model.get('created_at')}")
        
        # Display evaluation metrics
        if "evaluation" in model and model["evaluation"]:
            eval_metrics = model["evaluation"]
            logger.info("Performance metrics:")
            if "mae" in eval_metrics:
                logger.info(f"  - MAE: {eval_metrics['mae']}")
            if "rmse" in eval_metrics:
                logger.info(f"  - RMSE: {eval_metrics['rmse']}")
            if "r2" in eval_metrics:
                logger.info(f"  - R² Score: {eval_metrics['r2']}")
        
        return model
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    """Run tests for the latest model API endpoint."""
    if len(sys.argv) < 2:
        print("Usage: python test_latest_model_api.py <model_type> [min_accuracy] [max_error]")
        print("Example: python test_latest_model_api.py order_volume 0.8 5.0")
        return
    
    model_type = sys.argv[1]
    min_accuracy = float(sys.argv[2]) if len(sys.argv) > 2 else None
    max_error = float(sys.argv[3]) if len(sys.argv) > 3 else None
    
    logger.info(f"Testing latest model API with model_type: {model_type}")
    
    # Test basic latest model retrieval
    latest_model = test_get_latest_model(model_type)
    
    if latest_model:
        # Test with date filter
        test_get_latest_model_with_date_filter(model_type)
        
        # Test with metrics filter if provided
        if min_accuracy is not None:
            test_get_latest_model_with_metrics_filter(model_type, min_accuracy, max_error)
    
    logger.info("Tests completed")

if __name__ == "__main__":
    main() 