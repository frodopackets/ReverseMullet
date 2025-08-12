#!/usr/bin/env python3
"""
MCP Proxy Server - HTTP API bridge for MCP servers
Allows containerized services to access MCP servers via REST API
"""

import os
import json
import asyncio
import logging
import subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Proxy Server",
    description="HTTP proxy for MCP server access",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class MCPRequest(BaseModel):
    tool: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: str = ""

# AWS Pricing Tools Mapping
AWS_PRICING_TOOLS = {
    "get_pricing": {
        "command": ["uvx", "awslabs.aws-pricing-mcp-server@latest", "get_pricing"],
        "description": "Get AWS service pricing"
    },
    "get_pricing_service_codes": {
        "command": ["uvx", "awslabs.aws-pricing-mcp-server@latest", "get_pricing_service_codes"],
        "description": "Get available AWS service codes"
    },
    "get_pricing_service_attributes": {
        "command": ["uvx", "awslabs.aws-pricing-mcp-server@latest", "get_pricing_service_attributes"],
        "description": "Get pricing attributes for a service"
    },
    "get_pricing_attribute_values": {
        "command": ["uvx", "awslabs.aws-pricing-mcp-server@latest", "get_pricing_attribute_values"],
        "description": "Get valid values for pricing attributes"
    },
    "get_price_list_urls": {
        "command": ["uvx", "awslabs.aws-pricing-mcp-server@latest", "get_price_list_urls"],
        "description": "Get bulk pricing data URLs"
    },
    "generate_cost_report": {
        "command": ["uvx", "awslabs.aws-pricing-mcp-server@latest", "generate_cost_report"],
        "description": "Generate cost analysis report"
    }
}

def execute_mcp_tool(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an MCP tool via subprocess.
    This is a simplified approach that works with the AWS pricing MCP server.
    """
    try:
        if tool not in AWS_PRICING_TOOLS:
            return {
                "success": False,
                "error": f"Unknown tool: {tool}"
            }
        
        # Build command with parameters
        cmd = AWS_PRICING_TOOLS[tool]["command"].copy()
        
        # Add parameters as JSON input
        input_data = json.dumps(params) if params else None
        
        # Execute the command
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=30,
            env={
                **os.environ,
                "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
                "FASTMCP_LOG_LEVEL": "ERROR"
            }
        )
        
        if result.returncode == 0:
            try:
                # Try to parse as JSON
                data = json.loads(result.stdout) if result.stdout else {}
            except json.JSONDecodeError:
                # Return raw output if not JSON
                data = result.stdout
            
            return {
                "success": True,
                "data": data
            }
        else:
            return {
                "success": False,
                "error": result.stderr or f"Command failed with code {result.returncode}"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Tool execution timed out"
        }
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/mcp/aws-pricing/{tool}")
async def call_aws_pricing_tool(tool: str, request: MCPRequest) -> MCPResponse:
    """
    Execute an AWS pricing MCP tool.
    
    Example:
    POST /mcp/aws-pricing/get_pricing
    {
        "tool": "get_pricing",
        "params": {
            "service_code": "AmazonEC2",
            "region": "us-east-1"
        }
    }
    """
    try:
        logger.info(f"Executing AWS pricing tool: {tool} with params: {request.params}")
        
        result = execute_mcp_tool(tool, request.params)
        
        return MCPResponse(
            success=result["success"],
            data=result.get("data"),
            error=result.get("error"),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to execute tool {tool}: {e}")
        return MCPResponse(
            success=False,
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )

@app.get("/mcp/aws-pricing/tools")
async def list_aws_pricing_tools():
    """List available AWS pricing tools."""
    return {
        "tools": [
            {
                "name": name,
                "description": info["description"]
            }
            for name, info in AWS_PRICING_TOOLS.items()
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Test if uvx is available
    try:
        result = subprocess.run(
            ["uvx", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        uvx_available = result.returncode == 0
    except:
        uvx_available = False
    
    return {
        "status": "healthy",
        "uvx_available": uvx_available,
        "tools_count": len(AWS_PRICING_TOOLS)
    }

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "MCP Proxy Server",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/mcp/aws-pricing/tools",
            "/mcp/aws-pricing/{tool}"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("MCP_PROXY_PORT", "8001"))
    logger.info(f"Starting MCP Proxy Server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)