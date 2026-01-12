# OCI Deployment Guide for CGE Model

Deployment instructions for Oracle Cloud Infrastructure (OCI) Ubuntu 20.04 instance.

## Prerequisites

- OCI instance running (Ubuntu 20.04)
- SSH access to the instance
- SSH private key file

## Step 1: Connect to OCI Instance

```bash
# Replace with your actual values
ssh -i /path/to/your/private_key ubuntu@<instance_public_ip>
```

## Step 2: Clone Repository

Once connected to the instance:

```bash
# Install git if not already installed
sudo apt-get update
sudo apt-get install -y git

# Clone the repository
git clone https://github.com/FarooqSeeruAI/ecnometric-models.git
cd ecnometric-models
```

## Step 3: Run Deployment Script

```bash
# Make script executable
chmod +x deploy_oci.sh

# Run deployment
./deploy_oci.sh
```

Or manually follow the steps below.

## Step 4: Manual Setup (Alternative)

### Install Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and build tools
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
pip3 install --upgrade pip
pip3 install -r requirements_api.txt
```

### Create Directories

```bash
mkdir -p outputs
mkdir -p temp_closures
mkdir -p logs
```

### Set Permissions

```bash
chmod +x *.py
chmod +x *.sh
```

## Step 5: Configure Firewall

```bash
# Allow port 8000 for FastAPI
sudo ufw allow 8000/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

## Step 6: Start the API Server

### Option 1: Run Directly (Testing)

```bash
python3 api_server.py
```

### Option 2: Run as Systemd Service (Production)

```bash
# Start service
sudo systemctl start cge-model-api

# Enable on boot
sudo systemctl enable cge-model-api

# Check status
sudo systemctl status cge-model-api

# View logs
sudo journalctl -u cge-model-api -f
```

## Step 7: Configure OCI Security Rules

In OCI Console:

1. Go to **Networking** → **Virtual Cloud Networks**
2. Select your VCN
3. Go to **Security Lists**
4. Add Ingress Rule:
   - **Source Type**: CIDR
   - **Source CIDR**: `0.0.0.0/0` (or specific IPs)
   - **IP Protocol**: TCP
   - **Destination Port Range**: `8000`
   - **Description**: "CGE Model API"

## Step 8: Access the API

Once running, access via:

- **Local (on instance)**: http://localhost:8000/docs
- **Public**: http://<instance_public_ip>:8000/docs
- **OpenAPI Spec**: http://<instance_public_ip>:8000/openapi.json

## Step 9: Set Up Domain (Optional)

### Using OCI Load Balancer

1. Create Load Balancer in OCI Console
2. Configure backend set pointing to instance:8000
3. Configure SSL certificate
4. Update DNS to point to load balancer

### Using Nginx Reverse Proxy

```bash
# Install nginx
sudo apt-get install -y nginx

# Configure nginx
sudo nano /etc/nginx/sites-available/cge-model

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/cge-model /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 10: Set Up SSL (Optional)

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring

### Check API Status

```bash
curl http://localhost:8000/health
```

### View Logs

```bash
# Systemd service logs
sudo journalctl -u cge-model-api -f

# Application logs (if logging to file)
tail -f logs/api.log
```

### Check Process

```bash
ps aux | grep api_server
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Permission Denied

```bash
# Check file permissions
ls -la api_server.py

# Fix permissions
chmod +x api_server.py
```

### Module Not Found

```bash
# Reinstall requirements
pip3 install -r requirements_api.txt --force-reinstall
```

### Firewall Issues

```bash
# Check firewall status
sudo ufw status

# Check OCI security rules in console
```

## Backup and Updates

### Backup Configuration

```bash
# Create backup
tar -czf cge-model-backup-$(date +%Y%m%d).tar.gz \
    *.py *.yml *.model *.md \
    database/ closures/ \
    --exclude=outputs --exclude=temp_closures
```

### Update Code

```bash
# Pull latest changes
git pull origin main

# Restart service
sudo systemctl restart cge-model-api
```

## Environment Variables

Create `.env` file for configuration:

```bash
cat > .env <<EOF
MODEL_DIR=$(pwd)
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
EOF
```

## Performance Tuning

### Increase File Descriptors

```bash
# Edit limits
sudo nano /etc/security/limits.conf

# Add:
* soft nofile 65535
* hard nofile 65535
```

### Optimize Python

```bash
# Use production WSGI server
pip3 install gunicorn

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app --bind 0.0.0.0:8000
```

## Security Checklist

- [ ] Change default SSH port (optional)
- [ ] Use SSH keys only (disable password auth)
- [ ] Configure firewall rules
- [ ] Set up SSL/TLS
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup data regularly

## Next Steps

1. Test API endpoints
2. Set up monitoring/alerting
3. Configure auto-scaling (if needed)
4. Set up CI/CD pipeline
5. Configure backup strategy
