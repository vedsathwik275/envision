# API Documentation

## Overview

This API provides functionalities for a terminal-based Python application that allows users to train neural networks using CSV data. The API offers endpoints for loading CSV files, preprocessing data, training neural networks, and running predictions.

## Authentication

For local runs, authentication is not required. For deployment in non-local environments, consider implementing token-based authentication using JWT or API keys for secure access.

## Endpoints

### 1. Load CSV

- **Endpoint:** `/api/load-csv`
- **Method:** `POST`
- **Description:** Load and parse the columns of a CSV file.
- **Request Body:**
  ```json
  {
    "filename": "data.csv"
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "columns": ["column1", "column2", "column3"]
  }
  ```
- **Error Handling:**
  - `400 Bad Request`: If the file is not found or is malformed.
  - `415 Unsupported Media Type`: If the file is not a CSV.

### 2. Preprocess Data

- **Endpoint:** `/api/preprocess`
- **Method:** `POST`
- **Description:** Preprocess data by handling missing values, scaling, and encoding.
- **Request Body:**
  ```json
  {
    "filename": "data.csv",
    "target_feature": "target_column"
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "message": "Data preprocessed successfully."
  }
  ```
- **Error Handling:**
  - `400 Bad Request`: If the target feature is invalid or preprocessing fails.

### 3. Train Model

- **Endpoint:** `/api/train-model`
- **Method:** `POST`
- **Description:** Train a neural network model with preprocessed data.
- **Request Body:**
  ```json
  {
    "parameters": {
      "epochs": 100,
      "batch_size": 32
    }
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "model_id": "model_12345"
  }
  ```
- **Error Handling:**
  - `400 Bad Request`: If training parameters are invalid.
  - `500 Internal Server Error`: If the training process fails.

### 4. Run Prediction

- **Endpoint:** `/api/predict`
- **Method:** `POST`
- **Description:** Run predictions using a trained model.
- **Request Body:**
  ```json
  {
    "model_id": "model_12345",
    "input_data": [ ... ]
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "predictions": [0.95, 0.85, 0.80]
  }
  ```
- **Error Handling:**
  - `404 Not Found`: If the model is not found.
  - `400 Bad Request`: If input data is invalid.

## Rate Limiting

Currently, no rate limiting is implemented as the API is intended for local use. For deployment, consider implementing rate limiting to prevent abuse.

## Error Handling

Errors are returned in a structured format with a status code and message. Example:
```json
{
  "status": "error",
  "message": "Detailed error message"
}
```

## Setup and Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Application:**
   ```bash
   python app.py
   ```

## Usage Guidelines

- Ensure CSV files have a consistent structure and valid data types.
- Handle exceptions gracefully and provide meaningful error messages.
- Validate CSV file size and format before processing.

By following the above endpoint specifications, request/response examples, and error handling guidelines, users can effectively interact with the API for training and predicting neural networks using CSV data.