#!/usr/bin/env python3
"""
Strands Agents API Server - FastAPI wrapper for AWS deployment

This server exposes the Strands Agents (Router + AWS Pricing Agent) as REST API endpoints
for integration with the Amplify frontend.
"""

import os
import sys
import time
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global orchestrator
    
    # Startup
    logger.info("Starting Strands Agents API Server...")
    try:
        from agents.router_orchestrator import RouterOrchestrator
        orchestrator = RouterOrchestrator()
        logger.info("Router Orchestrator initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {str(e)}")
        # Continue with limited functionality
        yield
    finally:
        # Shutdown
        logger.info("Shutting down Strands Agents API Server...")
        if orchestrator:
            orchestrator.reset_conversation_context()

# Create FastAPI app
app = FastAPI(
    title="Strands Agents API",
    description="AI-powered AWS pricing analysis with MCP integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Amplify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.amplifyapp.com",
        "https://main.d1tq2relshaprns.amplifyapp.com",  # Your Amplify URL
        "*"  # Allow all origins for now - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to process")
    user_id: Optional[str] = Field(None, description="Optional user identifier")

class ChatResponse(BaseModel):
    id: str = Field(..., description="Unique response identifier")
    content: str = Field(..., description="Agent response content")
    role: str = Field(default="assistant", description="Response role")
    timestamp: str = Field(..., description="Response timestamp")
    agent_type: Optional[str] = Field(None, description="Agent that handled the request")
    intent_analysis: Optional[Dict[str, Any]] = Field(None, description="Intent classification results")
    orchestration_metadata: Optional[Dict[str, Any]] = Field(None, description="Orchestration metadata")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Health check timestamp")
    orchestration: Optional[Dict[str, Any]] = Field(None, description="Orchestration status")
    mcp_status: Optional[Dict[str, Any]] = Field(None, description="MCP server status")

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Strands Agents API",
        "version": "1.0.0",
        "description": "AI-powered AWS pricing analysis with MCP integration",
        "endpoints": {
            "chat": "/router-chat",
            "health": "/health",
            "status": "/status"
        }
    }

@app.post("/router-chat", response_model=ChatResponse)
async def router_chat(request: ChatRequest):
    """
    Process chat message through the Router Orchestrator.
    
    This endpoint routes messages to appropriate specialized agents
    (AWS Pricing Agent, General Agent, etc.) based on intent analysis.
    """
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(
            status_code=503, 
            detail="Router Orchestrator not available. Service may be starting up."
        )
    
    try:
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        # Process query through orchestrator
        response = await orchestrator.process_query(
            request.message, 
            request.user_id
        )
        
        # Create response
        chat_response = ChatResponse(
            id=f"assistant-{int(time.time() * 1000)}",
            content=response.get('content', 'No response generated'),
            role="assistant",
            timestamp=datetime.now().isoformat(),
            agent_type=response.get('agent_type'),
            intent_analysis=response.get('intent_analysis'),
            orchestration_metadata=response.get('orchestration_metadata')
        )
        
        logger.info(f"Response generated by {chat_response.agent_type}")
        return chat_response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        
        # Return error response in expected format
        error_response = ChatResponse(
            id=f"error-{int(time.time() * 1000)}",
            content=f"""I encountered an error while processing your request. Here's what happened:

**Error**: {str(e)}

**What you can try**:
- Rephrase your question with more specific details
- If asking about AWS costs, mention specific services (EC2, RDS, S3, etc.)
- Try breaking complex questions into smaller parts
- Check if you're asking about supported AWS services

**I'm still here to help!** Please try again with a different approach.""",
            role="assistant",
            timestamp=datetime.now().isoformat(),
            agent_type="error_handler",
            intent_analysis={
                "intent": "error_response",
                "confidence": "high",
                "error_handled": True
            }
        )
        
        return error_response

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for load balancer and monitoring.
    
    Returns service health status and orchestration information.
    """
    global orchestrator
    
    try:
        health_response = HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat()
        )
        
        if orchestrator:
            # Get orchestration status
            orchestration_status = orchestrator.get_orchestration_status()
            health_response.orchestration = orchestration_status
            
            # Check MCP status if available
            try:
                # Try to get AWS Pricing Agent status
                from agents.aws_pricing_agent_optimized import AWSPricingAgentOptimized
                pricing_agent = AWSPricingAgentOptimized()
                
                health_response.mcp_status = {
                    "aws_pricing_mcp_available": pricing_agent.pricing_mcp_client is not None,
                    "performance_stats": getattr(pricing_agent, 'performance_stats', {}),
                    "connection_status": getattr(pricing_agent, 'mcp_connection_status', 'unknown')
                }
            except Exception as e:
                health_response.mcp_status = {
                    "aws_pricing_mcp_available": False,
                    "error": str(e)
                }
        else:
            health_response.status = "degraded"
            health_response.orchestration = {"error": "Orchestrator not initialized"}
        
        return health_response
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.get("/status", response_model=Dict[str, Any])
async def service_status():
    """
    Detailed service status endpoint for monitoring and debugging.
    """
    global orchestrator
    
    try:
        status = {
            "service": "Strands Agents API",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "aws_region": os.getenv("AWS_REGION", "us-east-1"),
                "bedrock_model": os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
                "python_version": sys.version,
                "working_directory": os.getcwd()
            }
        }
        
        if orchestrator:
            status["orchestration"] = orchestrator.get_orchestration_status()
        else:
            status["orchestration"] = {"status": "not_initialized"}
        
        # Check agent availability
        try:
            from agents.aws_pricing_agent_optimized import AWSPricingAgentOptimized
            pricing_agent = AWSPricingAgentOptimized()
            
            status["agents"] = {
                "aws_pricing_agent": {
                    "available": True,
                    "mcp_client_available": pricing_agent.pricing_mcp_client is not None,
                    "performance_stats": getattr(pricing_agent, 'performance_stats', {})
                }
            }
        except Exception as e:
            status["agents"] = {
                "aws_pricing_agent": {
                    "available": False,
                    "error": str(e)
                }
            }
        
        return status
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Additional startup tasks."""
    logger.info("Strands Agents API Server started successfully")
    logger.info(f"Environment: AWS_REGION={os.getenv('AWS_REGION', 'us-east-1')}")
    logger.info(f"Bedrock Model: {os.getenv('BEDROCK_MODEL_ID', 'amazon.nova-lite-v1:0')}")

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    logger.info(f"Starting server on {host}:{port}")
    
    # Run server
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False,  # Disable reload in production
        access_log=True
    )