#!/bin/bash
# Start FastAPI server with ngrok tunnel

echo "Starting CGE Model API Server with ngrok..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "Error: ngrok is not installed."
    echo "Install from: https://ngrok.com/download"
    exit 1
fi

# Start the FastAPI server in background
echo "Starting FastAPI server on port 8000..."
python3 api_server.py &
API_PID=$!

# Wait a moment for server to start
sleep 3

# Start ngrok tunnel
echo "Starting ngrok tunnel..."
ngrok http 8000

# Cleanup on exit
trap "kill $API_PID 2>/dev/null" EXIT
