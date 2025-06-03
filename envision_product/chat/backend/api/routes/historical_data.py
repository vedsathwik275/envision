from fastapi import APIRouter, Depends, HTTPException, status
import logging

from ..services.historical_data_service import HistoricalDataService
from ..models import HistoricalDataRequest, HistoricalDataResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/historical-data", 
    tags=["Historical Data"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Not Found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)

# Dependency to get the service instance
# This allows FastAPI to manage the lifecycle of the service if needed (e.g., as a singleton)
# For now, it will create a new instance per request unless HistoricalDataService is implemented as a singleton elsewhere.
def get_historical_data_service():
    """FastAPI dependency to get an instance of HistoricalDataService."""
    # If the service had complex dependencies or needed to be a true singleton across the app,
    # you might initialize it in main.py lifespan and store it in app.state,
    # then retrieve it here from app.state.
    # For this service, creating an instance per request is acceptable as it primarily loads a static file.
    try:
        service = HistoricalDataService()
        if service.df is None or service.df.empty:
            logger.error("HistoricalDataService failed to load data. CSV might be missing or empty.")
            # This situation should ideally be caught during startup, but as a safeguard:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Historical data service is not available due to a data loading issue."
            )
        return service
    except Exception as e:
        logger.error(f"Failed to initialize HistoricalDataService: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Historical data service could not be initialized."
        )

@router.post(
    "/query", 
    response_model=HistoricalDataResponse,
    summary="Query Historical Transportation Data",
    description="Retrieves historical transportation records based on specified lane and other criteria."
)
async def query_historical_data(
    request: HistoricalDataRequest,
    service: HistoricalDataService = Depends(get_historical_data_service)
) -> HistoricalDataResponse:
    """
    Endpoint to query historical transportation data.
    
    Accepts a `HistoricalDataRequest` with parameters like source/destination city, state, country,
    transport mode, and a limit for the number of records.
    
    Returns a `HistoricalDataResponse` containing matching records, summary statistics,
    and the original query parameters.
    """
    try:
        logger.info(f"Received historical data query request: {request.model_dump_json(indent=2)}")
        response = await service.query_historical_data(request)
        if not response.records and response.total_count == 0:
            logger.info(f"No historical records found for query: {request.model_dump_json()}")
            # It's not an error if no records are found, frontend will handle empty display.
            # If a specific "not found" for the *lane* is desired, the service would need to indicate that.
        return response
    except HTTPException: # Re-raise HTTPExceptions directly (e.g., from dependency)
        raise
    except Exception as e:
        logger.error(f"Error processing historical data query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while querying historical data: {str(e)}"
        )

@router.get(
    "/health",
    tags=["Health"],
    summary="Health Check for Historical Data Service",
    description="Checks if the historical data service is operational and the data file is loaded."
)
async def historical_data_health(service: HistoricalDataService = Depends(get_historical_data_service)):
    """
    Health check endpoint for the historical data service.
    Relies on the `get_historical_data_service` dependency to check basic service availability.
    """
    # The Depends(get_historical_data_service) already performs a check
    # If it passes, the service is considered healthy enough to respond.
    return {"status": "ok", "message": "Historical Data Service is operational.", "data_records_loaded": len(service.df) if service.df is not None else 0}
