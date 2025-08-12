# ALB-only architecture for ECS Fargate
# VPC Link removed - saves $18/month by eliminating API Gateway integration

# Application Load Balancer for ECS (Public)
resource "aws_lb" "ecs_alb" {
  name               = "${var.project_name}-ecs-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_alb.id]
  subnets            = data.aws_subnets.default.ids

  enable_deletion_protection = false

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Security Group for Public ALB
resource "aws_security_group" "ecs_alb" {
  name        = "${var.project_name}-ecs-alb-${var.environment}"
  description = "Security group for public ECS ALB"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTP traffic from allowed IPs"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTPS traffic from allowed IPs"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-ecs-alb-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Target Group for ECS Service
resource "aws_lb_target_group" "ecs_targets" {
  name        = "${var.project_name}-ecs-tg-${var.environment}"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
    port                = "traffic-port"
    protocol            = "HTTP"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# ALB Listener - HTTP (redirect to HTTPS when domain is provided)
resource "aws_lb_listener" "ecs_listener_http" {
  count = var.domain_name != "" ? 1 : 0
  
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# ACM Certificate for HTTPS
resource "aws_acm_certificate" "alb_cert" {
  count = var.domain_name != "" ? 1 : 0
  
  domain_name       = var.domain_name
  validation_method = "DNS"

  tags = {
    Name        = "${var.project_name}-cert-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Self-signed certificate for demo HTTPS
resource "tls_private_key" "demo_key" {
  count = var.domain_name == "" ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "demo_cert" {
  count = var.domain_name == "" ? 1 : 0
  
  private_key_pem = tls_private_key.demo_key[0].private_key_pem

  subject {
    common_name  = "*.elb.amazonaws.com"
    organization = "Demo"
  }

  validity_period_hours = 8760 # 1 year

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

resource "aws_acm_certificate" "demo_cert" {
  count = var.domain_name == "" ? 1 : 0
  
  private_key      = tls_private_key.demo_key[0].private_key_pem
  certificate_body = tls_self_signed_cert.demo_cert[0].cert_pem

  tags = {
    Name        = "${var.project_name}-demo-cert-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ALB Listener - HTTPS (with custom domain)
resource "aws_lb_listener" "ecs_listener_https" {
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.domain_name != "" ? aws_acm_certificate.alb_cert[0].arn : null

  count = var.domain_name != "" ? 1 : 0

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_targets.arn
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# ALB Listener - HTTPS (demo with self-signed cert)
resource "aws_lb_listener" "ecs_listener_https_demo" {
  count = var.domain_name == "" ? 1 : 0
  
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.demo_cert[0].arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_targets.arn
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# HTTP listener for demo (when no custom domain)
resource "aws_lb_listener" "ecs_listener_demo" {
  count = var.domain_name == "" ? 1 : 0
  
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = "80"
  protocol          = "HTTP"

  # Default action - forward to ECS targets (no auth for demo)
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_targets.arn
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Cognito Authentication Rule for HTTPS (with domain)
resource "aws_lb_listener_rule" "cognito_auth_https" {
  count = var.domain_name != "" ? 1 : 0
  
  listener_arn = aws_lb_listener.ecs_listener_https[0].arn
  priority     = 100

  action {
    type = "authenticate-cognito"
    
    authenticate_cognito {
      user_pool_arn               = aws_cognito_user_pool.bedrock_chat_pool.arn
      user_pool_client_id         = aws_cognito_user_pool_client.bedrock_chat_client.id
      user_pool_domain           = aws_cognito_user_pool_domain.bedrock_chat_domain.domain
      authentication_request_extra_params = {
        display = "page"
        prompt  = "login"
      }
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_targets.arn
  }

  condition {
    path_pattern {
      values = ["/chat*", "/router-chat*"]
    }
  }
}

# Cognito Authentication Rule for HTTP demo (without domain) - TEMPORARILY DISABLED
# Cognito requires HTTPS but we're using HTTP ALB
resource "aws_lb_listener_rule" "cognito_auth_demo" {
  count = 0  # Disabled - was: var.domain_name == "" ? 1 : 0
  
  listener_arn = aws_lb_listener.ecs_listener_demo[0].arn
  priority     = 100

  action {
    type = "authenticate-cognito"
    
    authenticate_cognito {
      user_pool_arn               = aws_cognito_user_pool.bedrock_chat_pool.arn
      user_pool_client_id         = aws_cognito_user_pool_client.bedrock_chat_client.id
      user_pool_domain           = aws_cognito_user_pool_domain.bedrock_chat_domain.domain
      authentication_request_extra_params = {
        display = "page"
        prompt  = "login"
      }
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_targets.arn
  }

  condition {
    path_pattern {
      values = ["/chat*", "/router-chat*"]
    }
  }
}

# Health check rule (no auth required)
resource "aws_lb_listener_rule" "health_check" {
  listener_arn = var.domain_name != "" ? aws_lb_listener.ecs_listener_https[0].arn : aws_lb_listener.ecs_listener_demo[0].arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_targets.arn
  }

  condition {
    path_pattern {
      values = ["/health*"]
    }
  }
}

# Update ECS Service to use Target Group
resource "aws_ecs_service" "strands_agents_with_lb" {
  name            = "${var.project_name}-strands-agents-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.strands_agents.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_targets.arn
    container_name   = "strands-agents"
    container_port   = 8000
  }

  # Deployment configuration (using defaults)

  # Enable execute command for debugging
  enable_execute_command = true

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_execution_role_policy,
    aws_iam_role_policy.ecs_bedrock_policy,
    aws_lb_listener.ecs_listener_demo,
    aws_lb_listener.ecs_listener_https
  ]

  # This replaces the original ECS service
  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Target
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = var.ecs_max_capacity
  min_capacity       = var.ecs_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.strands_agents_with_lb.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Auto Scaling Policy - CPU
resource "aws_appautoscaling_policy" "ecs_cpu_policy" {
  name               = "${var.project_name}-cpu-scaling-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = var.cpu_target_value
  }
}

# Auto Scaling Policy - Memory
resource "aws_appautoscaling_policy" "ecs_memory_policy" {
  name               = "${var.project_name}-memory-scaling-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = var.memory_target_value
  }
}

# Scheduled Scaling - Scale Down (Evening)
resource "aws_appautoscaling_scheduled_action" "scale_down" {
  count = var.enable_scheduled_scaling ? 1 : 0

  name               = "${var.project_name}-scale-down-${var.environment}"
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension

  schedule = var.scale_down_schedule

  scalable_target_action {
    min_capacity = 0
    max_capacity = 1
  }
}

# Scheduled Scaling - Scale Up (Morning)
resource "aws_appautoscaling_scheduled_action" "scale_up" {
  count = var.enable_scheduled_scaling ? 1 : 0

  name               = "${var.project_name}-scale-up-${var.environment}"
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension

  schedule = var.scale_up_schedule

  scalable_target_action {
    min_capacity = var.ecs_min_capacity
    max_capacity = var.ecs_max_capacity
  }
}

# API Gateway completely removed - using ALB-only architecture for cost savings
# Direct ALB access with Cognito authentication at listener rule level

# Additional outputs for ECS
output "ecs_cluster_name" {
  description = "ECS Cluster Name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS Service Name"
  value       = aws_ecs_service.strands_agents_with_lb.name
}

output "ecr_repository_url" {
  description = "ECR Repository URL"
  value       = aws_ecr_repository.strands_agents.repository_url
}

output "internal_alb_dns" {
  description = "Internal ALB DNS Name"
  value       = aws_lb.ecs_alb.dns_name
}

# CloudWatch Alarms for monitoring
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${var.project_name}-ecs-cpu-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.cpu_alarm_threshold
  alarm_description   = "This metric monitors ECS CPU utilization"
  alarm_actions       = []  # Add SNS topic ARN here if you want notifications

  dimensions = {
    ServiceName = aws_ecs_service.strands_agents_with_lb.name
    ClusterName = aws_ecs_cluster.main.name
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  alarm_name          = "${var.project_name}-ecs-memory-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.memory_alarm_threshold
  alarm_description   = "This metric monitors ECS memory utilization"
  alarm_actions       = []  # Add SNS topic ARN here if you want notifications

  dimensions = {
    ServiceName = aws_ecs_service.strands_agents_with_lb.name
    ClusterName = aws_ecs_cluster.main.name
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

output "scheduled_scaling_enabled" {
  description = "Whether scheduled scaling is enabled"
  value       = var.enable_scheduled_scaling
}