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
from .order_release_service import OrderReleaseService
from dotenv import load_dotenv

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
base_url = os.getenv("BASE_URL")
auth_token = os.getenv("AUTH_TOKEN")

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

# New RIQ REST and XML Models
class LaneRequest(BaseModel):
    """Request model for lane-based location queries."""
    source_city: str = Field(..., description="Source city name")
    source_state: str = Field(..., description="Source state/province code")
    source_country: str = Field("US", description="Source country code")
    dest_city: str = Field(..., description="Destination city name")
    dest_state: str = Field(..., description="Destination state/province code")
    dest_country: str = Field("US", description="Destination country code")

class LocationResponse(BaseModel):
    """Response model for location ID queries."""
    success: bool = Field(..., description="Whether the request was successful")
    locations: Optional[Dict[str, str]] = Field(None, description="Location IDs (source_location_id, dest_location_id)")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Raw response from Oracle API")
    error: Optional[str] = Field(None, description="Error message if any")

class RIQXMLRequest(BaseModel):
    """Request model for XML-based RIQ queries."""
    source_location_id: str = Field(..., description="Source location XID")
    dest_location_id: str = Field(..., description="Destination location XID")
    weight: float = Field(..., description="Weight value in pounds")
    volume: float = Field(0, description="Volume value in cubic feet")
    transport_modes: List[str] = Field(["LTL", "TL"], description="Transport modes to query")

class RIQResult(BaseModel):
    """Individual RIQ result from XML response."""
    service_provider: Optional[str] = Field(None, description="Service provider code")
    transport_mode: Optional[str] = Field(None, description="Transport mode")
    cost: Optional[float] = Field(None, description="Cost amount")
    currency: Optional[str] = Field(None, description="Currency code")
    distance: Optional[float] = Field(None, description="Distance value")
    distance_unit: Optional[str] = Field(None, description="Distance unit")
    is_optimal: Optional[bool] = Field(None, description="Whether this is an optimal result")
    transit_time_hours: Optional[float] = Field(None, description="Transit time in hours")
    transit_time_unit: Optional[str] = Field(None, description="Transit time unit")

class RIQXMLResponse(BaseModel):
    """Response model for XML-based RIQ queries."""
    success: bool = Field(..., description="Whether the request was successful")
    results: List[RIQResult] = Field([], description="List of RIQ results")
    total_results: int = Field(0, description="Total number of results")
    raw_xml_request: Optional[str] = Field(None, description="Raw XML request sent")
    raw_xml_response: Optional[str] = Field(None, description="Raw XML response received")
    error: Optional[str] = Field(None, description="Error message if any")

# Order Release Models
class OrderReleaseResponse(BaseModel):
    """Response model for order release queries."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Order release data")
    error: Optional[str] = Field(None, description="Error message if any")
    order_release_gid: Optional[str] = Field(None, description="The order release GID that was queried")

class LocationDetail(BaseModel):
    """Detailed location information."""
    city: str = Field(..., description="City name")
    province_code: str = Field(..., description="Province/state code")
    country_code: str = Field(..., description="Country code")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP code")
    location_xid: str = Field(..., description="Location XID")
    location_name: Optional[str] = Field(None, description="Location name")

class LaneSummary(BaseModel):
    """Lane summary information."""
    route: str = Field(..., description="Route description (City, State to City, State)")
    origin: str = Field(..., description="Origin city and state")
    destination: str = Field(..., description="Destination city and state")

class OrderReleaseLocationResponse(BaseModel):
    """Response model for order release location consolidation."""
    success: bool = Field(..., description="Whether the request was successful")
    order_release_gid: str = Field(..., description="The order release GID queried")
    source_location: Optional[LocationDetail] = Field(None, description="Source location details")
    destination_location: Optional[LocationDetail] = Field(None, description="Destination location details")
    lane_summary: Optional[LaneSummary] = Field(None, description="Lane summary information")
    error: Optional[str] = Field(None, description="Error message if any")

class UnplannedOrdersRequest(BaseModel):
    """Request model for querying unplanned orders by lane."""
    origin_city: str = Field(..., description="Origin city for the lane")
    origin_state: str = Field(..., description="Origin state for the lane")
    origin_country: str = Field("US", description="Origin country for the lane")
    destination_city: str = Field(..., description="Destination city for the lane")
    destination_state: str = Field(..., description="Destination state for the lane")
    destination_country: str = Field("US", description="Destination country for the lane")

class UnplannedOrdersResponse(BaseModel):
    """Response model for unplanned orders queries."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Unplanned orders data")
    error: Optional[str] = Field(None, description="Error message if any")
    lane_info: Optional[Dict[str, str]] = Field(None, description="Lane information that was queried")

