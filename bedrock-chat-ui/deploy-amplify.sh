#!/bin/bash

echo "🚀 AWS Amplify Deployment Script"
echo "================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if Amplify CLI is installed
if ! command -v amplify &> /dev/null; then
    echo "📦 Installing Amplify CLI..."
    npm install -g @aws-amplify/cli
fi

echo "🔧 Configuring Amplify..."
echo "Please follow the prompts to configure your AWS credentials"

# Initialize Amplify
amplify init --yes

# Add hosting
amplify add hosting

# Deploy
echo "🚀 Deploying to AWS Amplify..."
amplify publish

echo "✅ Deployment complete!"
echo "Your app should now be live at the URL shown above"