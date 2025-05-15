# Envision Neural API Reference

## Overview

The Envision Neural API provides access to machine learning models for transportation logistics predictions, specifically focused on Order Volume forecasting and Tender Performance prediction. This API enables clients to train models, generate predictions, and access historical prediction data.

## Base URL

All API endpoints are relative to the base URL:
```
/api
```

## Response Format

All responses are in JSON format and follow a standard structure:
```json
{
  "success": true,
  "data": {
    // Response data specific to the endpoint
  }
}
```

For error responses:
```json
{
  "success": false,
  "error": {
    "code": 404,
    "message": "Resource not found"
  }
}
```

## API Endpoints

### 1. Model Management

#### 1.1 List All Models

Lists all available models with optional filtering.

**Endpoint:** `GET /models/list`

**Query Parameters:**
- `model_type` (optional): Filter by model type (e.g., "order_volume", "tender_performance")
- `min_created_at` (optional): Filter by minimum creation date (ISO format, e.g., "2025-05-01T00:00:00")
- `min_accuracy` (optional): Filter by minimum accuracy (0.0-1.0)
- `max_error` (optional): Filter by maximum error
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Response:**
```json
{
  "models": [
    {
      "model_id": "order_volume_20250512180020",
      "model_type": "order_volume",
      "created_at": "2025-05-12T18:00:20.355548",
      "description": "Order volume prediction model trained on dataset_xyz",
      "evaluation": {
        "mae": 0.152,
        "mse": 0.043,
        "r2": 0.876
      }
    },
    // More models...
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 45,
    "total_pages": 3
  }
}
```

**Example:**
```
GET /api/models/list?model_type=order_volume&min_accuracy=0.85
```

#### 1.2 Get Latest Model

Retrieves the latest model of a specified type with optional filtering.

**Endpoint:** `GET /models/latest`

**Query Parameters:**
- `model_type` (required): Model type to retrieve (e.g., "order_volume", "tender_performance")
- `min_created_at` (optional): Minimum creation date in ISO format
- `min_accuracy` (optional): Minimum accuracy threshold (0.0-1.0)
- `max_error` (optional): Maximum error threshold

**Response:**
```json
{
  "model_id": "order_volume_20250512180020",
  "model_type": "order_volume",
  "created_at": "2025-05-12T18:00:20.355548",
  "description": "Order volume prediction model trained on dataset_xyz",
  "evaluation": {
    "mae": 0.152,
    "mse": 0.043,
    "r2": 0.876
  },
  "training_data": "dataset_xyz.csv",
  "training_params": {
    "epochs": 100,
    "batch_size": 32,
    "validation_split": 0.2
  }
}
```

**Example:**
```
GET /api/models/latest?model_type=order_volume&min_accuracy=0.85
```

#### 1.3 Get Model Details

Gets detailed information about a specific model.

**Endpoint:** `GET /models/{model_id}`

**Path Parameters:**
- `model_id` (required): ID of the model to retrieve

**Response:**
```json
{
  "model_id": "order_volume_20250512180020",
  "model_type": "order_volume",
  "created_at": "2025-05-12T18:00:20.355548",
  "description": "Order volume prediction model trained on dataset_xyz",
  "evaluation": {
    "mae": 0.152,
    "mse": 0.043,
    "r2": 0.876
  },
  "training_data": "dataset_xyz.csv",
  "training_params": {
    "epochs": 100,
    "batch_size": 32,
    "validation_split": 0.2
  }
}
```

**Example:**
```
GET /api/models/order_volume_20250512180020
```

#### 1.4 Train New Model

Trains a new model using provided data and parameters.

**Endpoint:** `POST /models/train`

**Request Body:**
```json
{
  "model_type": "order_volume",
  "data_path": "datasets/order_data_2025.csv",
  "params": {
    "epochs": 100,
    "batch_size": 32,
    "validation_split": 0.2,
    "test_size": 0.2
  },
  "description": "Order volume model trained on 2025 data"
}
```

