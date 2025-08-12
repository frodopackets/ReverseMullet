const { spawn } = require('child_process');
const path = require('path');

/**
 * Lambda handler that uses the Router Orchestrator for intelligent agent routing
 * This replaces the direct Bedrock call with the multi-agent system
 */
exports.handler = async (event) => {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
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
    // Parse request body
    if (!event.body) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Request body is required' })
      };
    }
    
    const { message } = JSON.parse(event.body);
    
    if (!message || typeof message !== 'string') {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Message is required and must be a string' })
      };
    }

    // Extract user ID from authorization header if available
    let userId = null;
    try {
      const authHeader = event.headers?.Authorization || event.headers?.authorization;
      if (authHeader) {
        // This would be enhanced to properly decode JWT token
        userId = 'authenticated_user';
      }
    } catch (e) {
      console.log('Could not extract user ID from auth header');
    }

    // Call the Router Orchestrator Python script
    const response = await callRouterOrchestrator(message, userId);
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(response)
    };

  } catch (error) {
    console.error('Router Orchestrator Error:', error);
    
    // Fallback to basic error response
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        id: `error-${Date.now()}`,
        content: 'I apologize, but I encountered an error while processing your request. The intelligent routing system may be temporarily unavailable. Please try again.',
        role: 'assistant',
        timestamp: new Date().toISOString(),
        agent_type: 'fallback_error',
        intent_analysis: {
          intent: 'system_error',
          confidence: 'high'
        }
      })
    };
  }
};

/**
 * Call the Router Orchestrator Python script
 */
async function callRouterOrchestrator(message, userId = null) {
  return new Promise((resolve, reject) => {
    // Prepare the Python script execution
    const pythonScript = `
import sys
import json
import asyncio
import os

# Add the agents directory to Python path
sys.path.append('/opt/python/agents')

async def main():
    try:
        from router_orchestrator import RouterOrchestrator
        
        # Get input from command line arguments
        message = sys.argv[1] if len(sys.argv) > 1 else ""
        user_id = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "null" else None
        
        # Initialize orchestrator
        orchestrator = RouterOrchestrator()
        
        # Process the query
        response = await orchestrator.process_query(message, user_id)
        
        # Format response for Lambda
        lambda_response = {
            'id': f"assistant-{int(__import__('time').time() * 1000)}",
            'content': response.get('content', 'No response generated'),
            'role': 'assistant',
            'timestamp': response.get('timestamp') or __import__('datetime').datetime.now().isoformat(),
            'agent_type': response.get('agent_type', 'router'),
            'intent_analysis': response.get('intent_analysis', {}),
            'orchestration_metadata': response.get('orchestration_metadata', {})
        }
        
        print(json.dumps(lambda_response))
        
    except ImportError as e:
        # Handle missing dependencies gracefully
        error_response = {
            'id': f"error-{int(__import__('time').time() * 1000)}",
            'content': f"The intelligent routing system is not fully configured. Missing dependencies: {str(e)}. Falling back to basic response mode.",
            'role': 'assistant',
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'agent_type': 'fallback_import_error',
            'intent_analysis': {
                'intent': 'import_error',
                'confidence': 'high',
                'error_type': 'missing_dependencies'
            }
        }
        print(json.dumps(error_response))
        
    except Exception as e:
        # Handle other errors
        error_response = {
            'id': f"error-{int(__import__('time').time() * 1000)}",
            'content': f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or try again.",
            'role': 'assistant',
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'agent_type': 'fallback_error',
            'intent_analysis': {
                'intent': 'processing_error',
                'confidence': 'high',
                'error_message': str(e)
            }
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    asyncio.run(main())
`;

    // Write the Python script to a temporary file
    const fs = require('fs');
    const tempScriptPath = '/tmp/router_orchestrator_call.py';
    fs.writeFileSync(tempScriptPath, pythonScript);

    // Execute the Python script
    const pythonProcess = spawn('python3', [tempScriptPath, message, userId || 'null'], {
      env: {
        ...process.env,
        PYTHONPATH: '/opt/python:/opt/python/agents'
      }
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
      try {
        if (code === 0 && stdout.trim()) {
          // Parse the JSON response from Python
          const response = JSON.parse(stdout.trim());
          resolve(response);
        } else {
          // Handle Python script errors
          console.error('Python script error:', stderr);
          
          // Provide fallback response
          const fallbackResponse = {
            id: `fallback-${Date.now()}`,
            content: `I'm experiencing some technical difficulties with the intelligent routing system. Error code: ${code}. 

However, I can still help you! Please try:
- Rephrasing your question more specifically
- Asking about AWS pricing, costs, or architecture analysis
- Providing more details about what you're looking for

What would you like to know?`,
            role: 'assistant',
            timestamp: new Date().toISOString(),
            agent_type: 'fallback_system',
            intent_analysis: {
              intent: 'system_fallback',
              confidence: 'high',
              error_code: code,
              stderr_preview: stderr.substring(0, 200)
            }
          };
          
          resolve(fallbackResponse);
        }
      } catch (parseError) {
        console.error('Error parsing Python response:', parseError);
        console.error('Raw stdout:', stdout);
        console.error('Raw stderr:', stderr);
        
        // Final fallback
        const errorResponse = {
          id: `parse-error-${Date.now()}`,
          content: 'I encountered a technical issue while processing your request. The system is working to resolve this. Please try again with a simpler question.',
          role: 'assistant',
          timestamp: new Date().toISOString(),
          agent_type: 'parse_error_fallback',
          intent_analysis: {
            intent: 'parse_error',
            confidence: 'high'
          }
        };
        
        resolve(errorResponse);
      }
    });

    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python process:', error);
      
      const processErrorResponse = {
        id: `process-error-${Date.now()}`,
        content: 'The intelligent routing system is temporarily unavailable. This might be due to system configuration issues. Please try again later.',
        role: 'assistant',
        timestamp: new Date().toISOString(),
        agent_type: 'process_error_fallback',
        intent_analysis: {
          intent: 'process_error',
          confidence: 'high',
          error_type: 'python_process_failed'
        }
      };
      
      resolve(processErrorResponse);
    });

    // Set a timeout for the Python process
    setTimeout(() => {
      pythonProcess.kill('SIGTERM');
      
      const timeoutResponse = {
        id: `timeout-${Date.now()}`,
        content: 'Your request is taking longer than expected to process. This might be due to complex analysis or system load. Please try again with a more specific question.',
        role: 'assistant',
        timestamp: new Date().toISOString(),
        agent_type: 'timeout_fallback',
        intent_analysis: {
          intent: 'timeout_error',
          confidence: 'high'
        }
      };
      
      resolve(timeoutResponse);
    }, 25000); // 25 second timeout (Lambda has 30s max)
  });
}