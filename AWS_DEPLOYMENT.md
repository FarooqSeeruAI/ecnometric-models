# AWS Deployment Guide for CGE Model FastAPI Server

This guide covers deploying the CGE Model FastAPI application to AWS using multiple deployment options.

## Deployment Options

### Option 1: AWS ECS with Fargate (Recommended)
- **Best for**: Production deployments, auto-scaling, managed infrastructure
- **Pros**: No server management, auto-scaling, load balancing, high availability
- **Cons**: Slightly more complex setup

### Option 2: AWS EC2
- **Best for**: Simple deployments, full control
- **Pros**: Simple, predictable costs, full control
- **Cons**: Manual scaling, server management required

### Option 3: AWS App Runner
- **Best for**: Quick deployments, automatic scaling
- **Pros**: Very simple, auto-scaling, managed
- **Cons**: Less control, newer service

### Option 4: AWS Lambda + API Gateway
- **Best for**: Serverless, pay-per-use
- **Pros**: No server management, cost-effective for low traffic
- **Cons**: Cold starts, 15-minute timeout limit, not ideal for long-running model simulations

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured:
   ```bash
   aws --version
   aws configure
   ```
3. **Docker** installed (for building images)
4. **AWS ECR** access (for container registry)

## Option 1: AWS ECS with Fargate (Recommended)

### Step 1: Build and Push Docker Image to ECR

1. **Create ECR Repository**:
   ```bash
   aws ecr create-repository --repository-name cge-model-api --region us-east-1
   ```

2. **Get ECR Login**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   ```

3. **Build Docker Image**:
   ```bash
   docker build -t cge-model-api .
   ```

4. **Tag Image**:
   ```bash
   docker tag cge-model-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/cge-model-api:latest
   ```

5. **Push to ECR**:
   ```bash
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/cge-model-api:latest
   ```

### Step 2: Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name cge-model-cluster --region us-east-1
```

### Step 3: Create Task Definition

Create `ecs-task-definition.json` (see below) and register it:

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

### Step 4: Create ECS Service

```bash
aws ecs create-service \
  --cluster cge-model-cluster \
  --service-name cge-model-api \
  --task-definition cge-model-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/cge-api-tg/xxx,containerName=cge-model-api,containerPort=8000"
```

### Step 5: Create Application Load Balancer

1. Create Target Group:
   ```bash
   aws elbv2 create-target-group \
     --name cge-api-tg \
     --protocol HTTP \
     --port 8000 \
     --vpc-id vpc-xxx \
     --target-type ip \
     --health-check-path /health
   ```

2. Create Load Balancer:
   ```bash
   aws elbv2 create-load-balancer \
     --name cge-api-alb \
     --subnets subnet-xxx subnet-yyy \
     --security-groups sg-xxx
   ```

3. Create Listener:
   ```bash
   aws elbv2 create-listener \
     --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:xxx:loadbalancer/app/cge-api-alb/xxx \
     --protocol HTTP \
     --port 80 \
     --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/cge-api-tg/xxx
   ```

## Option 2: AWS EC2 Deployment

### Step 1: Launch EC2 Instance

1. **Launch EC2 Instance**:
   - AMI: Amazon Linux 2023 or Ubuntu 22.04
   - Instance Type: t3.medium or larger (for model computations)
   - Security Group: Allow HTTP (80) and HTTPS (443) from your IP
   - Storage: 20GB minimum

2. **Connect to Instance**:
   ```bash
   ssh -i your-key.pem ec2-user@<instance-ip>
   ```

### Step 2: Install Dependencies

**For Amazon Linux**:
```bash
sudo yum update -y
sudo yum install -y docker git python3.11 python3-pip
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user
```

**For Ubuntu**:
```bash
sudo apt update
sudo apt install -y docker.io git python3.11 python3-pip
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

### Step 3: Clone and Deploy

```bash
# Clone repository
git clone <your-repo-url>
cd cge_model

# Build and run with Docker
docker build -t cge-model-api .
docker run -d -p 80:8000 --name cge-api cge-model-api

# Or install directly
pip3 install -r requirements_api.txt
python3 api_server.py
```

### Step 4: Set Up Nginx (Optional but Recommended)

```bash
sudo yum install -y nginx  # Amazon Linux
# or
sudo apt install -y nginx  # Ubuntu

# Configure nginx
sudo nano /etc/nginx/conf.d/cge-api.conf
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## Option 3: AWS App Runner

### Step 1: Create App Runner Service

1. Go to AWS Console → App Runner → Create Service
2. Source: ECR (use the image from Step 1)
3. Configuration:
   - Port: 8000
   - Start command: `uvicorn api_server:app --host 0.0.0.0 --port 8000`
4. Auto-deploy: Enabled
5. Create Service

## Option 4: AWS Lambda (Not Recommended for Long-Running Simulations)

Lambda has a 15-minute timeout limit, which may not be sufficient for complex model simulations. Consider this only for simple queries.

## Configuration Files

### ECS Task Definition

See `ecs-task-definition.json` for the complete task definition.

### Environment Variables

Set these in your deployment:

- `PYTHONUNBUFFERED=1` - For proper logging
- `MODEL_DIR=/app` - Model directory path
- Any other configuration needed

## Storage Considerations

### For Output Files

1. **Use S3** for storing scenario outputs:
   - Create S3 bucket: `cge-model-outputs`
   - Modify `api_server.py` to save outputs to S3
   - Return S3 URLs instead of local file paths

2. **Use EFS** (Elastic File System) for shared storage:
   - Mount EFS to ECS tasks
   - Share outputs across multiple instances

### For Model Data Files

- Include in Docker image (if < 10GB)
- Or use S3 and download at startup
- Or use EFS for shared access

## Monitoring and Logging

### CloudWatch Logs

ECS automatically sends logs to CloudWatch. View logs:

```bash
aws logs tail /ecs/cge-model-api --follow
```

### CloudWatch Metrics

Monitor:
- CPU utilization
- Memory utilization
- Request count
- Error rate

### Set Up Alarms

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name cge-api-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

## Security Best Practices

1. **Use IAM Roles** instead of access keys
2. **Enable VPC** for ECS tasks
3. **Use Security Groups** to restrict access
4. **Enable HTTPS** with ACM certificate
5. **Use Secrets Manager** for sensitive data
6. **Enable CloudTrail** for audit logging

## Cost Optimization

1. **Use Spot Instances** for non-critical workloads
2. **Right-size instances** based on actual usage
3. **Use Reserved Instances** for predictable workloads
4. **Enable Auto Scaling** to scale down during low usage
5. **Use S3 Lifecycle Policies** to archive old outputs

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs cge-model-api

# Check ECS task logs
aws logs tail /ecs/cge-model-api --follow
```

### High Memory Usage

- Increase task memory in task definition
- Optimize model code
- Use larger instance types

### Slow Response Times

- Enable CloudFront CDN
- Use Application Load Balancer
- Optimize model computations
- Use caching where possible

## Next Steps

1. ✅ Choose deployment option
2. ✅ Set up infrastructure
3. ✅ Deploy application
4. ✅ Configure monitoring
5. ✅ Set up CI/CD pipeline
6. ✅ Test all endpoints
7. ✅ Configure custom domain
8. ✅ Set up backups

## CI/CD Pipeline

Consider setting up:
- **GitHub Actions** or **AWS CodePipeline** for automated deployments
- **Automated testing** before deployment
- **Blue/Green deployments** for zero-downtime updates
