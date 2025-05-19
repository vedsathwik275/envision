# Envision Neural API Reference

## Overview

The Envision Neural API provides access to machine learning models for transportation logistics predictions, specifically focused on Order Volume forecasting, Tender Performance prediction, and Carrier Performance prediction. This API enables clients to train models, generate predictions, and access historical prediction data.

This reference documents the streamlined API that focuses on essential functionality for model training and prediction workflows. The API has been optimized to support core use cases while removing redundant and rarely used endpoints.

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

### 1. File Management

#### 1.1 Upload File

Uploads a new file to the system.

**Endpoint:** `POST /files/upload`

**Request:**
- Form data with a file field

**Response:**
```json
{
  "status": "success",
  "file_id": "f1e8c34a-5c2b-4b5a-b8c9-7d8e9f0a1b2c",
  "filename": "order_data_2025.csv",
  "content_type": "text/csv"
}
```

### 2. Data Processing

#### 2.1 Upload CSV File

Uploads a CSV file specifically for neural network training.

**Endpoint:** `POST /data/upload`

**Request:**
- Form data with a file field (must be a CSV file)

**Response:**
```json
{
  "status": "success",
  "file_id": "d7c6b5a4-3f2e-1d0c-9b8a-7c6d5e4f3a2b",
  "filename": "training_data.csv",
  "timestamp": "2025-05-12T18:00:20.355548"
}
```

#### 2.2 Get Data Preview

Retrieves a preview of the uploaded data file.

**Endpoint:** `GET /data/preview/{file_id}`

**Path Parameters:**
- `file_id` (required): ID of the uploaded file

**Response:**
```json
{
  "file_id": "d7c6b5a4-3f2e-1d0c-9b8a-7c6d5e4f3a2b",
  "total_rows": 1500,
  "total_columns": 8,
  "sample_rows": [
    {
      "source_city": "ELWOOD",
      "destination_city": "ABINGDON",
      "carrier": "RBTW",
      "order_type": "FTL",
      "month": "2025-01",
      "volume": 35
    },
    // More sample rows...
  ],
  "column_info": {
    "source_city": {
      "type": "string",
      "unique_values": 45,
      "missing_values": 0
    },
    // More column info...
  },
  "missing_data_summary": {
    "total_missing": 12,
    "percent_missing": 0.1
  }
}
```

### 3. Model Management

#### 3.1 List All Models

Lists all available models with optional filtering.

**Endpoint:** `GET /models`

