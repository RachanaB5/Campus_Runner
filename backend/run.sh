#!/bin/bash

# Campus Runner Flask Backend Setup and Run Script

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Starting Flask backend server..."
python app.py
