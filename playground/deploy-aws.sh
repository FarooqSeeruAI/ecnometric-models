#!/bin/bash
# AWS Deployment Script for CGE Model API
# This script automates the deployment to AWS ECS

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO_NAME="cge-model-api"
ECS_CLUSTER_NAME="cge-model-cluster"
ECS_SERVICE_NAME="cge-model-api"
TASK_DEFINITION_NAME="cge-model-api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AWS deployment...${NC}"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo -e "${YELLOW}AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"
echo -e "${YELLOW}ECR URI: ${ECR_URI}${NC}"

# Step 1: Check if ECR repository exists, create if not
echo -e "${GREEN}Step 1: Checking ECR repository...${NC}"
if ! aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} &>/dev/null; then
    echo -e "${YELLOW}Creating ECR repository...${NC}"
    aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION}
else
    echo -e "${GREEN}ECR repository already exists${NC}"
fi

# Step 2: Login to ECR
echo -e "${GREEN}Step 2: Logging into ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

# Step 3: Build Docker image
echo -e "${GREEN}Step 3: Building Docker image...${NC}"
docker build -t ${ECR_REPO_NAME}:latest .

# Step 4: Tag image
echo -e "${GREEN}Step 4: Tagging Docker image...${NC}"
docker tag ${ECR_REPO_NAME}:latest ${ECR_URI}:latest

# Step 5: Push to ECR
echo -e "${GREEN}Step 5: Pushing Docker image to ECR...${NC}"
docker push ${ECR_URI}:latest

# Step 6: Update ECS task definition with new image
echo -e "${GREEN}Step 6: Updating ECS task definition...${NC}"
# Replace account ID in task definition
sed "s/<account-id>/${AWS_ACCOUNT_ID}/g" ecs-task-definition.json > ecs-task-definition-temp.json
sed "s/<account-id>/${AWS_ACCOUNT_ID}/g" ecs-task-definition-temp.json | \
    sed "s|<account-id>.dkr.ecr.us-east-1.amazonaws.com/cge-model-api:latest|${ECR_URI}:latest|g" > ecs-task-definition-updated.json

# Register new task definition
TASK_DEF_ARN=$(aws ecs register-task-definition \
    --cli-input-json file://ecs-task-definition-updated.json \
    --region ${AWS_REGION} \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo -e "${GREEN}New task definition registered: ${TASK_DEF_ARN}${NC}"

# Step 7: Update ECS service (if it exists)
echo -e "${GREEN}Step 7: Updating ECS service...${NC}"
if aws ecs describe-services --cluster ${ECS_CLUSTER_NAME} --services ${ECS_SERVICE_NAME} --region ${AWS_REGION} --query 'services[0].status' --output text 2>/dev/null | grep -q "ACTIVE"; then
    echo -e "${YELLOW}Updating existing service...${NC}"
    aws ecs update-service \
        --cluster ${ECS_CLUSTER_NAME} \
        --service ${ECS_SERVICE_NAME} \
        --task-definition ${TASK_DEF_ARN} \
        --force-new-deployment \
        --region ${AWS_REGION} > /dev/null
    
    echo -e "${GREEN}Service update initiated. Waiting for deployment to complete...${NC}"
    aws ecs wait services-stable \
        --cluster ${ECS_CLUSTER_NAME} \
        --services ${ECS_SERVICE_NAME} \
        --region ${AWS_REGION}
    
    echo -e "${GREEN}Deployment completed successfully!${NC}"
else
    echo -e "${YELLOW}Service does not exist. Please create it manually or use the AWS Console.${NC}"
    echo -e "${YELLOW}Task definition ARN: ${TASK_DEF_ARN}${NC}"
fi

# Cleanup
rm -f ecs-task-definition-temp.json ecs-task-definition-updated.json

echo -e "${GREEN}Deployment script completed!${NC}"
