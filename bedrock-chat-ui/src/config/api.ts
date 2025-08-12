// API Configuration
// This file is bundled with the app and provides the API endpoint

export const API_CONFIG = {
  // Primary API URL - update this when ALB DNS changes
  API_URL: 'https://bedrock-chat-ecs-alb-dev-435953948.us-east-1.elb.amazonaws.com',
  
  // Fallback to environment variable if available
  getApiUrl: () => {
    return process.env.NEXT_PUBLIC_API_URL || API_CONFIG.API_URL;
  }
};

// Endpoint paths
export const API_ENDPOINTS = {
  ROUTER_CHAT: '/router-chat',
  HEALTH: '/health',
  STATUS: '/status'
};