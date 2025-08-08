#!/bin/bash

# Simple Lambda deployment script
set -e

echo "🚀 Deploying Lambda functions for Bedrock Chat..."

# Configuration
FUNCTION_NAME="bedrock-chat-nova-lite"
REGION="us-east-1"
ROLE_NAME="bedrock-lambda-execution-role"

# Create IAM role for Lambda
echo "📋 Creating IAM role..."
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }' \
    --region $REGION || echo "Role may already exist"

# Attach basic execution policy
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
    --region $REGION

# Create Bedrock policy
aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name BedrockInvokePolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/*"
                ]
            }
        ]
    }' \
    --region $REGION

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text --region $REGION)
echo "Role ARN: $ROLE_ARN"

# Wait for role to be ready
echo "⏳ Waiting for role to be ready..."
sleep 10

# Create deployment package
echo "📦 Creating deployment package..."
cd lambda
npm install --production
zip -r ../lambda-deployment.zip .
cd ..

# Create or update Lambda function
echo "🔧 Creating Lambda function..."
aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime nodejs18.x \
    --role $ROLE_ARN \
    --handler chat-handler.handler \
    --zip-file fileb://lambda-deployment.zip \
    --timeout 30 \
    --environment Variables="{AWS_REGION=$REGION}" \
    --region $REGION || \
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda-deployment.zip \
    --region $REGION

# Get function ARN
FUNCTION_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --query 'Configuration.FunctionArn' --output text --region $REGION)
echo "Function ARN: $FUNCTION_ARN"

# Create API Gateway
echo "🌐 Creating API Gateway..."
API_ID=$(aws apigateway create-rest-api \
    --name "bedrock-chat-api" \
    --description "API for Bedrock Nova Lite Chat" \
    --region $REGION \
    --query 'id' --output text)

echo "API Gateway ID: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region $REGION \
    --query 'items[0].id' --output text)

# Create chat resource
CHAT_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part "chat" \
    --region $REGION \
    --query 'id' --output text)

# Create POST method
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region $REGION

# Set up integration
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$FUNCTION_ARN/invocations" \
    --region $REGION

# Add Lambda permission
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:apigateway:$REGION::/restapis/$API_ID/*/POST/chat" \
    --region $REGION || echo "Permission may already exist"

# Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name dev \
    --region $REGION

# Output the API URL
API_URL="https://$API_ID.execute-api.$REGION.amazonaws.com/dev"
echo ""
echo "✅ Deployment complete!"
echo "API Gateway URL: $API_URL"
echo "Chat Endpoint: $API_URL/chat"
echo ""
echo "🔧 Next steps:"
echo "1. Update .env.local with: NEXT_PUBLIC_API_URL=$API_URL"
echo "2. Build and deploy frontend to Amplify"

# Clean up
rm -f lambda-deployment.zip