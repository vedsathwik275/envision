from fastapi import APIRouter, Depends, HTTPException, status
import logging

from ..services.spot_rate_service import SpotRateService
from ..models import SpotRateRequest, SpotRateMatrixResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/spot-rate", 
    tags=["Spot Rate"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Not Found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)

# Dependency to get the service instance
def get_spot_rate_service():
    """FastAPI dependency to get an instance of SpotRateService."""
    try:
        service = SpotRateService()
        if service.df is None or service.df.empty:
            logger.error("SpotRateService failed to load data. CSV might be missing or empty.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Spot rate service is not available due to a data loading issue."
            )
        return service
    except Exception as e:
        logger.error(f"Failed to initialize SpotRateService: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Spot rate service could not be initialized."
        )

@router.post(
    "/matrix", 
    response_model=SpotRateMatrixResponse,
    summary="Query Spot Rate Matrix",
    description="Retrieves a 7-day spot rate matrix for carriers on a specified lane starting from the shipment date."
)
async def query_spot_rate_matrix(
    request: SpotRateRequest,
    service: SpotRateService = Depends(get_spot_rate_service)
) -> SpotRateMatrixResponse:
    """
    Endpoint to query spot rate matrix data.
    
    Accepts a `SpotRateRequest` with parameters like source/destination city, state, country,
    transport mode, and shipment date.
    
    Returns a `SpotRateMatrixResponse` containing carriers with their 7-day rate projections,
    date range, lane information, and the original query parameters.
    """
    try:
        logger.info(f"Received spot rate matrix query request: {request.model_dump_json(indent=2)}")
        response = await service.query_spot_rate_matrix(request)
        
        if not response.spot_costs:
            logger.info(f"No carriers found for spot rate query: {request.model_dump_json()}")
            # Return empty response rather than error for consistency with frontend expectations
        else:
            logger.info(f"Found {len(response.spot_costs)} carriers for spot rate query")
        
        return response
    except ValueError as e:
        # Handle specific business logic errors (e.g., no carriers found)
        logger.warning(f"Business logic error in spot rate query: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTPExceptions directly (e.g., from dependency)
        raise
    except Exception as e:
        logger.error(f"Error processing spot rate matrix query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while querying spot rate matrix: {str(e)}"
        )

@router.get(
    "/health",
    tags=["Health"],
    summary="Health Check for Spot Rate Service",
    description="Checks if the spot rate service is operational and the data file is loaded."
)
async def spot_rate_health(service: SpotRateService = Depends(get_spot_rate_service)):
    """
    Health check endpoint for the spot rate service.
    Relies on the `get_spot_rate_service` dependency to check basic service availability.
    """
    # The Depends(get_spot_rate_service) already performs a check
    # If it passes, the service is considered healthy enough to respond.
    return {
        "status": "ok", 
        "message": "Spot Rate Service is operational.", 
        "data_records_loaded": len(service.df) if service.df is not None else 0
    } 