# Strands Agents Terraform Deployment Guide

## 🎯 Overview

This guide walks you through deploying your Strands Agents (Router + AWS Pricing Agent) to AWS ECS Fargate using Terraform.

## 🏗️ Architecture

```
Amplify UI → ALB → ECS Fargate → Strands Agents → Bedrock + MCP Servers
```

**Components Deployed:**
- **VPC**: Custom VPC with public/private subnets
- **ECS Fargate**: Serverless containers for Strands Agents
- **Application Load Balancer**: Routes traffic to ECS tasks
- **ECR**: Container registry for Docker images
- **IAM Roles**: Permissions for Bedrock access
- **Auto Scaling**: Scales based on CPU/memory usage

## 🚀 Quick Deployment

### Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Docker installed** and running
3. **Terraform installed** (v1.0+)

### One-Command Deployment

```bash
# Make script executable
chmod +x deploy-terraform.sh

# Deploy everything
./deploy-terraform.sh
```

This script will:
1. Build your Docker image
2. Create ECR repository
3. Push image to ECR
4. Deploy all infrastructure with Terraform
5. Output API URLs and next steps

## 📋 Manual Step-by-Step Deployment

### Step 1: Build and Push Docker Image

```bash
# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-east-1

# Build image
docker build -f Dockerfile.agents -t strands-agents:latest .

# Create ECR repository (if needed)
aws ecr create-repository --repository-name strands-agents --region $AWS_REGION

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag and push
docker tag strands-agents:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/strands-agents:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/strands-agents:latest
```

### Step 2: Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Deploy
terraform apply
```

### Step 3: Get Deployment Information

```bash
# Get API URL
terraform output strands_agents_api_url

# Get ALB DNS name
terraform output strands_agents_alb_dns_name
```

## 🔧 Configuration

### Terraform Variables

Edit `terraform/terraform.tfvars`:

```hcl
# Basic Configuration
aws_region   = "us-east-1"
environment  = "dev"
project_name = "strands-agents"

# Container Configuration
strands_agents_cpu           = 1024  # 1 vCPU
strands_agents_memory        = 2048  # 2 GB
strands_agents_desired_count = 2     # Number of tasks
```

### Environment Variables

The containers will have these environment variables:
- `AWS_REGION`: AWS region
- `BEDROCK_MODEL_ID`: amazon.nova-lite-v1:0
- `LOG_LEVEL`: info

## 🧪 Testing Your Deployment

### Health Check

```bash
# Get API URL from Terraform output
API_URL=$(cd terraform && terraform output -raw strands_agents_api_url)

# Test health endpoint
curl $API_URL/health

# Test status endpoint
curl $API_URL/status
```

### Test Chat API

```bash
# Test router-chat endpoint
curl -X POST $API_URL/router-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the cost of a t3.small EC2 instance?"}'
```

### Expected Response

```json
{
  "id": "assistant-1234567890",
  "content": "Based on current AWS pricing data...",
  "role": "assistant",
  "timestamp": "2024-01-15T10:30:00Z",
  "agent_type": "aws_pricing_optimized",
  "intent_analysis": {
    "intent": "aws_pricing",
    "confidence": "high"
  }
}
```

## 🔄 Updating Your Deployment

### Code Changes

```bash
# Build new image with version tag
docker build -f Dockerfile.agents -t strands-agents:v1.1 .

# Deploy with new tag
IMAGE_TAG=v1.1 ./deploy-terraform.sh
```

### Infrastructure Changes

```bash
cd terraform

# Modify terraform.tfvars or .tf files
# Then apply changes
terraform plan
terraform apply
```

## 📊 Monitoring

### CloudWatch Logs

```bash
# View logs
aws logs tail /ecs/strands-agents --follow --region us-east-1
```

### ECS Service Status

```bash
# Get cluster and service names
CLUSTER_NAME=$(cd terraform && terraform output -raw strands_agents_cluster_name)
SERVICE_NAME=$(cd terraform && terraform output -raw strands_agents_service_name)

# Check service status
aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region us-east-1
```

### Auto Scaling

The deployment includes auto scaling based on:
- **CPU utilization**: Scales when > 70%
- **Memory utilization**: Scales when > 80%
- **Min tasks**: 2
- **Max tasks**: 10

## 🔗 Connecting to Amplify

### Update Amplify Environment Variables

```bash
# Get API URL
API_URL=$(cd terraform && terraform output -raw strands_agents_api_url)

# Update Amplify (replace with your app ID)
aws amplify put-app --app-id YOUR_AMPLIFY_APP_ID --environment-variables NEXT_PUBLIC_API_URL=$API_URL
```

### Test End-to-End

1. Open your Amplify app
2. Ask a pricing question: "What's the cost of EC2?"
3. Verify you get a response from the Strands Agents

## 💰 Cost Estimation

### Monthly Costs (us-east-1)

- **ECS Fargate (2 tasks)**: ~$50-70/month
- **Application Load Balancer**: ~$16/month
- **NAT Gateways (2)**: ~$32/month
- **CloudWatch Logs**: ~$5/month
- **Data Transfer**: ~$5-10/month
- **Bedrock Nova Lite**: ~$10-50/month (usage-based)

**Total**: ~$118-183/month

### Cost Optimization

- Use **FARGATE_SPOT** for non-critical workloads (50-70% savings)
- Reduce to **1 NAT Gateway** if high availability isn't critical
- Use **CloudWatch Logs retention** to control log costs

## 🛠️ Troubleshooting

### Common Issues

#### 1. Docker Build Fails
```bash
# Check Dockerfile.agents exists
ls -la Dockerfile.agents

# Check requirements file
ls -la requirements-agents.txt
```

#### 2. ECR Push Fails
```bash
# Re-login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

#### 3. ECS Tasks Not Starting
```bash
# Check task definition
aws ecs describe-task-definition --task-definition strands-agents-dev --region us-east-1

# Check service events
aws ecs describe-services --cluster strands-agents-cluster-dev --services strands-agents-service-dev --region us-east-1
```

#### 4. Health Check Failing
```bash
# Check container logs
aws logs tail /ecs/strands-agents --follow --region us-east-1
```

### Getting Help

1. **Check CloudWatch Logs** for application errors
2. **Review ECS Service Events** for deployment issues
3. **Verify IAM Permissions** for Bedrock access
4. **Test locally** with Docker before deploying

## 🧹 Cleanup

### Destroy Infrastructure

```bash
cd terraform
terraform destroy
```

### Remove ECR Images

```bash
# List images
aws ecr list-images --repository-name strands-agents --region us-east-1

# Delete repository (removes all images)
aws ecr delete-repository --repository-name strands-agents --force --region us-east-1
```

## 🎯 Next Steps

1. **Deploy the infrastructure** using the guide above
2. **Test the API endpoints** to ensure everything works
3. **Update your Amplify app** to use the new API URL
4. **Monitor the service** and adjust scaling as needed
5. **Set up CI/CD** for automated deployments

Your Strands Agents are now running on AWS with full MCP integration! 🚀