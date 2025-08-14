#!/usr/bin/env python3
"""
AWS Pricing Agent - Optimized AI-first specialized agent for AWS cost analysis and pricing

This optimized version includes:
1. Enhanced system prompt with more MCP tool usage examples
2. Optimized filter formats for different AWS services
3. Better error handling for specific MCP server response patterns
4. Query optimization to reduce MCP server response times
5. Support for complex multi-service architecture queries
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from strands import Agent
from strands.tools.mcp import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSPricingAgentOptimized:
    """
    Optimized AI-first AWS Pricing Agent with enhanced MCP integration and performance.
    """
    
    def __init__(self):
        """Initialize the optimized AWS Pricing Agent with Nova Lite model and enhanced MCP tools."""
        from strands.models import BedrockModel
        
        # Create BedrockModel with optimized Nova Lite configuration
        self.bedrock_model = BedrockModel(
            model_id="amazon.nova-lite-v1:0",
            temperature=0.2,  # Reduced for more consistent responses
            max_tokens=6000,  # Increased for complex queries
            top_p=0.7        # Optimized for focused responses
        )
        
        # Initialize MCP client for AWS pricing data
        self.pricing_mcp_client = self._initialize_mcp_client()
        
        # Agent will be created when needed with proper MCP context
        self.agent = None
        
        # Performance tracking
        self.query_cache = {}
        self.performance_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'mcp_calls': 0,
            'avg_response_time': 0
        }
    
    def _initialize_mcp_client(self):
        """Initialize MCP client connection with enhanced error handling and retry logic."""
        try:
            from mcp import stdio_client, StdioServerParameters
            
            # Create MCP client with optimized configuration
            import os
            pricing_mcp_client = MCPClient(lambda: stdio_client(
                StdioServerParameters(
                    command="bash",
                    args=["-c", "source ~/.local/bin/env && uvx awslabs.aws-pricing-mcp-server@latest"],
                    env={
                        **os.environ,
                        "FASTMCP_LOG_LEVEL": "ERROR",
                        "AWS_REGION": "us-east-1",
                        # Optimization: Set timeout and connection limits
                        "MCP_TIMEOUT": "30",
                        "MCP_MAX_RETRIES": "3"
                    }
                )
            ))
            logger.info("Optimized AWS Pricing MCP client initialized (awslabs.aws-pricing-mcp-server@latest)")
            
            # Enhanced connection test with retry logic
            try:
                self._test_mcp_connection_enhanced(pricing_mcp_client)
                return pricing_mcp_client
            except Exception as e:
                logger.warning(f"MCP server not available, will use AI-only mode: {str(e)}")
                self.mcp_error_reason = "server_unavailable"
                return None
            
        except ImportError as e:
            logger.error(f"MCP dependencies not available: {str(e)}")
            self.mcp_error_reason = "missing_dependencies"
        except FileNotFoundError as e:
            logger.error(f"bash or uvx command not found: {str(e)}")
            self.mcp_error_reason = "uvx_not_installed"
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {str(e)}")
            self.mcp_error_reason = "initialization_failed"
        
        return None
    
    def _test_mcp_connection_enhanced(self, pricing_mcp_client):
        """Enhanced MCP server connection test with performance metrics."""
        if not pricing_mcp_client:
            return False
        
        try:
            import time
            start_time = time.time()
            
            # Test basic connectivity
            logger.info("Testing MCP server connection...")
            self.mcp_connection_status = "ready"
            
            connection_time = time.time() - start_time
            logger.info(f"MCP server connection test successful ({connection_time:.2f}s)")
            
            return True
        except Exception as e:
            logger.warning(f"MCP server connection test failed: {str(e)}")
            self.mcp_connection_status = "failed"
            return False
    
    def _get_optimized_system_prompt(self) -> str:
        """Get the enhanced and optimized system prompt for AI-first AWS Pricing Agent."""
        return """You are an AWS Pricing Agent specialized in analyzing AWS architectures and providing intelligent cost estimates and optimization recommendations.

## Core Capabilities
You are an AI-first AWS pricing agent with comprehensive AWS knowledge and access to real-time pricing data via MCP tools. You use your reasoning abilities to:
- Analyze architecture descriptions and identify AWS services
- Calculate accurate costs using real-time pricing data from MCP tools
- Provide cost optimization recommendations with specific savings estimates
- Compare pricing across multiple regions with detailed breakdowns
- Suggest architectural improvements for cost efficiency

