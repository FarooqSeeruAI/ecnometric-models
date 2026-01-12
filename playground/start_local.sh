#!/bin/bash
# Start CGE Model API locally (without nginx)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting CGE Model API"
echo "========================"

# Check if Python dependencies are installed
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements_api.txt
fi

# Create necessary directories
mkdir -p outputs temp_closures logs static

# Check if API server is already running
if pgrep -f "api_server.py" > /dev/null; then
    echo "⚠️  API server is already running. Stopping it..."
    pkill -f api_server.py
    sleep 2
fi

# Start API server in background
echo "🔧 Starting API server on port 8000..."
export PATH="$HOME/.local/bin:$PATH"
nohup python3 api_server.py > logs/api.log 2>&1 &
API_PID=$!

# Wait for server to start
echo "⏳ Waiting for API server to start..."
sleep 3

# Check if server started successfully
if curl -s http://localhost:8000/health > /dev/null; then
    echo ""
    echo "✅ SUCCESS! API is running"
    echo ""
    echo "Access your API at:"
    echo "  🌐 Swagger UI: http://localhost:8000/docs"
    echo "  📋 OpenAPI: http://localhost:8000/openapi.json"
    echo "  ❤️  Health: http://localhost:8000/health"
    echo ""
    echo "API server logs: tail -f logs/api.log"
    echo ""
    echo "To stop: pkill -f api_server.py"
else
    echo "❌ API server failed to start. Check logs/api.log"
    kill $API_PID 2>/dev/null || true
    exit 1
fi