# Configuration
def get_riq_client() -> RIQClient:
    """Get RIQ client instance with configuration."""
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

def get_order_release_service() -> OrderReleaseService:
    """FastAPI dependency to get an instance of OrderReleaseService."""
    try:
        if not base_url or not auth_token:
            logger.error("BASE_URL or AUTH_TOKEN environment variables are not set.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Order Release service configuration is missing."
            )
        return OrderReleaseService(base_url, auth_token)
    except Exception as e:
        logger.error(f"Failed to initialize OrderReleaseService: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Order Release service could not be initialized."
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

# New RIQ REST and XML Routes
@app.post(
    "/new-riq-rest",
    response_model=LocationResponse,
    tags=["RIQ Location"],
    summary="Get Location IDs for Lane",
    description="Retrieves location IDs from Oracle's REST API for a given transportation lane.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Locations Not Found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)
async def get_location_ids(
    request: LaneRequest,
    client: RIQClient = Depends(get_riq_client)
) -> LocationResponse:
    """
    Query Oracle's REST API to get location IDs for a given lane.
    
    This endpoint accepts lane parameters (source and destination city, state, country)
    and returns the location XIDs needed for subsequent RIQ XML API calls.
    
    Args:
        request: LaneRequest containing source and destination location details
        client: RIQ client instance
        
    Returns:
        LocationResponse containing location IDs or error information
    """
    try:
        logger.info(f"Received location ID query request: {request.model_dump_json(indent=2)}")
        
        # Call the RIQ client to get location IDs
        result = client.get_location_ids(
            request.source_city,
            request.source_state,
            request.source_country,
            request.dest_city,
            request.dest_state,
            request.dest_country
        )
        
        # Check if there was an error in the service response
        if "error" in result:
            error_msg = result["error"]
            logger.error(f"Location query error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error querying locations: {error_msg}"
            )
        
        # Check if locations were found
        locations = result.get("locations", {})
        if not locations.get("source_location_id") or not locations.get("dest_location_id"):
            logger.warning(f"Incomplete location data found for lane: {request.source_city}, {request.source_state} -> {request.dest_city}, {request.dest_state}")
            missing = []
            if not locations.get("source_location_id"):
                missing.append(f"source ({request.source_city}, {request.source_state})")
            if not locations.get("dest_location_id"):
                missing.append(f"destination ({request.dest_city}, {request.dest_state})")
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find location IDs for: {', '.join(missing)}"
            )
        
        logger.info(f"Successfully retrieved location IDs for lane: {request.source_city}, {request.source_state} -> {request.dest_city}, {request.dest_state}")
        return LocationResponse(
            success=True,
            locations=locations,
            raw_response=result.get("raw_response")
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing location ID query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while querying location IDs: {str(e)}"
        )

@app.post(
    "/riq-xml",
    response_model=RIQXMLResponse,
    tags=["RIQ XML"],
    summary="Get RIQ Quote via XML API",
    description="Gets comprehensive rate quotes using Oracle's XML-based RIQ API with location IDs.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "No Results Found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)
async def get_riq_xml_quote(
    request: RIQXMLRequest,
    client: RIQClient = Depends(get_riq_client)
) -> RIQXMLResponse:
    """
    Get comprehensive rate quotes using Oracle's XML-based RIQ API.
    
    This endpoint accepts location IDs (obtained from /new-riq-rest or provided directly)
    along with shipment parameters to get detailed rate information including all carriers,
    costs, distances, and transit times.
    
    Args:
        request: RIQXMLRequest containing location IDs and shipment parameters
        client: RIQ client instance
        
    Returns:
        RIQXMLResponse containing comprehensive rate information or error
    """
    try:
        logger.info(f"Received RIQ XML query request: {request.model_dump_json(indent=2)}")
        
        # Call the RIQ client to get XML quote
        result = client.get_riq_xml_quote(
            request.source_location_id,
            request.dest_location_id,
            request.weight,
            request.volume,
            request.transport_modes
        )
        
        # Check if there was an error in the service response
        if "error" in result:
            error_msg = result["error"]
            logger.error(f"RIQ XML query error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error executing RIQ XML query: {error_msg}"
            )
        
        # Convert results to Pydantic models
        riq_results = []
        for raw_result in result.get("results", []):
            riq_result = RIQResult(**raw_result)
            riq_results.append(riq_result)
        
        logger.info(f"Successfully processed RIQ XML query, found {len(riq_results)} results")
        return RIQXMLResponse(
            success=True,
            results=riq_results,
            total_results=result.get("total_results", len(riq_results)),
            raw_xml_request=result.get("raw_xml_request"),
            raw_xml_response=result.get("raw_xml_response")
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing RIQ XML query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while executing RIQ XML query: {str(e)}"
        )

# Order Release Routes
@app.get(
    "/order-release/{order_release_gid}",
    response_model=OrderReleaseResponse,
    tags=["Order Release"],
    summary="Get Order Release by GID",
    description="Fetches order release data from Oracle Transportation Management by order release GID.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Order Release Not Found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)
async def get_order_release(
    order_release_gid: str,
    service: OrderReleaseService = Depends(get_order_release_service)
) -> OrderReleaseResponse:
    """
    Fetch order release data by order release GID.
    
    Args:
        order_release_gid: The order release GID to fetch
        service: OrderReleaseService instance
        
    Returns:
        OrderReleaseResponse containing order release data or error information
    """
    try:
        logger.info(f"Received order release query for GID: {order_release_gid}")
        
        # Call the service to get order release data
        result = service.get_order_release(order_release_gid)
        
        # Check if there was an error in the service response
        if "error" in result:
            error_msg = result["error"]
            status_code = result.get("status_code", 500)
            
            if status_code == 404:
                logger.warning(f"Order release not found for GID: {order_release_gid}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order release with GID '{order_release_gid}' not found"
                )
            else:
                logger.error(f"Order release service error for GID {order_release_gid}: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error fetching order release: {error_msg}"
                )
        
        logger.info(f"Successfully retrieved order release for GID: {order_release_gid}")
        return OrderReleaseResponse(
            success=True,
            data=result,
            order_release_gid=order_release_gid
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing order release query for GID {order_release_gid}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching order release: {str(e)}"
        )

@app.get(
    "/order-release/{order_release_gid}/locations",
    response_model=OrderReleaseLocationResponse,
    tags=["Order Release"],
    summary="Get Consolidated Location Details for Order Release",
    description="Fetches order release data and returns consolidated source and destination location information including city, state, and country details.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Order Release Not Found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)
async def get_order_release_locations(
    order_release_gid: str,
    service: OrderReleaseService = Depends(get_order_release_service)
) -> OrderReleaseLocationResponse:
    """
    Get consolidated location information for an order release.
    
    This endpoint fetches the order release data, extracts location URLs,
    fetches detailed location information for both source and destination,
    and returns consolidated location details.
    
    Args:
        order_release_gid: The order release GID to fetch locations for
        service: OrderReleaseService instance
        
    Returns:
        OrderReleaseLocationResponse containing consolidated location information
    """
    try:
        logger.info(f"Received order release locations query for GID: {order_release_gid}")
        
        # Call the service to get consolidated location information
        result = service.get_order_release_locations(order_release_gid)
        
        # Check if the service call was successful
        if not result.get("success", False):
            error_msg = result.get("error", "Unknown error occurred")
            
            if "Order release not found" in error_msg or "404" in error_msg:
                logger.warning(f"Order release not found for locations query GID: {order_release_gid}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order release with GID '{order_release_gid}' not found"
                )
            else:
                logger.error(f"Order release locations service error for GID {order_release_gid}: {error_msg}")
                # Return partial success response for other errors (e.g., location API failures)
                return OrderReleaseLocationResponse(
                    success=False,
                    order_release_gid=order_release_gid,
                    source_location=None,
                    destination_location=None,
                    lane_summary=None,
                    error=error_msg
                )
        
        # Build LocationDetail objects from the raw location data
        source_location_detail = None
        dest_location_detail = None
        
        if result.get("source_location"):
            source_data = result["source_location"]
            source_location_detail = LocationDetail(
                city=source_data.get("city", ""),
                province_code=source_data.get("provinceCode", ""),
                country_code=source_data.get("countryCode3Gid", ""),
                postal_code=source_data.get("postalCode"),
                location_xid=source_data.get("locationXid", ""),
                location_name=source_data.get("locationName")
            )
        
        if result.get("destination_location"):
            dest_data = result["destination_location"]
            dest_location_detail = LocationDetail(
                city=dest_data.get("city", ""),
                province_code=dest_data.get("provinceCode", ""),
                country_code=dest_data.get("countryCode3Gid", ""),
                postal_code=dest_data.get("postalCode"),
                location_xid=dest_data.get("locationXid", ""),
                location_name=dest_data.get("locationName")
            )
        
        # Build LaneSummary object if available
        lane_summary_detail = None
        if result.get("lane_summary"):
            lane_data = result["lane_summary"]
            lane_summary_detail = LaneSummary(
                route=lane_data.get("route", ""),
                origin=lane_data.get("origin", ""),
                destination=lane_data.get("destination", "")
            )
        
        logger.info(f"Successfully retrieved consolidated locations for GID: {order_release_gid}")
        return OrderReleaseLocationResponse(
            success=result.get("success", False),
            order_release_gid=order_release_gid,
            source_location=source_location_detail,
            destination_location=dest_location_detail,
            lane_summary=lane_summary_detail,
            error=result.get("error")
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing order release locations query for GID {order_release_gid}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching order release locations: {str(e)}"
        )

@app.post(
    "/order-release/unplanned-orders",
    response_model=UnplannedOrdersResponse,
    tags=["Order Release"],
    summary="Get Unplanned Orders by Lane",
    description="Fetches unplanned orders from Oracle Transportation Management by lane parameters (origin/destination city, state, country).",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "No Unplanned Orders Found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)
async def get_unplanned_orders(
    request: UnplannedOrdersRequest,
    service: OrderReleaseService = Depends(get_order_release_service)
) -> UnplannedOrdersResponse:
    """
    Fetch unplanned orders by lane parameters.
    
    Args:
        request: UnplannedOrdersRequest containing origin and destination lane information
        service: OrderReleaseService instance
        
    Returns:
        UnplannedOrdersResponse containing unplanned orders data or error information
    """
    try:
        logger.info(f"Received unplanned orders query for lane: {request.origin_city}, {request.origin_state} -> {request.destination_city}, {request.destination_state}")
        
        # Call the service to get unplanned orders data
        result = service.get_unplanned_orders(
            request.origin_city,
            request.origin_state, 
            request.origin_country,
            request.destination_city,
            request.destination_state,
            request.destination_country
        )
        
        # Check if there was an error in the service response
        if "error" in result:
            error_msg = result["error"]
            status_code = result.get("status_code", 500)
            
            if status_code == 404:
                logger.warning(f"No unplanned orders found for lane: {request.origin_city}, {request.origin_state} -> {request.destination_city}, {request.destination_state}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No unplanned orders found for the specified lane"
                )
            else:
                logger.error(f"Unplanned orders service error for lane: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error fetching unplanned orders: {error_msg}"
                )
        
        lane_info = {
            "origin_city": request.origin_city,
            "origin_state": request.origin_state,
            "origin_country": request.origin_country,
            "destination_city": request.destination_city,
            "destination_state": request.destination_state,
            "destination_country": request.destination_country
        }
        
        logger.info(f"Successfully retrieved unplanned orders for lane: {request.origin_city}, {request.origin_state} -> {request.destination_city}, {request.destination_state}")
        return UnplannedOrdersResponse(
            success=True,
            data=result,
            lane_info=lane_info
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing unplanned orders query for lane: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching unplanned orders: {str(e)}"
        )

@app.get(
    "/order-release/health",
    tags=["Order Release", "Health"],
    summary="Health Check for Order Release Service",
    description="Checks if the order release service is operational and properly configured."
)
async def order_release_health(service: OrderReleaseService = Depends(get_order_release_service)):
    """
    Health check endpoint for the order release service.
    Relies on the `get_order_release_service` dependency to check basic service availability.
    """
    # The Depends(get_order_release_service) already performs a check
    # If it passes, the service is considered healthy enough to respond.
    return {
        "status": "ok", 
        "message": "Order Release Service is operational.",
        "base_url": service.base_url,
        "endpoint": service.endpoint
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 