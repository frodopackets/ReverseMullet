terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables are now defined in variables.tf

# Data sources
data "aws_caller_identity" "current" {}

# Cognito User Pool
resource "aws_cognito_user_pool" "bedrock_chat_pool" {
  name = "${var.project_name}-user-pool-${var.environment}"

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # User attributes
  username_attributes = ["email"]
  
  # Auto-verified attributes
  auto_verified_attributes = ["email"]

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # User pool add-ons
  user_pool_add_ons {
    advanced_security_mode = "OFF"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Cognito User Pool Client
resource "aws_cognito_user_pool_client" "bedrock_chat_client" {
  name         = "${var.project_name}-client-${var.environment}"
  user_pool_id = aws_cognito_user_pool.bedrock_chat_pool.id

  # Client settings
  generate_secret = false
  
  # OAuth settings
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  
  # Callback URLs - ALB endpoints for OAuth flow
  callback_urls = [
    "http://localhost:3000",
    "https://main.d1tq2relshaprns.amplifyapp.com",
    var.domain_name != "" ? "https://${var.domain_name}/oauth2/idpresponse" : "http://${aws_lb.ecs_alb.dns_name}/oauth2/idpresponse"
  ]
  
  logout_urls = [
    "http://localhost:3000",
    "https://main.d1tq2relshaprns.amplifyapp.com",
    var.domain_name != "" ? "https://${var.domain_name}" : "http://${aws_lb.ecs_alb.dns_name}"
  ]

  # Token validity (in minutes for access/id tokens, days for refresh)
  access_token_validity  = 60    # 1 hour
  id_token_validity     = 60    # 1 hour
  refresh_token_validity = 30   # 30 days
  
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  # Prevent user existence errors
  prevent_user_existence_errors = "ENABLED"

  # Explicit auth flows
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}

# Cognito User Pool Domain
resource "aws_cognito_user_pool_domain" "bedrock_chat_domain" {
  domain       = "${var.project_name}-${var.environment}-${random_string.domain_suffix.result}"
  user_pool_id = aws_cognito_user_pool.bedrock_chat_pool.id
}

# Random string for unique domain
resource "random_string" "domain_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Lambda infrastructure removed - replaced with ECS Fargate

# Note: Lambda functions, IAM roles, and related resources have been moved to ECS Fargate
# See ecs-fargate.tf and api-gateway-ecs.tf for the new infrastructure

# API Gateway resources removed - migrated to ALB-only architecture
# This saves ~$35+/month by eliminating API Gateway + VPC Link costs

# API Gateway resources completely removed - using ALB-only architecture

# Outputs - Updated for ALB-only architecture
output "alb_dns_name" {
  description = "ALB DNS Name"
  value       = aws_lb.ecs_alb.dns_name
}

output "chat_endpoint" {
  description = "Chat API Endpoint via ALB"
  value       = var.domain_name != "" ? "https://${var.domain_name}/chat" : "http://${aws_lb.ecs_alb.dns_name}/chat"
}

output "router_chat_endpoint" {
  description = "Router Chat API Endpoint via ALB"
  value       = var.domain_name != "" ? "https://${var.domain_name}/router-chat" : "http://${aws_lb.ecs_alb.dns_name}/router-chat"
}

output "health_endpoint" {
  description = "Health Check Endpoint via ALB"
  value       = var.domain_name != "" ? "https://${var.domain_name}/health" : "http://${aws_lb.ecs_alb.dns_name}/health"
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.bedrock_chat_pool.id
}

output "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  value       = aws_cognito_user_pool_client.bedrock_chat_client.id
}

output "cognito_domain" {
  description = "Cognito Hosted UI Domain"
  value       = "https://${aws_cognito_user_pool_domain.bedrock_chat_domain.domain}.auth.${var.aws_region}.amazoncognito.com"
}