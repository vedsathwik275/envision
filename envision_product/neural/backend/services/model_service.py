import os
import json
import logging
import shutil
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

from models.order_volume_model import OrderVolumeModel
from models.tender_performance_model import TenderPerformanceModel

logger = logging.getLogger(__name__)

class ModelService:
    """Service for managing machine learning models."""
    
    def __init__(self, base_path: str = "data/models"):
        """Initialize the model service.
        
        Args:
            base_path: Base directory for storing models
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_path / "model_metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Load model metadata from JSON file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("Error parsing model metadata file. Creating new metadata.")
                return {"models": {}}
        return {"models": {}}
    
    def _save_metadata(self):
        """Save model metadata to JSON file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)
            
    def list_models(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available models with their metadata.
        
        Args:
            model_type: Optional filter by model type
            
        Returns:
            List of model metadata dictionaries
        """
        result = []
        for model_id, metadata in self.metadata["models"].items():
            if model_type is None or metadata.get("model_type") == model_type:
                model_info = {
                    "model_id": model_id,
                    **metadata
                }
                result.append(model_info)
        
        # Sort by creation time (newest first)
        result.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return result
    
    def get_model_path(self, model_id: str) -> Optional[Path]:
        """Get the filesystem path for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Path to the model directory or None if model doesn't exist
        """
        if model_id not in self.metadata["models"]:
            return None
        
        return self.base_path / model_id
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict]:
        """Get metadata for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Model metadata dictionary or None if model doesn't exist
        """
        return self.metadata["models"].get(model_id)
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a model and its metadata.
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if model_id not in self.metadata["models"]:
            return False
        
        model_path = self.get_model_path(model_id)
        if model_path and model_path.exists():
            try:
                shutil.rmtree(model_path)
                del self.metadata["models"][model_id]
                self._save_metadata()
                return True
            except Exception as e:
                logger.error(f"Error deleting model {model_id}: {str(e)}")
                return False
        return False
    
    def register_model(self, model_path: Union[str, Path], metadata: Dict) -> str:
        """Register a new model with metadata.
        
        Args:
            model_path: Path to the model files
            metadata: Dictionary of metadata for the model
            
        Returns:
            ID of the registered model
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise ValueError(f"Model path does not exist: {model_path}")
        
        # Generate a unique model ID based on timestamp and model type
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        model_type = metadata.get("model_type", "unknown")
        model_id = f"{model_type}_{timestamp}"
        
        # Create a directory for the model
        target_path = self.base_path / model_id
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Copy model files to the target directory
        if model_path.is_dir():
            for item in model_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, target_path)
                else:
                    shutil.copytree(item, target_path / item.name)
        else:
            shutil.copy2(model_path, target_path)
        
        # Update metadata
        full_metadata = {
            **metadata,
            "created_at": datetime.now().isoformat(),
            "model_path": str(target_path)
        }
        
        self.metadata["models"][model_id] = full_metadata
        self._save_metadata()
        
        return model_id
    
    def load_order_volume_model(self, model_id: str) -> Optional[OrderVolumeModel]:
        """Load an order volume model by ID.
        
        Args:
            model_id: ID of the model to load
            
        Returns:
            Loaded OrderVolumeModel instance or None if loading fails
        """
        model_path = self.get_model_path(model_id)
        if not model_path or not model_path.exists():
            logger.error(f"Model path does not exist: {model_path}")
            return None
        
        metadata = self.get_model_metadata(model_id)
        if not metadata or metadata.get("model_type") != "order_volume":
            logger.error(f"Model {model_id} is not an order volume model")
            return None
        
        try:
            model = OrderVolumeModel(model_path=str(model_path))
            return model
        except Exception as e:
            logger.error(f"Error loading order volume model {model_id}: {str(e)}")
            return None
    
    def load_tender_performance_model(self, model_id: str) -> Optional[TenderPerformanceModel]:
        """Load a tender performance model by ID.
        
        Args:
            model_id: ID of the model to load
            
        Returns:
            Loaded TenderPerformanceModel instance or None if loading fails
        """
        model_path = self.get_model_path(model_id)
        if not model_path or not model_path.exists():
            logger.error(f"Model path does not exist: {model_path}")
            return None
        
        metadata = self.get_model_metadata(model_id)
        if not metadata or metadata.get("model_type") != "tender_performance":
            logger.error(f"Model {model_id} is not a tender performance model")
            return None
        
        try:
            model = TenderPerformanceModel(model_path=str(model_path))
            return model
        except Exception as e:
            logger.error(f"Error loading tender performance model {model_id}: {str(e)}")
            return None
    
    def train_order_volume_model(self, data_path: str, params: Dict = None) -> Optional[str]:
        """Train a new order volume model.
        
        Args:
            data_path: Path to the training data file
            params: Dictionary of training parameters
            
        Returns:
            ID of the newly trained model or None if training fails
        """
        if not os.path.exists(data_path):
            logger.error(f"Training data not found: {data_path}")
            return None
        
        # Default parameters
        default_params = {
            "epochs": 100,
            "batch_size": 32,
            "validation_split": 0.2,
            "test_size": 0.2
        }
        
        # Override defaults with provided params
        if params:
            training_params = {**default_params, **params}
        else:
            training_params = default_params
        
        try:
            # Create a temporary directory for the model
            temp_model_dir = self.base_path / "temp_model"
            os.makedirs(temp_model_dir, exist_ok=True)
            
            # Train the model
            model = OrderVolumeModel(data_path=data_path)
            
            # Make sure raw_data is loaded and processed
            if not hasattr(model, 'raw_data') or model.raw_data is None:
                model.load_data()
            
            model.preprocess_data()
            model.prepare_train_test_split(test_size=training_params["test_size"])
            model.build_model()
            
            # Use a smaller number of epochs for testing
            actual_epochs = 5 if os.environ.get("TESTING", "0") == "1" else training_params["epochs"]
            
            history = model.train(
                epochs=actual_epochs,
                batch_size=training_params["batch_size"],
                validation_split=training_params["validation_split"]
            )
            
            # Evaluate the model
            evaluation = model.evaluate()
            
            # Save the model - this will now also save raw_data
            model.save_model(str(temp_model_dir))
            
            # Copy the original data file to ensure it's available
            training_data_file = os.path.join(temp_model_dir, "training_data.csv")
            if not os.path.exists(training_data_file):
                logger.info(f"Copying original training data to model directory")
                shutil.copy2(data_path, training_data_file)
            
            # Register the model with metadata
            metadata = {
                "model_type": "order_volume",
                "training_data": data_path,
                "training_params": training_params,
                "evaluation": evaluation,
                "description": f"Order volume prediction model trained on {os.path.basename(data_path)}"
            }
            
            model_id = self.register_model(temp_model_dir, metadata)
            
            # Clean up temporary directory
            shutil.rmtree(temp_model_dir, ignore_errors=True)
            
            return model_id
            
        except Exception as e:
            logger.error(f"Error training order volume model: {str(e)}")
            return None
            
    def train_tender_performance_model(self, data_path: str, params: Dict = None) -> Optional[str]:
        """Train a new tender performance model.
        
        Args:
            data_path: Path to the training data file
            params: Dictionary of training parameters
            
        Returns:
            ID of the newly trained model or None if training fails
        """
        if not os.path.exists(data_path):
            logger.error(f"Training data not found: {data_path}")
            return None
        
        # Default parameters
        default_params = {
            "epochs": 100,
            "batch_size": 32,
            "validation_split": 0.2,
            "test_size": 0.2
        }
        
        # Override defaults with provided params
        if params:
            training_params = {**default_params, **params}
        else:
            training_params = default_params
        
        try:
            # Create a temporary directory for the model
            temp_model_dir = self.base_path / "temp_model"
            os.makedirs(temp_model_dir, exist_ok=True)
            
            # Train the model
            model = TenderPerformanceModel(data_path=data_path)
            
            # Make sure raw_data is loaded and processed
            if not hasattr(model, 'raw_data') or model.raw_data is None:
                model.load_data()
            
            model.preprocess_data()
            model.prepare_train_test_split(test_size=training_params["test_size"])
            model.build_model()
            
            # Use a smaller number of epochs for testing
            actual_epochs = 5 if os.environ.get("TESTING", "0") == "1" else training_params["epochs"]
            
            history = model.train(
                epochs=actual_epochs,
                batch_size=training_params["batch_size"],
                validation_split=training_params["validation_split"]
            )
            
            # Evaluate the model
            evaluation = model.evaluate()
            
            # Save the model
            model.save_model(str(temp_model_dir))
            
            # Copy the original data file to ensure it's available
            training_data_file = os.path.join(temp_model_dir, "training_data.csv")
            if not os.path.exists(training_data_file):
                logger.info(f"Copying original training data to model directory")
                shutil.copy2(data_path, training_data_file)
            
            # Register the model with metadata
            metadata = {
                "model_type": "tender_performance",
                "training_data": data_path,
                "training_params": training_params,
                "evaluation": evaluation,
                "description": f"Tender performance prediction model trained on {os.path.basename(data_path)}"
            }
            
            model_id = self.register_model(temp_model_dir, metadata)
            
            # Clean up temporary directory
            shutil.rmtree(temp_model_dir, ignore_errors=True)
            
            return model_id
            
        except Exception as e:
            logger.error(f"Error training tender performance model: {str(e)}")
            return None
    
    def predict_future_order_volumes(self, model_id: str, months: int = 6) -> Optional[Dict]:
        """Generate predictions for future order volumes.
        
        Args:
            model_id: ID of the model to use for prediction
            months: Number of future months to predict
            
        Returns:
            Dictionary with prediction results or None if prediction fails
        """
        model = self.load_order_volume_model(model_id)
        if not model:
            logger.error(f"Failed to load model {model_id}")
            return None
        
        try:
            # Generate predictions
            logger.info(f"Generating predictions using model {model_id} for {months} months")
            predictions_df = model.predict_future(months=months)
            
            if predictions_df.empty:
                logger.warning(f"Model {model_id} generated an empty prediction dataframe")
                return {
                    "model_id": model_id,
                    "prediction_time": datetime.now().isoformat(),
                    "months_predicted": months,
                    "predictions": [],
                    "warning": "No predictions were generated. The model may not have enough training data."
                }
            
            # Convert predictions to a dictionary format
            predictions = predictions_df.to_dict(orient="records")
            
            result = {
                "model_id": model_id,
                "prediction_time": datetime.now().isoformat(),
                "months_predicted": months,
                "predictions": predictions
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating predictions with model {model_id}: {str(e)}")
            return None
            
    def predict_tender_performance(self, model_id: str, carriers: List[str], source_cities: List[str], dest_cities: List[str]) -> Optional[Dict]:
        """Generate predictions for tender performance.
        
        Args:
            model_id: ID of the model to use for prediction
            carriers: List of carriers
            source_cities: List of source cities
            dest_cities: List of destination cities
            
        Returns:
            Dictionary with prediction results or None if prediction fails
        """
        # Load the model
        logger.info(f"Loading tender performance model {model_id} for prediction")
        model = self.load_tender_performance_model(model_id)
        if not model:
            logger.error(f"Failed to load model {model_id}")
            return None
        
        try:
            # Validate input lists have the same length
            if not (len(carriers) == len(source_cities) == len(dest_cities)):
                error_msg = "Input lists (carriers, source_cities, dest_cities) must have the same length"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Generate predictions
            logger.info(f"Generating tender performance predictions using model {model_id}")
            predictions = []
            
            for i in range(len(carriers)):
                logger.info(f"Processing prediction {i+1}/{len(carriers)}: {carriers[i]} from {source_cities[i]} to {dest_cities[i]}")
                
                try:
                    single_prediction = model.predict(
                        carrier=carriers[i],
                        source_city=source_cities[i],
                        dest_city=dest_cities[i]
                    )
                    
                    if single_prediction:
                        predictions.append(single_prediction)
                    else:
                        logger.warning(f"Failed to generate prediction for carrier={carriers[i]}, source={source_cities[i]}, dest={dest_cities[i]}")
                except Exception as e:
                    logger.error(f"Error generating single prediction: {str(e)}")
            
            if not predictions:
                logger.warning("No successful predictions were generated")
                return {
                    "model_id": model_id,
                    "prediction_time": datetime.now().isoformat(),
                    "predictions": [],
                    "warning": "No valid predictions could be generated. The model may not have enough training data for these carrier-lane combinations."
                }
            
            result = {
                "model_id": model_id,
                "prediction_time": datetime.now().isoformat(),
                "predictions": predictions
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating tender performance predictions with model {model_id}: {str(e)}")
            return None

    def predict_tender_performance_on_training_data(self, model_id: str) -> Optional[Dict]:
        """Generate predictions for tender performance on the training data.
        
        This method loads the tender performance model and predicts on the data
        that was used for training. This can be useful for analyzing model performance
        and understanding prediction accuracy.
        
        Args:
            model_id: ID of the model to use for prediction
            
        Returns:
            Dictionary with prediction results or None if prediction fails
        """
        # Get model directory to check for existing predictions
        model_path = self.get_model_path(model_id)
        if not model_path:
            logger.error(f"Model directory for {model_id} not found")
            return None
        
        # Create training predictions directory
        training_predictions_dir = os.path.join(model_path, "training_predictions")
        os.makedirs(training_predictions_dir, exist_ok=True)
        
        # Check if predictions already exist
        json_file = os.path.join(training_predictions_dir, "prediction_data.json")
        csv_file = os.path.join(training_predictions_dir, "prediction_data.csv")
        simplified_csv_file = os.path.join(training_predictions_dir, "prediction_data_simplified.csv")
        
        if os.path.exists(json_file):
            logger.info(f"Found existing training predictions for model {model_id}")
            try:
                # Load existing predictions
                with open(json_file, 'r') as f:
                    result = json.load(f)
                
                # Ensure CSV files exist
                if not os.path.exists(csv_file):
                    try:
                        from utils.file_converters import convert_tender_performance_training_predictions
                        csv_path = convert_tender_performance_training_predictions(training_predictions_dir)
                        if csv_path:
                            logger.info(f"Generated missing complete CSV file: {csv_path}")
                    except Exception as e:
                        logger.error(f"Error creating complete CSV for training predictions: {str(e)}")
                
                if not os.path.exists(simplified_csv_file):
                    try:
                        from utils.file_converters import convert_tender_performance_simplified
                        simplified_csv_path = convert_tender_performance_simplified(training_predictions_dir)
                        if simplified_csv_path:
                            logger.info(f"Generated missing simplified CSV file: {simplified_csv_path}")
                    except Exception as e:
                        logger.error(f"Error creating simplified CSV for training predictions: {str(e)}")
                
                return result
            except Exception as e:
                logger.warning(f"Error loading existing predictions, will regenerate: {str(e)}")
                # Continue to regenerate predictions if loading fails
        else:
            logger.info(f"No existing predictions found for model {model_id}, generating new predictions")
        
        # Load the model
        logger.info(f"Loading tender performance model {model_id} for training data prediction")
        model = self.load_tender_performance_model(model_id)
        if not model:
            logger.error(f"Failed to load model {model_id}")
            return None
        
        try:
            # Generate predictions on training data
            logger.info(f"Generating predictions on training data for model {model_id}")
            result = model.predict_on_training_data(output_dir=training_predictions_dir)
            
            if not result:
                logger.error("Failed to generate predictions on training data")
                return None
            
            # Add model_id to the result
            result["model_id"] = model_id
            
            # Ensure complete CSV file is created
            try:
                from utils.file_converters import convert_tender_performance_training_predictions
                csv_path = convert_tender_performance_training_predictions(training_predictions_dir)
                if csv_path:
                    logger.info(f"Complete training predictions CSV created at {csv_path}")
            except Exception as e:
                logger.error(f"Error creating complete CSV for training predictions: {str(e)}")
            
            # Also generate simplified CSV
            try:
                from utils.file_converters import convert_tender_performance_simplified
                simplified_csv_path = convert_tender_performance_simplified(training_predictions_dir)
                if simplified_csv_path:
                    logger.info(f"Simplified training predictions CSV created at {simplified_csv_path}")
            except Exception as e:
                logger.error(f"Error creating simplified CSV for training predictions: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating predictions on training data for model {model_id}: {str(e)}")
            return None 