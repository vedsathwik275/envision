#!/usr/bin/env python3
"""
File format conversion utilities for Envision Neural API.
These utilities convert between different file formats for prediction results.
"""

import os
import json
import csv
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

def json_to_csv(json_file_path: Union[str, Path], csv_file_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """Convert a prediction JSON file to CSV format.
    
    Args:
        json_file_path: Path to the JSON file to convert
        csv_file_path: Optional path for the output CSV file. If not provided, 
                       it will be generated from the JSON path.
    
    Returns:
        Path to the generated CSV file or None if conversion fails
    """
    try:
        # Ensure paths are Path objects
        json_path = Path(json_file_path)
        
        # If CSV path not provided, derive it from JSON path
        if csv_file_path is None:
            csv_file_path = json_path.with_suffix('.csv')
        else:
            csv_file_path = Path(csv_file_path)
        
        # Read the JSON file
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Check if this is a prediction file
        if 'predictions' not in data:
            logger.error(f"JSON file does not contain a 'predictions' key: {json_path}")
            return None
        
        # Extract predictions
        predictions = data.get('predictions', [])
        
        if not predictions:
            logger.warning(f"No predictions found in {json_path}")
            # Create an empty CSV with headers
            with open(csv_file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['No predictions available'])
            return csv_file_path
        
        # Convert list of predictions to DataFrame for easy CSV export
        df = pd.DataFrame(predictions)
        
        # Write to CSV
        df.to_csv(csv_file_path, index=False)
        logger.info(f"Successfully converted {json_path} to {csv_file_path}")
        
        return csv_file_path
        
    except Exception as e:
        logger.error(f"Error converting JSON to CSV: {str(e)}")
        return None

def convert_order_volume_predictions(prediction_dir: Union[str, Path]) -> Optional[Path]:
    """Convert order volume prediction JSON to CSV.
    
    Args:
        prediction_dir: Directory containing the prediction files
    
    Returns:
        Path to the generated CSV file or None if conversion fails
    """
    try:
        prediction_dir = Path(prediction_dir)
        json_file = prediction_dir / "prediction_data.json"
        csv_file = prediction_dir / "prediction_data.csv"
        
        if not json_file.exists():
            logger.error(f"Prediction JSON file not found: {json_file}")
            return None
        
        # Read the JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract predictions
        predictions = data.get('predictions', [])
        
        if not predictions:
            logger.warning(f"No predictions found in {json_file}. Creating empty CSV with headers.")
            # Create a minimal CSV with expected headers even if there are no predictions
            empty_df = pd.DataFrame(columns=[
                'source_city', 'destination_city', 'order_type', 'month', 
                'predicted_volume', 'confidence'
            ])
            empty_df.to_csv(csv_file, index=False)
            logger.info(f"Created empty CSV with headers: {csv_file}")
            return csv_file
        
        # Extract a sample prediction to get all available fields
        sample = predictions[0]
        all_fields = list(sample.keys())
        
        # Ensure standard fields are present, add empty ones if missing
        standard_fields = [
            'source_city', 'destination_city', 'order_type', 'month', 
            'predicted_volume', 'confidence'
        ]
        
        # Create a normalized dataset ensuring all standard fields exist
        csv_data = []
        for pred in predictions:
            row = {}
            # Add all existing fields from the prediction
            for field in all_fields:
                row[field] = pred.get(field, '')
                
            # Ensure standard fields exist, even if empty
            for field in standard_fields:
                if field not in row:
                    row[field] = ''
                    
            csv_data.append(row)
        
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False)
        
        logger.info(f"Successfully converted order volume predictions to CSV: {csv_file}")
        return csv_file
    
    except Exception as e:
        logger.error(f"Error converting order volume predictions to CSV: {str(e)}")
        try:
            # Create a minimal CSV with basic headers as fallback
            empty_df = pd.DataFrame(columns=[
                'source_city', 'destination_city', 'order_type', 'month', 
                'predicted_volume', 'confidence'
            ])
            empty_df.to_csv(csv_file, index=False)
            logger.warning(f"Created fallback empty CSV due to conversion error: {csv_file}")
            return csv_file
        except:
            return None

def convert_tender_performance_predictions(prediction_dir: Union[str, Path]) -> Optional[Path]:
    """Convert tender performance prediction JSON to CSV.
    
    Args:
        prediction_dir: Directory containing the prediction files
    
    Returns:
        Path to the generated CSV file or None if conversion fails
    """
    try:
        prediction_dir = Path(prediction_dir)
        json_file = prediction_dir / "prediction_data.json"
        csv_file = prediction_dir / "prediction_data.csv"
        
        if not json_file.exists():
            logger.error(f"Prediction JSON file not found: {json_file}")
            return None
        
        # Read the JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract predictions
        predictions = data.get('predictions', [])
        
        if not predictions:
            logger.warning(f"No predictions found in {json_file}")
            return None
        
        # Tender performance predictions typically have these fields
        # Normalize the data for CSV format
        csv_data = []
        for pred in predictions:
            row = {
                'carrier': pred.get('carrier', ''),
                'source_city': pred.get('source_city', ''),
                'dest_city': pred.get('dest_city', ''),
                'predicted_performance': pred.get('predicted_performance', 0)
            }
            csv_data.append(row)
        
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False)
        
        logger.info(f"Successfully converted tender performance predictions to CSV: {csv_file}")
        return csv_file
    
    except Exception as e:
        logger.error(f"Error converting tender performance predictions to CSV: {str(e)}")
        return None

