#!/bin/bash
# Quick status check for AWS FastAPI server

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="13.203.193.142"

echo "🔍 Checking AWS FastAPI Server Status"
echo "======================================"
echo ""

# Check Docker container status
echo "📦 Docker Containers:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
echo ""

# Check if FastAPI is responding locally
echo "🏥 Health Check (from server):"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'curl -s http://localhost:8000/health || echo "❌ Port 8000 not responding"'
echo ""

# Check if nginx is running and configured
echo "🌐 Nginx Status:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'systemctl is-active nginx 2>/dev/null && echo "✅ Nginx is running" || echo "❌ Nginx not running"'
echo ""

# Check if port 80 is proxying to 8000
echo "🔗 Testing Port 80 (via nginx):"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'curl -s http://localhost/health 2>/dev/null && echo "✅ Port 80 responding" || echo "❌ Port 80 not responding"'
echo ""

# Check container logs (last 10 lines)
echo "📋 Recent Container Logs:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker logs cge-model-api --tail 10 2>/dev/null || echo "Container not found or no logs"'
echo ""

# Test external access
echo "🌍 External Access Test:"
echo "Testing http://${EC2_IP}:8000/health"
curl -s --connect-timeout 5 http://${EC2_IP}:8000/health && echo "✅ Port 8000 accessible externally" || echo "❌ Port 8000 not accessible (check security group)"
echo ""

echo "Testing http://${EC2_IP}/health"
curl -s --connect-timeout 5 http://${EC2_IP}/health && echo "✅ Port 80 accessible externally" || echo "❌ Port 80 not accessible"
echo ""

echo "✅ Status check complete!"
echo ""
echo "📝 Access URLs:"
echo "   - Swagger UI: http://${EC2_IP}:8000/docs (if port 8000 is open)"
echo "   - Swagger UI: http://${EC2_IP}/docs (if nginx is configured)"
echo "   - Health: http://${EC2_IP}:8000/health"
echo "   - Health: http://${EC2_IP}/health"
