import os
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from services.model_service import ModelService

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for managing predictions from machine learning models."""
    
    def __init__(self, base_path: str = "data/predictions"):
        """Initialize the prediction service.
        
        Args:
            base_path: Base directory for storing predictions
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_path / "prediction_metadata.json"
        self.metadata = self._load_metadata()
        self.model_service = ModelService()
        
    def _load_metadata(self) -> Dict:
        """Load prediction metadata from JSON file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("Error parsing prediction metadata file. Creating new metadata.")
                return {"predictions": {}}
        return {"predictions": {}}
    
    def _save_metadata(self):
        """Save prediction metadata to JSON file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def _generate_prediction_id(self) -> str:
        """Generate a unique ID for a prediction."""
        return f"pred_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d')}"
    
    def save_prediction(self, prediction_data: Dict[str, Any]) -> str:
        """Save a prediction and its metadata.
        
        Args:
            prediction_data: Dictionary containing prediction data and metadata
            
        Returns:
            ID of the saved prediction
        """
        prediction_id = self._generate_prediction_id()
        
        # Create directory for prediction data
        prediction_dir = self.base_path / prediction_id
        prediction_dir.mkdir(parents=True, exist_ok=True)
        
        # Save prediction data as JSON
        prediction_file = prediction_dir / "prediction_data.json"
        with open(prediction_file, "w") as f:
            json.dump(prediction_data, f, indent=2)
        
        # Extract and save metadata
        metadata = {
            "prediction_id": prediction_id,
            "model_id": prediction_data.get("model_id"),
            "model_type": self._get_model_type(prediction_data.get("model_id")),
            "created_at": datetime.now().isoformat(),
            "months_predicted": prediction_data.get("months_predicted", 0),
            "prediction_count": len(prediction_data.get("predictions", [])),
            "prediction_file": str(prediction_file)
        }
        
        self.metadata["predictions"][prediction_id] = metadata
        self._save_metadata()
        
        return prediction_id
    
    def _get_model_type(self, model_id: str) -> str:
        """Get the model type from a model ID."""
        if not model_id:
            return "unknown"
        
        model_metadata = self.model_service.get_model_metadata(model_id)
        if not model_metadata:
            return "unknown"
        
        return model_metadata.get("model_type", "unknown")
    
    def get_prediction(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """Get a prediction by ID.
        
        Args:
            prediction_id: ID of the prediction to retrieve
            
        Returns:
            Dictionary with prediction data or None if not found
        """
        metadata = self.metadata["predictions"].get(prediction_id)
        if not metadata:
            return None
        
        prediction_file = metadata.get("prediction_file")
        if not prediction_file or not Path(prediction_file).exists():
            logger.error(f"Prediction file not found for ID {prediction_id}")
            return None
        
        try:
            with open(prediction_file, "r") as f:
                prediction_data = json.load(f)
                
            return {
                **metadata,
                "data": prediction_data
            }
        except Exception as e:
            logger.error(f"Error loading prediction data for ID {prediction_id}: {str(e)}")
            return None
    
    def list_predictions(self, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all predictions with optional filtering by model ID.
        
        Args:
            model_id: Optional filter by model ID
            
        Returns:
            List of prediction metadata dictionaries
        """
        result = []
        for pred_id, metadata in self.metadata["predictions"].items():
            if model_id is None or metadata.get("model_id") == model_id:
                result.append(metadata)
        
        # Sort by creation time (newest first)
        result.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return result
    
    def delete_prediction(self, prediction_id: str) -> bool:
        """Delete a prediction and its data.
        
        Args:
            prediction_id: ID of the prediction to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if prediction_id not in self.metadata["predictions"]:
            return False
        
        prediction_dir = self.base_path / prediction_id
        if prediction_dir.exists():
            try:
                for file in prediction_dir.iterdir():
                    file.unlink()
                prediction_dir.rmdir()
                
                del self.metadata["predictions"][prediction_id]
                self._save_metadata()
                return True
            except Exception as e:
                logger.error(f"Error deleting prediction {prediction_id}: {str(e)}")
                return False
        return False
    
    def predict_order_volume(self, model_id: str, months: int = 6) -> Optional[Dict[str, Any]]:
        """Generate order volume predictions using the specified model.
        
        Args:
            model_id: ID of the model to use
            months: Number of months to predict
            
        Returns:
            Dictionary with prediction results or None if prediction fails
        """
        # Generate predictions using the model service
        prediction_data = self.model_service.predict_future_order_volumes(
            model_id=model_id,
            months=months
        )
        
        if not prediction_data:
            logger.error(f"Failed to generate predictions with model {model_id}")
            return None
        
        # Save the prediction
        prediction_id = self.save_prediction(prediction_data)
        
        # Return the full prediction with ID
        return {
            "prediction_id": prediction_id,
            **prediction_data
        } 