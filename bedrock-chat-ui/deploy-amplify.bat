@echo off
echo 🚀 AWS Amplify Deployment Script
echo =================================

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS CLI not found. Please install it first:
    echo    https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    pause
    exit /b 1
)

REM Check if Amplify CLI is installed
amplify --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing Amplify CLI...
    npm install -g @aws-amplify/cli
)

echo 🔧 Configuring Amplify...
echo Please follow the prompts to configure your AWS credentials

REM Initialize Amplify
amplify init --yes

REM Add hosting
amplify add hosting

REM Deploy
echo 🚀 Deploying to AWS Amplify...
amplify publish

echo ✅ Deployment complete!
echo Your app should now be live at the URL shown above
pause