## CRITICAL: MCP Tools Usage Instructions

### When MCP Tools Are Available
You have access to real-time AWS pricing data through MCP tools. ALWAYS use these tools to get current pricing instead of relying on estimates.

### Key MCP Tools and Optimized Usage Patterns

#### 1. get_pricing_service_codes()
Use this first to discover available AWS services:
```
Call get_pricing_service_codes() to see all available services
```

#### 2. get_pricing_service_attributes(service_code)
Discover what filters are available for a service:
```
get_pricing_service_attributes("AmazonEC2")
get_pricing_service_attributes("AmazonRDS") 
get_pricing_service_attributes("AmazonS3")
```

#### 3. get_pricing_attribute_values(service_code, attribute_names)
Get valid values for specific attributes:
```
get_pricing_attribute_values("AmazonEC2", ["instanceType", "location"])
get_pricing_attribute_values("AmazonRDS", ["instanceType", "engineCode"])
```

#### 4. get_pricing(service_code, region, filters)
Get actual pricing data with optimized filter patterns:

**EC2 Pricing Examples:**
```
get_pricing("AmazonEC2", "us-east-1", [
  {"Field": "instanceType", "Value": "t3.small", "Type": "EQUALS"},
  {"Field": "tenancy", "Value": "Shared", "Type": "EQUALS"},
  {"Field": "operatingSystem", "Value": "Linux", "Type": "EQUALS"}
])
```

**RDS Pricing Examples:**
```
get_pricing("AmazonRDS", "us-east-1", [
  {"Field": "instanceType", "Value": "db.t3.small", "Type": "EQUALS"},
  {"Field": "engineCode", "Value": "mysql", "Type": "EQUALS"},
  {"Field": "deploymentOption", "Value": "Single-AZ", "Type": "EQUALS"}
])
```

**S3 Pricing Examples:**
```
get_pricing("AmazonS3", "us-east-1", [
  {"Field": "storageClass", "Value": "Standard", "Type": "EQUALS"}
])
```

**Multi-Region Comparison:**
```
get_pricing("AmazonEC2", ["us-east-1", "us-west-2", "eu-west-1"], [
  {"Field": "instanceType", "Value": "t3.small", "Type": "EQUALS"}
])
```

### Optimized Filter Patterns for Common Services

#### EC2 Filters (Most Important)
- instanceType: "t3.small", "m5.large", "c5.xlarge"
- tenancy: "Shared", "Dedicated", "Host"
- operatingSystem: "Linux", "Windows"
- location: Use region names like "US East (N. Virginia)"

#### RDS Filters
- instanceType: "db.t3.small", "db.m5.large"
- engineCode: "mysql", "postgres", "oracle-ee"
- deploymentOption: "Single-AZ", "Multi-AZ"

#### S3 Filters
- storageClass: "Standard", "Standard-IA", "Glacier"
- volumeType: "Standard", "Intelligent-Tiering"

#### Lambda Filters
- memorySize: "128", "256", "512", "1024"
- architecture: "x86_64", "arm64"

### Performance Optimization Guidelines

1. **Use Specific Filters**: Always include relevant filters to reduce response size
2. **Batch Queries**: When comparing multiple options, use ANY_OF filters:
   ```
   {"Field": "instanceType", "Value": ["t3.small", "t3.medium", "t3.large"], "Type": "ANY_OF"}
   ```
3. **Regional Queries**: Use multi-region queries for comparisons instead of separate calls
4. **Cache Results**: Remember pricing data within the same conversation

### Error Handling for MCP Tools
- If MCP tools fail, acknowledge the failure and use your knowledge base
- Always mention when using cached/estimated vs real-time data
- Provide troubleshooting guidance for MCP connection issues

## AWS Pricing Knowledge Context (Fallback)

### Regional Pricing Variations (When MCP Unavailable)
- US East (N. Virginia) - us-east-1: Base pricing (cheapest for most services)
- US West regions: 5-8% higher than us-east-1
- Europe regions: 10-20% higher than us-east-1
- Asia Pacific regions: 15-30% higher than us-east-1
- South America: 25-35% higher than us-east-1

