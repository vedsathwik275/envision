# Order Release Location Consolidation - Implementation Plan

## Overview
Enhance the existing Data Tools API to provide consolidated location information for order releases. The feature will take an order release GID, fetch the order release data, extract source and destination location URLs, fetch detailed location information, and return consolidated location details.

## Current Architecture Analysis

### Existing Components
- **OrderReleaseService**: Already handles order release API calls
- **FastAPI Main App**: Has `/order-release/{order_release_gid}` endpoint
- **Pydantic Models**: Already defined for order release responses
- **Error Handling**: Established patterns for HTTP exceptions

### Current Flow
1. `/order-release/{order_release_gid}` → OrderReleaseService.get_order_release() → Raw order release JSON

## New Feature Requirements

### API Workflow
1. **Input**: Order Release GID (e.g., "BSL.313736")
2. **Step 1**: Call order release API to get order release data
3. **Step 2**: Extract canonical href URLs for source and destination locations
4. **Step 3**: Call location API twice to get detailed location information
5. **Step 4**: Consolidate and return structured location data

### Example Data Flow
```
Input: "BSL.313736"
↓
Order Release API Response: Contains sourceLocation and destinationLocation hrefs
↓
Extract URLs:
- Source: "https://...../locations/BSL.300000001357157-300000054405994"
- Destination: "https://...../locations/BSL.100000086293039"
↓
Location API Calls (2x): Get detailed location data
↓
Consolidated Response: Source and destination city, state, country
```

## Implementation Plan

### Phase 1: Enhance OrderReleaseService

#### 1.1 Add Location Extraction Method
```python
def extract_location_urls(self, order_release_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract canonical href URLs for source and destination locations."""
```

#### 1.2 Add Location Fetching Method
```python
def get_location_details(self, location_url: str) -> Dict[str, Any]:
    """Fetch detailed location information from canonical href URL."""
```

#### 1.3 Add Consolidated Location Method
```python
def get_order_release_locations(self, order_release_gid: str) -> Dict[str, Any]:
    """Get consolidated location information for an order release."""
```

### Phase 2: Add Pydantic Models

#### 2.1 Location Detail Model
```python
class LocationDetail(BaseModel):
    city: str
    province_code: str
    country_code: str
    postal_code: Optional[str]
    location_xid: str
    location_name: Optional[str]
```

#### 2.2 Consolidated Location Response Model
```python
class OrderReleaseLocationResponse(BaseModel):
    success: bool
    order_release_gid: str
    source_location: LocationDetail
    destination_location: LocationDetail
    lane_summary: Dict[str, str]  # Combined lane info
    error: Optional[str] = None
```

### Phase 3: Add API Endpoint

#### 3.1 New Endpoint
```python
@app.get(
    "/order-release/{order_release_gid}/locations",
    response_model=OrderReleaseLocationResponse,
    tags=["Order Release"],
    summary="Get Consolidated Location Details for Order Release"
)
async def get_order_release_locations(order_release_gid: str, service: OrderReleaseService = Depends(get_order_release_service)):
```

### Phase 4: Error Handling & Validation

#### 4.1 Error Scenarios
- Order release not found
- Invalid or missing location URLs
- Location API failures
- Network connectivity issues

#### 4.2 Validation
- Order release GID format validation
- URL extraction validation
- Response data validation

### Phase 5: Testing

#### 5.1 Unit Tests
- Test location URL extraction
- Test location detail fetching
- Test error handling scenarios

#### 5.2 Integration Tests
- End-to-end workflow testing
- API endpoint testing

## Technical Specifications

### URL Extraction Logic
```python
# From order release response:
source_url = order_release_data["sourceLocation"]["links"][1]["href"]  # canonical link
dest_url = order_release_data["destinationLocation"]["links"][1]["href"]  # canonical link
```

### Location API Call
```python
# Extract location GID from URL and call:
# GET https://otmgtm-test-ejhu.otmgtm.us-ashburn-1.ocs.oraclecloud.com:443/logisticsRestApi/resources-int/v2/locations/{location_gid}
```

### Response Mapping
```python
# Map location response fields:
location_detail = {
    "city": location_data["city"],
    "province_code": location_data["provinceCode"], 
    "country_code": location_data["countryCode3Gid"],
    "postal_code": location_data.get("postalCode"),
    "location_xid": location_data["locationXid"],
    "location_name": location_data.get("locationName")
}
```

## File Structure Changes

### Modified Files
- `order_release_service.py`: Add new methods
- `main.py`: Add new endpoint and Pydantic models
- `test_riq_apis.py`: Add tests for new functionality (optional)

### New Files (if needed)
- `test_order_release_locations.py`: Dedicated test file

## API Documentation Updates

### OpenAPI Schema
- New endpoint documentation
- Request/response examples
- Error response documentation

### Tags
- Use existing "Order Release" tag
- Add appropriate descriptions and examples

## Backward Compatibility
- All existing endpoints remain unchanged
- New endpoint is additive
- No breaking changes to existing functionality

## Security Considerations
- Use existing authentication mechanisms
- Validate all input parameters
- Sanitize URLs before making external calls
- Handle sensitive data appropriately

## Performance Considerations
- Implement proper error handling to avoid cascading failures
- Consider caching frequently accessed location data
- Set appropriate timeouts for external API calls
- Log performance metrics for monitoring

## Future Enhancements
- Batch processing for multiple order releases
- Caching layer for location data
- Rate limiting for external API calls
- Enhanced error reporting and logging