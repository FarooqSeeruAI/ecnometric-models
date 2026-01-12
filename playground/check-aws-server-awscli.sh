#!/bin/bash
# AWS CLI-based status check for FastAPI server
# Uses AWS CLI to check instance and optionally SSM to run commands

EC2_IP="13.203.193.142"
INSTANCE_ID="i-045456211a080a8bc"
AWS_REGION="ap-south-1"

echo "🔍 Checking AWS FastAPI Server Status (via AWS CLI)"
echo "===================================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed"
    echo ""
    echo "Install AWS CLI:"
    echo "  macOS: brew install awscli"
    echo "  Linux: https://aws.amazon.com/cli/"
    echo ""
    echo "Then configure it with: aws configure"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured"
    echo "Run: aws configure"
    exit 1
fi

echo "✅ AWS CLI configured"
echo ""

# Get instance status
echo "📊 EC2 Instance Status:"
INSTANCE_STATE=$(aws ec2 describe-instances --instance-ids ${INSTANCE_ID} --region ${AWS_REGION} --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null)

if [ "$INSTANCE_STATE" = "running" ]; then
    echo "✅ Instance is RUNNING"
else
    echo "❌ Instance state: ${INSTANCE_STATE}"
    exit 1
fi

# Get instance details
echo ""
echo "📋 Instance Details:"
aws ec2 describe-instances --instance-ids ${INSTANCE_ID} --region ${AWS_REGION} --query 'Reservations[0].Instances[0].[PublicIpAddress,PrivateIpAddress,InstanceType,LaunchTime]' --output table

# Get security group rules
echo ""
echo "🔒 Security Group Rules:"
SG_ID=$(aws ec2 describe-instances --instance-ids ${INSTANCE_ID} --region ${AWS_REGION} --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text)

echo "Security Group: ${SG_ID}"
aws ec2 describe-security-groups --group-ids ${SG_ID} --region ${AWS_REGION} --query 'SecurityGroups[0].IpPermissions[*].[IpProtocol,FromPort,ToPort,IpRanges[0].CidrIp]' --output table

# Try to use SSM (Systems Manager) to run commands without SSH
echo ""
echo "🔧 Checking SSM Agent Status:"
SSM_STATUS=$(aws ssm describe-instance-information --filters "Key=InstanceIds,Values=${INSTANCE_ID}" --region ${AWS_REGION} --query 'InstanceInformationList[0].PingStatus' --output text 2>/dev/null)

if [ "$SSM_STATUS" = "Online" ]; then
    echo "✅ SSM Agent is Online - Can run commands via SSM"
    echo ""
    
    # Check Docker containers via SSM
    echo "📦 Docker Containers (via SSM):"
    COMMAND_ID=$(aws ssm send-command --instance-ids ${INSTANCE_ID} --region ${AWS_REGION} --document-name "AWS-RunShellScript" --parameters 'commands=["docker ps --format \"table {{.Names}}\t{{.Status}}\t{{.Ports}}\""]' --query 'Command.CommandId' --output text)
    echo "Command ID: ${COMMAND_ID}"
    echo "Waiting for command to complete..."
    sleep 3
    
    aws ssm get-command-invocation --command-id ${COMMAND_ID} --instance-id ${INSTANCE_ID} --region ${AWS_REGION} --query 'StandardOutputContent' --output text 2>/dev/null || echo "Command still running or failed"
    
    # Check health endpoint via SSM
    echo ""
    echo "🏥 Health Check (via SSM):"
    HEALTH_CMD_ID=$(aws ssm send-command --instance-ids ${INSTANCE_ID} --region ${AWS_REGION} --document-name "AWS-RunShellScript" --parameters 'commands=["curl -s http://localhost:8000/health"]' --query 'Command.CommandId' --output text)
    
    sleep 3
    aws ssm get-command-invocation --command-id ${HEALTH_CMD_ID} --instance-id ${INSTANCE_ID} --region ${AWS_REGION} --query 'StandardOutputContent' --output text 2>/dev/null || echo "Health check failed"
    
else
    echo "❌ SSM Agent is not Online (Status: ${SSM_STATUS:-Not found})"
    echo "   Cannot run remote commands without SSH"
    echo ""
    echo "To enable SSM:"
    echo "1. Install SSM Agent on the instance (usually pre-installed on Ubuntu)"
    echo "2. Attach IAM role with SSM permissions to the instance"
    echo "3. Wait a few minutes for agent to register"
fi

# Test external HTTP access
echo ""
echo "🌍 External Access Test:"
echo "Testing http://${EC2_IP}:8000/health"
if curl -s --connect-timeout 5 http://${EC2_IP}:8000/health > /dev/null 2>&1; then
    echo "✅ Port 8000 accessible externally"
    curl -s http://${EC2_IP}:8000/health
else
    echo "❌ Port 8000 not accessible (check security group)"
fi

echo ""
echo "Testing http://${EC2_IP}/health"
if curl -s --connect-timeout 5 http://${EC2_IP}/health > /dev/null 2>&1; then
    echo "✅ Port 80 accessible externally"
    curl -s http://${EC2_IP}/health
else
    echo "❌ Port 80 not accessible"
fi

echo ""
echo "✅ Status check complete!"
echo ""
echo "📝 Access URLs:"
echo "   - Swagger UI: http://${EC2_IP}:8000/docs"
echo "   - Health: http://${EC2_IP}:8000/health"
