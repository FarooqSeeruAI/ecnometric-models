#!/bin/bash
# Quick deployment script - run this on OCI instance after cloning

set -e

echo "🚀 Quick Deployment for CGE Model API"
echo "======================================"

# Install dependencies
echo "📦 Installing dependencies..."
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip git > /dev/null 2>&1

# Install Python packages
echo "📚 Installing Python packages..."
pip3 install --upgrade pip -q
pip3 install -r requirements_api.txt -q

# Create directories
echo "📁 Creating directories..."
mkdir -p outputs temp_closures logs

# Make scripts executable
chmod +x *.py *.sh 2>/dev/null || true

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To start the API server:"
echo "  python3 api_server.py"
echo ""
echo "Or run in background:"
echo "  nohup python3 api_server.py > logs/api.log 2>&1 &"
echo ""
echo "API will be available at:"
echo "  http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
