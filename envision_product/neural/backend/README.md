# Envision Neural API

This is the backend API for the Envision Neural application. It provides endpoints for data management, model training, and predictions.

## Features

- File upload and management
- Data preprocessing and preview generation
- Model training for order volume prediction
- Prediction generation and storage
- RESTful API with FastAPI

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
├── services/          # Business logic services
├── tests/             # Test cases
├── main.py            # FastAPI application entry point
└── requirements.txt   # Python dependencies
```

## API Endpoints

### Files API

- `GET /api/files/` - List all uploaded files
- `POST /api/files/upload` - Upload a new file
- `GET /api/files/{file_id}` - Download a file
- `DELETE /api/files/{file_id}` - Delete a file

### Data API

- `GET /api/data/preview/{file_id}` - Get a preview of file data
- `POST /api/data/process` - Process a data file

### Models API

- `GET /api/models/` - List all models
- `GET /api/models/{model_id}` - Get model details
- `POST /api/models/train/order-volume` - Train a new order volume model
- `DELETE /api/models/{model_id}` - Delete a model

### Predictions API

- `GET /api/predictions/` - List all predictions
- `GET /api/predictions/{prediction_id}` - Get prediction details
- `POST /api/predictions/order-volume` - Generate order volume predictions
- `DELETE /api/predictions/{prediction_id}` - Delete a prediction

## Development

### Adding New Models

To add a new model type:

1. Create a new model implementation in the `models/` directory
2. Add appropriate methods to the `ModelService` in `services/model_service.py`
3. Create endpoints in the appropriate API router 