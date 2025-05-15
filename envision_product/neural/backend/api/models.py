#!/usr/bin/env python3
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import logging
import datetime


from services.model_service import ModelService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)

class ModelType(BaseModel):
    id: str
    name: str
    description: str
    params: Dict[str, Any] = {}

class TrainingRequest(BaseModel):
    file_id: str
    model_type: str
    params: Optional[Dict[str, Any]] = None

class TrainingParams(BaseModel):
    epochs: int = Field(100, description="Number of training epochs")
    batch_size: int = Field(32, description="Training batch size")
    validation_split: float = Field(0.2, description="Validation data split ratio")
    test_size: float = Field(0.2, description="Test data split ratio")
    description: Optional[str] = Field(None, description="Model description")

class ModelMetadata(BaseModel):
    model_id: str
    model_type: str
    created_at: str
    description: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None
    training_data: Optional[str] = None
    training_params: Optional[Dict[str, Any]] = None

class ModelList(BaseModel):
    models: List[ModelMetadata]

class TrainingResponse(BaseModel):
    status: str
    message: str
    model_id: Optional[str] = None

class OrderVolumePredictionRequest(BaseModel):
    model_id: str
    months: int = Field(6, description="Number of months to predict")

class TenderPerformancePredictionRequest(BaseModel):
    model_id: str
    carriers: List[str] = Field(..., description="List of carriers")
    source_cities: List[str] = Field(..., description="List of source cities")
    dest_cities: List[str] = Field(..., description="List of destination cities")
    
class OrderVolumePredictionResponse(BaseModel):
    model_id: str
    prediction_time: str
    months_predicted: int
    predictions: List[Dict[str, Any]]

class TenderPerformancePredictionResponse(BaseModel):
    model_id: str
    prediction_time: str
    predictions: List[Dict[str, Any]]

def get_model_service():
    return ModelService()

@router.get("/", response_model=ModelList)
async def list_models(
    model_type: Optional[str] = None,
    model_service: ModelService = Depends(get_model_service)
):
    """List all available models with optional filtering by model type."""
    models = model_service.list_models(model_type=model_type)
    return {"models": models}

@router.get("/latest", response_model=ModelMetadata)
async def get_latest_model(
    model_type: str,
    min_created_at: Optional[str] = None,
    min_accuracy: Optional[float] = None,
    max_error: Optional[float] = None,
    model_service: ModelService = Depends(get_model_service)
):
    """
    Get the latest model by type with optional filtering.
    
    This endpoint returns the most recently created model of the specified type
    that matches the provided filters.
    
    - **model_type**: The type of model to retrieve (required)
    - **min_created_at**: Optional minimum creation date (format: YYYY-MM-DD)
    - **min_accuracy**: Optional minimum accuracy/r2 score
    - **max_error**: Optional maximum error (MAE/RMSE)
    """
    models = model_service.list_models(model_type=model_type)
    
    if not models:
        raise HTTPException(
            status_code=404, 
            detail=f"No models found for type: {model_type}"
        )
    
    # Apply date filter if provided
    if min_created_at:
        try:
            min_date = datetime.datetime.fromisoformat(min_created_at.replace('Z', '+00:00'))
            filtered_models = []
            
            for model in models:
                model_date_str = model.get("created_at", "")
                if model_date_str:
                    # Handle both formats with and without timezone
                    model_date_str = model_date_str.replace('Z', '+00:00')
                    try:
                        model_date = datetime.datetime.fromisoformat(model_date_str)
                        if model_date >= min_date:
                            filtered_models.append(model)
                    except ValueError:
                        # If date parsing fails, keep the model in the list
                        filtered_models.append(model)
                else:
                    filtered_models.append(model)
                    
            models = filtered_models
            
            if not models:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No models found for type: {model_type} created after {min_created_at}"
                )
                
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format for min_created_at. Expected format: YYYY-MM-DD"
            )
    
    # Apply performance metric filters if provided
    if min_accuracy is not None or max_error is not None:
        filtered_models = []
        
        for model in models:
            evaluation = model.get("evaluation", {})
            if not evaluation:
                continue
                
            # Check R² score (accuracy) if min_accuracy is provided
            if min_accuracy is not None:
                r2 = evaluation.get("r2")
                if r2 is None or r2 < min_accuracy:
                    continue
            
            # Check error metrics if max_error is provided
            if max_error is not None:
                mae = evaluation.get("mae")
                rmse = evaluation.get("rmse")
                
                # If both metrics exist, use the smaller one
                if mae is not None and rmse is not None:
                    error = min(mae, rmse)
                elif mae is not None:
                    error = mae
                elif rmse is not None:
                    error = rmse
                else:
                    error = None
                
                if error is None or error > max_error:
                    continue
            
            filtered_models.append(model)
        
        models = filtered_models
        
        if not models:
            error_detail = f"No models found for type: {model_type} matching the performance criteria"
            if min_accuracy is not None:
                error_detail += f", min_accuracy: {min_accuracy}"
            if max_error is not None:
                error_detail += f", max_error: {max_error}"
                
            raise HTTPException(
                status_code=404,
                detail=error_detail
            )
    
    # The models are already sorted by creation time (newest first) from list_models
    latest_model = models[0]
    
    return {
        "model_id": latest_model["model_id"],
        **latest_model
    }