**Response:**
```json
{
  "model_id": "order_volume_20250518123045",
  "status": "success",
  "training_time": 145.32,
  "evaluation": {
    "mae": 0.152,
    "mse": 0.043,
    "r2": 0.876
  }
}
```

#### 1.5 Delete Model

Deletes a model and all its associated files.

**Endpoint:** `DELETE /models/{model_id}`

**Path Parameters:**
- `model_id` (required): ID of the model to delete

**Response:**
```json
{
  "status": "success",
  "message": "Model order_volume_20250512180020 deleted successfully"
}
```

**Example:**
```
DELETE /api/models/order_volume_20250512180020
```

### 2. Order Volume Predictions

#### 2.1 Get Order Volume Predictions

Retrieves order volume predictions for a specified model with optional filtering.

**Endpoint:** `GET /predictions/order-volume/{model_id}`

**Path Parameters:**
- `model_id` (required): ID of the model

**Query Parameters:**
- `source_city` (optional): Filter by source city
- `destination_city` (optional): Filter by destination city
- `order_type` (optional): Filter by order type (e.g., "FTL", "LTL")
- `month` (optional): Filter by month (format: YYYY-MM)
- `limit` (optional): Maximum number of predictions to return (default: 1000)
- `offset` (optional): Number of predictions to skip (default: 0)

**Response:**
```json
{
  "model_id": "order_volume_20250512180020",
  "prediction_id": "pred_a70084a3_20250512",
  "created_at": "2025-05-12T18:07:12.088224",
  "total_predictions": 3250,
  "filtered_predictions": 250,
  "returned_predictions": 100,
  "has_csv_export": true,
  "csv_path": "data/predictions/pred_a70084a3_20250512/prediction_data.csv",
  "json_path": "data/predictions/pred_a70084a3_20250512/prediction_data.json",
  "predictions": [
    {
      "source_city": "ELWOOD",
      "destination_city": "ABINGDON",
      "carrier": "RBTW",
      "order_type": "FTL",
      "month": "2025-06",
      "predicted_volume": 42.5
    },
    // More predictions...
  ]
}
```

**Example:**
```
GET /api/predictions/order-volume/order_volume_20250512180020?source_city=ELWOOD&destination_city=ABINGDON
```

#### 2.2 Get Order Volume Predictions by Lane

Retrieves order volume predictions for a specific lane.

**Endpoint:** `GET /predictions/order-volume/{model_id}/by-lane`

**Path Parameters:**
- `model_id` (required): ID of the model

**Query Parameters:**
- `source_city` (required): Source city name
- `destination_city` (required): Destination city name
- `order_type` (optional): Order type filter
- `month` (optional): Month filter in YYYY-MM format

**Response:**
```json
{
  "model_id": "order_volume_20250512180020",
  "lane": {
    "source_city": "ELWOOD",
    "destination_city": "ABINGDON"
  },
  "predictions": [
    {
      "source_city": "ELWOOD",
      "destination_city": "ABINGDON",
      "carrier": "RBTW",
      "order_type": "FTL",
      "month": "2025-06",
      "predicted_volume": 42.5
    },
    // More predictions...
  ],
  "prediction_count": 12
}
```

**Example:**
```
GET /api/predictions/order-volume/order_volume_20250512180020/by-lane?source_city=ELWOOD&destination_city=ABINGDON
```

#### 2.3 Download Order Volume Predictions

Downloads order volume predictions in the specified format.

**Endpoint:** `GET /predictions/order-volume/{model_id}/download`

**Path Parameters:**
- `model_id` (required): ID of the model

**Query Parameters:**
- `format` (optional): Format to download (csv or json, default: csv)

**Response:**
File download (CSV or JSON)

**Example:**
```
GET /api/predictions/order-volume/order_volume_20250512180020/download?format=csv
```

#### 2.4 Create New Order Volume Predictions

Generates new order volume predictions using a specified model.

**Endpoint:** `POST /predictions/order-volume`

**Request Body:**
```json
{
  "model_id": "order_volume_20250512180020",
  "months": 6
}
```

