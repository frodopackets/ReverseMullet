@echo off
REM Deploy AWS Infrastructure for Bedrock Chat
REM This script deploys Lambda functions and API Gateway

setlocal enabledelayedexpansion

REM Configuration
set STACK_NAME=bedrock-chat-infrastructure
set ENVIRONMENT=dev
set REGION=us-east-1

echo 🚀 Deploying Bedrock Chat Infrastructure...
echo Stack: %STACK_NAME%
echo Environment: %ENVIRONMENT%
echo Region: %REGION%

REM Check if AWS CLI is configured
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI not configured. Please run 'aws configure' first.
    exit /b 1
)

REM Deploy CloudFormation stack
echo 📦 Deploying CloudFormation stack...
aws cloudformation deploy ^
    --template-file aws-infrastructure.yaml ^
    --stack-name %STACK_NAME% ^
    --parameter-overrides Environment=%ENVIRONMENT% ^
    --capabilities CAPABILITY_NAMED_IAM ^
    --region %REGION%

if errorlevel 1 (
    echo ❌ CloudFormation deployment failed
    exit /b 1
)

REM Get API Gateway URL
echo 🔍 Getting API Gateway URL...
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %REGION% --query "Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue" --output text') do set API_URL=%%i

if "%API_URL%"=="" (
    echo ❌ Failed to get API Gateway URL
    exit /b 1
)

echo ✅ Infrastructure deployed successfully!
echo.
echo 📋 Deployment Details:
echo API Gateway URL: %API_URL%
echo Chat Endpoint: %API_URL%/chat
echo Health Endpoint: %API_URL%/health
echo.
echo 🔧 Next Steps:
echo 1. Update your .env.local file:
echo    NEXT_PUBLIC_API_URL=%API_URL%
echo.
echo 2. Test the endpoints:
echo    curl %API_URL%/health
echo.
echo 3. Deploy frontend to Amplify:
echo    npm run build
echo    amplify publish

REM Test health endpoint
echo 🧪 Testing health endpoint...
curl -s "%API_URL%/health" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Health endpoint not responding yet (may take a few minutes)
) else (
    echo ✅ Health endpoint is responding
)