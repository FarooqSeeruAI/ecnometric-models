#!/bin/bash
# Deployment script for OCI Ubuntu instance
# Run this on the OCI instance after SSH connection

set -e

echo "=========================================="
echo "CGE Model Deployment Script for OCI"
echo "=========================================="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
echo "Installing Python and system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

# Install Python packages
echo "Installing Python packages..."
pip3 install --upgrade pip
pip3 install -r requirements_api.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p outputs
mkdir -p temp_closures
mkdir -p logs

# Set permissions
echo "Setting permissions..."
chmod +x *.py
chmod +x *.sh

# Create systemd service for FastAPI
echo "Creating systemd service..."
sudo tee /etc/systemd/system/cge-model-api.service > /dev/null <<EOF
[Unit]
Description=CGE Model FastAPI Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 $(pwd)/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

echo "=========================================="
echo "Deployment completed!"
echo "=========================================="
echo ""
echo "To start the API server:"
echo "  sudo systemctl start cge-model-api"
echo ""
echo "To enable on boot:"
echo "  sudo systemctl enable cge-model-api"
echo ""
echo "To check status:"
echo "  sudo systemctl status cge-model-api"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u cge-model-api -f"
echo ""
