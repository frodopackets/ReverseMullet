"""
MCP Proxy Client - HTTP client for accessing MCP servers via proxy
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class MCPProxyClient:
    """Client for accessing MCP servers through HTTP proxy."""
    
    def __init__(self, proxy_url: str = None):
        """
        Initialize MCP Proxy client.
        
        Args:
            proxy_url: URL of the MCP proxy server (e.g., "http://localhost:8001")
        """
        self.proxy_url = proxy_url or os.getenv("MCP_PROXY_URL", "http://localhost:8001")
        self.session = requests.Session()
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if the proxy server is available."""
        try:
            response = self.session.get(
                urljoin(self.proxy_url, "/health"),
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"MCP Proxy server available at {self.proxy_url}")
                return True
        except Exception as e:
            logger.warning(f"MCP Proxy server not available: {e}")
        return False
    
    def call_tool(self, tool: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call an MCP tool through the proxy.
        
        Args:
            tool: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            Tool response data
        """
        if not self.available:
            raise ConnectionError("MCP Proxy server is not available")
        
        try:
            response = self.session.post(
                urljoin(self.proxy_url, f"/mcp/aws-pricing/{tool}"),
                json={
                    "tool": tool,
                    "params": params or {}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("data", {})
                else:
                    raise Exception(f"Tool call failed: {result.get('error')}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to call tool {tool}: {e}")
            raise
    
    def get_pricing(self, service_code: str, region: str, filters: list = None) -> Dict[str, Any]:
        """Get AWS service pricing."""
        return self.call_tool("get_pricing", {
            "service_code": service_code,
            "region": region,
            "filters": filters or []
        })
    
    def get_service_codes(self) -> list:
        """Get available AWS service codes."""
        result = self.call_tool("get_pricing_service_codes")
        if isinstance(result, str):
            # Parse the concatenated service codes
            return [code for code in result.split() if code]
        return result
    
    def get_service_attributes(self, service_code: str) -> list:
        """Get pricing attributes for a service."""
        return self.call_tool("get_pricing_service_attributes", {
            "service_code": service_code
        })
    
    def get_attribute_values(self, service_code: str, attribute_names: list) -> Dict[str, list]:
        """Get valid values for pricing attributes."""
        return self.call_tool("get_pricing_attribute_values", {
            "service_code": service_code,
            "attribute_names": attribute_names
        })
    
    def generate_cost_report(self, pricing_data: Any, service_name: str, **kwargs) -> str:
        """Generate a cost analysis report."""
        return self.call_tool("generate_cost_report", {
            "pricing_data": pricing_data,
            "service_name": service_name,
            **kwargs
        })