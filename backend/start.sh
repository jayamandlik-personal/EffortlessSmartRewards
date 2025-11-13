#!/bin/bash

# Start script for Effortless Backend

echo "Starting Effortless Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your OPENAI_API_KEY"
fi

# Check if database exists, if not run seed
if [ ! -f "effortless.db" ]; then
    echo "Initializing database and seeding data..."
    python seed_data.py
fi

# Start server
echo "Starting FastAPI server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

