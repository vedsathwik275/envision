"""
Data Tools API for managing transportation rate quotes, spot rates, and historical data.

This FastAPI application consolidates:
- RIQ (Rate, Inventory, Quote) functionality 
- Spot rate matrix analysis
- Historical transportation data queries
"""
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from .riq import RIQClient
from .spot_rate_service import SpotRateService
from .historical_data_service import HistoricalDataService

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Tools API",
    description="Consolidated API for transportation data tools including RIQ rate quotes, spot rate analysis, and historical data queries",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import models and services for spot rate and historical data
# We'll add these after we copy the files

# Pydantic models for request/response (RIQ functionality)
class LocationModel(BaseModel):
    """Location model for RIQ requests."""
    city: str = Field(..., description="City name")
    province_code: str = Field(..., description="State/Province code")
    postal_code: str = Field(default="00000", description="Postal/ZIP code")
    country_code: str = Field(default="US", description="Country code")

class ItemModel(BaseModel):
    """Item model for RIQ requests."""
    weight_value: float = Field(..., description="Weight value")
    weight_unit: str = Field(default="LB", description="Weight unit")
    volume_value: float = Field(default=0, description="Volume value")
    volume_unit: str = Field(default="CUFT", description="Volume unit")
    declared_value: float = Field(default=0, description="Declared value")
    currency: str = Field(default="USD", description="Currency code")
    package_count: int = Field(default=1, description="Number of packages")
    packaged_item_gid: str = Field(default="DEFAULT", description="Packaged item GID")

class RateRequestModel(BaseModel):
    """Complete rate request model."""
    source_location: LocationModel = Field(..., description="Source location")
    destination_location: LocationModel = Field(..., description="Destination location")
    items: List[ItemModel] = Field(..., description="List of items to ship")
    servprov_gid: str = Field(default="BSL.RYGB", description="Service provider GID")
    request_type: str = Field(default="AllOptions", description="Request type")
    perspective: str = Field(default="B", description="Perspective")
    max_primary_options: str = Field(default="99", description="Maximum primary options")
    primary_option_definition: str = Field(default="BY_ITINERARY", description="Primary option definition")

class SimpleRateRequestModel(BaseModel):
    """Simplified rate request model without servprov_gid."""
    source_location: LocationModel = Field(..., description="Source location")
    destination_location: LocationModel = Field(..., description="Destination location")
    items: List[ItemModel] = Field(..., description="List of items to ship")
    request_type: str = Field(default="AllOptions", description="Request type")
    perspective: str = Field(default="B", description="Perspective")
    max_primary_options: str = Field(default="99", description="Maximum primary options")
    primary_option_definition: str = Field(default="BY_ITINERARY", description="Primary option definition")

