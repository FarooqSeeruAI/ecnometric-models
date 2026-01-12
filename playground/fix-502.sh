#!/bin/bash
# Quick fix for 502 Bad Gateway error

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="13.203.193.142"

echo "🔧 Fixing 502 Bad Gateway Error"
echo "================================"
echo ""

# Check container status
echo "1️⃣ Checking container status..."
CONTAINER_STATUS=$(ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker ps -a --filter "name=cge-model-api" --format "{{.Status}}"')
echo "Container status: ${CONTAINER_STATUS}"

# Check if container is running
if ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker ps --filter "name=cge-model-api" --format "{{.Names}}" | grep -q cge-model-api'; then
    echo "✅ Container is running"
    
    # Check if FastAPI is responding
    echo ""
    echo "2️⃣ Testing FastAPI on port 8000..."
    HEALTH_RESPONSE=$(ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'curl -s http://localhost:8000/health 2>&1')
    
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        echo "✅ FastAPI is responding: $HEALTH_RESPONSE"
        echo ""
        echo "3️⃣ Checking nginx configuration..."
        ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo nginx -t 2>&1'
        echo ""
        echo "4️⃣ Restarting nginx..."
        ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo systemctl restart nginx'
        echo "✅ Nginx restarted"
    else
        echo "❌ FastAPI not responding: $HEALTH_RESPONSE"
        echo ""
        echo "3️⃣ Restarting container..."
        ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker restart cge-model-api'
        echo "⏳ Waiting 10 seconds for container to start..."
        sleep 10
        
        # Test again
        HEALTH_RESPONSE=$(ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'curl -s http://localhost:8000/health 2>&1')
        if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
            echo "✅ FastAPI is now responding: $HEALTH_RESPONSE"
        else
            echo "❌ FastAPI still not responding"
            echo ""
            echo "📋 Container logs:"
            ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker logs cge-model-api --tail 20'
        fi
    fi
else
    echo "❌ Container is not running"
    echo ""
    echo "2️⃣ Starting container..."
    ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker start cge-model-api || docker run -d --name cge-model-api -p 8000:8000 -v ~/cge_model/outputs:/app/outputs -v ~/cge_model/temp_closures:/app/temp_closures -v ~/cge_model/database:/app/database -v ~/cge_model/closures:/app/closures --restart unless-stopped cge-model-api'
    echo "⏳ Waiting 10 seconds for container to start..."
    sleep 10
    
    # Test
    HEALTH_RESPONSE=$(ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'curl -s http://localhost:8000/health 2>&1')
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        echo "✅ Container started and FastAPI is responding: $HEALTH_RESPONSE"
    else
        echo "❌ Container started but FastAPI not responding"
        echo ""
        echo "📋 Container logs:"
        ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker logs cge-model-api --tail 30'
    fi
fi

echo ""
echo "✅ Fix attempt complete!"
echo ""
echo "Test the API:"
echo "curl http://${EC2_IP}/health"
