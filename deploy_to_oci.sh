#!/bin/bash
# Complete deployment script for OCI instance
# Usage: ./deploy_to_oci.sh <OCI_INSTANCE_IP>

set -e

# Configuration
OCI_USER="ubuntu"
OCI_KEY="./keys/ssh-key-2026-01-11.key"
REMOTE_DIR="~/ecnometric-models"

# Get instance IP from argument
if [ -z "$1" ]; then
    echo "Usage: ./deploy_to_oci.sh <OCI_INSTANCE_IP>"
    echo "Example: ./deploy_to_oci.sh 129.213.45.67"
    exit 1
fi

OCI_HOST="$1"

echo "=========================================="
echo "Deploying CGE Model to OCI Instance"
echo "=========================================="
echo "Instance: $OCI_USER@$OCI_HOST"
echo "Key: $OCI_KEY"
echo ""

# Check if key exists
if [ ! -f "$OCI_KEY" ]; then
    echo "Error: SSH key not found at $OCI_KEY"
    exit 1
fi

# Set proper permissions
chmod 600 "$OCI_KEY"

# Test SSH connection
echo "Testing SSH connection..."
if ! ssh -i "$OCI_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$OCI_USER@$OCI_HOST" "echo 'Connection successful'" 2>/dev/null; then
    echo "Error: Cannot connect to instance. Please check:"
    echo "  1. Instance IP is correct: $OCI_HOST"
    echo "  2. Instance is running"
    echo "  3. Security rules allow SSH (port 22)"
    echo "  4. SSH key is correct"
    exit 1
fi

echo "✅ SSH connection successful"
echo ""

# Step 1: Install git if needed
echo "Step 1: Installing git..."
ssh -i "$OCI_KEY" "$OCI_USER@$OCI_HOST" "sudo apt-get update -qq && sudo apt-get install -y git > /dev/null 2>&1"

# Step 2: Clone repository
echo "Step 2: Cloning repository..."
ssh -i "$OCI_KEY" "$OCI_USER@$OCI_HOST" "rm -rf $REMOTE_DIR && git clone https://github.com/FarooqSeeruAI/ecnometric-models.git $REMOTE_DIR"

# Step 3: Run deployment
echo "Step 3: Running deployment script..."
ssh -i "$OCI_KEY" "$OCI_USER@$OCI_HOST" "cd $REMOTE_DIR && chmod +x quick_deploy.sh && ./quick_deploy.sh"

# Step 4: Configure firewall
echo "Step 4: Configuring firewall..."
ssh -i "$OCI_KEY" "$OCI_USER@$OCI_HOST" "sudo ufw allow 8000/tcp && sudo ufw allow 22/tcp && sudo ufw --force enable || true"

# Step 5: Get instance IP
INSTANCE_IP=$(ssh -i "$OCI_KEY" "$OCI_USER@$OCI_HOST" "hostname -I | awk '{print \$1}'")

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. SSH into the instance:"
echo "   ssh -i $OCI_KEY $OCI_USER@$OCI_HOST"
echo ""
echo "2. Start the API server:"
echo "   cd $REMOTE_DIR"
echo "   python3 api_server.py"
echo ""
echo "   Or run in background:"
echo "   nohup python3 api_server.py > logs/api.log 2>&1 &"
echo ""
echo "3. Access the API:"
echo "   http://$INSTANCE_IP:8000/docs"
echo "   http://$INSTANCE_IP:8000/openapi.json"
echo ""
echo "4. Configure OCI Security Rules:"
echo "   - Go to OCI Console → Networking → Security Lists"
echo "   - Add Ingress Rule: TCP port 8000 from 0.0.0.0/0"
echo ""
