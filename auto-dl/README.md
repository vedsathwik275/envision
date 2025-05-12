# Terminal-Based Neural Network Trainer

A command-line application for training neural networks using CSV data.

## Overview

This application allows users to:
- Load and parse CSV files
- Select target features for prediction
- Automatically preprocess data (handle missing values, scale features, encode categorical data)
- Train neural network models
- Save and load trained models
- Make predictions on new data

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone this repository or download the source code

2. Navigate to the application directory
```bash
cd terminal-neural-network-trainer
```

3. Run the setup script
```bash
# On Unix-like systems (Linux/macOS)
chmod +x setup.sh
./setup.sh

# On Windows
# Run setup.sh using Git Bash or manually follow these steps:
# 1. Create a virtual environment: python -m venv venv
# 2. Activate it: venv\Scripts\activate
# 3. Install requirements: pip install -r requirements.txt
# 4. Create directories: mkdir models predictions
```

## Usage

1. Activate the virtual environment
```bash
# On Unix-like systems (Linux/macOS)
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

2. Run the application
```bash
python app.py
```

3. Follow the on-screen prompts to:
   - Train a new neural network model using your CSV data
   - Load an existing model to make predictions
   - Select target features
   - Configure and start training
   - Save trained models
   - Make and save predictions

### Example Workflow

1. Prepare your CSV data file
2. Choose "Train New Model" from the main menu
3. Enter the path to your CSV file
4. Select the target feature for prediction
5. The application will automatically preprocess your data
6. Confirm to start training with default parameters
7. After training, save the model
8. Use "Load Existing Model" to make predictions on new data

## Project Structure

```
terminal-neural-network-trainer/
├── app.py                 # Main application
├── ui.py                  # User interface component
├── data_handler.py        # Data handling component
├── model_trainer.py       # Model training component
├── predictor.py           # Prediction component
├── requirements.txt       # Python dependencies
├── setup.sh               # Setup script
├── models/                # Directory for saved models
└── predictions/           # Directory for saved predictions
```

## Dependencies

- simple-term-menu: Terminal menu interface
- pandas: Data manipulation and analysis
- scikit-learn: Data preprocessing
- tensorflow: Neural network implementation

## Proof of Concept

This implementation is a proof of concept designed to demonstrate the feasibility of a terminal-based neural network trainer. It includes basic functionality with minimal error handling and optimization.

## License

This project is licensed under the MIT License - see the LICENSE file for details.