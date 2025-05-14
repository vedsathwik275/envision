# Envision Neural API

This is the backend API for the Envision Neural application. It provides endpoints for data management, model training, and predictions for order volumes and tender performance.

## Features

- File upload and management
- Data preprocessing and preview generation
- Multiple prediction models:
  - Order Volume Prediction: Forecasts future order volumes based on historical data
  - Tender Performance Prediction: Predicts carrier performance on specific lanes
- RESTful API with FastAPI
- Comprehensive Swagger UI documentation

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository
2. Navigate to the backend directory
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

Start the API server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Directory Structure

```
backend/
├── api/               # API routes and endpoints
├── config/            # Configuration settings
├── data/              # Data storage (created at runtime)
│   ├── uploads/       # Uploaded files
│   ├── previews/      # Data previews
│   ├── models/        # Trained models
│   └── predictions/   # Stored predictions
├── models/            # ML model implementations
│   ├── order_volume_model.py       # Order volume prediction model
│   └── tender_performance_model.py # Tender performance prediction model
├── services/          # Business logic services
├── tests/             # Test cases
├── main.py            # FastAPI application entry point
└── requirements.txt   # Python dependencies
```

## Models Overview

### Order Volume Model

The Order Volume Model predicts future order volumes based on historical data.

**Input Data:**
- Historical order volume data with columns:
  - ORDER MONTH
  - SOURCE CITY
  - DESTINATION CITY
  - ORDER TYPE
  - ORDER VOLUME

**Prediction Output:**
- Future order volumes for the next N months (default: 6 months)
- Predictions for each lane (source-destination combination) and order type

**Use Cases:**
- Capacity planning
- Resource allocation
- Demand forecasting

### Tender Performance Model

The Tender Performance Model predicts carrier performance on specific lanes based on historical performance data.

**Input Data:**
- Historical tender performance data with columns:
  - TENDER_PERF_PERCENTAGE
  - CARRIER
  - SOURCE_CITY
  - DEST_CITY

**Prediction Output:**
- Predicted tender performance percentage for specific carrier-lane combinations

**Use Cases:**
- Carrier selection optimization
- Performance benchmarking
- Lane strategy planning

## API Endpoints

### Files API

- `GET /api/files/` - List all uploaded files
- `POST /api/files/upload` - Upload a new file
- `GET /api/files/{file_id}` - Download a file
- `DELETE /api/files/{file_id}` - Delete a file

### Data API

- `GET /api/data/preview/{file_id}` - Get a preview of file data

### Models API

- `GET /api/models/` - List all models
- `GET /api/models/{model_id}` - Get model details
- `POST /api/models/train/order-volume` - Train a new order volume model
- `POST /api/models/train/tender-performance` - Train a new tender performance model
- `POST /api/models/predict/order-volume` - Generate order volume predictions
- `POST /api/models/predict/tender-performance` - Generate tender performance predictions
- `DELETE /api/models/{model_id}` - Delete a model

### Predictions API

- `GET /api/predictions/` - List all predictions
- `GET /api/predictions/{prediction_id}` - Get prediction details
- `POST /api/predictions/order-volume` - Generate order volume predictions
- `POST /api/predictions/tender-performance` - Generate tender performance predictions
- `DELETE /api/predictions/{prediction_id}` - Delete a prediction
- `POST /api/predictions/{model_id}/filter` - Filter predictions by criteria

## Usage Examples

### Using the Swagger UI

The Swagger UI provides an interactive interface to explore and test the API:

1. Start the server: `uvicorn main:app --reload`
2. Open a browser and navigate to `http://localhost:8000/docs`
3. The UI shows all available endpoints with documentation
4. You can expand each endpoint to see details and try it out

### Complete Workflow Example: Tender Performance Model

Here's a step-by-step guide to use the tender performance prediction functionality:

#### 1. Upload Data

**Endpoint:** `POST /api/files/upload`