**Query Parameters:**
- `model_type` (optional): Filter by model type (e.g., "order_volume", "tender_performance", "carrier_performance")
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
GET /api/models?model_type=order_volume&min_accuracy=0.85
```

#### 3.2 Get Latest Model

Retrieves the latest model of a specified type with optional filtering.

**Endpoint:** `GET /models/latest`

**Query Parameters:**
- `model_type` (required): Model type to retrieve (e.g., "order_volume", "tender_performance", "carrier_performance")
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

#### 3.3 Get Model Details

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

#### 3.4 Train Order Volume Model

Trains a new Order Volume model using provided data.

**Endpoint:** `POST /models/train/order-volume`

**Query Parameters:**
- `data_file_id` (required): ID of the uploaded CSV file to use for training

**Request Body (optional):**
```json
{
  "epochs": 100,
  "batch_size": 32,
  "validation_split": 0.2,
  "test_size": 0.2,
  "description": "Order volume model trained on 2025 data"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Order volume model training started",
  "model_id": "order_volume_20250518123045"
}
```

#### 3.5 Train Tender Performance Model

Trains a new Tender Performance model using provided data.

**Endpoint:** `POST /models/train/tender-performance`

**Query Parameters:**
- `data_file_id` (required): ID of the uploaded CSV file to use for training

**Request Body (optional):**
```json
{
  "epochs": 100,
  "batch_size": 32,
  "validation_split": 0.2,
  "test_size": 0.2,
  "description": "Tender performance model trained on 2025 data"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Tender performance model training started",
  "model_id": "tender_performance_20250518123045"
}
```

#### 3.6 Train Carrier Performance Model

Trains a new Carrier Performance model using provided data.

**Endpoint:** `POST /models/train/carrier-performance`

**Query Parameters:**
- `data_file_id` (required): ID of the uploaded CSV file to use for training

**Request Body (optional):**
```json
{
  "epochs": 100,
  "batch_size": 32,
  "validation_split": 0.2,
  "test_size": 0.2,
  "description": "Carrier performance model trained on 2025 data"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Carrier performance model training started",
  "model_id": "carrier_performance_20250518123045"
}
```

### 4. Order Volume Predictions

#### 4.1 Get Order Volume Predictions

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

#### 4.2 Get Order Volume Predictions by Lane

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

#### 4.3 Download Order Volume Predictions

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

#### 4.4 Create New Order Volume Predictions

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

### 5. Tender Performance Predictions

#### 5.1 Get Tender Performance Predictions

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

#### 5.2 Get Tender Performance Predictions by Lane

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

#### 5.3 Download Tender Performance Predictions

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

#### 5.4 Create New Tender Performance Predictions

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

### 6. Carrier Performance Predictions

#### 6.1 Get Carrier Performance Predictions

Retrieves carrier performance predictions for a specified model.

**Endpoint:** `GET /predictions/carrier-performance/{model_id}`

**Path Parameters:**
- `model_id` (required): ID of the model

**Query Parameters:**
- `simplified` (optional): Whether to return simplified predictions with only essential fields (default: true)

**Response:**
```json
{
  "prediction_id": "pred_d80195a3_20250516",
  "model_id": "carrier_performance_20250516091734",
  "model_type": "carrier_performance",
  "created_at": "2025-05-16T09:17:34.123456",
  "prediction_count": 450,
  "data": {
    "prediction_time": "2025-05-16T09:17:34.123456",
    "metrics": {
      "mae": 3.42,
      "mape": 4.87,
      "rmse": 5.21,
      "records_analyzed": 450
    },
    "predictions": [
      {
        "carrier": "RBTW",
        "source_city": "ELWOOD",
        "dest_city": "PLANO",
        "predicted_ontime_performance": 89.7
      },
      // More predictions...
    ]
  }
}
```

**Example:**
```
GET /api/predictions/carrier-performance/carrier_performance_20250516091734?simplified=true
```

#### 6.2 Get Carrier Performance Predictions by Lane

Retrieves carrier performance predictions for a specific lane.

**Endpoint:** `GET /predictions/carrier-performance/{model_id}/by-lane`

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
  "prediction_id": "pred_d80195a3_20250516",
  "model_id": "carrier_performance_20250516091734",
  "source_city": "ELWOOD",
  "dest_city": "PLANO",
  "carrier": null,
  "metrics": {
    "avg_predicted_ontime_performance": 85.6,
    "carrier_count": 3,
    "carriers": ["RBTW", "BTRH", "ALMO"]
  },
  "predictions": [
    {
      "carrier": "RBTW",
      "source_city": "ELWOOD",
      "dest_city": "PLANO",
      "predicted_ontime_performance": 89.7
    },
    // More predictions...
  ],
  "prediction_count": 3
}
```

**Example:**
```
GET /api/predictions/carrier-performance/carrier_performance_20250516091734/by-lane?source_city=ELWOOD&dest_city=PLANO
```

#### 6.3 Download Carrier Performance Predictions

Downloads carrier performance predictions in the specified format.

**Endpoint:** `GET /predictions/carrier-performance/{model_id}/download`

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
GET /api/predictions/carrier-performance/carrier_performance_20250516091734/download?format=csv&simplified=true
```

#### 6.4 Create New Carrier Performance Predictions

Generates new carrier performance predictions on training data.

**Endpoint:** `POST /predictions/carrier-performance`

**Request Body:**
```json
{
  "model_id": "carrier_performance_20250516091734"
}
```

**Response:**
```json
{
  "prediction_id": "pred_d80195a3_20250516",
  "model_id": "carrier_performance_20250516091734",
  "model_type": "carrier_performance",
  "created_at": "2025-05-16T09:22:15.987654",
  "prediction_count": 450,
  "metrics": {
    "mae": 3.42,
    "mape": 4.87,
    "rmse": 5.21,
    "records_analyzed": 450
  }
}
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