**Response:**
```json
{
  "prediction_id": "pred_b80195c4_20250518",
  "model_id": "order_volume_20250512180020",
  "prediction_time": "2025-05-18T14:23:15.432876",
  "months_predicted": 6,
  "prediction_count": 3250,
  "data": {
    // Full prediction data
  }
}
```

### 3. Tender Performance Predictions

#### 3.1 Get Tender Performance Predictions

Retrieves tender performance predictions for a specified model.

**Endpoint:** `GET /predictions/tender-performance/{model_id}`

**Path Parameters:**
- `model_id` (required): ID of the model

**Query Parameters:**
- `simplified` (optional): Whether to return simplified predictions with only essential fields (default: true)

**Response:**
```json
{
  "model_id": "tender_performance_20250515080638",
  "prediction_count": 520,
  "metrics": {
    "mae": 0.063,
    "mape": 0.078
  },
  "predictions": [
    {
      "carrier": "RBTW",
      "source_city": "ELWOOD",
      "dest_city": "VILLA RICA",
      "predicted_performance": 92.11
    },
    // More predictions (limited to first 100)...
  ],
  "note": "Only showing first 100 predictions in the API response. Full data available via download endpoint."
}
```

**Example:**
```
GET /api/predictions/tender-performance/tender_performance_20250515080638?simplified=true
```

#### 3.2 Get Tender Performance Predictions by Lane

Retrieves tender performance predictions for a specific lane.

**Endpoint:** `GET /predictions/tender-performance/{model_id}/by-lane`

**Path Parameters:**
- `model_id` (required): ID of the model

**Query Parameters:**
- `source_city` (required): Source city name
- `dest_city` (required): Destination city name
- `carrier` (optional): Carrier filter
- `simplified` (optional): Whether to return simplified predictions (default: true)

**Response:**
```json
{
  "model_id": "tender_performance_20250515080638",
  "lane": {
    "source_city": "ELWOOD",
    "dest_city": "REDLANDS",
    "carrier": null
  },
  "prediction_count": 3,
  "metrics": {
    "count": 3,
    "mae": 0.058,
    "mape": 0.062
  },
  "predictions": [
    {
      "carrier": "RBTW",
      "source_city": "ELWOOD",
      "dest_city": "REDLANDS",
      "predicted_performance": 94.17
    },
    // More predictions...
  ]
}
```

**Example:**
```
GET /api/predictions/tender-performance/tender_performance_20250515080638/by-lane?source_city=ELWOOD&dest_city=REDLANDS
```

#### 3.3 Download Tender Performance Predictions

Downloads tender performance predictions in the specified format.

**Endpoint:** `GET /predictions/tender-performance/{model_id}/download`

**Path Parameters:**
- `model_id` (required): ID of the model

**Query Parameters:**
- `format` (optional): Format to download (csv or json, default: csv)
- `simplified` (optional): Whether to provide a simplified CSV with only essential fields (default: true)
- `source_city` (optional): Filter by source city
- `dest_city` (optional): Filter by destination city
- `carrier` (optional): Filter by carrier

**Response:**
File download (CSV or JSON)

**Example:**
```
GET /api/predictions/tender-performance/tender_performance_20250515080638/download?format=csv&simplified=true
```

#### 3.4 Create New Tender Performance Predictions

Generates new tender performance predictions on training data.

**Endpoint:** `POST /predictions/tender-performance`

**Request Body:**
```json
{
  "model_id": "tender_performance_20250515080638"
}
```

**Response:**
```json
{
  "prediction_id": "pred_c70195d5_20250518",
  "model_id": "tender_performance_20250515080638",
  "model_type": "tender_performance",
  "created_at": "2025-05-18T14:28:12.432876",
  "prediction_count": 520,
  "metrics": {
    "mae": 0.063,
    "mape": 0.078
  }
}
```

### 4. Prediction Management

#### 4.1 List All Predictions

Lists all available predictions with optional filtering by model ID.

