# Envision Neural - Proof of Concept Frontend

This is a simple proof-of-concept frontend for the Envision Neural API, which demonstrates the capabilities of the backend API for transportation logistics predictions.

## Features

- **File Upload**: Upload CSV files containing transportation logistics data.
- **File Preview**: View uploaded data files with basic statistics.
- **Model Training**: Train three types of prediction models:
  - Order Volume forecasting
  - Tender Performance prediction
  - Carrier Performance prediction
- **Model Management**: View all trained models and their statistics.
- **Predictions**: Generate predictions using trained models.

## Setup Instructions

1. **Start the Backend Server**

   Make sure the Envision Neural backend server is running. By default, it runs on `http://localhost:8000`.

   ```bash
   cd ../backend
   python main.py
   ```

2. **Serve the Frontend**

   You can use any static file server to serve the frontend files. For example, with Python:

   ```bash
   # Python 3
   python -m http.server 5000
   ```

   Or with Node.js and http-server:

   ```bash
   # Install http-server if you don't have it
   npm install -g http-server

   # Serve the frontend
   http-server -p 5000
   ```

3. **Access the Frontend**

   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## API Configuration

The frontend is configured to connect to the backend API at `http://localhost:8000/api`. If your backend is running on a different host or port, update the `API_BASE_URL` constant in `script.js`.

## Usage Workflow

1. **Upload Data**
   - Navigate to the "File Upload" tab
   - Select a CSV file with transportation logistics data
   - Upload the file

2. **Preview Data**
   - Navigate to the "File Preview" tab
   - Select the uploaded file from the dropdown
   - Click "Preview" to see the data

3. **Train a Model**
   - Navigate to the "Model Training" tab
   - Select the data file to use for training
   - Choose the model type (Order Volume, Tender Performance, or Carrier Performance)
   - Configure training parameters if needed
   - Click "Start Training"

4. **View Models**
   - Navigate to the "Model List" tab
   - Use the filter to see specific model types
   - Click "Details" on any model to see more information
   - Click "Predict" to generate predictions with a model

5. **Generate Predictions**
   - Navigate to the "Predictions" tab
   - Select the model type and specific model
   - Configure prediction parameters
   - Click "Generate Predictions"
   - View or download the prediction results

## Known Limitations

- This is a proof-of-concept implementation with simplified error handling
- Some features are simulated for demonstration purposes
- The UI is minimal and designed for functionality rather than aesthetics

## Notes

This frontend is designed to showcase the capabilities of the Envision Neural API and is not intended for production use. 