@router.get("/{model_id}", response_model=ModelMetadata)
async def get_model(
    model_id: str,
    model_service: ModelService = Depends(get_model_service)
):
    """Get details for a specific model."""
    metadata = model_service.get_model_metadata(model_id)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    return {
        "model_id": model_id,
        **metadata
    }

@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    model_service: ModelService = Depends(get_model_service)
):
    """Delete a model."""
    if not model_service.delete_model(model_id):
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found or could not be deleted")
    
    return {"status": "success", "message": f"Model {model_id} deleted successfully"}

@router.post("/train/order-volume", response_model=TrainingResponse)
async def train_order_volume_model(
    background_tasks: BackgroundTasks,
    data_file_id: str,
    params: Optional[TrainingParams] = None,
    model_service: ModelService = Depends(get_model_service)
):
    """Train a new order volume prediction model.
    
    This is a long-running task that will be executed in the background.
    """
    from services.file_service import FileService
    
    file_service = FileService()
    data_path = file_service.get_file_path(data_file_id)
    
    if not data_path:
        raise HTTPException(status_code=404, detail=f"Data file with ID {data_file_id} not found")
    
    # Function to run training in the background
    def train_model_task(data_path: str, params: Dict = None):
        try:
            model_id = model_service.train_order_volume_model(
                data_path=data_path,
                params=params.dict() if params else None
            )
            logger.info(f"Model training completed. Model ID: {model_id}")
        except Exception as e:
            logger.error(f"Error in background training task: {str(e)}")
    
    # Add the training task to background tasks
    background_tasks.add_task(
        train_model_task,
        data_path=data_path,
        params=params
    )
    
    return {
        "status": "pending",
        "message": "Model training started in the background. Check model list for completion status."
    }

@router.post("/train/tender-performance", response_model=TrainingResponse)
async def train_tender_performance_model(
    background_tasks: BackgroundTasks,
    data_file_id: str,
    params: Optional[TrainingParams] = None,
    model_service: ModelService = Depends(get_model_service)
):
    """Train a new tender performance prediction model.
    
    This is a long-running task that will be executed in the background.
    """
    from services.file_service import FileService
    
    file_service = FileService()
    data_path = file_service.get_file_path(data_file_id)
    
    if not data_path:
        raise HTTPException(status_code=404, detail=f"Data file with ID {data_file_id} not found")
    
    # Function to run training in the background
    def train_model_task(data_path: str, params: Dict = None):
        try:
            model_id = model_service.train_tender_performance_model(
                data_path=data_path,
                params=params.dict() if params else None
            )
            logger.info(f"Tender performance model training completed. Model ID: {model_id}")
        except Exception as e:
            logger.error(f"Error in background training task: {str(e)}")
    
    # Add the training task to background tasks
    background_tasks.add_task(
        train_model_task,
        data_path=data_path,
        params=params
    )
    
    return {
        "status": "pending",
        "message": "Tender performance model training started in the background. Check model list for completion status."
    }

@router.post("/predict/order-volume", response_model=OrderVolumePredictionResponse)
async def predict_order_volume(
    request: OrderVolumePredictionRequest,
    model_service: ModelService = Depends(get_model_service)
):
    """Generate predictions for future order volumes."""
    # Check if model exists
    if not model_service.get_model_metadata(request.model_id):
        raise HTTPException(status_code=404, detail=f"Model {request.model_id} not found")
    
    # Generate predictions
    result = model_service.predict_future_order_volumes(
        model_id=request.model_id,
        months=request.months
    )
    
    if not result:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate predictions with model {request.model_id}"
        )
    
    return result

@router.post("/predict/tender-performance", response_model=TenderPerformancePredictionResponse)
async def predict_tender_performance(
    request: TenderPerformancePredictionRequest,
    model_service: ModelService = Depends(get_model_service)
):
    """Generate predictions for tender performance."""
    # Check if model exists
    if not model_service.get_model_metadata(request.model_id):
        raise HTTPException(status_code=404, detail=f"Model {request.model_id} not found")
    
    # Check if input lists have the same length
    if len(request.carriers) != len(request.source_cities) or len(request.carriers) != len(request.dest_cities):
        raise HTTPException(
            status_code=400,
            detail="Input lists (carriers, source_cities, dest_cities) must have the same length"
        )
    
    # Generate predictions
    result = model_service.predict_tender_performance(
        model_id=request.model_id,
        carriers=request.carriers,
        source_cities=request.source_cities,
        dest_cities=request.dest_cities
    )
    
    if not result:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate predictions with model {request.model_id}"
        )
    
    return result 