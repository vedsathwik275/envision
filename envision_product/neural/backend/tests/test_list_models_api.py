#!/usr/bin/env python3
"""
Test script for the List All Models API endpoints.
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

def test_list_models():
    """Test the basic list models endpoint."""
    endpoint = f"{API_BASE_URL}/models"
    logger.info(f"Testing GET {endpoint}")
    
    response = requests.get(endpoint)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        pagination = data.get("pagination", {})
        
        logger.info(f"Successfully retrieved models:")
        logger.info(f"  - Total models: {pagination.get('total', len(models))}")
        logger.info(f"  - Page: {pagination.get('page', 1)}/{pagination.get('pages', 1)}")
        logger.info(f"  - Page size: {pagination.get('page_size', len(models))}")
        
        # Log some model details
        for i, model in enumerate(models[:5]):  # Show first 5 models
            logger.info(f"Model {i+1}:")
            logger.info(f"  - ID: {model.get('model_id')}")
            logger.info(f"  - Type: {model.get('model_type')}")
            logger.info(f"  - Created: {model.get('created_at')}")
        
        if len(models) > 5:
            logger.info(f"... and {len(models) - 5} more models")
        
        return data
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def test_list_models_alternative_endpoint():
    """Test the alternative list models endpoint."""
    endpoint = f"{API_BASE_URL}/models/list"
    logger.info(f"Testing GET {endpoint}")
    
    response = requests.get(endpoint)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        pagination = data.get("pagination", {})
        
        logger.info(f"Successfully retrieved models from alternative endpoint:")
        logger.info(f"  - Total models: {pagination.get('total', len(models))}")
        logger.info(f"  - Page: {pagination.get('page', 1)}/{pagination.get('pages', 1)}")
        
        return data
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def test_list_models_with_type_filter(model_type):
    """Test listing models with type filter."""
    endpoint = f"{API_BASE_URL}/models"
    params = {"model_type": model_type}
    
    logger.info(f"Testing GET {endpoint} with params {params}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        pagination = data.get("pagination", {})
        
        logger.info(f"Successfully retrieved {model_type} models:")
        logger.info(f"  - Total models: {pagination.get('total', len(models))}")
        logger.info(f"  - Page: {pagination.get('page', 1)}/{pagination.get('pages', 1)}")
        
        return data
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def test_pagination(page=2, page_size=3):
    """Test pagination of model list."""
    endpoint = f"{API_BASE_URL}/models"
    params = {"page": page, "page_size": page_size}
    
    logger.info(f"Testing GET {endpoint} with params {params}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        pagination = data.get("pagination", {})
        
        logger.info(f"Successfully retrieved paginated models:")
        logger.info(f"  - Total models: {pagination.get('total')}")
        logger.info(f"  - Page: {pagination.get('page')}/{pagination.get('pages')}")
        logger.info(f"  - Models on this page: {len(models)}")
        
        return data
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def test_performance_metrics_filter(min_accuracy=0.8, max_error=None):
    """Test filtering by performance metrics."""
    endpoint = f"{API_BASE_URL}/models"
    params = {}
    
    if min_accuracy is not None:
        params["min_accuracy"] = min_accuracy
    
    if max_error is not None:
        params["max_error"] = max_error
    
    logger.info(f"Testing GET {endpoint} with params {params}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        pagination = data.get("pagination", {})
        
        logger.info(f"Successfully retrieved models with performance filters:")
        logger.info(f"  - Total models: {pagination.get('total', len(models))}")
        
        # Log performance metrics for retrieved models
        for i, model in enumerate(models[:3]):  # Show first 3 models
            logger.info(f"Model {i+1}:")
            logger.info(f"  - ID: {model.get('model_id')}")
            logger.info(f"  - Type: {model.get('model_type')}")
            
            evaluation = model.get("evaluation", {})
            if evaluation:
                logger.info(f"  - R² Score: {evaluation.get('r2')}")
                logger.info(f"  - MAE: {evaluation.get('mae')}")
                logger.info(f"  - RMSE: {evaluation.get('rmse')}")
        
        return data
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def test_date_filter():
    """Test filtering by creation date."""
    # Get date 30 days ago
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    endpoint = f"{API_BASE_URL}/models"
    params = {"min_created_at": thirty_days_ago}
    
    logger.info(f"Testing GET {endpoint} with params {params}")
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        pagination = data.get("pagination", {})
        
        logger.info(f"Successfully retrieved models created after {thirty_days_ago}:")
        logger.info(f"  - Total models: {pagination.get('total', len(models))}")
        
        return data
    else:
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    """Run tests for the list models API endpoints."""
    logger.info("Starting List Models API Tests")
    
    # Test the basic endpoint
    test_list_models()
    
    # Test alternative endpoint
    test_list_models_alternative_endpoint()
    
    # Test with model type filter if specified
    if len(sys.argv) > 1:
        model_type = sys.argv[1]
        test_list_models_with_type_filter(model_type)
    
    # Test pagination
    test_pagination()
    
    # Test performance metrics filter
    test_performance_metrics_filter()
    
    # Test date filter
    test_date_filter()
    
    logger.info("All List Models API tests completed")

if __name__ == "__main__":
    main() 