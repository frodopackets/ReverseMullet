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

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "bedrock-chat"
}

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
  
  # Callback URLs (update these with your actual domain)
  callback_urls = [
    "http://localhost:3000",
    "https://main.d1tq2relshaprns.amplifyapp.com"
  ]
  
  logout_urls = [
    "http://localhost:3000",
    "https://main.d1tq2relshaprns.amplifyapp.com"
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

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Policy for Bedrock access
resource "aws_iam_role_policy" "lambda_bedrock_policy" {
  name = "${var.project_name}-bedrock-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-lite-v1:0"
        ]
      }
    ]
  })
}

# Attach basic execution role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

# Create deployment package for Lambda
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../lambda"
  output_path = "lambda-deployment.zip"
}

# Chat Lambda Function
resource "aws_lambda_function" "chat_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-chat-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "chat-handler.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "nodejs18.x"
  timeout         = 30

  environment {
    variables = {
      BEDROCK_REGION = var.aws_region
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Health Lambda Function
resource "aws_lambda_function" "health_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-health-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "health-handler.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "nodejs18.x"
  timeout         = 30

  environment {
    variables = {
      BEDROCK_REGION = var.aws_region
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "bedrock_api" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "API Gateway for Bedrock Nova Lite Chat"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# API Gateway Resources
resource "aws_api_gateway_resource" "chat_resource" {
  rest_api_id = aws_api_gateway_rest_api.bedrock_api.id
  parent_id   = aws_api_gateway_rest_api.bedrock_api.root_resource_id
  path_part   = "chat"
}

resource "aws_api_gateway_resource" "health_resource" {
  rest_api_id = aws_api_gateway_rest_api.bedrock_api.id
  parent_id   = aws_api_gateway_rest_api.bedrock_api.root_resource_id
  path_part   = "health"
}

# API Gateway Authorizer
resource "aws_api_gateway_authorizer" "cognito_authorizer" {
  name                   = "${var.project_name}-cognito-authorizer-${var.environment}"
  rest_api_id           = aws_api_gateway_rest_api.bedrock_api.id
  type                  = "COGNITO_USER_POOLS"
  provider_arns         = [aws_cognito_user_pool.bedrock_chat_pool.arn]
  identity_source       = "method.request.header.Authorization"
}

# API Gateway Methods - Chat POST
resource "aws_api_gateway_method" "chat_post" {
  rest_api_id   = aws_api_gateway_rest_api.bedrock_api.id
  resource_id   = aws_api_gateway_resource.chat_resource.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
  
  request_parameters = {
    "method.request.header.Content-Type" = false
    "method.request.header.Authorization" = true
  }
}

# API Gateway Methods - Chat OPTIONS (CORS)
resource "aws_api_gateway_method" "chat_options" {
  rest_api_id   = aws_api_gateway_rest_api.bedrock_api.id
  resource_id   = aws_api_gateway_resource.chat_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# API Gateway Methods - Health GET
resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.bedrock_api.id
  resource_id   = aws_api_gateway_resource.health_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# API Gateway Integrations - Chat POST
resource "aws_api_gateway_integration" "chat_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.bedrock_api.id
  resource_id = aws_api_gateway_resource.chat_resource.id
  http_method = aws_api_gateway_method.chat_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.chat_function.invoke_arn
  content_handling       = "CONVERT_TO_TEXT"
  timeout_milliseconds   = 29000
  
  # Ensure request body is passed through
  passthrough_behavior = "WHEN_NO_MATCH"
}

# API Gateway Integrations - Chat OPTIONS (CORS)
resource "aws_api_gateway_integration" "chat_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.bedrock_api.id
  resource_id = aws_api_gateway_resource.chat_resource.id
  http_method = aws_api_gateway_method.chat_options.http_method

  type = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}

# API Gateway Method Response - Chat OPTIONS
resource "aws_api_gateway_method_response" "chat_options_response" {
  rest_api_id = aws_api_gateway_rest_api.bedrock_api.id
  resource_id = aws_api_gateway_resource.chat_resource.id
  http_method = aws_api_gateway_method.chat_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

# API Gateway Integration Response - Chat OPTIONS
resource "aws_api_gateway_integration_response" "chat_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.bedrock_api.id
  resource_id = aws_api_gateway_resource.chat_resource.id
  http_method = aws_api_gateway_method.chat_options.http_method
  status_code = aws_api_gateway_method_response.chat_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# API Gateway Integrations - Health GET
resource "aws_api_gateway_integration" "health_get_integration" {
  rest_api_id = aws_api_gateway_rest_api.bedrock_api.id
  resource_id = aws_api_gateway_resource.health_resource.id
  http_method = aws_api_gateway_method.health_get.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.health_function.invoke_arn
}

# Lambda Permissions
resource "aws_lambda_permission" "chat_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chat_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.bedrock_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "health_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.bedrock_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "bedrock_api_deployment" {
  depends_on = [
    aws_api_gateway_method.chat_post,
    aws_api_gateway_method.chat_options,
    aws_api_gateway_method.health_get,
    aws_api_gateway_integration.chat_post_integration,
    aws_api_gateway_integration.chat_options_integration,
    aws_api_gateway_integration.health_get_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.bedrock_api.id
  stage_name  = var.environment
  
  # Force redeployment when integration changes
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_integration.chat_post_integration.content_handling,
      aws_api_gateway_integration.chat_post_integration.timeout_milliseconds,
      aws_api_gateway_integration.chat_post_integration.passthrough_behavior,
      aws_api_gateway_method.chat_post.request_parameters,
    ]))
  }
}

# Outputs
output "api_gateway_url" {
  description = "API Gateway URL"
  value       = "https://${aws_api_gateway_rest_api.bedrock_api.id}.execute-api.${var.aws_region}.amazonaws.com/${var.environment}"
}

output "chat_endpoint" {
  description = "Chat API Endpoint"
  value       = "https://${aws_api_gateway_rest_api.bedrock_api.id}.execute-api.${var.aws_region}.amazonaws.com/${var.environment}/chat"
}

output "health_endpoint" {
  description = "Health Check Endpoint"
  value       = "https://${aws_api_gateway_rest_api.bedrock_api.id}.execute-api.${var.aws_region}.amazonaws.com/${var.environment}/health"
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