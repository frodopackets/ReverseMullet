# VPC Endpoints for Bedrock and AWS Pricing API
# These endpoints allow ECS tasks to reach AWS services without internet access

# Get the default VPC
data "aws_vpc" "default_vpc" {
  default = true
}

# Get route tables for the default VPC
data "aws_route_tables" "default" {
  vpc_id = data.aws_vpc.default_vpc.id
}

# Bedrock Runtime VPC Endpoint already exists (vpce-099b871353550810b)
# Reference the existing endpoint instead of creating a new one
data "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id       = data.aws_vpc.default_vpc.id
  service_name = "com.amazonaws.${var.aws_region}.bedrock-runtime"
}

# AWS Pricing API VPC Endpoint (for MCP pricing tools)
resource "aws_vpc_endpoint" "pricing" {
  vpc_id              = data.aws_vpc.default_vpc.id
  service_name        = "com.amazonaws.${var.aws_region}.pricing.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = data.aws_subnets.default.ids
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  
  private_dns_enabled = true
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = [
          "pricing:GetProducts",
          "pricing:GetAttributeValues", 
          "pricing:DescribeServices"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-pricing-endpoint-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 Gateway Endpoint (for any model artifacts or caching)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = data.aws_vpc.default_vpc.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = data.aws_route_tables.default.ids

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-s3-endpoint-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Security Group for VPC Endpoints
resource "aws_security_group" "vpc_endpoints" {
  name        = "${var.project_name}-vpc-endpoints-${var.environment}"
  description = "Security group for VPC endpoints"
  vpc_id      = data.aws_vpc.default_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.default_vpc.cidr_block]
    description = "HTTPS traffic from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-vpc-endpoints-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "bedrock_runtime_endpoint_id" {
  description = "ID of the existing Bedrock Runtime VPC endpoint"
  value       = data.aws_vpc_endpoint.bedrock_runtime.id
}

output "pricing_endpoint_id" {
  description = "ID of the Pricing API VPC endpoint"
  value       = aws_vpc_endpoint.pricing.id
}

output "s3_endpoint_id" {
  description = "ID of the S3 VPC endpoint"
  value       = aws_vpc_endpoint.s3.id
}