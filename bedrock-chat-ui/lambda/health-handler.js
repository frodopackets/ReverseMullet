const { BedrockRuntimeClient, InvokeModelCommand } = require('@aws-sdk/client-bedrock-runtime');

// Initialize Bedrock client
const client = new BedrockRuntimeClient({
  region: process.env.BEDROCK_REGION || process.env.AWS_REGION || 'us-east-1'
});

exports.handler = async (event) => {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Handle preflight OPTIONS request
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  try {
    // Simple health check - try to invoke Bedrock
    const modelId = 'amazon.nova-lite-v1:0';
    
    const payload = {
      messages: [
        {
          role: 'user',
          content: [
            {
              text: 'Hello'
            }
          ]
        }
      ],
      inferenceConfig: {
        maxTokens: 10,
        temperature: 0.1,
        topP: 0.9
      }
    };

    const command = new InvokeModelCommand({
      modelId,
      body: JSON.stringify(payload),
      contentType: 'application/json',
      accept: 'application/json',
    });

    await client.send(command);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        status: 'healthy',
        bedrock: true,
        model: 'amazon.nova-lite-v1:0',
        timestamp: new Date().toISOString()
      })
    };

  } catch (error) {
    console.error('Health check failed:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        status: 'unhealthy',
        bedrock: false,
        error: 'Health check failed',
        model: 'amazon.nova-lite-v1:0',
        timestamp: new Date().toISOString()
      })
    };
  }
};