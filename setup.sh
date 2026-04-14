#!/bin/bash

# Exit on error
set -e

echo "--------------------------------------------------"
echo "Setting up Quantum Graph Analyzer..."
echo "--------------------------------------------------"

# Check for python3
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 could not be found. Please install it."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo "--------------------------------------------------"
echo "Setup complete! Starting application..."
echo "--------------------------------------------------"

# Run the app
python3 app.py
