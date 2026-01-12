#!/bin/bash
# Deploy async fix for /api/v1/scenarios/run endpoint

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="13.203.193.142"
REMOTE_DIR="~/cge_model"

echo "🚀 Deploying async fix for scenarios/run endpoint"
echo "=================================================="

# Upload the updated api_server.py
echo "📤 Uploading updated api_server.py..."
scp -i ${SSH_KEY} api_server.py ${EC2_USER}@${EC2_IP}:${REMOTE_DIR}/api_server.py

# Restart the container
echo "🔄 Restarting Docker container..."
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker restart cge-model-api'

echo "⏳ Waiting 10 seconds for container to start..."
sleep 10

# Test the endpoint
echo "🧪 Testing endpoint..."
HEALTH=$(ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'curl -s http://localhost:8000/health')
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Container is healthy"
    echo ""
    echo "Test the endpoint:"
    echo "curl -X POST http://${EC2_IP}/api/v1/scenarios/run \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"scenario_name\":\"test\",\"year\":2025,\"steps\":1,\"shocks\":{\"realgdp\":1.0}}'"
else
    echo "❌ Container health check failed"
    echo "Check logs: ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker logs cge-model-api --tail 30'"
fi
