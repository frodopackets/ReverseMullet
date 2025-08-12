# Core Variables
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

variable "domain_name" {
  description = "Domain name for HTTPS certificate (optional, will use ALB DNS if not provided)"
  type        = string
  default     = ""
}

# ECS Configuration Variables
variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1  # Start with 1 for personal use, can scale to 2+
}

variable "ecs_min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 1
}

variable "ecs_max_capacity" {
  description = "Maximum number of ECS tasks"
  type        = number
  default     = 4
}

variable "ecs_cpu" {
  description = "CPU units for ECS task (1024 = 1 vCPU)"
  type        = number
  default     = 1024
}

variable "ecs_memory" {
  description = "Memory for ECS task in MB"
  type        = number
  default     = 2048
}

# Scheduled Scaling Configuration
variable "enable_scheduled_scaling" {
  description = "Enable scheduled scaling (scale down during off-hours)"
  type        = bool
  default     = false  # Disabled for initial testing
}

variable "scale_down_schedule" {
  description = "Cron expression for scaling down (UTC time)"
  type        = string
  default     = "cron(0 22 * * ? *)"  # 10 PM UTC (6 PM EST)
}

variable "scale_up_schedule" {
  description = "Cron expression for scaling up (UTC time)"
  type        = string
  default     = "cron(0 14 * * ? *)"  # 2 PM UTC (10 AM EST)
}

# Cost Optimization Variables
variable "enable_fargate_spot" {
  description = "Enable Fargate Spot for cost savings (may cause interruptions)"
  type        = bool
  default     = false  # Disabled by default for reliability
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7  # Keep logs for 1 week
}

# Monitoring and Alerting
variable "cpu_alarm_threshold" {
  description = "CPU utilization threshold for alarms (%)"
  type        = number
  default     = 80
}

variable "memory_alarm_threshold" {
  description = "Memory utilization threshold for alarms (%)"
  type        = number
  default     = 85
}

variable "enable_container_insights" {
  description = "Enable ECS Container Insights for detailed monitoring"
  type        = bool
  default     = true
}

# Security Configuration
variable "enable_execute_command" {
  description = "Enable ECS Exec for debugging containers"
  type        = bool
  default     = true
}

# Auto Scaling Configuration
variable "cpu_target_value" {
  description = "Target CPU utilization for auto scaling (%)"
  type        = number
  default     = 70
}

variable "memory_target_value" {
  description = "Target memory utilization for auto scaling (%)"
  type        = number
  default     = 80
}

# Development vs Production Configuration
variable "is_production" {
  description = "Whether this is a production environment"
  type        = bool
  default     = false
}

# Service Discovery Configuration
variable "create_service_discovery" {
  description = "Whether to create a new service discovery namespace"
  type        = bool
  default     = true
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Local values for computed configurations
# Security Configuration
variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the ALB"
  type        = list(string)
  default     = ["151.196.42.101/32"]  # Default to current IP whitelist
}

locals {
  # Common tags applied to all resources
  common_tags = merge(
    {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "terraform"
      CostCenter  = "development"
    },
    var.additional_tags
  )

  # ECS capacity provider strategy based on environment
  capacity_provider_strategy = var.enable_fargate_spot ? [
    {
      capacity_provider = "FARGATE_SPOT"
      weight           = 100
      base             = 0
    }
  ] : [
    {
      capacity_provider = "FARGATE"
      weight           = 100
      base             = 1
    }
  ]

  # Scheduled scaling configuration
  scheduled_scaling_config = var.enable_scheduled_scaling ? {
    scale_down = {
      schedule     = var.scale_down_schedule
      min_capacity = 0
      max_capacity = 1
    }
    scale_up = {
      schedule     = var.scale_up_schedule
      min_capacity = var.ecs_min_capacity
      max_capacity = var.ecs_max_capacity
    }
  } : {}
}