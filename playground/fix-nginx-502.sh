#!/bin/bash
# Fix nginx 502 error for /api/v1/scenarios/run endpoint

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="13.203.193.142"

echo "🔧 Fixing nginx configuration for 502 error"
echo "==========================================="

# Create improved nginx config
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo bash -c "cat > /etc/nginx/sites-available/cge-api << '\''NGINXEOF
server {
    listen 80;
    server_name 13.203.193.142;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Connection \"\";
    }
}
NGINXEOF
"'

# Enable site
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo ln -sf /etc/nginx/sites-available/cge-api /etc/nginx/sites-enabled/cge-api'

# Test and reload
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} 'sudo nginx -t && sudo systemctl reload nginx'

echo "✅ Nginx configuration updated!"
