# AWS Bedrock Integration Guide

This guide explains how to integrate the chat UI with actual AWS Bedrock Knowledge Bases.

## Prerequisites

1. AWS Account with Bedrock access
2. Bedrock Knowledge Bases created and indexed
3. Appropriate IAM permissions

## Required AWS Permissions

Create an IAM policy with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListKnowledgeBases",
                "bedrock:GetKnowledgeBase",
                "bedrock:RetrieveAndGenerate"
            ],
            "Resource": "*"
        }
    ]
}
```

## Installation Steps

### 1. Install AWS SDK

```bash
npm install @aws-sdk/client-bedrock-runtime @aws-sdk/client-bedrock-agent-runtime
```

### 2. Environment Configuration

Copy `.env.example` to `.env.local` and configure:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### 3. Replace Mock API

Replace `src/lib/mock-api.ts` with actual Bedrock integration:

```typescript
import { 
  BedrockRuntimeClient, 
  InvokeModelCommand 
} from "@aws-sdk/client-bedrock-runtime";
import { 
  BedrockAgentRuntimeClient,
  RetrieveAndGenerateCommand,
  ListKnowledgeBasesCommand
} from "@aws-sdk/client-bedrock-agent-runtime";

const bedrockClient = new BedrockRuntimeClient({
  region: process.env.AWS_REGION!,
});

const bedrockAgentClient = new BedrockAgentRuntimeClient({
  region: process.env.AWS_REGION!,
});

export async function sendMessage(
  message: string, 
  knowledgeBaseId: string
): Promise<Message> {
  try {
    const command = new RetrieveAndGenerateCommand({
      input: {
        text: message,
      },
      retrieveAndGenerateConfiguration: {
        type: "KNOWLEDGE_BASE",
        knowledgeBaseConfiguration: {
          knowledgeBaseId: knowledgeBaseId,
          modelArn: `arn:aws:bedrock:${process.env.AWS_REGION}::foundation-model/${process.env.BEDROCK_MODEL_ID}`,
        },
      },
    });

    const response = await bedrockAgentClient.send(command);
    
    return {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      content: response.output?.text || "No response generated",
      role: 'assistant',
      timestamp: new Date(),
      knowledgeBase: knowledgeBaseId
    };
  } catch (error) {
    console.error('Bedrock API error:', error);
    throw error;
  }
}

export async function getKnowledgeBases(): Promise<KnowledgeBase[]> {
  try {
    const command = new ListKnowledgeBasesCommand({});
    const response = await bedrockAgentClient.send(command);
    
    return response.knowledgeBaseSummaries?.map(kb => ({
      id: kb.knowledgeBaseId!,
      name: kb.name!,
      description: kb.description || 'No description available',
      status: kb.status === 'ACTIVE' ? 'active' : 'inactive',
      documentCount: 0 // This would need to be fetched separately
    })) || [];
  } catch (error) {
    console.error('Failed to fetch knowledge bases:', error);
    throw error;
  }
}
```

### 4. Update API Routes

Update `src/app/api/chat/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { sendMessage } from '@/lib/bedrock-api'

export async function POST(request: NextRequest) {
  try {
    const { message, knowledgeBaseId } = await request.json()
    
    const response = await sendMessage(message, knowledgeBaseId)
    
    return NextResponse.json(response)
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Failed to process chat message' },
      { status: 500 }
    )
  }
}
```

### 5. Error Handling

Add proper error handling for common Bedrock errors:

- Rate limiting
- Model not available
- Knowledge base not found
- Authentication errors

### 6. Security Considerations

- Use IAM roles instead of access keys in production
- Implement request validation
- Add rate limiting
- Sanitize user inputs
- Use HTTPS in production

## Testing

1. Verify AWS credentials are configured correctly
2. Test with a simple knowledge base query
3. Check CloudWatch logs for any errors
4. Monitor Bedrock usage and costs

## Deployment

### Vercel Deployment

1. Add environment variables in Vercel dashboard
2. Deploy using Vercel CLI or GitHub integration

### AWS Deployment

1. Use AWS Amplify or ECS for container deployment
2. Configure IAM roles for the application
3. Set up CloudWatch monitoring

## Troubleshooting

### Common Issues

1. **Authentication Error**: Check AWS credentials and permissions
2. **Model Not Available**: Verify model ID and region
3. **Knowledge Base Not Found**: Confirm knowledge base ID and status
4. **Rate Limiting**: Implement exponential backoff

### Debug Mode

Enable debug logging by setting:
```env
DEBUG=bedrock:*
```

## Cost Optimization

- Implement response caching
- Use appropriate model sizes
- Monitor token usage
- Set up billing alerts

## Monitoring

Set up CloudWatch dashboards to monitor:
- API response times
- Error rates
- Token usage
- Knowledge base query patterns