'use client'

export default function DebugPage() {
  const envVars = {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_AUTH_MODE: process.env.NEXT_PUBLIC_AUTH_MODE,
    NODE_ENV: process.env.NODE_ENV,
  };

  const handleTestFetch = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://bedrock-chat-ecs-alb-dev-435953948.us-east-1.elb.amazonaws.com';
    console.log('API URL being used:', apiUrl);
    console.log('Full endpoint:', `${apiUrl}/router-chat`);
    
    fetch(`${apiUrl}/router-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: 'debug test' }),
    })
    .then(response => response.json())
    .then(data => console.log('Response:', data))
    .catch(error => console.error('Error:', error));
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Debug Information</h1>
      
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Environment Variables</h2>
        <pre className="bg-gray-100 p-4 rounded">
          {JSON.stringify(envVars, null, 2)}
        </pre>
      </div>
      
      <button 
        onClick={handleTestFetch}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Test API Call (check console)
      </button>
      
      <div className="mt-4">
        <p>Open browser console to see detailed fetch information</p>
      </div>
    </div>
  );
}