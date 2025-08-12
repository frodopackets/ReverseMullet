# MCP Proxy Service for Strands Agents
# Provides HTTP access to MCP servers for containerized agents

# ECR Repository for MCP Proxy
resource "aws_ecr_repository" "mcp_proxy" {
  name                 = "${var.project_name}-mcp-proxy-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}-mcp-proxy-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ECS Task Definition for MCP Proxy
resource "aws_ecs_task_definition" "mcp_proxy" {
  family                   = "${var.project_name}-mcp-proxy-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "mcp-proxy"
      image = "${aws_ecr_repository.mcp_proxy.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8001
          hostPort      = 8001
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "MCP_PROXY_PORT"
          value = "8001"
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "FASTMCP_LOG_LEVEL"
          value = "ERROR"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.mcp_proxy.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      
      healthCheck = {
        command = ["CMD-SHELL", "curl -f http://localhost:8001/health || exit 1"]
        interval = 30
        timeout = 10
        retries = 3
        startPeriod = 60
      }
      
      essential = true
    }
  ])

  tags = {
    Name        = "${var.project_name}-mcp-proxy-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudWatch Log Group for MCP Proxy
resource "aws_cloudwatch_log_group" "mcp_proxy" {
  name              = "/ecs/${var.project_name}-mcp-proxy-${var.environment}"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-mcp-proxy-logs-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Security Group for MCP Proxy
resource "aws_security_group" "mcp_proxy" {
  name        = "${var.project_name}-mcp-proxy-${var.environment}"
  description = "Security group for MCP Proxy service"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = 8001
    to_port         = 8001
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
    description     = "MCP Proxy access from agents"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic for MCP servers"
  }

  tags = {
    Name        = "${var.project_name}-mcp-proxy-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ECS Service for MCP Proxy
resource "aws_ecs_service" "mcp_proxy" {
  name            = "${var.project_name}-mcp-proxy-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.mcp_proxy.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    assign_public_ip = true
    security_groups  = [aws_security_group.mcp_proxy.id]
  }

  # Service discovery for internal communication
  service_registries {
    registry_arn = aws_service_discovery_service.mcp_proxy.arn
  }

  depends_on = [
    aws_service_discovery_service.mcp_proxy
  ]

  tags = {
    Name        = "${var.project_name}-mcp-proxy-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Use existing service discovery namespace from ecs-fargate.tf

# Service Discovery Service for MCP Proxy
resource "aws_service_discovery_service" "mcp_proxy" {
  name = "mcp-proxy"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  tags = {
    Name        = "${var.project_name}-mcp-proxy-discovery-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Output for MCP Proxy service URL (internal)
output "mcp_proxy_internal_url" {
  description = "Internal URL for MCP Proxy service"
  value       = "http://mcp-proxy.${var.project_name}-${var.environment}.local:8001"
}