# RIQ Rate API

A FastAPI application that provides REST endpoints for Oracle Transportation Management RIQ (Rate, Inventory, Quote) functionality.

## Features

- **Full Rate Quote**: Complete rate request with detailed location and item information
- **Quick Quote**: Simplified endpoint for basic rate quotes with minimal parameters
- **Environment Configuration**: Configurable via environment variables
- **Comprehensive Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Error Handling**: Proper error responses and validation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (optional):
```bash
export RIQ_BASE_URL="your-otm-base-url"
export RIQ_AUTH_TOKEN="your-auth-token"
```

## Running the API

### Development
```bash
python main.py
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- **GET** `/health` - Health check endpoint
- **GET** `/` - Root endpoint

### Rate Quotes

#### Full Rate Quote
- **POST** `/rate-quote`

Complete rate request with detailed parameters.

**Request Body:**
```json
{
  "source_location": {
    "city": "LANCASTER",
    "province_code": "TX",
    "postal_code": "75134",
    "country_code": "US"
  },
  "destination_location": {
    "city": "OWASSO",
    "province_code": "OK",
    "postal_code": "74055",
    "country_code": "US"
  },
  "items": [
    {
      "weight_value": 2400,
      "weight_unit": "LB",
      "volume_value": 150,
      "volume_unit": "CUFT",
      "declared_value": 0,
      "currency": "USD",
      "package_count": 1,
      "packaged_item_gid": "DEFAULT"
    }
  ],
  "servprov_gid": "BSL.RYGB",
  "request_type": "AllOptions",
  "perspective": "B",
  "max_primary_options": "99",
  "primary_option_definition": "BY_ITINERARY"
}
```

#### Quick Quote
- **POST** `/quick-quote`

Simplified rate request with query parameters.

**Query Parameters:**
- `source_city` (string): Source city name
- `source_state` (string): Source state/province code
- `source_zip` (string): Source postal code
- `dest_city` (string): Destination city name
- `dest_state` (string): Destination state/province code
- `dest_zip` (string): Destination postal code
- `weight` (float): Weight in pounds
- `volume` (float, optional): Volume in cubic feet

**Example:**
```bash
curl -X POST "http://localhost:8000/quick-quote?source_city=LANCASTER&source_state=TX&source_zip=75134&dest_city=OWASSO&dest_state=OK&dest_zip=74055&weight=2400&volume=150"
```

## Response Format

All endpoints return a standardized response:

```json
{
  "success": true,
  "data": {
    // RIQ API response data
  },
  "error": null
}
```

Error response:
```json
{
  "success": false,
  "data": null,
  "error": "Error message"
}
```

## Configuration

The API uses the following environment variables:

- `RIQ_BASE_URL`: Base URL for the RIQ API (default: "otmgtm-test-ejhu.otmgtm.us-ashburn-1.ocs.oraclecloud.com")
- `RIQ_AUTH_TOKEN`: Authentication token for API access (default: hardcoded test token)

## Example Usage

### Python with requests
```python
import requests

# Quick quote
response = requests.post(
    "http://localhost:8000/quick-quote",
    params={
        "source_city": "LANCASTER",
        "source_state": "TX",
        "source_zip": "75134",
        "dest_city": "OWASSO",
        "dest_state": "OK",
        "dest_zip": "74055",
        "weight": 2400,
        "volume": 150
    }
)

result = response.json()
print(f"Success: {result['success']}")
if result['success']:
    print(f"Rate data: {result['data']}")
else:
    print(f"Error: {result['error']}")
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/quick-quote?' + new URLSearchParams({
    source_city: 'LANCASTER',
    source_state: 'TX',
    source_zip: '75134',
    dest_city: 'OWASSO',
    dest_state: 'OK',
    dest_zip: '74055',
    weight: 2400,
    volume: 150
}), {
    method: 'POST'
});

const result = await response.json();
console.log('Success:', result.success);
if (result.success) {
    console.log('Rate data:', result.data);
} else {
    console.log('Error:', result.error);
}
```

## Project Structure

```
envision_product/tools/data_tool/
├── __init__.py          # Package initialization
├── main.py              # FastAPI application
├── riq.py              # RIQ client implementation
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server implementation
- **Pydantic**: Data validation and parsing using Python type hints
- **python-multipart**: For handling form data

## Error Handling

The API includes comprehensive error handling:

- **Validation Errors**: Automatic validation of request data using Pydantic models
- **HTTP Exceptions**: Proper HTTP status codes for different error conditions
- **RIQ API Errors**: Forwarded errors from the underlying RIQ service
- **Internal Errors**: Graceful handling of unexpected errors

## Security Considerations

- Authentication tokens are handled securely
- CORS is enabled for cross-origin requests (configure as needed for production)
- Input validation prevents injection attacks
- Error messages don't expose sensitive information 