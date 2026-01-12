#!/bin/bash
# Setup script for EC2 instance - installs dependencies for CGE Model API

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="13.203.193.142"

echo "Setting up EC2 instance for CGE Model API deployment..."

# Run setup commands on EC2
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} << 'ENDSSH'
set -e

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    sudo apt install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
    echo "Docker installed successfully"
else
    echo "Docker already installed"
fi

echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo apt install -y docker-compose
    echo "Docker Compose installed successfully"
else
    echo "Docker Compose already installed"
fi

echo "Installing Git..."
if ! command -v git &> /dev/null; then
    sudo apt install -y git
    echo "Git installed successfully"
else
    echo "Git already installed"
fi

echo "Installing Python3 and pip..."
if ! command -v python3 &> /dev/null; then
    sudo apt install -y python3 python3-pip
    echo "Python3 installed successfully"
else
    echo "Python3 already installed"
fi

echo "Installing curl (for health checks)..."
sudo apt install -y curl

echo "Creating application directory..."
mkdir -p ~/cge_model
cd ~/cge_model

echo "Setup complete!"
echo "Next steps:"
echo "1. Clone your repository or upload files"
echo "2. Build and run with: docker-compose up -d"
echo "3. Or run directly: python3 api_server.py"

ENDSSH

echo "Setup completed on EC2 instance!"
