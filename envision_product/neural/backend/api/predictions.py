#!/usr/bin/env python3
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/predictions",
    tags=["predictions"],
    responses={404: {"description": "Not found"}},
)

prediction_service = PredictionService()

class OrderVolumePredictionRequest(BaseModel):
    model_id: str
    months: int = Field(6, ge=1, le=24, description="Number of months to predict (1-24)")

class TenderPerformancePredictionRequest(BaseModel):
    model_id: str
    carriers: List[str] = Field(..., description="List of carriers")
    source_cities: List[str] = Field(..., description="List of source cities")
    dest_cities: List[str] = Field(..., description="List of destination cities")

class PredictionMetadata(BaseModel):
    prediction_id: str
    model_id: str
    model_type: str
    created_at: str
    months_predicted: Optional[int] = None
    prediction_count: int

class PredictionList(BaseModel):
    predictions: List[PredictionMetadata]

class PredictionDetail(BaseModel):
    prediction_id: str
    model_id: str
    model_type: str
    created_at: str
    months_predicted: Optional[int] = None
    prediction_count: int
    data: Dict[str, Any]

class FilterRequest(BaseModel):
    source_cities: Optional[List[str]] = None
    destination_cities: Optional[List[str]] = None
    order_types: Optional[List[str]] = None
    carriers: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None

def get_prediction_service():
    return PredictionService()

@router.get("/", response_model=PredictionList)
async def list_predictions(
    model_id: Optional[str] = None,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """List all predictions with optional filtering by model ID."""
    predictions = prediction_service.list_predictions(model_id=model_id)
    return {"predictions": predictions}

@router.get("/{prediction_id}", response_model=PredictionDetail)
async def get_prediction(
    prediction_id: str,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Get details for a specific prediction."""
    prediction = prediction_service.get_prediction(prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail=f"Prediction {prediction_id} not found")
    
    return prediction

@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: str,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Delete a prediction."""
    if not prediction_service.delete_prediction(prediction_id):
        raise HTTPException(status_code=404, detail=f"Prediction {prediction_id} not found or could not be deleted")
    
    return {"status": "success", "message": f"Prediction {prediction_id} deleted successfully"}

@router.post("/order-volume", response_model=PredictionDetail)
async def create_order_volume_prediction(
    request: OrderVolumePredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Generate predictions for future order volumes."""
    result = prediction_service.predict_order_volume(
        model_id=request.model_id,
        months=request.months
    )
    
    if not result:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate predictions with model {request.model_id}"
        )
    
    # Get full prediction details including ID
    prediction_id = result.get("prediction_id")
    prediction = prediction_service.get_prediction(prediction_id)
    
    if not prediction:
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction was created but could not be retrieved: {prediction_id}"
        )
    
    return prediction

@router.post("/tender-performance", response_model=PredictionDetail)
async def create_tender_performance_prediction(
    request: TenderPerformancePredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Generate predictions for tender performance."""
    # Check if input lists have the same length
    if len(request.carriers) != len(request.source_cities) or len(request.carriers) != len(request.dest_cities):
        raise HTTPException(
            status_code=400,
            detail="Input lists (carriers, source_cities, dest_cities) must have the same length"
        )
    
    result = prediction_service.predict_tender_performance(
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
    
    # Get full prediction details including ID
    prediction_id = result.get("prediction_id")
    prediction = prediction_service.get_prediction(prediction_id)
    
    if not prediction:
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction was created but could not be retrieved: {prediction_id}"
        )
    
    return prediction

@router.get("/{model_id}")
async def get_predictions(
    model_id: str,
    source_city: Optional[str] = None,
    destination_city: Optional[str] = None,
    order_type: Optional[str] = None,
    carrier: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0
):
    """
    Get predictions for a specific model.
    Optional filtering parameters can be provided.
    """
    try:
        filters = {}
        if source_city:
            filters["source_city"] = source_city
        if destination_city:
            filters["destination_city"] = destination_city
        if order_type:
            filters["order_type"] = order_type
        if carrier:
            filters["carrier"] = carrier
            
        predictions = prediction_service.get_predictions(
            model_id=model_id,
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        if predictions is None:
            raise HTTPException(status_code=404, detail="Predictions not found for this model")
            
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting predictions: {str(e)}")

@router.post("/{model_id}/generate")
async def generate_predictions(
    model_id: str,
    request: OrderVolumePredictionRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate new predictions for a model.
    This will use the trained model to predict future values.
    """
    try:
        job_id = prediction_service.initialize_prediction_job(
            model_id=model_id,
            months=request.months or 6,
            params=request.dict()
        )
        
        background_tasks.add_task(
            prediction_service.run_prediction_job,
            job_id=job_id
        )
        
        return {
            "status": "prediction_started",
            "job_id": job_id,
            "model_id": model_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")

@router.get("/{model_id}/export")
async def export_predictions(
    model_id: str,
    format: str = "csv",
    source_city: Optional[str] = None,
    destination_city: Optional[str] = None,
    order_type: Optional[str] = None,
    carrier: Optional[str] = None
):
    """
    Export predictions to a file.
    Supported formats: csv, excel
    """
    try:
        filters = {}
        if source_city:
            filters["source_city"] = source_city
        if destination_city:
            filters["destination_city"] = destination_city
        if order_type:
            filters["order_type"] = order_type
        if carrier:
            filters["carrier"] = carrier
            
        # Additional logic for export will be implemented in the prediction service
        return {"status": "not_implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting predictions: {str(e)}")

@router.post("/{model_id}/filter")
async def filter_predictions(
    model_id: str, 
    filter_request: FilterRequest
):
    """
    Filter predictions by multiple criteria.
    """
    try:
        filters = {}
        
        if filter_request.source_cities:
            filters["source_cities"] = filter_request.source_cities
        
        if filter_request.destination_cities:
            filters["destination_cities"] = filter_request.destination_cities
        
        if filter_request.order_types:
            filters["order_types"] = filter_request.order_types
            
        if filter_request.carriers:
            filters["carriers"] = filter_request.carriers
        
        if filter_request.date_range:
            filters["date_range"] = filter_request.date_range
        
        # Call prediction service with filters
        filtered_predictions = prediction_service.filter_predictions(
            model_id=model_id,
            filters=filters
        )
        
        if filtered_predictions is None:
            raise HTTPException(status_code=404, detail="No predictions found for this model with the given filters")
        
        return filtered_predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering predictions: {str(e)}") 