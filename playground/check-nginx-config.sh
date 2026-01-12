#!/bin/bash
# Check nginx configuration for timeout and size settings

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="13.203.193.142"

echo "🔍 Checking Nginx Configuration"
echo "================================"
echo ""

# Check nginx config files
echo "📋 Nginx Configuration Files:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo find /etc/nginx -name "*.conf" -type f | head -10'
echo ""

# Check for timeout settings
echo "⏱️  Timeout Settings:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo grep -r "timeout\|proxy_read_timeout\|proxy_send_timeout\|proxy_connect_timeout" /etc/nginx/ 2>/dev/null | grep -v "#" || echo "No timeout settings found"'
echo ""

# Check for body size limits
echo "📦 Body Size Limits:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo grep -r "client_max_body_size" /etc/nginx/ 2>/dev/null | grep -v "#" || echo "No body size limit found"'
echo ""

# Check proxy_pass configuration
echo "🔗 Proxy Pass Configuration:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo grep -A 10 -B 5 "proxy_pass" /etc/nginx/sites-enabled/* /etc/nginx/conf.d/* 2>/dev/null | head -30 || echo "No proxy_pass found"'
echo ""

# Check nginx error logs for this endpoint
echo "📋 Recent Nginx Error Logs:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo tail -20 /var/log/nginx/error.log 2>/dev/null | grep -i "scenarios\|timeout\|502" || echo "No relevant errors found"'
echo ""

# Test the endpoint directly (bypassing nginx)
echo "🧪 Testing endpoint directly on port 8000:"
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'curl -X POST http://localhost:8000/api/v1/scenarios/run -H "Content-Type: application/json" -d "{\"scenario_name\":\"test\",\"year\":2025,\"steps\":1,\"shocks\":{\"realgdp\":1.0}}" --max-time 5 2>&1 | head -20'
echo ""

echo "💡 If direct test works but nginx fails, check timeout settings"
