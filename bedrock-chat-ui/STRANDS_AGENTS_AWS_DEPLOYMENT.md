# Strands Agents AWS Deployment Strategy

## 🎯 **Deployment Architecture**

```
Amplify UI → ALB → ECS Fargate → Strands Agents → Bedrock + MCP Servers
```

### **Components**
- **Frontend**: Amplify (already deployed)
- **Load Balancer**: Application Load Balancer
- **Compute**: ECS Fargate containers
- **Agents**: Strands Router + AWS Pricing Agent
- **External**: Bedrock models + AWS Labs MCP servers

## 🏗️ **Recommended Deployment: ECS Fargate**

### **Why ECS Fargate?**
✅ **Serverless containers** - No EC2 management
✅ **Supports long-running processes** - Perfect for MCP servers
✅ **Auto-scaling** - Scales with demand
✅ **Cost-effective** - Pay only for what you use
✅ **Full Python environment** - Supports uvx, MCP, Strands
✅ **Internet access** - Can reach AWS Labs MCP servers

## 📦 **Container Strategy**

### **Option 1: Single Container (Recommended)**
```
Container: strands-agents-api
├── Router Orchestrator
├── AWS Pricing Agent
├── FastAPI web server
├── MCP client dependencies (uvx, uv)
└── Strands SDK
```

### **Option 2: Multi-Container**
```
Container 1: router-agent
Container 2: pricing-agent
Container 3: nginx (load balancer)
```

## 🚀 **Implementation Plan**

### **Step 1: Create FastAPI Wrapper**

Create a web API that wraps your Strands Agents:

```python
# api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import logging
from router_orchestrator import RouterOrchestrator

app = FastAPI(title="Strands Agents API")
orchestrator = RouterOrchestrator()

class ChatRequest(BaseModel):
    message: str
    user_id: str = None

class ChatResponse(BaseModel):
    id: str
    content: str
    role: str
    timestamp: str
    agent_type: str = None
    intent_analysis: dict = None
    orchestration_metadata: dict = None

@app.post("/router-chat", response_model=ChatResponse)
async def router_chat(request: ChatRequest):
    try:
        response = await orchestrator.process_query(
            request.message, 
            request.user_id
        )
        
        return ChatResponse(
            id=f"assistant-{int(time.time() * 1000)}",
            content=response['content'],
            role="assistant",
            timestamp=datetime.now().isoformat(),
            agent_type=response.get('agent_type'),
            intent_analysis=response.get('intent_analysis'),
            orchestration_metadata=response.get('orchestration_metadata')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    status = orchestrator.get_orchestration_status()
    return {"status": "healthy", "orchestration": status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### **Step 2: Create Dockerfile**

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv and uvx for MCP servers
RUN pip install uv
RUN pip install uvx

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY api_server.py .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "api_server.py"]
```

### **Step 3: Create requirements.txt**

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
strands-agents>=1.0.0
mcp>=0.1.0
boto3>=1.34.0
asyncio-mqtt>=0.13.0
python-multipart==0.0.6
```

### **Step 4: ECS Infrastructure (Terraform)**

```hcl
# ecs-infrastructure.tf
resource "aws_ecs_cluster" "strands_agents" {
  name = "strands-agents-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "strands_agents_api" {
  family                   = "strands-agents-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"  # 1 vCPU
  memory                   = "2048"  # 2 GB
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "strands-agents-api"
      image = "${aws_ecr_repository.strands_agents.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "BEDROCK_MODEL_ID"
          value = "amazon.nova-lite-v1:0"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.strands_agents.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}

resource "aws_ecs_service" "strands_agents_api" {
  name            = "strands-agents-api"
  cluster         = aws_ecs_cluster.strands_agents.id
  task_definition = aws_ecs_task_definition.strands_agents_api.arn
  desired_count   = 2  # For high availability
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.strands_agents.arn
    container_name   = "strands-agents-api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.strands_agents]
}

# Application Load Balancer
resource "aws_lb" "strands_agents" {
  name               = "strands-agents-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false
}

resource "aws_lb_target_group" "strands_agents" {
  name     = "strands-agents-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "strands_agents" {
  load_balancer_arn = aws_lb.strands_agents.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.strands_agents.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.strands_agents.arn
  }
}
```

### **Step 5: IAM Roles**

```hcl
# iam-roles.tf
resource "aws_iam_role" "ecs_execution_role" {
  name = "strands-agents-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "strands-agents-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_bedrock_policy" {
  name = "bedrock-access-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-lite-v1:0"
        ]
      }
    ]
  })
}
```

## 🚀 **Deployment Steps**

### **Step 1: Build and Push Container**

```bash
# Build container
docker build -t strands-agents-api .

# Tag for ECR
docker tag strands-agents-api:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/strands-agents:latest

# Push to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/strands-agents:latest
```

### **Step 2: Deploy Infrastructure**

```bash
# Initialize Terraform
cd terraform
terraform init

# Plan deployment
terraform plan

# Deploy
terraform apply
```

### **Step 3: Update Amplify Environment Variables**

```bash
# Get ALB URL from Terraform output
STRANDS_API_URL=$(terraform output -raw alb_dns_name)

# Update Amplify environment variables
aws amplify put-app --app-id $AMPLIFY_APP_ID --environment-variables NEXT_PUBLIC_API_URL=https://$STRANDS_API_URL
```

## 💰 **Cost Estimation**

### **Monthly Costs (us-east-1)**
- **ECS Fargate (2 tasks)**: ~$50-70/month
- **Application Load Balancer**: ~$16/month
- **CloudWatch Logs**: ~$5/month
- **Data Transfer**: ~$5-10/month
- **Bedrock Nova Lite**: ~$10-50/month (usage-based)

**Total**: ~$86-151/month

## 🔧 **Alternative: EC2 with Docker Compose**

If you prefer EC2:

```yaml
# docker-compose.yml
version: '3.8'
services:
  strands-agents:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AWS_REGION=us-east-1
      - BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Deploy on EC2:
```bash
# On EC2 instance
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy
docker-compose up -d
```

## 🎯 **Next Steps**

1. **Choose deployment method** (ECS Fargate recommended)
2. **Create FastAPI wrapper** for your Strands Agents
3. **Build and test container locally**
4. **Deploy infrastructure** using Terraform
5. **Update Amplify** to point to new API endpoint
6. **Test end-to-end** functionality

Would you like me to help you implement any of these steps?