**Endpoint:** `GET /predictions/`

**Query Parameters:**
- `model_id` (optional): Filter by model ID

**Response:**
```json
{
  "predictions": [
    {
      "prediction_id": "pred_a70084a3_20250512",
      "model_id": "order_volume_20250512180020",
      "model_type": "order_volume",
      "created_at": "2025-05-12T18:07:12.088224",
      "months_predicted": 6,
      "prediction_count": 3250
    },
    // More predictions...
  ]
}
```

**Example:**
```
GET /api/predictions?model_id=order_volume_20250512180020
```

#### 4.2 Get Prediction Details

Gets detailed information about a specific prediction.

**Endpoint:** `GET /predictions/{prediction_id}`

**Path Parameters:**
- `prediction_id` (required): ID of the prediction to retrieve

**Response:**
```json
{
  "prediction_id": "pred_a70084a3_20250512",
  "model_id": "order_volume_20250512180020",
  "model_type": "order_volume",
  "created_at": "2025-05-12T18:07:12.088224",
  "months_predicted": 6,
  "prediction_count": 3250,
  "data": {
    // Full prediction data
  }
}
```

**Example:**
```
GET /api/predictions/pred_a70084a3_20250512
```

#### 4.3 Delete Prediction

Deletes a prediction and all its associated files.

**Endpoint:** `DELETE /predictions/{prediction_id}`

**Path Parameters:**
- `prediction_id` (required): ID of the prediction to delete

**Response:**
```json
{
  "status": "success",
  "message": "Prediction pred_a70084a3_20250512 deleted successfully"
}
```

**Example:**
```
DELETE /api/predictions/pred_a70084a3_20250512
```

### 5. Advanced Features

#### 5.1 Filter Predictions by Multiple Criteria

Filters predictions using complex criteria.

**Endpoint:** `POST /predictions/{model_id}/filter`

**Path Parameters:**
- `model_id` (required): ID of the model

**Request Body:**
```json
{
  "source_cities": ["ELWOOD", "RICHMOND"],
  "destination_cities": ["ABINGDON", "REDLANDS"],
  "order_types": ["FTL"],
  "carriers": ["RBTW"],
  "date_range": {
    "start": "2025-06-01",
    "end": "2025-08-31"
  }
}
```

**Response:**
```json
{
  "model_id": "order_volume_20250512180020",
  "prediction_id": "pred_a70084a3_20250512",
  "created_at": "2025-05-12T18:07:12.088224",
  "model_type": "order_volume",
  "total_predictions": 3250,
  "filtered_count": 24,
  "predictions": [
    // Filtered predictions...
  ]
}
```

**Example:**
```
POST /api/predictions/order_volume_20250512180020/filter
```

## Lane Handling Utility

The API leverages a Lane Handling Utility for consistent city name processing and lane matching.

### Key Features:

- Case-insensitive matching for city names
- Standardized field naming conventions
- Flexible field name variations (SOURCE CITY, source_city, etc.)
- Advanced lane filtering capabilities

### Field Name Standardization:

The API normalizes various field name conventions:

| Standard Field | Variations |
|----------------|------------|
| source_city    | SOURCE CITY, SOURCE, src, SRC, source, origin, ORIGIN |
| destination_city | DESTINATION CITY, DESTINATION, dest, DEST, dst, DST, destination |
| carrier        | CARRIER, carrier_name, CARRIER_NAME |
| order_type     | ORDER TYPE, type, TYPE, shipment_type, SHIPMENT_TYPE |

## Error Codes

| Status Code | Description                           |
|-------------|---------------------------------------|
| 400         | Bad Request - Invalid parameters      |
| 401         | Unauthorized - Authentication failed  |
| 404         | Not Found - Resource does not exist   |
| 500         | Server Error - Internal error         |

## Rate Limiting

API requests are limited to 100 requests per minute per API key. Exceeding this limit will result in a 429 Too Many Requests response.

## Changelog

For a detailed history of API changes and updates, please refer to the [Changelog](changelog.md).