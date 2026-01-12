#!/bin/bash
# Deploy CGE Model API to EC2 instance

set -e

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="3.110.189.51"
REMOTE_DIR="~/cge_model"

echo "🚀 Deploying CGE Model API to EC2..."

# Create a tarball of the application (excluding unnecessary files)
echo "📦 Creating deployment package..."
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='env' \
    --exclude='outputs' \
    --exclude='temp_closures' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    --exclude='pem' \
    -czf /tmp/cge_model_deploy.tar.gz .

# Upload to EC2
echo "📤 Uploading files to EC2..."
scp -i ${SSH_KEY} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/cge_model_deploy.tar.gz ${EC2_USER}@${EC2_IP}:/tmp/

# Extract and deploy on EC2
echo "🔧 Setting up application on EC2..."
ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${EC2_USER}@${EC2_IP} << 'ENDSSH'
set -e

cd ~
mkdir -p cge_model
cd cge_model

# Extract files
echo "Extracting application files..."
tar -xzf /tmp/cge_model_deploy.tar.gz
rm /tmp/cge_model_deploy.tar.gz

# Create necessary directories
mkdir -p outputs temp_closures

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "🐳 Building Docker image..."
    docker build -t cge-model-api .
    
    # Stop existing container if running
    docker stop cge-model-api 2>/dev/null || true
    docker rm cge-model-api 2>/dev/null || true
    
    # Run new container
    echo "🚀 Starting container..."
    docker run -d \
        --name cge-model-api \
        -p 8000:8000 \
        -v $(pwd)/outputs:/app/outputs \
        -v $(pwd)/temp_closures:/app/temp_closures \
        -v $(pwd)/database:/app/database \
        -v $(pwd)/closures:/app/closures \
        --restart unless-stopped \
        cge-model-api
    
    echo "✅ Container started successfully!"
    echo "Waiting for service to be ready..."
    sleep 5
    
    # Check health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Health check passed!"
    else
        echo "⚠️  Health check failed, but container is running"
        echo "Check logs with: docker logs cge-model-api"
    fi
else
    echo "⚠️  Docker not found, installing Python dependencies..."
    pip3 install -r requirements_api.txt
    
    echo "🚀 Starting FastAPI server directly..."
    # Stop existing process if running
    pkill -f "api_server.py" 2>/dev/null || true
    
    # Start in background
    nohup python3 api_server.py > api_server.log 2>&1 &
    
    echo "✅ Server started!"
    echo "Check logs with: tail -f api_server.log"
fi

ENDSSH

# Cleanup
rm -f /tmp/cge_model_deploy.tar.gz

echo ""
echo "✅ Deployment completed!"
echo ""
echo "🌐 Your API is available at:"
echo "   Swagger UI: http://${EC2_IP}:8000/docs"
echo "   Health: http://${EC2_IP}:8000/health"
echo "   API Root: http://${EC2_IP}:8000/"
echo ""
echo "📝 To check logs:"
echo "   ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker logs cge-model-api'"
echo "   or"
echo "   ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'tail -f ~/cge_model/api_server.log'"
