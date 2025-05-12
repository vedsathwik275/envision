# Order Volume Neural Network Model

This is a neural network model for predicting order volumes based on historical data. It's designed as part of the Neural Network Training Platform MVP.

## Overview

The model predicts future order volumes for each unique lane (combination of source city, destination city, and order type) based on historical data patterns.

## Features

- Data preprocessing and validation
- Neural network training with early stopping
- Model evaluation with metrics (MAE, RMSE, R²)
- Future prediction generation for 6 months
- Model saving and loading capabilities

## Requirements

- Python 3.8+
- TensorFlow 2.x
- pandas
- numpy
- scikit-learn
- matplotlib

## Installation

Install the required packages:

```bash
pip install tensorflow pandas numpy scikit-learn matplotlib
```

## Usage

### Training a new model

```python
from order_volume_model import OrderVolumeModel

# Initialize with data path
model = OrderVolumeModel(data_path="data/OrderVolume_ByMonth_v2.csv")

# Preprocess data
model.preprocess_data()

# Split data
model.prepare_train_test_split(test_size=0.2)

# Build and train model
model.build_model()
model.train(epochs=100, batch_size=32)

# Evaluate model
metrics = model.evaluate()

# Generate predictions for next 6 months
predictions = model.predict_future(months=6)

# Save model for future use
model.save_model("order_volume_model")
```

### Loading a pre-trained model and making predictions

```python
from order_volume_model import OrderVolumeModel

# Load existing model
model = OrderVolumeModel(
    data_path="data/OrderVolume_ByMonth_v2.csv",
    model_path="order_volume_model"
)

# Generate predictions
predictions = model.predict_future(months=6)
```

## Model Architecture

The neural network model consists of:
- Input layer based on encoded features
- 3 dense layers (128, 64, 32 neurons) with ReLU activation
- Dropout layers for regularization
- Output layer (single neuron) for regression

## Data Format

The expected input data format is a CSV file with the following columns:
- SOURCE CITY: Origin city
- DESTINATION CITY: Destination city
- ORDER TYPE: Type of order (e.g., "Prepaid", "Collect", "Transfer")
- ORDER MONTH: Month in format "YYYY MM"
- ORDER VOLUME: Number of orders (target variable)

## Output

The model generates predictions in a CSV file called `future_predictions.csv` with the following columns:
- SOURCE CITY: Origin city
- DESTINATION CITY: Destination city
- ORDER TYPE: Type of order
- PREDICTION YEAR: Year of prediction
- PREDICTION MONTH: Month of prediction (1-12)
- PREDICTION DATE: Year-month in format "YYYY-MM"
- PREDICTED ORDER VOLUME: Predicted number of orders 