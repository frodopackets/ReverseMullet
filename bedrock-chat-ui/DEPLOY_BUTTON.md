# One-Click Deploy to AWS Amplify

Add this button to your README for easy deployment:

## Deploy Button

[![Deploy to Amplify](https://oneclick.amplifyapp.com/button.svg)](https://console.aws.amazon.com/amplify/home#/deploy?repo=https://github.com/YOUR_USERNAME/ReverseMullet)

## How to Use

1. **Replace `YOUR_USERNAME`** in the URL above with your actual GitHub username
2. **Add this to your README.md**:
   ```markdown
   ## 🚀 Quick Deploy
   
   [![Deploy to Amplify](https://oneclick.amplifyapp.com/button.svg)](https://console.aws.amazon.com/amplify/home#/deploy?repo=https://github.com/YOUR_USERNAME/ReverseMullet)
   
   Click the button above to deploy this app to AWS Amplify in one click!
   ```

3. **Users can then**:
   - Click the button
   - Connect their AWS account
   - Deploy automatically with your configuration

## Manual Deploy Alternative

If the button doesn't work, users can:

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click "Get Started" under "Amplify Hosting"  
3. Connect GitHub repository: `ReverseMullet`
4. Select branch: `main`
5. Deploy with auto-detected configuration

## What Gets Deployed

- ✅ Main UI at `/`
- ✅ Terminal theme at `/terminal`
- ✅ Bubblegum theme at `/bubblegum`
- ✅ Mock API for testing
- ✅ Automatic SSL certificates
- ✅ Global CDN
- ✅ Automatic builds on git push

## Cost

- ~$0.30/month (mostly free with AWS free tier)
- Nova Lite API: ~$0.008/month
- **Total: Less than $0.35/month**