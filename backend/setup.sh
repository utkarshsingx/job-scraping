#!/bin/bash

# Backend Setup Script
# This script sets up the Django backend environment

echo "Setting up Django backend..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python3 manage.py migrate

echo ""
echo "✓ Backend setup complete!"
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  python3 manage.py runserver"
echo ""

