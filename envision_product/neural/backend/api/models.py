#!/usr/bin/env python3
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import logging


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

class PredictionRequest(BaseModel):
    model_id: str
    months: int = Field(6, description="Number of months to predict")

class PredictionResponse(BaseModel):
    model_id: str
    prediction_time: str
    months_predicted: int
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

@router.post("/predict/order-volume", response_model=PredictionResponse)
async def predict_order_volume(
    request: PredictionRequest,
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