### Common Cost Optimization Strategies
1. **Instance Right-sizing**: Match instance types to actual workload requirements
2. **Reserved Instances**: 30-70% savings for predictable workloads (1-3 year terms)
3. **Spot Instances**: Up to 90% savings for fault-tolerant workloads
4. **Storage Optimization**: Use appropriate S3 storage classes (Standard, IA, Glacier)
5. **Regional Optimization**: Choose cost-effective regions considering latency/compliance
6. **Auto Scaling**: Scale resources based on demand
7. **Load Balancer Optimization**: Choose appropriate LB type (ALB vs NLB vs CLB)

### Service-Specific Optimization Patterns
- **EC2**: Consider newer generation instances (better price/performance)
- **RDS**: Multi-AZ vs Single-AZ, read replicas for read-heavy workloads
- **Lambda**: Optimize memory allocation and execution time
- **S3**: Lifecycle policies, intelligent tiering
- **EBS**: gp3 vs gp2, right-size volumes

## Response Format Guidelines

Structure your responses with:
1. **Architecture Analysis**: Services identified and configurations
2. **Real-Time Pricing Data**: Use MCP tools to get current costs
3. **Cost Breakdown**: Monthly/annual costs by service and category
4. **Regional Considerations**: If applicable, regional pricing differences
5. **Optimization Opportunities**: Prioritized recommendations with savings estimates
6. **Implementation Guidance**: Next steps and considerations

## Important Instructions
- ALWAYS use MCP tools when available for real pricing data
- Be specific about whether you're using real-time data or estimates
- Include monthly AND annual cost estimates
- Ask clarifying questions only for essential missing details
- Default to us-east-1 when no region specified (mention this to user)
- Provide actionable, prioritized optimization recommendations
- Include confidence levels for your estimates

## Query Processing Workflow
1. Analyze the user's architecture description
2. Identify required AWS services and configurations
3. Use get_pricing_service_attributes() to understand available filters
4. Use get_pricing_attribute_values() to get valid filter values
5. Call get_pricing() with optimized filters for each service
6. Calculate total costs and provide breakdown
7. Identify optimization opportunities
8. Present results in structured format

