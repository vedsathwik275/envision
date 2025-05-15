import os
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from services.model_service import ModelService
from utils.file_converters import json_to_csv, convert_order_volume_predictions, convert_tender_performance_predictions

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
        
        # Also save as CSV
        try:
            csv_file = prediction_dir / "prediction_data.csv"
            json_to_csv(prediction_file, csv_file)
            logger.info(f"Generated CSV prediction file: {csv_file}")
        except Exception as e:
            logger.error(f"Error generating CSV file: {str(e)}")
        
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
                
            # Include prediction_id in the top level of the response
            return {
                "prediction_id": prediction_id,  # Ensure prediction_id is included at the top level
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
        
        # Generate CSV file specifically for order volume
        try:
            prediction_dir = self.base_path / prediction_id
            convert_order_volume_predictions(prediction_dir)
        except Exception as e:
            logger.error(f"Error generating order volume CSV: {str(e)}")
        
        # Return the full prediction with ID
        return {
            "prediction_id": prediction_id,
            **prediction_data
        }
    
    def predict_tender_performance(self, model_id: str, carriers: List[str], source_cities: List[str], dest_cities: List[str]) -> Optional[Dict[str, Any]]:
        """Generate tender performance predictions using a trained model.
        
        Args:
            model_id: ID of the model to use
            carriers: List of carriers
            source_cities: List of source cities
            dest_cities: List of destination cities
            
        Returns:
            Dictionary with prediction results or None if prediction fails
        """
        # Get predictions from the model service
        prediction_data = self.model_service.predict_tender_performance(
            model_id=model_id,
            carriers=carriers,
            source_cities=source_cities,
            dest_cities=dest_cities
        )
        
        if not prediction_data:
            logger.error(f"Failed to generate tender performance predictions with model {model_id}")
            return None
        
        # Generate a unique ID for this prediction
        prediction_id = str(uuid.uuid4())
        
        # Create directory for prediction data
        prediction_dir = self.base_path / prediction_id
        prediction_dir.mkdir(parents=True, exist_ok=True)
        
        # Save prediction data as JSON
        prediction_file = prediction_dir / "prediction_data.json"
        with open(prediction_file, "w") as f:
            json.dump(prediction_data, f, indent=2)
        
        # Also save as CSV
        try:
            csv_file = prediction_dir / "prediction_data.csv"
            convert_tender_performance_predictions(prediction_dir)
            logger.info(f"Generated CSV prediction file: {csv_file}")
        except Exception as e:
            logger.error(f"Error generating CSV file: {str(e)}")
        
        # Create metadata for the prediction
        metadata = {
            "prediction_id": prediction_id,
            "model_id": model_id,
            "model_type": "tender_performance",
            "created_at": datetime.now().isoformat(),
            "prediction_count": len(prediction_data.get("predictions", [])),
            "prediction_file": str(prediction_file)
        }
        
        # Save metadata
        self.metadata["predictions"][prediction_id] = metadata
        self._save_metadata()
        
        # Return the result with prediction ID
        return {
            "prediction_id": prediction_id,
            **prediction_data
        }
    
    def get_predictions(self, model_id: str, filters: Dict = None, limit: int = 1000, offset: int = 0) -> Optional[Dict[str, Any]]:
        """Get filtered predictions for a model.
        
        Args:
            model_id: ID of the model
            filters: Dictionary of filters to apply
            limit: Maximum number of predictions to return
            offset: Number of predictions to skip
            
        Returns:
            Dictionary with filtered predictions or None if model not found
        """
        # Find the latest prediction for this model
        model_predictions = [p for p in self.list_predictions(model_id=model_id)]
        
        if not model_predictions:
            return None
        
        # Sort by creation time (newest first)
        model_predictions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        latest_prediction = model_predictions[0]
        
        # Get the full prediction data
        prediction_data = self.get_prediction(latest_prediction["prediction_id"])
        
        if not prediction_data or "data" not in prediction_data:
            return None
        
        # Extract the predictions
        predictions = prediction_data["data"].get("predictions", [])
        
        # Apply filters if provided
        if filters:
            filtered_predictions = []
            for pred in predictions:
                match = True
                
                # Check each filter
                for key, value in filters.items():
                    # Handle special case for carrier filter
                    if key == "carrier" and "carrier" in pred:
                        if pred["carrier"].lower() != value.lower():
                            match = False
                            break
                    # Handle regular source/destination/order_type filters
                    elif key in pred:
                        if pred[key].lower() != value.lower():
                            match = False
                            break
                
                if match:
                    filtered_predictions.append(pred)
            
            predictions = filtered_predictions
        
        # Apply limit and offset
        paginated_predictions = predictions[offset:offset+limit]
        
        result = {
            "model_id": model_id,
            "prediction_id": latest_prediction["prediction_id"],
            "created_at": latest_prediction["created_at"],
            "total_predictions": len(predictions),
            "filtered_predictions": len(paginated_predictions),
            "predictions": paginated_predictions
        }
        
        return result
    
    def initialize_prediction_job(self, model_id: str, months: int = 6, params: Dict = None) -> str:
        """Initialize a background prediction job.
        
        Args:
            model_id: ID of the model to use
            months: Number of future months to predict
            params: Additional parameters for prediction
            
        Returns:
            Job ID for tracking the prediction job
        """
        job_id = str(uuid.uuid4())
        
        # Create a job file with metadata
        job_data = {
            "job_id": job_id,
            "model_id": model_id,
            "months": months,
            "params": params or {},
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        job_path = self.base_path / "jobs" / f"{job_id}.json"
        os.makedirs(os.path.dirname(job_path), exist_ok=True)
        
        with open(job_path, "w") as f:
            json.dump(job_data, f, indent=2)
        
        return job_id
    
    def run_prediction_job(self, job_id: str) -> Optional[str]:
        """Run a prediction job in the background.
        
        Args:
            job_id: ID of the job to run
            
        Returns:
            Prediction ID or None if the job fails
        """
        job_path = self.base_path / "jobs" / f"{job_id}.json"
        
        if not job_path.exists():
            logger.error(f"Job file not found: {job_path}")
            return None
        
        try:
            # Load the job data
            with open(job_path, "r") as f:
                job_data = json.load(f)
            
            # Update job status
            job_data["status"] = "running"
            job_data["started_at"] = datetime.now().isoformat()
            
            with open(job_path, "w") as f:
                json.dump(job_data, f, indent=2)
            
            # Get model metadata to determine model type
            model_id = job_data["model_id"]
            model_metadata = self.model_service.get_model_metadata(model_id)
            
            if not model_metadata:
                logger.error(f"Model {model_id} not found")
                job_data["status"] = "failed"
                job_data["error"] = f"Model {model_id} not found"
                with open(job_path, "w") as f:
                    json.dump(job_data, f, indent=2)
                return None
            
            # Run the appropriate prediction method based on model type
            model_type = model_metadata.get("model_type")
            
            if model_type == "order_volume":
                # Generate order volume predictions
                result = self.predict_order_volume(
                    model_id=model_id,
                    months=job_data.get("months", 6)
                )
            elif model_type == "tender_performance":
                # For tender performance, we need specific parameters from the job
                params = job_data.get("params", {})
                carriers = params.get("carriers", [])
                source_cities = params.get("source_cities", [])
                dest_cities = params.get("dest_cities", [])
                
                if not carriers or not source_cities or not dest_cities:
                    logger.error("Missing required parameters for tender performance prediction")
                    job_data["status"] = "failed"
                    job_data["error"] = "Missing required parameters for tender performance prediction"
                    with open(job_path, "w") as f:
                        json.dump(job_data, f, indent=2)
                    return None
                
                result = self.predict_tender_performance(
                    model_id=model_id,
                    carriers=carriers,
                    source_cities=source_cities,
                    dest_cities=dest_cities
                )
            else:
                logger.error(f"Unsupported model type: {model_type}")
                job_data["status"] = "failed"
                job_data["error"] = f"Unsupported model type: {model_type}"
                with open(job_path, "w") as f:
                    json.dump(job_data, f, indent=2)
                return None
            
            if not result:
                logger.error(f"Failed to generate predictions with model {model_id}")
                job_data["status"] = "failed"
                job_data["error"] = f"Failed to generate predictions with model {model_id}"
                with open(job_path, "w") as f:
                    json.dump(job_data, f, indent=2)
                return None
            
            # Update job status
            prediction_id = result.get("prediction_id")
            job_data["status"] = "completed"
            job_data["completed_at"] = datetime.now().isoformat()
            job_data["prediction_id"] = prediction_id
            
            with open(job_path, "w") as f:
                json.dump(job_data, f, indent=2)
            
            return prediction_id
            
        except Exception as e:
            logger.error(f"Error running prediction job {job_id}: {str(e)}")
            
            try:
                # Update job status with error
                job_data = {"status": "failed", "error": str(e)}
                with open(job_path, "w") as f:
                    json.dump(job_data, f, indent=2)
            except:
                pass
                
            return None
            
    def filter_predictions(self, model_id: str, filters: Dict) -> Optional[Dict[str, Any]]:
        """Filter predictions using complex criteria.
        
        Args:
            model_id: ID of the model
            filters: Dictionary of filter criteria
            
        Returns:
            Dictionary with filtered predictions or None if no matches
        """
        # Get the latest prediction for this model
        model_predictions = self.list_predictions(model_id=model_id)
        
        if not model_predictions:
            return None
        
        # Sort by creation time (newest first)
        model_predictions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        latest_prediction = model_predictions[0]
        
        # Get the full prediction data
        prediction_data = self.get_prediction(latest_prediction["prediction_id"])
        
        if not prediction_data or "data" not in prediction_data:
            return None
        
        # Extract the predictions
        predictions = prediction_data["data"].get("predictions", [])
        
        # Get model type to determine filtering strategy
        model_type = prediction_data.get("model_type")
        
        # Apply filters based on model type
        if model_type == "order_volume":
            filtered_predictions = self._filter_order_volume_predictions(predictions, filters)
        elif model_type == "tender_performance":
            filtered_predictions = self._filter_tender_performance_predictions(predictions, filters)
        else:
            # Generic filtering
            filtered_predictions = self._filter_generic_predictions(predictions, filters)
        
        result = {
            "model_id": model_id,
            "prediction_id": latest_prediction["prediction_id"],
            "created_at": latest_prediction["created_at"],
            "model_type": model_type,
            "total_predictions": len(predictions),
            "filtered_count": len(filtered_predictions),
            "predictions": filtered_predictions
        }
        
        return result
    
    def _filter_order_volume_predictions(self, predictions: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters specific to order volume predictions."""
        result = []
        
        # Extract filter criteria
        source_cities = filters.get("source_cities", [])
        destination_cities = filters.get("destination_cities", [])
        order_types = filters.get("order_types", [])
        date_range = filters.get("date_range", {})
        
        for pred in predictions:
            match = True
            
            # Filter by source city
            if source_cities and pred.get("source_city") not in source_cities:
                match = False
                
            # Filter by destination city
            if destination_cities and pred.get("destination_city") not in destination_cities:
                match = False
                
            # Filter by order type
            if order_types and pred.get("order_type") not in order_types:
                match = False
                
            # Filter by date range
            if date_range:
                start_date = date_range.get("start")
                end_date = date_range.get("end")
                pred_date = pred.get("month")
                
                if start_date and pred_date < start_date:
                    match = False
                    
                if end_date and pred_date > end_date:
                    match = False
            
            if match:
                result.append(pred)
                
        return result
    
    def _filter_tender_performance_predictions(self, predictions: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters specific to tender performance predictions."""
        result = []
        
        # Extract filter criteria
        source_cities = filters.get("source_cities", [])
        destination_cities = filters.get("destination_cities", [])
        carriers = filters.get("carriers", [])
        
        for pred in predictions:
            match = True
            
            # Filter by carrier
            if carriers and pred.get("carrier") not in carriers:
                match = False
                
            # Filter by source city
            if source_cities and pred.get("source_city") not in source_cities:
                match = False
                
            # Filter by destination city
            if destination_cities and pred.get("dest_city") not in destination_cities:
                match = False
            
            if match:
                result.append(pred)
                
        return result
    
    def _filter_generic_predictions(self, predictions: List[Dict], filters: Dict) -> List[Dict]:
        """Apply generic filters to predictions."""
        result = []
        
        for pred in predictions:
            match = True
            
            # Check each filter criterion
            for key, values in filters.items():
                if key == "date_range":
                    # Skip date range for generic filtering
                    continue
                    
                if not values:
                    # Skip empty filter values
                    continue
                    
                # Check if this prediction matches any of the filter values for this key
                pred_value = pred.get(key)
                if pred_value is None:
                    match = False
                    break
                    
                # Handle list of values vs single value
                if isinstance(values, list):
                    if pred_value not in values:
                        match = False
                        break
                else:
                    if pred_value != values:
                        match = False
                        break
            
            if match:
                result.append(pred)
                
        return result
    
    def get_order_volume_predictions(
        self, 
        model_id: str,
        source_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        order_type: Optional[str] = None,
        month: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Get order volume predictions for a specific model with optional filtering.
        
        Args:
            model_id: ID of the model
            source_city: Optional source city filter
            destination_city: Optional destination city filter
            order_type: Optional order type filter
            month: Optional month filter (format: YYYY-MM)
            limit: Maximum number of predictions to return
            offset: Number of predictions to skip
            
        Returns:
            Dictionary with filtered predictions or None if model not found
        """
        logger.info(f"Getting order volume predictions for model {model_id} with filters: "
                  f"source_city={source_city}, destination_city={destination_city}, "
                  f"order_type={order_type}, month={month}")
        
        # Find the latest prediction for this model
        model_predictions = [p for p in self.list_predictions(model_id=model_id) 
                           if p.get("model_type") == "order_volume"]
        
        if not model_predictions:
            logger.warning(f"No order volume predictions found for model {model_id}")
            return None
        
        # Sort by creation time (newest first)
        model_predictions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        latest_prediction = model_predictions[0]
        
        # Get the full prediction data
        prediction_data = self.get_prediction(latest_prediction["prediction_id"])
        
        if not prediction_data or "data" not in prediction_data:
            logger.error(f"Prediction data not found for ID {latest_prediction['prediction_id']}")
            return None
        
        # Extract the predictions
        predictions = prediction_data["data"].get("predictions", [])
        
        # Apply filters
        filtered_predictions = self._filter_order_volume_predictions_advanced(
            predictions=predictions,
            source_city=source_city,
            destination_city=destination_city,
            order_type=order_type,
            month=month
        )
        
        # Apply limit and offset
        paginated_predictions = filtered_predictions[offset:offset+limit]
        
        # Check if CSV file exists
        prediction_id = latest_prediction["prediction_id"]
        prediction_dir = self.base_path / prediction_id
        csv_file = prediction_dir / "prediction_data.csv"
        json_file = prediction_dir / "prediction_data.json"
        
        # Generate CSV file if it doesn't exist
        if not csv_file.exists() and json_file.exists():
            logger.info(f"CSV file not found for prediction {prediction_id}. Generating it now.")
            try:
                from utils.file_converters import convert_order_volume_predictions
                csv_path = convert_order_volume_predictions(prediction_dir)
                csv_exists = csv_path is not None and csv_path.exists()
            except Exception as e:
                logger.error(f"Failed to generate CSV file on demand: {str(e)}")
                csv_exists = False
        else:
            csv_exists = csv_file.exists()
            
        # Always check again after potential generation
        if csv_file.exists():
            csv_exists = True
            csv_path = str(csv_file)
        else:
            csv_exists = False
            csv_path = None
        
        result = {
            "model_id": model_id,
            "prediction_id": prediction_id,
            "created_at": latest_prediction["created_at"],
            "total_predictions": len(predictions),
            "filtered_predictions": len(filtered_predictions),
            "returned_predictions": len(paginated_predictions),
            "has_csv_export": csv_exists,
            "csv_path": csv_path,
            "json_path": str(json_file) if json_file.exists() else None,
            "predictions": paginated_predictions
        }
        
        return result
    
    def get_order_volume_by_lane(
        self,
        model_id: str,
        source_city: str,
        destination_city: str,
        order_type: Optional[str] = None,
        month: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get order volume predictions for a specific lane.
        
        Args:
            model_id: ID of the model
            source_city: Source city
            destination_city: Destination city
            order_type: Optional order type filter
            month: Optional month filter (format: YYYY-MM)
            
        Returns:
            Dictionary with lane predictions or None if not found
        """
        if not source_city or not destination_city:
            logger.error("Source city and destination city are required for lane predictions")
            return None
        
        # Get predictions with filtering
        result = self.get_order_volume_predictions(
            model_id=model_id,
            source_city=source_city,
            destination_city=destination_city,
            order_type=order_type,
            month=month
        )
        
        if not result or not result.get("predictions"):
            logger.warning(f"No predictions found for lane {source_city} to {destination_city}")
            return None
        
        # Format the response specifically for lane view
        lane_data = {
            "model_id": model_id,
            "lane": {
                "source_city": source_city,
                "destination_city": destination_city
            },
            "predictions": result["predictions"],
            "prediction_count": len(result["predictions"])
        }
        
        return lane_data
    
    def _filter_order_volume_predictions_advanced(
        self,
        predictions: List[Dict],
        source_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        order_type: Optional[str] = None,
        month: Optional[str] = None
    ) -> List[Dict]:
        """Apply advanced filters to order volume predictions.
        
        Args:
            predictions: List of prediction dictionaries
            source_city: Optional source city filter
            destination_city: Optional destination city filter
            order_type: Optional order type filter
            month: Optional month filter (format: YYYY-MM)
            
        Returns:
            Filtered list of predictions
        """
        result = []
        
        for pred in predictions:
            match = True
            
            # Filter by source city (case-insensitive)
            if source_city and pred.get("source_city", "").upper() != source_city.upper():
                match = False
                
            # Filter by destination city (case-insensitive)
            if destination_city and pred.get("destination_city", "").upper() != destination_city.upper():
                match = False
                
            # Filter by order type (case-insensitive)
            if order_type and pred.get("order_type", "").upper() != order_type.upper():
                match = False
                
            # Filter by month
            if month and pred.get("month", "") != month:
                match = False
            
            if match:
                result.append(pred)
                
        return result 