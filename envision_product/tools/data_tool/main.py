from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from .riq import RIQClient

app = FastAPI(
    title="RIQ Rate API",
    description="Oracle Transportation Management RIQ (Rate, Inventory, Quote) API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
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

# Configuration
def get_riq_client() -> RIQClient:
    """Get RIQ client instance with configuration."""
    base_url = os.getenv("RIQ_BASE_URL", "otmgtm-test-ejhu.otmgtm.us-ashburn-1.ocs.oraclecloud.com")
    auth_token = os.getenv("RIQ_AUTH_TOKEN", "QlNMLkNIUl9JTlRFR1JBVElPTjpyNWgzRDFiQ21WMWxmUmQ4cUBpNHpnNiZJ")
    return RIQClient(base_url, auth_token)

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "RIQ Rate API is running"}

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/rate-quote", response_model=RateResponseModel)
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

@app.post("/cheap-rate-quote", response_model=RateResponseModel)
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

@app.post("/quick-quote")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 