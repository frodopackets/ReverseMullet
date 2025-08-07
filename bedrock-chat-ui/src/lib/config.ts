export const config = {
  app: {
    name: process.env.NEXT_PUBLIC_APP_NAME || 'Bedrock Knowledge Base Chat',
    description: process.env.NEXT_PUBLIC_APP_DESCRIPTION || 'Chat with your AWS Bedrock Knowledge Bases',
    version: '1.0.0'
  },
  
  bedrock: {
    region: process.env.AWS_REGION || 'us-east-1',
    modelId: process.env.BEDROCK_MODEL_ID || 'anthropic.claude-3-sonnet-20240229-v1:0',
    knowledgeBaseId: process.env.BEDROCK_KNOWLEDGE_BASE_ID
  },
  
  ui: {
    maxMessages: 100,
    typingDelay: 1000,
    maxMessageLength: 4000,
    theme: {
      primaryColor: 'blue',
      borderRadius: 'md'
    }
  },
  
  features: {
    mockMode: process.env.NODE_ENV === 'development',
    enableFileUpload: false,
    enableVoiceInput: false,
    enableExport: true
  }
}