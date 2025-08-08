#!/bin/bash

# Deploy AWS Infrastructure for Bedrock Chat
# This script deploys Lambda functions and API Gateway

set -e

# Configuration
STACK_NAME="bedrock-chat-infrastructure"
ENVIRONMENT="dev"
REGION="us-east-1"

echo "🚀 Deploying Bedrock Chat Infrastructure..."
echo "Stack: $STACK_NAME"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Deploy CloudFormation stack
echo "📦 Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file aws-infrastructure.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides Environment=$ENVIRONMENT \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

# Get API Gateway URL
echo "🔍 Getting API Gateway URL..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
    --output text)

if [ -z "$API_URL" ]; then
    echo "❌ Failed to get API Gateway URL"
    exit 1
fi

echo "✅ Infrastructure deployed successfully!"
echo ""
echo "📋 Deployment Details:"
echo "API Gateway URL: $API_URL"
echo "Chat Endpoint: $API_URL/chat"
echo "Health Endpoint: $API_URL/health"
echo ""
echo "🔧 Next Steps:"
echo "1. Update your .env.local file:"
echo "   NEXT_PUBLIC_API_URL=$API_URL"
echo ""
echo "2. Test the endpoints:"
echo "   curl $API_URL/health"
echo ""
echo "3. Deploy frontend to Amplify:"
echo "   npm run build"
echo "   amplify publish"

# Test health endpoint
echo "🧪 Testing health endpoint..."
if curl -s "$API_URL/health" > /dev/null; then
    echo "✅ Health endpoint is responding"
else
    echo "⚠️  Health endpoint not responding yet (may take a few minutes)"
fi