def convert_tender_performance_training_predictions(prediction_dir: Union[str, Path]) -> Optional[Path]:
    """Convert tender performance training data predictions JSON to CSV.
    
    This function handles the specific format of training data predictions, which include
    actual performance values and error metrics.
    
    Args:
        prediction_dir: Directory containing the prediction files
    
    Returns:
        Path to the generated CSV file or None if conversion fails
    """
    try:
        prediction_dir = Path(prediction_dir)
        json_file = prediction_dir / "prediction_data.json"
        csv_file = prediction_dir / "prediction_data.csv"
        
        if not json_file.exists():
            logger.error(f"Training prediction JSON file not found: {json_file}")
            return None
        
        # Read the JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract predictions
        predictions = data.get('predictions', [])
        
        if not predictions:
            logger.warning(f"No predictions found in {json_file}")
            # Create an empty CSV with expected headers
            empty_df = pd.DataFrame(columns=[
                'carrier', 'source_city', 'dest_city', 
                'predicted_performance', 'actual_performance',
                'absolute_error', 'percent_error'
            ])
            empty_df.to_csv(csv_file, index=False)
            logger.info(f"Created empty CSV with headers for training predictions: {csv_file}")
            return csv_file
        
        # Training predictions have additional fields compared to regular predictions
        # Normalize the data for CSV format
        csv_data = []
        for pred in predictions:
            row = {
                'carrier': pred.get('carrier', ''),
                'source_city': pred.get('source_city', ''),
                'dest_city': pred.get('dest_city', ''),
                'predicted_performance': pred.get('predicted_performance', 0),
                'actual_performance': pred.get('actual_performance', 0),
                'absolute_error': pred.get('absolute_error', 0),
                'percent_error': pred.get('percent_error', 0)
            }
            csv_data.append(row)
        
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False)
        
        # Also create summary CSV with metrics
        if 'metrics' in data:
            metrics_file = prediction_dir / "prediction_metrics.csv"
            metrics_data = data.get('metrics', {})
            metrics_df = pd.DataFrame([metrics_data])
            metrics_df.to_csv(metrics_file, index=False)
            logger.info(f"Created metrics summary CSV: {metrics_file}")
        
        logger.info(f"Successfully converted tender performance training predictions to CSV: {csv_file}")
        return csv_file
    
    except Exception as e:
        logger.error(f"Error converting tender performance training predictions to CSV: {str(e)}")
        try:
            # Create a minimal CSV with basic headers as fallback
            empty_df = pd.DataFrame(columns=[
                'carrier', 'source_city', 'dest_city', 
                'predicted_performance', 'actual_performance',
                'absolute_error', 'percent_error'
            ])
            empty_df.to_csv(csv_file, index=False)
            logger.warning(f"Created fallback empty CSV due to conversion error: {csv_file}")
            return csv_file
        except:
            return None

def convert_tender_performance_simplified(prediction_dir: Union[str, Path]) -> Optional[Path]:
    """Convert tender performance prediction JSON to simplified CSV.
    
    This function creates a simplified CSV with just the essential fields:
    carrier, source_city, dest_city, and predicted_performance.
    No error metrics or actual performance is included.
    
    Args:
        prediction_dir: Directory containing the prediction files
    
    Returns:
        Path to the generated simplified CSV file or None if conversion fails
    """
    try:
        prediction_dir = Path(prediction_dir)
        json_file = prediction_dir / "prediction_data.json"
        simplified_csv_file = prediction_dir / "prediction_data_simplified.csv"
        
        if not json_file.exists():
            logger.error(f"Prediction JSON file not found: {json_file}")
            return None
        
        # Read the JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract predictions
        predictions = data.get('predictions', [])
        
        if not predictions:
            logger.warning(f"No predictions found in {json_file}")
            # Create an empty CSV with expected headers
            empty_df = pd.DataFrame(columns=[
                'carrier', 'source_city', 'dest_city', 'predicted_performance'
            ])
            empty_df.to_csv(simplified_csv_file, index=False)
            logger.info(f"Created empty simplified CSV with headers: {simplified_csv_file}")
            return simplified_csv_file
        
        # Create simplified data with only the essential fields
        csv_data = []
        for pred in predictions:
            row = {
                'carrier': pred.get('carrier', ''),
                'source_city': pred.get('source_city', ''),
                'dest_city': pred.get('dest_city', ''),
                'predicted_performance': pred.get('predicted_performance', 0)
            }
            csv_data.append(row)
        
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(simplified_csv_file, index=False)
        
        logger.info(f"Successfully created simplified CSV: {simplified_csv_file}")
        return simplified_csv_file
    
    except Exception as e:
        logger.error(f"Error creating simplified CSV: {str(e)}")
        try:
            # Create a minimal CSV with basic headers as fallback
            empty_df = pd.DataFrame(columns=[
                'carrier', 'source_city', 'dest_city', 'predicted_performance'
            ])
            empty_df.to_csv(simplified_csv_file, index=False)
            logger.warning(f"Created fallback empty simplified CSV due to conversion error: {simplified_csv_file}")
            return simplified_csv_file
        except:
            return None 