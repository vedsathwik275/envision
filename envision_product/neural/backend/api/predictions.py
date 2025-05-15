#!/usr/bin/env python3
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import os
import json
import pandas as pd
from datetime import datetime

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

@router.post("/tender-performance")
async def create_tender_performance_prediction(
    request: TenderPerformancePredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    Generate predictions for tender performance.
    
    This endpoint creates a new prediction using the specified model by
    predicting performance across all lanes and carriers in the training data.
    
    In the transportation industry, the prediction set is typically the same
    as the training data, with model-generated predictions compared against 
    actual historical performance.
    
    - **model_id**: The ID of the model to use for prediction
    """
    try:
        # Use the model service to generate predictions on the training data
        from services.model_service import ModelService
        model_service = ModelService()
        
        logger.info(f"Generating tender performance predictions using model {request.model_id}")
        result = model_service.predict_tender_performance_on_training_data(model_id=request.model_id)
        
        if not result:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate predictions with model {request.model_id}"
            )
        
        # Create a new prediction record using the prediction service
        prediction_id = prediction_service._generate_prediction_id()
        
        # Create directory for prediction data
        prediction_dir = prediction_service.base_path / prediction_id
        prediction_dir.mkdir(parents=True, exist_ok=True)
        
        # Save prediction data as JSON
        prediction_file = prediction_dir / "prediction_data.json"
        with open(prediction_file, "w") as f:
            json.dump(result, f, indent=2)
        
        # Generate complete CSV with all metrics
        try:
            from utils.file_converters import convert_tender_performance_training_predictions
            csv_file = convert_tender_performance_training_predictions(prediction_dir)
            logger.info(f"Generated complete CSV prediction file: {csv_file}")
        except Exception as e:
            logger.error(f"Error generating complete CSV file: {str(e)}")
            
        # Also generate simplified CSV with only essential fields
        try:
            from utils.file_converters import convert_tender_performance_simplified
            simplified_csv_file = convert_tender_performance_simplified(prediction_dir)
            logger.info(f"Generated simplified CSV prediction file: {simplified_csv_file}")
        except Exception as e:
            logger.error(f"Error generating simplified CSV file: {str(e)}")
        
        # Create metadata for the prediction
        metadata = {
            "prediction_id": prediction_id,
            "model_id": request.model_id,
            "model_type": "tender_performance",
            "created_at": datetime.now().isoformat(),
            "prediction_count": len(result.get("predictions", [])),
            "prediction_file": str(prediction_file)
        }
        
        # Save metadata
        prediction_service.metadata["predictions"][prediction_id] = metadata
        prediction_service._save_metadata()
        
        # Get full prediction details including ID
        prediction = {
            "prediction_id": prediction_id,
            "model_id": request.model_id,
            "model_type": "tender_performance",
            "created_at": metadata["created_at"],
            "prediction_count": metadata["prediction_count"],
            "metrics": result.get("metrics", {}),
            "data": result
        }
        
        return prediction
    except Exception as e:
        logger.error(f"Error generating tender performance predictions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating tender performance predictions: {str(e)}"
        )

@router.get("/tender-performance/{model_id}")
async def get_tender_performance_predictions(
    model_id: str,
    simplified: bool = True
):
    """
    Get predictions for tender performance.
    
    This endpoint returns predictions for the given model ID.
    In the transportation industry, the prediction set is typically the same
    as the training data, with model-generated predictions compared against 
    actual historical performance.
    
    - **model_id**: The ID of the model
    - **simplified**: Whether to return simplified predictions with only essential fields (defaults to True)
    """
    try:
        # Use the model service directly
        from services.model_service import ModelService
        model_service = ModelService()
        
        # Check if model exists
        model_metadata = model_service.get_model_metadata(model_id)
        if not model_metadata:
            raise HTTPException(
                status_code=404, 
                detail=f"Model {model_id} not found"
            )
        
        # Get or generate predictions
        logger.info(f"Fetching tender performance predictions for model {model_id}")
        result = model_service.predict_tender_performance_on_training_data(model_id=model_id)
        
        if not result:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to retrieve or generate predictions with model {model_id}"
            )
        
        # Get all predictions
        predictions = result.get("predictions", [])
        
        # Simplify predictions if requested
        if simplified:
            simplified_predictions = []
            for pred in predictions:
                simplified_pred = {
                    'carrier': pred.get('carrier', ''),
                    'source_city': pred.get('source_city', ''),
                    'dest_city': pred.get('dest_city', ''),
                    'predicted_performance': pred.get('predicted_performance', 0)
                }
                simplified_predictions.append(simplified_pred)
            
            # Replace full predictions with simplified ones
            predictions = simplified_predictions
        
        # Prepare the response
        return {
            "model_id": model_id,
            "prediction_count": len(predictions),
            "metrics": result.get("metrics", {}) if not simplified else {},
            "predictions": predictions[:100],  # Limit to first 100 for API response
            "note": "Only showing first 100 predictions in the API response. Full data available via download endpoint."
        }
    except Exception as e:
        logger.error(f"Error retrieving predictions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving predictions: {str(e)}"
        )

@router.get("/tender-performance/{model_id}/by-lane")
async def get_tender_performance_by_lane(
    model_id: str,
    source_city: str,
    dest_city: str,
    carrier: Optional[str] = None,
    simplified: bool = True
):
    """
    Get tender performance predictions for a specific lane.
    
    This endpoint filters predictions for a specific source-destination pair,
    with an optional carrier filter.
    
    - **model_id**: The ID of the model
    - **source_city**: The source city (required)
    - **destination_city**: The destination city (required)
    - **carrier**: Optional carrier filter
    - **simplified**: Whether to return simplified predictions with only essential fields (defaults to True)
    """
    try:
        # Check if model exists first
        from services.model_service import ModelService
        model_service = ModelService()
        
        model_metadata = model_service.get_model_metadata(model_id)
        if not model_metadata:
            raise HTTPException(
                status_code=404, 
                detail=f"Model {model_id} not found"
            )
        
        # Get existing or generate new predictions
        logger.info(f"Fetching tender performance predictions for model {model_id} and lane {source_city} to {dest_city}")
        result = model_service.predict_tender_performance_on_training_data(model_id=model_id)
        
        if not result:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to retrieve or generate predictions with model {model_id}"
            )
        
        # Filter predictions by lane
        predictions = result.get("predictions", [])
        filtered_predictions = []
        
        for pred in predictions:
            if (pred.get("source_city") == source_city and 
                pred.get("dest_city") == dest_city and
                (carrier is None or pred.get("carrier") == carrier)):
                filtered_predictions.append(pred)
        
        if not filtered_predictions:
            raise HTTPException(
                status_code=404,
                detail=f"No predictions found for lane {source_city} to {dest_city}"
                + (f" with carrier {carrier}" if carrier else "")
            )
        
        # Calculate lane-specific metrics
        lane_metrics = {}
        if filtered_predictions:
            # Calculate MAE and MAPE for this lane
            mae = sum(p.get('absolute_error', 0) for p in filtered_predictions) / len(filtered_predictions)
            mape = sum(p.get('percent_error', 0) for p in filtered_predictions) / len(filtered_predictions)
            lane_metrics = {
                "count": len(filtered_predictions),
                "mae": float(mae),
                "mape": float(mape)
            }
        
        # Simplify predictions if requested
        if simplified:
            simplified_predictions = []
            for pred in filtered_predictions:
                simplified_pred = {
                    'carrier': pred.get('carrier', ''),
                    'source_city': pred.get('source_city', ''),
                    'dest_city': pred.get('dest_city', ''),
                    'predicted_performance': pred.get('predicted_performance', 0)
                }
                simplified_predictions.append(simplified_pred)
            
            # Replace full predictions with simplified ones
            filtered_predictions = simplified_predictions
        
        return {
            "model_id": model_id,
            "lane": {
                "source_city": source_city,
                "dest_city": dest_city,
                "carrier": carrier
            },
            "prediction_count": len(filtered_predictions),
            "metrics": lane_metrics if not simplified else {},
            "predictions": filtered_predictions
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error retrieving predictions by lane: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving predictions by lane: {str(e)}"
        )

@router.get("/tender-performance/{model_id}/download")
async def download_tender_performance_predictions(
    model_id: str,
    format: str = "csv",
    simplified: bool = True,
    source_city: Optional[str] = None,
    dest_city: Optional[str] = None,
    carrier: Optional[str] = None
):
    """
    Download tender performance predictions.
    
    This endpoint provides download access to the full set of predictions.
    
    - **model_id**: The ID of the model
    - **format**: The format to download (csv or json, defaults to csv)
    - **simplified**: Whether to provide a simplified CSV with only essential fields (defaults to True)
    - **source_city**: Optional filter by source city
    - **dest_city**: Optional filter by destination city
    - **carrier**: Optional filter by carrier
    """
    try:
        # Get the model path
        from services.model_service import ModelService
        model_service = ModelService()
        
        model_path = model_service.get_model_path(model_id)
        if not model_path:
            raise HTTPException(
                status_code=404,
                detail=f"Model {model_id} not found"
            )
            
        # Check for the training predictions directory
        training_predictions_dir = os.path.join(model_path, "training_predictions")
        if not os.path.exists(training_predictions_dir):
            # Try to generate them if they don't exist
            result = model_service.predict_tender_performance_on_training_data(model_id=model_id)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Predictions not found for model {model_id} and could not be generated"
                )
        
        # Check for the specific format requested
        json_file = os.path.join(training_predictions_dir, "prediction_data.json")
        csv_file = os.path.join(training_predictions_dir, "prediction_data.csv")
        simplified_csv_file = os.path.join(training_predictions_dir, "prediction_data_simplified.csv")
        
        # Handle filtering if requested
        if source_city or dest_city or carrier:
            # Need to load, filter and re-save
            try:
                # Load the predictions
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                predictions = data.get('predictions', [])
                # Apply filters
                filtered_predictions = []
                for pred in predictions:
                    if ((not source_city or pred.get('source_city') == source_city) and
                        (not dest_city or pred.get('dest_city') == dest_city) and
                        (not carrier or pred.get('carrier') == carrier)):
                        filtered_predictions.append(pred)
                
                # Create filtered files
                filtered_json = {
                    "model_id": model_id,
                    "prediction_time": data.get("prediction_time", datetime.now().isoformat()),
                    "predictions": filtered_predictions,
                    "filter_applied": {
                        "source_city": source_city,
                        "dest_city": dest_city,
                        "carrier": carrier
                    }
                }
                
                # Save filtered JSON
                filtered_json_path = os.path.join(training_predictions_dir, "filtered_predictions.json")
                with open(filtered_json_path, 'w') as f:
                    json.dump(filtered_json, f, indent=2)
                
                # Save filtered CSV
                filtered_csv_path = os.path.join(training_predictions_dir, "filtered_predictions.csv")
                filtered_df = pd.DataFrame(filtered_predictions)
                filtered_df.to_csv(filtered_csv_path, index=False)
                
                # Also create simplified filtered CSV if needed
                if simplified and format.lower() == "csv":
                    simplified_filtered_csv_path = os.path.join(training_predictions_dir, "filtered_predictions_simplified.csv")
                    # Keep only the essential fields
                    simplified_data = []
                    for pred in filtered_predictions:
                        simplified_data.append({
                            'carrier': pred.get('carrier', ''),
                            'source_city': pred.get('source_city', ''),
                            'dest_city': pred.get('dest_city', ''),
                            'predicted_performance': pred.get('predicted_performance', 0)
                        })
                    simplified_df = pd.DataFrame(simplified_data)
                    simplified_df.to_csv(simplified_filtered_csv_path, index=False)
                    filtered_csv_path = simplified_filtered_csv_path
                
                # Update file paths to use filtered data
                json_file = filtered_json_path
                csv_file = filtered_csv_path
                
            except Exception as e:
                logger.error(f"Error filtering predictions: {str(e)}")
                # Continue with unfiltered data if filtering fails
                
        # For unfiltered CSV, generate the simplified version if needed
        if simplified and format.lower() == "csv" and not (source_city or dest_city or carrier):
            # Check if simplified file exists, if not generate it
            if not os.path.exists(simplified_csv_file):
                try:
                    from utils.file_converters import convert_tender_performance_simplified
                    simplified_csv_path = convert_tender_performance_simplified(training_predictions_dir)
                    if simplified_csv_path:
                        csv_file = str(simplified_csv_path)
                        logger.info(f"Generated simplified CSV file: {csv_file}")
                except Exception as e:
                    logger.error(f"Error generating simplified CSV: {str(e)}")
                    # Continue with regular CSV if simplified generation fails
            else:
                csv_file = simplified_csv_file
                logger.info(f"Using existing simplified CSV file: {csv_file}")
        
        if format.lower() == "json" and os.path.exists(json_file):
            filename = f"tender_performance_predictions_{model_id}.json"
            if source_city or dest_city or carrier:
                filename = f"tender_performance_predictions_{model_id}_filtered.json"
            
            return FileResponse(
                path=json_file,
                filename=filename,
                media_type="application/json"
            )
        elif format.lower() == "csv" and os.path.exists(csv_file):
            filename = f"tender_performance_predictions_{model_id}.csv"
            if source_city or dest_city or carrier:
                filename = f"tender_performance_predictions_{model_id}_filtered.csv"
            if simplified:
                filename = f"tender_performance_predictions_{model_id}_simplified.csv"
                if source_city or dest_city or carrier:
                    filename = f"tender_performance_predictions_{model_id}_filtered_simplified.csv"
                
            return FileResponse(
                path=csv_file,
                filename=filename,
                media_type="text/csv"
            )
        elif os.path.exists(json_file) and format.lower() == "csv":
            # Try to generate CSV if it doesn't exist but JSON does
            try:
                if simplified:
                    from utils.file_converters import convert_tender_performance_simplified
                    csv_path = convert_tender_performance_simplified(training_predictions_dir)
                else:
                    from utils.file_converters import convert_tender_performance_training_predictions
                    csv_path = convert_tender_performance_training_predictions(training_predictions_dir)
                
                if csv_path and os.path.exists(csv_path):
                    filename = f"tender_performance_predictions_{model_id}.csv"
                    if source_city or dest_city or carrier:
                        filename = f"tender_performance_predictions_{model_id}_filtered.csv"
                    if simplified:
                        filename = f"tender_performance_predictions_{model_id}_simplified.csv"
                        if source_city or dest_city or carrier:
                            filename = f"tender_performance_predictions_{model_id}_filtered_simplified.csv"
                    
                    return FileResponse(
                        path=str(csv_path),
                        filename=filename,
                        media_type="text/csv"
                    )
            except Exception as e:
                logger.error(f"Failed to generate CSV on demand: {str(e)}")
                
            # Fallback to JSON if CSV generation failed
            filename = f"tender_performance_predictions_{model_id}.json"
            if source_city or dest_city or carrier:
                filename = f"tender_performance_predictions_{model_id}_filtered.json"
                
            return FileResponse(
                path=json_file,
                filename=filename,
                media_type="application/json",
                headers={"X-File-Format-Fallback": "true"}
            )
        elif os.path.exists(csv_file) and format.lower() == "json":
            # Return CSV if JSON doesn't exist
            filename = f"tender_performance_predictions_{model_id}.csv"
            if source_city or dest_city or carrier:
                filename = f"tender_performance_predictions_{model_id}_filtered.csv"
            if simplified:
                filename = f"tender_performance_predictions_{model_id}_simplified.csv"
                if source_city or dest_city or carrier:
                    filename = f"tender_performance_predictions_{model_id}_filtered_simplified.csv"
                
            return FileResponse(
                path=csv_file,
                filename=filename,
                media_type="text/csv",
                headers={"X-File-Format-Fallback": "true"}
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No prediction files found for model {model_id}"
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error downloading predictions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading predictions: {str(e)}"
        )

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

@router.get("/order-volume/{model_id}", response_model=Dict[str, Any])
async def get_order_volume_predictions(
    model_id: str,
    source_city: Optional[str] = None,
    destination_city: Optional[str] = None,
    order_type: Optional[str] = None,
    month: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    Get order volume predictions for a specific model with optional filtering.
    
    - **model_id**: The ID of the model
    - **source_city**: Optional filter by source city
    - **destination_city**: Optional filter by destination city
    - **order_type**: Optional filter by order type (e.g., FTL, LTL)
    - **month**: Optional filter by month (format: YYYY-MM)
    - **limit**: Maximum number of predictions to return
    - **offset**: Number of predictions to skip
    """
    try:
        result = prediction_service.get_order_volume_predictions(
            model_id=model_id,
            source_city=source_city,
            destination_city=destination_city,
            order_type=order_type,
            month=month,
            limit=limit,
            offset=offset
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Order volume predictions not found for model {model_id}"
            )
            
        return result
    except Exception as e:
        logger.error(f"Error getting order volume predictions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting order volume predictions: {str(e)}"
        )

@router.get("/order-volume/{model_id}/by-lane", response_model=Dict[str, Any])
async def order_volume_by_lane(
    model_id: str, 
    source_city: str = Query(..., description="Source city name"),
    destination_city: str = Query(..., description="Destination city name"),
    order_type: Optional[str] = Query(None, description="Order type filter (optional)"),
    month: Optional[str] = Query(None, description="Month filter in YYYY-MM format (optional)")
):
    """Get order volume predictions for a specific lane.
    
    Returns order volume predictions filtered by source city, destination city, and optionally by order type and month.
    """
    try:
        # Import the lane utility here to avoid circular imports
        from utils.lane_utils import normalize_city_name
        
        # Validate required parameters
        if not source_city or not destination_city:
            logger.error(f"Missing required parameters: source_city={source_city}, destination_city={destination_city}")
            raise HTTPException(status_code=400, detail="Source city and destination city are required")
            
        # Log the lane request with normalized city names
        logger.info(f"Lane prediction request: {normalize_city_name(source_city)} to {normalize_city_name(destination_city)}")
        
        # Check if model exists and is of correct type
        prediction_service = PredictionService()
        models = prediction_service.model_service.list_models(model_type="order_volume")
        model_ids = [model["model_id"] for model in models]
        if model_id not in model_ids:
            logger.error(f"Model {model_id} not found or is not an order volume model")
            logger.debug(f"Available order volume models: {model_ids}")
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found or is not an order volume model")
            
        # Get predictions for the lane
        lane_predictions = prediction_service.get_order_volume_by_lane(
            model_id=model_id,
            source_city=source_city,
            destination_city=destination_city,
            order_type=order_type,
            month=month
        )
        
        # Handle case where no predictions are found
        if lane_predictions is None:
            logger.warning(f"No predictions found for lane {source_city} to {destination_city}")
            # Return empty result with 200 status instead of 404
            return {
                "model_id": model_id,
                "lane": {
                    "source_city": source_city,
                    "destination_city": destination_city
                },
                "predictions": [],
                "prediction_count": 0,
                "message": "No predictions found for this lane"
            }
            
        # Check if there was an error in the prediction service
        if lane_predictions.get("error") is True:
            logger.error(f"Error retrieving predictions: {lane_predictions.get('error_details', 'Unknown error')}")
            # Return the error details but with a 200 status code for API consistency
            return lane_predictions
            
        return lane_predictions
    except ImportError:
        # Fallback if lane utility is not available
        logger.warning("Lane utility not available, using original implementation")
        
        # Validate required parameters
        if not source_city or not destination_city:
            raise HTTPException(status_code=400, detail="Source city and destination city are required")
        
        # Get predictions for the lane
        prediction_service = PredictionService()
        lane_predictions = prediction_service.get_order_volume_by_lane(
            model_id=model_id,
            source_city=source_city,
            destination_city=destination_city,
            order_type=order_type,
            month=month
        )
        
        # Handle case where no predictions are found
        if lane_predictions is None:
            # Return empty result with 200 status instead of 404
            return {
                "model_id": model_id,
                "lane": {
                    "source_city": source_city,
                    "destination_city": destination_city
                },
                "predictions": [],
                "prediction_count": 0,
                "message": "No predictions found for this lane"
            }
            
        return lane_predictions
    except Exception as e:
        # Log the full error details for debugging
        logger.error(f"Unexpected error in order_volume_by_lane endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/order-volume/{model_id}/download")
async def download_order_volume_predictions(
    model_id: str,
    format: Optional[str] = "csv",
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    Download order volume predictions as CSV for a specific model.
    
    - **model_id**: The ID of the model
    - **format**: Format to download (csv or json, defaults to csv)
    """
    try:
        # Get the latest prediction for this model
        model_predictions = [p for p in prediction_service.list_predictions(model_id=model_id)
                           if p.get("model_type") == "order_volume"]
        
        if not model_predictions:
            raise HTTPException(
                status_code=404,
                detail=f"No order volume predictions found for model {model_id}"
            )
        
        # Sort by creation time (newest first)
        model_predictions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        latest_prediction = model_predictions[0]
        
        prediction_id = latest_prediction["prediction_id"]
        prediction_dir = prediction_service.base_path / prediction_id
        csv_file = prediction_dir / "prediction_data.csv"
        json_file = prediction_dir / "prediction_data.json"
        
        # Check if files exist
        has_json = json_file.exists()
        has_csv = csv_file.exists()
        
        # Try to generate CSV if it doesn't exist but JSON does
        if not has_csv and has_json and format.lower() == "csv":
            logger.info(f"CSV file not found for prediction {prediction_id}. Attempting to generate it.")
            try:
                from utils.file_converters import convert_order_volume_predictions
                csv_path = convert_order_volume_predictions(prediction_dir)
                has_csv = csv_path is not None and Path(csv_path).exists()
                if has_csv:
                    logger.info(f"Successfully generated CSV file on demand: {csv_path}")
            except Exception as e:
                logger.error(f"Failed to generate CSV on demand: {str(e)}")
                has_csv = False
        
        # Check if user explicitly requested JSON
        if format.lower() == "json" and has_json:
            return FileResponse(
                path=str(json_file),
                filename=f"order_volume_predictions_{model_id}.json",
                media_type="application/json"
            )
        
        # Return CSV if available
        if has_csv:
            return FileResponse(
                path=str(csv_file),
                filename=f"order_volume_predictions_{model_id}.csv",
                media_type="text/csv"
            )
        # Fallback to JSON if CSV not available
        elif has_json:
            logger.warning(f"CSV file not available for prediction {prediction_id}, serving JSON instead")
            return FileResponse(
                path=str(json_file),
                filename=f"order_volume_predictions_{model_id}.json",
                media_type="application/json",
                headers={"X-File-Format-Fallback": "true"}
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No prediction files found for model {model_id}"
            )
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error downloading order volume predictions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading order volume predictions: {str(e)}"
        ) 