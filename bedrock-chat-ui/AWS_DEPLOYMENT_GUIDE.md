# AWS Native Deployment Guide

## 🏗️ **Architecture Overview**

```
Frontend (Amplify) → API Gateway → Lambda Functions → Bedrock Nova Lite
```

- **Frontend**: Static React app hosted on AWS Amplify
- **API**: Lambda functions behind API Gateway
- **AI**: Direct connection to Bedrock Nova Lite model

## 🚀 **Deployment Steps**

### **Step 1: Deploy Backend Infrastructure**

1. **Ensure AWS CLI is configured**:
   ```bash
   aws configure
   # Enter your AWS Access Key, Secret Key, Region (us-east-1), and output format (json)
   ```

2. **Deploy Lambda functions and API Gateway**:
   ```bash
   # On Linux/Mac
   chmod +x deploy-aws-infrastructure.sh
   ./deploy-aws-infrastructure.sh

   # On Windows
   deploy-aws-infrastructure.bat
   ```

3. **Note the API Gateway URL** from the output (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/dev`)

### **Step 2: Configure Frontend**

1. **Update environment variables** in `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/dev
   ```

2. **Test locally**:
   ```bash
   npm run dev
   ```

### **Step 3: Deploy Frontend to Amplify**

1. **Initialize Amplify** (if not already done):
   ```bash
   amplify init
   ```

2. **Add hosting**:
   ```bash
   amplify add hosting
   # Choose "Amazon CloudFront and S3"
   ```

3. **Build and deploy**:
   ```bash
   npm run build
   amplify publish
   ```

## 🔑 **Required IAM Permissions**

Your AWS user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "lambda:*",
        "apigateway:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PassRole",
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🧪 **Testing**

### **Test API Endpoints**:
```bash
# Health check
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/health

# Chat test
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Nova Lite!"}'
```

### **Test Frontend**:
1. Open your Amplify app URL
2. Send a test message
3. Verify Nova Lite responds

## 💰 **Cost Breakdown**

**Monthly costs for 100 messages/day**:
- **Lambda**: ~$0.20 (2M requests free tier)
- **API Gateway**: ~$3.50 (1M requests free tier first year)
- **Bedrock Nova Lite**: ~$2.40 (input + output tokens)
- **Amplify Hosting**: ~$1.00 (5GB free tier)
- **Total**: ~$7.10/month (after free tiers)

## 🔧 **Troubleshooting**

### **Common Issues**:

1. **"AccessDenied" errors**:
   - Check IAM permissions for Bedrock
   - Verify Nova Lite is available in your region

2. **CORS errors**:
   - API Gateway includes CORS headers
   - Check browser developer tools

3. **Lambda timeout**:
   - Functions have 30-second timeout
   - Check CloudWatch logs for details

4. **Amplify build fails**:
   - Ensure `output: 'export'` in `next.config.ts`
   - Check build logs in Amplify console

### **Monitoring**:
- **CloudWatch Logs**: Lambda function logs
- **API Gateway**: Request/response logs
- **Amplify Console**: Build and deployment logs

## 🔄 **Updates and Maintenance**

### **Update Lambda Functions**:
```bash
# Redeploy infrastructure
./deploy-aws-infrastructure.sh
```

### **Update Frontend**:
```bash
# Build and redeploy
npm run build
amplify publish
```

### **Monitor Costs**:
- Use AWS Cost Explorer
- Set up billing alerts
- Monitor Bedrock usage in console

## 🎯 **Production Considerations**

1. **Environment Variables**:
   - Use AWS Systems Manager Parameter Store
   - Separate dev/staging/prod environments

2. **Security**:
   - Enable API Gateway authentication
   - Use VPC for Lambda functions
   - Implement rate limiting

3. **Monitoring**:
   - Set up CloudWatch alarms
   - Enable X-Ray tracing
   - Monitor Bedrock quotas

4. **Scaling**:
   - Lambda auto-scales
   - API Gateway handles high traffic
   - Consider caching for repeated queries