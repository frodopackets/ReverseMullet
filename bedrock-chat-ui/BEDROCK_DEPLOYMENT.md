# AWS Bedrock Direct Integration Deployment

## 🚀 Deployment Options

### Option A: Vercel (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add direct Bedrock Nova Lite integration"
   git push origin main
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Add environment variables:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
     - `NEXT_PUBLIC_AWS_REGION=us-east-1`

3. **Access your app**: `https://your-app.vercel.app`

### Option B: AWS Lambda + Amplify

1. **Create Lambda functions** for API routes
2. **Set up API Gateway** 
3. **Keep Amplify** for frontend hosting
4. **Configure CORS** between services

## 🔑 AWS Credentials Setup

### For Development:
1. **Install AWS CLI**: `aws configure`
2. **Create IAM user** with Bedrock permissions
3. **Add to `.env.local`**:
   ```
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   ```

### For Production:
- **Vercel**: Add in dashboard environment variables
- **AWS**: Use IAM roles and policies

## 🛡️ Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/amazon.nova-lite-v1:0"
      ]
    }
  ]
}
```

## 💰 Cost Estimate

**Nova Lite Direct (10 prompts/day)**:
- **API calls**: ~$0.008/month
- **Vercel hosting**: Free tier available
- **Total**: ~$0.01/month

**Much cheaper than Knowledge Bases!**

## 🧪 Testing

1. **Local development**:
   ```bash
   npm install
   npm run dev
   ```

2. **Test API endpoint**:
   ```bash
   curl -X POST http://localhost:3000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello Nova Lite!"}'
   ```

3. **Health check**:
   ```bash
   curl http://localhost:3000/api/health
   ```

## 🎨 Theme Support

All four themes work with direct Bedrock:
- **Professional UI**: Direct Nova Lite chat
- **Terminal**: Command-line style Bedrock
- **Bubblegum**: Colorful Nova Lite chat  
- **Medieval**: Royal Bedrock conversations

## 🔧 Troubleshooting

**Common Issues**:
- **Credentials**: Ensure AWS keys are set correctly
- **Permissions**: Verify IAM policy allows Bedrock access
- **Region**: Nova Lite must be available in your region
- **CORS**: Check API route configuration

**Error Messages**:
- `AccessDenied`: Check IAM permissions
- `ModelNotFound`: Verify Nova Lite model ID
- `ThrottlingException`: Reduce request rate