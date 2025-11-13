#!/bin/bash

# Start script for Effortless Frontend

echo "Starting Effortless Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start development server
echo "Starting Vite development server..."
npm run dev