Upload a CSV file containing tender performance data with these columns:
- TENDER_PERF_PERCENTAGE
- CARRIER
- SOURCE_CITY
- DEST_CITY

**Response:** You'll receive a file ID (save this for the next steps)

#### 2. Preview Data (Optional)

**Endpoint:** `GET /api/data/preview/{file_id}`

This shows a preview of the uploaded data to verify its structure.

#### 3. Train Model

**Endpoint:** `POST /api/models/train/tender-performance`

**Request Body:**
```json
{
  "data_file_id": "your-file-id-from-step-1",
  "params": {
    "epochs": 100,
    "batch_size": 32,
    "validation_split": 0.2,
    "test_size": 0.2,
    "description": "Tender performance model trained on historical data"
  }
}
```

Training happens in the background. The model automatically:
- Loads the data
- Preprocesses it (encoding categorical variables, handling high-cardinality features)
- Trains the neural network
- Evaluates performance
- Saves the model

#### 4. Check Model Status

**Endpoint:** `GET /api/models/`

List available models to find your newly trained model. Note the model_id for the next step.

#### 5. Generate Predictions

**Endpoint:** `POST /api/predictions/tender-performance`

**Request Body:**
```json
{
  "model_id": "your-model-id-from-step-4",
  "carriers": ["RBTW", "FDEG"],
  "source_cities": ["PHARR", "RICHMOND"],
  "dest_cities": ["ELWOOD", "LANCASTER"]
}
```

This will predict tender performance for the specified carrier-lane combinations.

**Response:**
```json
{
  "prediction_id": "pred_12345678",
  "model_id": "your-model-id",
  "predictions": [
    {
      "carrier": "RBTW",
      "source_city": "PHARR",
      "dest_city": "ELWOOD",
      "predicted_performance": 92.3
    },
    {
      "carrier": "FDEG",
      "source_city": "RICHMOND",
      "dest_city": "LANCASTER",
      "predicted_performance": 87.1
    }
  ]
}
```

### Complete Workflow Example: Order Volume Model

#### 1. Upload Data

**Endpoint:** `POST /api/files/upload`

Upload a CSV file containing order volume data.

#### 2. Train Model

**Endpoint:** `POST /api/models/train/order-volume`

Provide the file ID and optional training parameters.

#### 3. Generate Predictions

**Endpoint:** `POST /api/predictions/order-volume`

**Request Body:**
```json
{
  "model_id": "your-order-volume-model-id",
  "months": 6
}
```

This generates predictions for the specified number of future months.

## Model Training Details

### Order Volume Model

The order volume model uses a neural network to predict future order volumes based on:
- Historical time series patterns
- Seasonal components
- Source/destination relationships
- Order type

The model automatically performs:
- Time feature engineering
- Categorical variable encoding
- Data normalization
- Feature extraction

### Tender Performance Model

The tender performance model uses a neural network to predict performance based on:
- Carrier performance patterns
- Lane characteristics
- Geographical relationships

The model handles:
- Carrier encoding
- Source/destination city encoding
- High-cardinality features (many unique values)
- Performance score normalization

## Troubleshooting

### Common Issues

**404 for favicon.ico in logs**
- This is normal and can be ignored - it occurs when a browser automatically requests a favicon

**Training taking a long time**
- For testing, set the TESTING environment variable to reduce epochs:
  ```bash
  TESTING=1 uvicorn main:app --reload
  ```

**Prediction errors**
- Verify that your input data matches the format used during training
- For tender performance predictions, ensure carriers and cities exist in the training data
- Check that lists of carriers, source cities, and destination cities have the same length

## Development

### Adding New Models

To add a new model type:

1. Create a new model implementation in the `models/` directory
2. Add appropriate methods to the `ModelService` in `services/model_service.py`
3. Add prediction methods to the `PredictionService` in `services/prediction_service.py`
4. Create endpoints in the appropriate API routers
5. Update documentation 