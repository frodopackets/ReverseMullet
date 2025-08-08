import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime'

// AWS Bedrock configuration
const client = new BedrockRuntimeClient({
  region: process.env.NEXT_PUBLIC_AWS_REGION || 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || '',
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || '',
  },
})

export interface BedrockMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

export async function sendMessageToBedrock(message: string): Promise<BedrockMessage> {
  try {
    // Nova Lite model configuration
    const modelId = 'amazon.nova-lite-v1:0'
    
    // Prepare the request payload for Nova Lite
    const payload = {
      messages: [
        {
          role: 'user',
          content: [
            {
              text: message
            }
          ]
        }
      ],
      inferenceConfig: {
        maxTokens: 1000,
        temperature: 0.7,
        topP: 0.9
      }
    }

    const command = new InvokeModelCommand({
      modelId,
      body: JSON.stringify(payload),
      contentType: 'application/json',
      accept: 'application/json',
    })

    const response = await client.send(command)
    
    if (!response.body) {
      throw new Error('No response body from Bedrock')
    }

    // Parse the response
    const responseBody = JSON.parse(new TextDecoder().decode(response.body))
    
    // Extract the assistant's response (Nova Lite format)
    const assistantMessage = responseBody.output?.message?.content?.[0]?.text || 'Sorry, I could not generate a response.'

    return {
      id: `assistant-${Date.now()}`,
      content: assistantMessage,
      role: 'assistant',
      timestamp: new Date()
    }
  } catch (error) {
    console.error('Bedrock API Error:', error)
    // Return error message
    return {
      id: `error-${Date.now()}`,
      content: 'I apologize, but I encountered an error while processing your request. Please try again.',
      role: 'assistant',
      timestamp: new Date()
    }
  }
}

// Health check function
export async function checkBedrockConnection(): Promise<boolean> {
  try {
    // Simple test message to verify connection
    await sendMessageToBedrock('Hello')
    return true
  } catch (error) {
    console.error('Bedrock connection check failed:', error)
    return false
  }
}