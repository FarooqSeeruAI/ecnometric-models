#!/bin/bash
# Troubleshoot 502 Bad Gateway error

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="13.203.193.142"

echo "🔍 Troubleshooting 502 Bad Gateway Error"
echo "========================================="
echo ""

# Check if container is running
echo "📦 Docker Container Status:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker ps -a | grep cge-model-api' || echo "❌ Container not found"
echo ""

# Check if port 8000 is listening
echo "🔌 Port 8000 Status:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'netstat -tlnp | grep 8000 || ss -tlnp | grep 8000 || echo "Port 8000 not listening"'
echo ""

# Check container logs (last 30 lines)
echo "📋 Recent Container Logs:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker logs cge-model-api --tail 30 2>&1' || echo "Cannot get logs"
echo ""

# Check for errors in logs
echo "❌ Errors in Container Logs:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker logs cge-model-api 2>&1 | grep -i error | tail -10' || echo "No errors found"
echo ""

# Test FastAPI directly
echo "🏥 Testing FastAPI on port 8000:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'curl -s http://localhost:8000/health || echo "FastAPI not responding on port 8000"'
echo ""

# Check nginx status
echo "🌐 Nginx Status:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'systemctl status nginx --no-pager -l | head -20 || echo "Nginx not running"'
echo ""

# Check nginx error logs
echo "📋 Nginx Error Logs (last 10 lines):"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo tail -10 /var/log/nginx/error.log 2>/dev/null || echo "Cannot read nginx error log"'
echo ""

# Check nginx configuration
echo "⚙️  Nginx Configuration (proxy_pass):"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo grep -r "proxy_pass.*8000" /etc/nginx/ 2>/dev/null || echo "No proxy_pass configuration found"'
echo ""

# Restart suggestions
echo "💡 Suggested Actions:"
echo "1. Restart container: ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker restart cge-model-api'"
echo "2. Check container logs: ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'docker logs cge-model-api'"
echo "3. Restart nginx: ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo systemctl restart nginx'"
