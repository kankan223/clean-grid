#!/bin/bash

# CleanGrid Backend Server Startup Script
# This script properly activates the virtual environment and sets PYTHONPATH

echo "Starting CleanGrid Backend Server..."

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH to include current directory
export PYTHONPATH=.

# Run the server on port 8003 (to avoid conflicts)
echo "Server will start on http://localhost:8003"
echo "API Documentation: http://localhost:8003/docs"
echo "Health Check: http://localhost:8003/health"

# Start the server
python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8003, reload=True)"
