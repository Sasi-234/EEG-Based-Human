#!/bin/bash

# EEG Emotion Recognition System - Setup Script
# This script sets up the project environment

echo "=========================================="
echo "EEG Emotion Recognition System Setup"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from template
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env file with your settings"
fi

# Create necessary directories
echo "Creating project directories..."
mkdir -p backend/config
mkdir -p backend/users
mkdir -p backend/eeg_processing
mkdir -p backend/ml_models
mkdir -p backend/api
mkdir -p backend/recommendations
mkdir -p backend/media/eeg_uploads
mkdir -p backend/media/reports
mkdir -p backend/media/models
mkdir -p backend/static/css
mkdir -p backend/static/js
mkdir -p backend/static/images
mkdir -p backend/templates/users
mkdir -p backend/templates/eeg
mkdir -p backend/templates/admin
mkdir -p dataset/DEAP/raw
mkdir -p dataset/DEAP/processed
mkdir -p notebooks
mkdir -p tests
mkdir -p docs

# Create .gitkeep files
touch backend/media/eeg_uploads/.gitkeep
touch backend/media/reports/.gitkeep
touch backend/media/models/.gitkeep
touch dataset/DEAP/raw/.gitkeep
touch dataset/DEAP/processed/.gitkeep

echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update .env file with your settings"
echo "2. Run: cd backend && python manage.py migrate"
echo "3. Run: python manage.py createsuperuser"
echo "4. Run: python manage.py runserver"
echo ""

# Made with Bob
