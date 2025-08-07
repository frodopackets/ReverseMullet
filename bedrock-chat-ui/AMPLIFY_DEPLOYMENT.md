# AWS Amplify Deployment Guide

This guide will help you deploy your Next.js Bedrock Chat UI to AWS Amplify.

## Prerequisites

1. **AWS Account** - You'll need an AWS account
2. **GitHub Repository** - Your code should be in a GitHub repository
3. **AWS CLI** (optional) - For advanced configuration

## Step 1: Prepare Your Repository

Your app is already configured for static export with:
- ✅ `next.config.ts` configured for static export
- ✅ `amplify.yml` build configuration
- ✅ Environment variables setup
- ✅ All three themes (UI, Terminal, Bubblegum) ready

## Step 2: Deploy to AWS Amplify

### Option A: Using AWS Console (Recommended)

1. **Go to AWS Amplify Console**
   - Visit: https://console.aws.amazon.com/amplify/
   - Click "Get Started" under "Amplify Hosting"

2. **Connect Your Repository**
   - Choose "GitHub" as your Git provider
   - Authorize AWS Amplify to access your GitHub account
   - Select your repository: `ReverseMullet`
   - Choose branch: `main` (or your default branch)

3. **Configure Build Settings**
   - Amplify should auto-detect the `amplify.yml` file
   - App name: `bedrock-chat-ui`
   - Environment: `production`
   - The build configuration should show:
     ```yaml
     version: 1
     frontend:
       phases:
         preBuild:
           commands:
             - npm ci
         build:
           commands:
             - npm run build
       artifacts:
         baseDirectory: out
         files:
           - '**/*'
     ```

4. **Environment Variables** (Optional for now)
   - Skip for now since we're using mock API
   - Later, add your AWS credentials for real Bedrock integration

5. **Deploy**
   - Click "Save and Deploy"
   - Wait for the build to complete (usually 2-5 minutes)

### Option B: Using AWS CLI

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Configure Amplify
amplify configure

# Initialize Amplify in your project
cd bedrock-chat-ui
amplify init

# Add hosting
amplify add hosting

# Deploy
amplify publish
```

## Step 3: Access Your Deployed App

After deployment, you'll get URLs like:
- **Main App**: `https://main.d1234567890.amplifyapp.com/`
- **Terminal Theme**: `https://main.d1234567890.amplifyapp.com/terminal/`
- **Bubblegum Theme**: `https://main.d1234567890.amplifyapp.com/bubblegum/`

## Step 4: Custom Domain (Optional)

1. In Amplify Console, go to "Domain management"
2. Add your custom domain
3. Amplify will handle SSL certificates automatically

## Step 5: Environment Configuration

### For Mock API (Current Setup)
- No additional configuration needed
- App will use mock responses

### For Real AWS Bedrock Integration (Later)
Add these environment variables in Amplify Console:

```
NEXT_PUBLIC_AWS_REGION=us-east-1
NEXT_PUBLIC_BEDROCK_MODEL=nova-lite
NEXT_PUBLIC_USE_MOCK_API=false
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## Step 6: Automatic Deployments

Once connected, Amplify will automatically:
- ✅ Deploy when you push to your main branch
- ✅ Build and test your app
- ✅ Update all three theme URLs
- ✅ Invalidate CDN cache
- ✅ Send deployment notifications

## Monitoring and Logs

- **Build Logs**: Available in Amplify Console
- **Access Logs**: CloudWatch integration
- **Performance**: Built-in monitoring dashboard

## Cost Estimation

For your usage (1,000 page views/month):
- **Build minutes**: ~15 minutes/month = $0.15
- **Data transfer**: ~1GB/month = $0.15
- **Hosting requests**: ~1,000/month = $0.0003
- **Storage**: ~100MB = $0.002

**Total**: ~$0.30/month (mostly covered by free tier)

## Troubleshooting

### Build Fails
- Check build logs in Amplify Console
- Ensure all dependencies are in `package.json`
- Verify `amplify.yml` configuration

### 404 Errors
- Ensure `trailingSlash: true` in `next.config.ts`
- Check that all routes are properly exported

### Environment Variables Not Working
- Prefix client-side variables with `NEXT_PUBLIC_`
- Restart build after adding variables

## Next Steps

1. **Deploy to Amplify** using the steps above
2. **Test all three themes** work correctly
3. **Set up custom domain** if desired
4. **Integrate real AWS Bedrock** when ready
5. **Monitor costs** and usage

## Support

- **AWS Amplify Docs**: https://docs.amplify.aws/
- **Next.js Static Export**: https://nextjs.org/docs/app/building-your-application/deploying/static-exports
- **GitHub Issues**: Create issues in your repository for bugs

---

Your app is now ready for deployment! The mock API will work perfectly for testing and demonstration purposes.