class RateResponseModel(BaseModel):
    """Rate response model."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")

# Spot Rate Models (migrated from RAG API)
class SpotRateRequest(BaseModel):
    """Request model for querying spot rate matrix data."""
    source_city: Optional[str] = Field(None, description="Source city for the lane.")
    source_state: Optional[str] = Field(None, description="Source state for the lane.")
    source_country: Optional[str] = Field("US", description="Source country for the lane.")
    dest_city: Optional[str] = Field(None, description="Destination city for the lane.")
    dest_state: Optional[str] = Field(None, description="Destination state for the lane.")
    dest_country: Optional[str] = Field("US", description="Destination country for the lane.")
    shipment_date: str = Field(..., description="Base shipment date in YYYY-MM-DD format for 7-day projection.")

class CostDetail(BaseModel):
    """Represents cost details for a specific shipment date."""
    ship_date: str = Field(..., description="Shipment date in MM/DD/YYYY format.")
    total_spot_cost: str = Field(..., description="Total spot cost as string.")
    cost_currency: str = Field("USD", description="Currency code.")
    line_haul: str = Field(..., description="Line haul cost as string.")
    fuel: str = Field("0", description="Fuel cost as string.")
    quote_id: str = Field("AUTO_GENERATED", description="Quote identifier.")
    transport_mode: str = Field(..., description="Transport mode (e.g., TL, LTL).")

class CarrierSpotCost(BaseModel):
    """Represents spot costs for a single carrier across multiple dates."""
    carrier: str = Field(..., description="Carrier code/name.")
    cost_details: List[CostDetail] = Field(..., description="List of cost details for each shipment date.")

class SpotRateMatrixResponse(BaseModel):
    """Response model for spot rate matrix queries."""
    origin_city: str = Field(..., description="Origin city name.")
    origin_state: str = Field(..., description="Origin state code.")
    destination_city: str = Field(..., description="Destination city name.")
    destination_state: str = Field(..., description="Destination state code.")
    shipment_date: str = Field(..., description="Base shipment date in MM/DD/YYYY format.")
    spot_costs: List[CarrierSpotCost] = Field(..., description="List of carriers with their cost details.")
    query_parameters: SpotRateRequest = Field(..., description="The parameters used for this query.")

# Historical Data Models (migrated from RAG API)
class HistoricalDataRequest(BaseModel):
    """Request model for querying historical transportation data."""
    source_city: Optional[str] = Field(None, description="Source city for the lane.")
    source_state: Optional[str] = Field(None, description="Source state for the lane.")
    source_country: Optional[str] = Field("US", description="Source country for the lane.")
    dest_city: Optional[str] = Field(None, description="Destination city for the lane.")
    dest_state: Optional[str] = Field(None, description="Destination state for the lane.")
    dest_country: Optional[str] = Field("US", description="Destination country for the lane.")
    transport_mode: Optional[str] = Field(None, description="Transport mode (e.g., LTL, TL).")
    limit: int = Field(50, description="Maximum number of records to return.", ge=1, le=1000)

class HistoricalRecord(BaseModel):
    """Represents a single historical transportation record."""
    source_city: str
    source_state: str
    source_country: str
    dest_city: str
    dest_state: str
    dest_country: str
    transport_mode: str = Field(..., alias="TMODE")
    cost_per_lb: Optional[float] = Field(None, alias="COST_PER_LB")
    cost_per_mile: Optional[float] = Field(None, alias="COST_PER_MILE")
    cost_per_cuft: Optional[float] = Field(None, alias="COST_PER_CUFT")
    shipment_count: Optional[int] = Field(None, alias="SHP_COUNT")
    mode_preference: Optional[str] = Field(None, alias="MODE_PREFERENCE")

    class Config:
        populate_by_name = True # Allows using alias for field names

class HistoricalDataResponse(BaseModel):
    """Response model for historical data queries."""
    records: List[HistoricalRecord] = Field(..., description="List of matching historical records.")
    total_count: int = Field(..., description="Total number of matching records found (before limit).")
    lane_summary: Dict[str, Any] = Field(..., description="Summary statistics for the queried lane.")
    cost_statistics: Dict[str, Optional[float]] = Field(..., description="Overall cost statistics for the queried lane.")
    query_parameters: HistoricalDataRequest = Field(..., description="The parameters used for this query.")

# General Error Response Model
class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="The type of error that occurred.")
    message: str = Field(..., description="A human-readable message describing the error.")
    details: Optional[Any] = Field(None, description="Optional details about the error, can be a dict or list.")

# Configuration
def get_riq_client() -> RIQClient:
    """Get RIQ client instance with configuration."""
    base_url = os.getenv("RIQ_BASE_URL", "otmgtm-test-ejhu.otmgtm.us-ashburn-1.ocs.oraclecloud.com")
    auth_token = os.getenv("RIQ_AUTH_TOKEN", "QlNMLkNIUl9JTlRFR1JBVElPTjpyNWgzRDFiQ21WMWxmUmQ4cUBpNHpnNiZJ")
    return RIQClient(base_url, auth_token)

# Dependency functions for new services
def get_spot_rate_service() -> SpotRateService:
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

def get_historical_data_service() -> HistoricalDataService:
    """FastAPI dependency to get an instance of HistoricalDataService."""
    try:
        service = HistoricalDataService()
        if service.df is None or service.df.empty:
            logger.error("HistoricalDataService failed to load data. CSV might be missing or empty.")
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

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "Data Tools API is running"}

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

# RIQ Rate Quote Routes
@app.post("/rate-quote", response_model=RateResponseModel, tags=["RIQ Rate Quotes"])
async def get_rate_quote(request: RateRequestModel, client: RIQClient = Depends(get_riq_client)) -> RateResponseModel:
    """
    Get rate quote for shipment.
    
    Args:
        request: Complete rate request with source, destination, and items
        client: RIQ client instance
        
    Returns:
        Rate response with quote data or error
    """
    try:
        # Convert Pydantic models to dictionaries
        source_dict = client.create_location(
            request.source_location.city,
            request.source_location.province_code,
            request.source_location.postal_code,
            request.source_location.country_code
        )
        
        destination_dict = client.create_location(
            request.destination_location.city,
            request.destination_location.province_code,
            request.destination_location.postal_code,
            request.destination_location.country_code
        )
        
        items_list = []
        for item in request.items:
            item_dict = client.create_item(
                item.weight_value,
                item.weight_unit,
                item.volume_value,
                item.volume_unit,
                item.declared_value,
                item.currency,
                item.package_count,
                item.packaged_item_gid
            )
            items_list.append(item_dict)
        
        # Create request payload
        request_payload = client.create_rate_request(
            source_dict,
            destination_dict,
            items_list,
            request.servprov_gid,
            request.request_type,
            request.perspective,
            request.max_primary_options,
            request.primary_option_definition
        )
        
        # Get rate quote
        result = client.get_rate_quote(request_payload)
        
        if "error" in result:
            return RateResponseModel(success=False, error=result["error"])
        
        return RateResponseModel(success=True, data=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/cheap-rate-quote", response_model=RateResponseModel, tags=["RIQ Rate Quotes"])
async def get_cheap_rate_quote(request: SimpleRateRequestModel, client: RIQClient = Depends(get_riq_client)) -> RateResponseModel:
    """
    Get rate quote for shipment with simplified request (no servprov_gid required).
    Returns rates from all service providers to find the cheapest option.
    
    Args:
        request: Simplified rate request with source, destination, and items
        client: RIQ client instance
        
    Returns:
        Rate response with quote data from all service providers or error
    """
    try:
        # Convert Pydantic models to dictionaries
        source_dict = client.create_location(
            request.source_location.city,
            request.source_location.province_code,
            request.source_location.postal_code,
            request.source_location.country_code
        )
        
        destination_dict = client.create_location(
            request.destination_location.city,
            request.destination_location.province_code,
            request.destination_location.postal_code,
            request.destination_location.country_code
        )
        
        items_list = []
        for item in request.items:
            item_dict = client.create_item(
                item.weight_value,
                item.weight_unit,
                item.volume_value,
                item.volume_unit,
                item.declared_value,
                item.currency,
                item.package_count,
                item.packaged_item_gid
            )
            items_list.append(item_dict)
        
        # Create request payload WITHOUT service provider GID to get all providers
        request_payload = client.create_rate_request(
            source_dict,
            destination_dict,
            items_list,
            None,  # No service provider GID - gets rates from all providers
            request.request_type,
            request.perspective,
            request.max_primary_options,
            request.primary_option_definition
        )
        
        # Get rate quote
        result = client.get_rate_quote(request_payload)
        
        if "error" in result:
            return RateResponseModel(success=False, error=result["error"])
        
        return RateResponseModel(success=True, data=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/quick-quote", tags=["RIQ Rate Quotes"])
async def get_quick_quote(
    source_city: str,
    source_state: str,
    source_zip: str,
    dest_city: str,
    dest_state: str,
    dest_zip: str,
    weight: float,
    volume: float = 0,
    client: RIQClient = Depends(get_riq_client)
) -> RateResponseModel:
    """
    Get a quick rate quote with minimal parameters.
    
    Args:
        source_city: Source city
        source_state: Source state/province code
        source_zip: Source postal code
        dest_city: Destination city
        dest_state: Destination state/province code  
        dest_zip: Destination postal code
        weight: Weight in pounds
        volume: Volume in cubic feet (optional)
        client: RIQ client instance
        
    Returns:
        Rate response with quote data or error
    """
    try:
        # Create locations
        source = client.create_location(source_city, source_state, source_zip)
        destination = client.create_location(dest_city, dest_state, dest_zip)
        
        # Create items
        items = [client.create_item(weight_value=weight, volume_value=volume)]
        
        # Create request
        request_payload = client.create_rate_request(source, destination, items)
        
        # Get rate quote
        result = client.get_rate_quote(request_payload)
        
        if "error" in result:
            return RateResponseModel(success=False, error=result["error"])
        
        return RateResponseModel(success=True, data=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Spot Rate Routes (migrated from RAG API)
@app.post(
    "/spot-rate/matrix", 
    response_model=SpotRateMatrixResponse,
    tags=["Spot Rate"],
    summary="Query Spot Rate Matrix",
    description="Retrieves a 7-day spot rate matrix for carriers on a specified lane starting from the shipment date.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Not Found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
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

@app.get(
    "/spot-rate/health",
    tags=["Spot Rate", "Health"],
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

# Historical Data Routes (migrated from RAG API)
@app.post(
    "/historical-data/query", 
    response_model=HistoricalDataResponse,
    tags=["Historical Data"],
    summary="Query Historical Transportation Data",
    description="Retrieves historical transportation records based on specified lane and other criteria.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Not Found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
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

@app.get(
    "/historical-data/health",
    tags=["Historical Data", "Health"],
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 