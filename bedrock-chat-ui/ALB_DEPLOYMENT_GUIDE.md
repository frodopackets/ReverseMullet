# ALB-Only Deployment Guide

This guide explains how to deploy the Bedrock Chat UI with the cost-optimized ALB-only architecture (no API Gateway).

## Cost Comparison

- **Old Architecture**: API Gateway + VPC Link + Internal ALB = ~$50+/month
- **New Architecture**: Public ALB only = ~$16-20/month  
- **Savings**: ~$30-35/month (60%+ cost reduction)

## Prerequisites

1. **Terraform 1.0+** installed
2. **AWS CLI** configured with appropriate permissions
3. **Node.js 18+** for frontend development
4. **Domain name** (optional, for HTTPS)

## Step 1: Deploy Infrastructure

### 1.1 Configure Terraform Variables

Create or update `terraform/terraform.tfvars`:

```hcl
# Basic Configuration
project_name = "bedrock-chat"
environment = "dev"
aws_region = "us-east-1"

# Optional: Custom domain for HTTPS (leave empty for HTTP demo)
domain_name = ""  # or "chat.yourdomain.com"

# ECS Configuration
ecs_desired_count = 1
ecs_min_capacity = 1
ecs_max_capacity = 2
ecs_cpu = 1024
ecs_memory = 2048
```

### 1.2 Deploy with Terraform

```bash
cd terraform/
terraform init
terraform plan -out=alb-plan
terraform apply alb-plan
```

### 1.3 Note the Outputs

After deployment, note these important outputs:
- `alb_dns_name`: Your ALB DNS name (e.g., `bedrock-chat-alb-dev-123456.us-east-1.elb.amazonaws.com`)
- `cognito_user_pool_id`: For frontend configuration
- `cognito_user_pool_client_id`: For frontend configuration
- `cognito_domain`: For OAuth configuration

## Step 2: Configure Frontend

### 2.1 Environment Variables

Create `.env.local` in the project root:

```bash
# API Configuration - Use the ALB DNS name from Terraform output
NEXT_PUBLIC_API_URL=http://YOUR_ALB_DNS_NAME

# Authentication Mode - Use ALB OAuth flow
NEXT_PUBLIC_AUTH_MODE=alb

# AWS Configuration
NEXT_PUBLIC_AWS_REGION=us-east-1

# Cognito Configuration - From Terraform outputs
NEXT_PUBLIC_COGNITO_USER_POOL_ID=YOUR_USER_POOL_ID
NEXT_PUBLIC_COGNITO_USER_POOL_CLIENT_ID=YOUR_CLIENT_ID
NEXT_PUBLIC_COGNITO_DOMAIN=YOUR_COGNITO_DOMAIN

# Application Configuration
NEXT_PUBLIC_APP_NAME="AWS Pricing Agent"
```

### 2.2 Replace Terraform Output Values

```bash
# Get the ALB DNS name
export ALB_DNS=$(terraform -chdir=terraform output -raw alb_dns_name)
export USER_POOL_ID=$(terraform -chdir=terraform output -raw cognito_user_pool_id)
export CLIENT_ID=$(terraform -chdir=terraform output -raw cognito_user_pool_client_id)
export COGNITO_DOMAIN=$(terraform -chdir=terraform output -raw cognito_domain | sed 's|https://||' | sed 's|\.auth\..*||')

# Update .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://${ALB_DNS}
NEXT_PUBLIC_AUTH_MODE=alb
NEXT_PUBLIC_AWS_REGION=us-east-1
NEXT_PUBLIC_COGNITO_USER_POOL_ID=${USER_POOL_ID}
NEXT_PUBLIC_COGNITO_USER_POOL_CLIENT_ID=${CLIENT_ID}
NEXT_PUBLIC_COGNITO_DOMAIN=${COGNITO_DOMAIN}
NEXT_PUBLIC_APP_NAME="AWS Pricing Agent"
EOF
```

## Step 3: Test the Application

### 3.1 Build and Start Frontend

```bash
npm install
npm run build
npm start
```

### 3.2 Access the Application

1. Open `http://localhost:3000`
2. Click "Sign In" - you'll be redirected to Cognito hosted UI
3. Create an account or sign in
4. After authentication, you'll be redirected back to the chat interface
5. Test the chat functionality with AWS pricing queries

### 3.3 Test Different Themes

- **Professional UI**: `http://localhost:3000/`
- **Terminal Mode**: `http://localhost:3000/terminal`  
- **Bubblegum Mode**: `http://localhost:3000/bubblegum`
- **Medieval Mode**: `http://localhost:3000/medieval`

## Step 4: Production Deployment

### 4.1 Custom Domain (Optional)

If you want HTTPS with a custom domain:

1. Update `domain_name` in `terraform.tfvars`
2. Run `terraform apply` again
3. Create a DNS CNAME record pointing to the ALB DNS name
4. Wait for ACM certificate validation

### 4.2 Deploy to Amplify/Vercel

The frontend can be deployed to any static hosting service:

```bash
# Build for production
npm run build

# Deploy the 'out' directory to your hosting service
```

Update the Cognito callback URLs to include your production domain.

## Authentication Flow

### ALB OAuth Flow

1. User visits protected endpoint (e.g., `/chat`)
2. ALB redirects to Cognito hosted UI
3. User authenticates with Cognito
4. Cognito redirects back to ALB with authorization code
5. ALB exchanges code for tokens and sets session cookies
6. ALB forwards request to ECS with user information in headers
7. Frontend makes API calls with `credentials: 'include'` for cookies

### Key Differences from API Gateway

- **No JWT tokens** - ALB uses session cookies
- **No Authorization headers** - authentication handled by ALB
- **Cognito hosted UI** - no embedded auth forms
- **Server-side sessions** - more secure than client-side JWT

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure `credentials: 'include'` in fetch calls
2. **Auth Loop**: Check callback URLs match exactly
3. **API Not Found**: Verify ALB DNS name is correct in environment variables
4. **ECS Not Responding**: Check ECS service status and logs

### Useful Commands

```bash
# Check ALB status
aws elbv2 describe-load-balancers --names bedrock-chat-alb-dev

# Check ECS service
aws ecs describe-services --cluster bedrock-chat-cluster-dev --services bedrock-chat-strands-agents-dev

# View ECS logs
aws logs tail /ecs/bedrock-chat-dev --follow

# Test ALB endpoint directly
curl http://YOUR_ALB_DNS/health
```

## Cost Monitoring

Monitor your costs in the AWS Cost Explorer:

1. **ECS Fargate**: ~$10-15/month for 1-2 tasks
2. **Application Load Balancer**: ~$16/month
3. **CloudWatch Logs**: ~$1-2/month  
4. **Total**: ~$16-20/month vs $50+/month with API Gateway

## Next Steps

1. **Enable Container Insights** for better monitoring
2. **Add WAF** for additional security (~$5/month)
3. **Configure Auto Scaling** based on CPU/memory
4. **Set up CI/CD** for automated deployments
5. **Add custom domain** with HTTPS