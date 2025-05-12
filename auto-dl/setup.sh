#!/bin/bash

# Setup script for Terminal-Based Neural Network Trainer

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    echo "Activating virtual environment on Unix-like system..."
    source venv/bin/activate
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "Activating virtual environment on Windows..."
    source venv/Scripts/activate
else
    echo "Unknown operating system. Please activate the virtual environment manually."
    exit 1
fi

# Install requirements
echo "Installing required Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p models
mkdir -p predictions

# Check if installation was successful
if pip show tensorflow > /dev/null && pip show pandas > /dev/null && pip show simple-term-menu > /dev/null; then
    echo "Setup completed successfully!"
    echo "To start the application, run:"
    echo "  source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
    echo "  python app.py"
else
    echo "Setup failed. Please check the error messages and try again."
fi