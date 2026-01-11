#!/bin/bash
# Start CGE Model API locally behind nginx

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting CGE Model API with Nginx"
echo "======================================"

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "❌ nginx is not installed"
    echo ""
    echo "Install nginx:"
    echo "  macOS: brew install nginx"
    echo "  Ubuntu: sudo apt-get install nginx"
    exit 1
fi

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
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ API server failed to start. Check logs/api.log"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo "✅ API server started (PID: $API_PID)"

# Determine nginx config location
NGINX_CONFIG=""
NGINX_PREFIX=""
if [ -d "/opt/homebrew/etc/nginx/servers" ]; then
    # Homebrew nginx (Apple Silicon)
    NGINX_CONFIG="/opt/homebrew/etc/nginx/servers/cge_api.conf"
    NGINX_CONF_DIR="/opt/homebrew/etc/nginx"
    NGINX_PREFIX="/opt/homebrew"
elif [ -d "/usr/local/etc/nginx/servers" ]; then
    # Homebrew nginx (macOS Intel)
    NGINX_CONFIG="/usr/local/etc/nginx/servers/cge_api.conf"
    NGINX_CONF_DIR="/usr/local/etc/nginx"
    NGINX_PREFIX="/usr/local"
elif [ -d "/etc/nginx/sites-available" ]; then
    # Linux nginx
    NGINX_CONFIG="/etc/nginx/sites-available/cge_api.conf"
    NGINX_CONF_DIR="/etc/nginx"
    NGINX_PREFIX="/etc/nginx"
else
    echo "⚠️  Could not find nginx config directory"
    echo "   Please manually copy nginx_cge_api.conf to your nginx config"
    echo "   Then run: sudo nginx -t && sudo nginx -s reload"
    exit 1
fi

# Copy nginx config
echo "📝 Installing nginx configuration..."
sudo cp nginx_cge_api.conf "$NGINX_CONFIG"

# Update paths in config if needed (for macOS Homebrew)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Update log paths for Homebrew nginx
    BREW_PREFIX=$(brew --prefix)
    sudo sed -i '' "s|/opt/homebrew/var/log/nginx|$BREW_PREFIX/var/log/nginx|g" "$NGINX_CONFIG" 2>/dev/null || true
    sudo sed -i '' "s|/usr/local/var/log/nginx|$BREW_PREFIX/var/log/nginx|g" "$NGINX_CONFIG" 2>/dev/null || true
fi

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if [ -n "$NGINX_PREFIX" ] && [ "$NGINX_PREFIX" != "/etc/nginx" ]; then
    # Homebrew nginx
    if sudo "$NGINX_PREFIX/opt/nginx/bin/nginx" -t; then
        echo "✅ Nginx configuration is valid"
    else
        echo "❌ Nginx configuration test failed"
        exit 1
    fi
    # Reload nginx
    echo "🔄 Reloading nginx..."
    sudo "$NGINX_PREFIX/opt/nginx/bin/nginx" -s reload 2>/dev/null || sudo "$NGINX_PREFIX/opt/nginx/bin/nginx"
else
    # System nginx
    if sudo nginx -t; then
        echo "✅ Nginx configuration is valid"
    else
        echo "❌ Nginx configuration test failed"
        exit 1
    fi
    # Reload nginx
    echo "🔄 Reloading nginx..."
    sudo nginx -s reload || sudo nginx
fi

# Wait a moment
sleep 2

# Test nginx proxy
echo "🧪 Testing nginx proxy..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo ""
    echo "✅ SUCCESS! API is running behind nginx"
    echo ""
    echo "Access your API at:"
    echo "  🌐 Swagger UI: http://localhost:8080/docs"
    echo "  📋 OpenAPI: http://localhost:8080/openapi.json"
    echo "  ❤️  Health: http://localhost:8080/health"
    echo ""
    echo "API server logs: tail -f logs/api.log"
    BREW_PREFIX=$(brew --prefix 2>/dev/null || echo "$NGINX_PREFIX")
    echo "Nginx logs: tail -f $BREW_PREFIX/var/log/nginx/cge_api_access.log"
    echo ""
    echo "To stop:"
    echo "  pkill -f api_server.py"
    if [ -n "$NGINX_PREFIX" ] && [ "$NGINX_PREFIX" != "/etc/nginx" ]; then
        echo "  sudo $NGINX_PREFIX/opt/nginx/bin/nginx -s stop"
    else
        echo "  sudo nginx -s stop"
    fi
else
    echo "⚠️  Nginx proxy test failed, but API server is running on port 8000"
    echo "   Check nginx error logs for details"
    echo "   Direct API access: http://localhost:8000/docs"
fi