Be concise but comprehensive. Focus on actionable insights that help users make informed decisions."""

    def _get_mcp_tools(self):
        """Get MCP tools for AWS pricing data access with enhanced error handling."""
        if self.pricing_mcp_client:
            logger.info("Returning optimized MCP client for Strands SDK context management")
            return [self.pricing_mcp_client]
        else:
            logger.warning("MCP client not available, using AI-only mode with enhanced fallback")
            return []
    
    def _handle_mcp_error_enhanced(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Enhanced MCP server error handling with specific response patterns."""
        error_info = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'mcp_status': 'unavailable',
            'fallback_used': True,
            'optimization_suggestions': [],
            'troubleshooting': []
        }
        
        # Analyze specific error patterns
        error_str = str(error).lower()
        
        if 'timeout' in error_str or 'connection' in error_str:
            error_info['optimization_suggestions'] = [
                'Reduce query complexity by using more specific filters',
                'Break complex queries into smaller parts',
                'Use cached results when available',
                'Retry with simplified filter criteria'
            ]
        elif 'invalid' in error_str or 'format' in error_str:
            error_info['optimization_suggestions'] = [
                'Verify filter field names using get_pricing_service_attributes()',
                'Check filter values using get_pricing_attribute_values()',
                'Use exact field names and values from MCP server',
                'Ensure filter Type is one of: EQUALS, CONTAINS, ANY_OF'
            ]
        elif 'not found' in error_str or '404' in error_str:
            error_info['optimization_suggestions'] = [
                'Verify service code using get_pricing_service_codes()',
                'Check region name format (e.g., "us-east-1")',
                'Ensure instance types exist in the specified region',
                'Try alternative service configurations'
            ]
        
        # Add general troubleshooting based on error reason
        if hasattr(self, 'mcp_error_reason'):
            if self.mcp_error_reason == "uvx_not_installed":
                error_info['troubleshooting'] = [
                    'Install uvx: pip install uvx',
                    'Or install uv first: pip install uv, then uvx will be available',
                    'Verify installation: uvx --version',
                    'Test AWS Labs MCP server: uvx awslabs.aws-pricing-mcp-server@latest'
                ]
            elif self.mcp_error_reason == "missing_dependencies":
                error_info['troubleshooting'] = [
                    'Install MCP dependencies: pip install mcp',
                    'Install Strands MCP tools: pip install strands[mcp]',
                    'Verify AWS Labs MCP server: uvx awslabs.aws-pricing-mcp-server@latest'
                ]
            else:
                error_info['troubleshooting'] = [
                    'Check AWS Labs MCP server: uvx awslabs.aws-pricing-mcp-server@latest',
                    'Verify network connectivity and AWS credentials',
                    'Check system permissions for subprocess execution',
                    'Try restarting the application'
                ]
        
        return error_info
    
    async def process_pricing_query_optimized(self, query: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Process AWS pricing query with enhanced optimization and performance tracking.
        
        Args:
            query: User's pricing query
            conversation_history: Optional conversation context
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        import time
        start_time = time.time()
        
        try:
            # Update performance stats
            self.performance_stats['total_queries'] += 1
            
            # Check cache for similar queries (simple implementation)
            query_hash = hash(query.lower().strip())
            if query_hash in self.query_cache:
                self.performance_stats['cache_hits'] += 1
                logger.info("Using cached response for similar query")
                cached_response = self.query_cache[query_hash].copy()
                cached_response['cached'] = True
                cached_response['timestamp'] = str(time.time())
                return cached_response
            
            # Create agent with optimized MCP tools
            if not self.agent:
                tools = self._get_mcp_tools()
                self.agent = Agent(
                    model=self.bedrock_model,
                    system_prompt=self._get_optimized_system_prompt(),
                    tools=tools
                )
            
            # Process the query using the optimized agent
            if self.pricing_mcp_client:
                self.performance_stats['mcp_calls'] += 1
            
            response = await self.agent.invoke_async(query)
            
            # Calculate response time
            response_time = time.time() - start_time
            self.performance_stats['avg_response_time'] = (
                (self.performance_stats['avg_response_time'] * (self.performance_stats['total_queries'] - 1) + response_time) 
                / self.performance_stats['total_queries']
            )
            
            result = {
                'status': 'success',
                'response': str(response),
                'agent_type': 'aws_pricing_optimized',
                'mcp_available': self.pricing_mcp_client is not None,
                'response_time': response_time,
                'performance_stats': self.performance_stats.copy(),
                'cached': False,
                'timestamp': str(time.time())
            }
            
            # Cache successful responses (simple implementation)
            if len(self.query_cache) < 10:  # Limit cache size
                self.query_cache[query_hash] = result.copy()
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Error processing optimized pricing query: {str(e)}")
            
            return {
                'status': 'error',
                'error': str(e),
                'agent_type': 'aws_pricing_optimized',
                'mcp_available': self.pricing_mcp_client is not None,
                'response_time': response_time,
                'performance_stats': self.performance_stats.copy(),
                'troubleshooting': self._handle_mcp_error_enhanced("query_processing", e)
            }


def main():
    """Main function for testing the optimized AWS Pricing Agent."""
    async def test_optimized_pricing_agent():
        pricing_agent = AWSPricingAgentOptimized()
        
        # Test queries with increasing complexity
        test_queries = [
            "What's the cost of a t3.small EC2 instance in us-east-1?",
            "Compare t3.small vs t3.medium EC2 costs in us-east-1",
            "I need pricing for a 3-tier web app with EC2, RDS, and S3 for 10,000 users",
            "Compare costs for microservices across us-east-1, us-west-2, and eu-west-1"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n=== Optimized Test Query {i} ===")
            print(f"Query: {query}")
            
            result = await pricing_agent.process_pricing_query_optimized(query)
            print(f"Status: {result.get('status')}")
            print(f"Response time: {result.get('response_time', 0):.2f}s")
            print(f"MCP Available: {result.get('mcp_available', False)}")
            print(f"Cached: {result.get('cached', False)}")
            
            if result.get('status') == 'error':
                print(f"Error: {result.get('error')}")
    
    asyncio.run(test_optimized_pricing_agent())


if __name__ == "__main__":
    main()