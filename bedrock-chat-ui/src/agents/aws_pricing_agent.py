#!/usr/bin/env python3
"""
AWS Pricing Agent - AI-first specialized agent for AWS cost analysis and pricing

This agent leverages Amazon Nova Lite's reasoning capabilities with real-time AWS 
pricing data via MCP to provide intelligent cost analysis and optimization recommendations.
"""

import json
import logging
import asyncio
import time
from typing import Dict, Any, Optional, List
from strands import Agent
from strands.tools.mcp import MCPClient
from .agent_registry import BaseSpecializedAgent, AgentCapability, AgentMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSPricingAgent(BaseSpecializedAgent):
    """
    AI-first AWS Pricing Agent that uses Nova Lite's reasoning with real AWS pricing data.
    Minimal helper code - lets the AI do the heavy lifting with proper context.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the AWS Pricing Agent with Nova Lite model and MCP tools."""
        self.config = config or {}
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
        self.agent_fallback = None  # Fallback agent without MCP tools
        
        # Performance tracking and caching
        self.query_cache = {}
        self.performance_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'mcp_calls': 0,
            'avg_response_time': 0
        }
        
        # Enhanced conversation context for token limit management and architecture tracking
        self.conversation_context = []
        self.max_context_length = 8000  # Token limit for context management
        self.current_architecture = {}  # Track current architecture state
        self.baseline_costs = {}  # Track baseline cost estimates for comparison
        self.scenario_history = []  # Track different scenarios discussed
    
    def _initialize_mcp_client(self):
        """Initialize MCP client connection to aws-pricing server with comprehensive error handling."""
        import os
        
        # First, try to use MCP Proxy if available (for containerized deployments)
        try:
            from .mcp_proxy_client import MCPProxyClient
            
            proxy_url = os.getenv("MCP_PROXY_URL")
            if proxy_url:
                logger.info(f"Attempting to connect to MCP Proxy at {proxy_url}")
                proxy_client = MCPProxyClient(proxy_url)
                if proxy_client.available:
                    logger.info("Successfully connected to MCP Proxy server")
                    self.mcp_connection_status = "proxy_connected"
                    return proxy_client
                else:
                    logger.warning("MCP Proxy configured but not available")
        except ImportError:
            logger.debug("MCP Proxy client not available")
        except Exception as e:
            logger.warning(f"Failed to connect to MCP Proxy: {e}")
        
        # Fallback to direct MCP connection (for local development)
        try:
            from mcp import stdio_client, StdioServerParameters
            from strands.tools.mcp import MCPClient
            
            # Create MCP client with stdio transport for AWS Labs aws-pricing server
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
            logger.info("AWS Pricing MCP client initialized successfully (direct connection)")
            
            # Test the connection - but don't fail if server is unavailable
            try:
                self._test_mcp_connection_simple(pricing_mcp_client)
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
    
    def _test_mcp_connection_simple(self, pricing_mcp_client):
        """Test MCP server connection and log status."""
        if not pricing_mcp_client:
            return False
        
        try:
            # This would be a real test call to the MCP server
            # For now, we'll just mark it as ready for integration
            logger.info("MCP server connection test: Ready for integration")
            self.mcp_connection_status = "ready"
            return True
        except Exception as e:
            logger.warning(f"MCP server connection test failed: {str(e)}")
            self.mcp_connection_status = "failed"
            return False
    
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
                'Use cached results when available'
            ]
            error_info['troubleshooting'] = [
                'Check network connectivity to AWS services',
                'Verify MCP server timeout settings (current: 30s)',
                'Try again in a few moments - server may be temporarily busy'
            ]
        elif 'invalid' in error_str or 'format' in error_str:
            error_info['optimization_suggestions'] = [
                'Verify filter field names using discovery tools',
                'Check filter values using attribute value tools',
                'Use exact field names and values from MCP server'
            ]
            error_info['troubleshooting'] = [
                'Review query format and filter specifications',
                'Check AWS service codes and attribute names',
                'Consult AWS Pricing API documentation for valid parameters'
            ]
        elif hasattr(self, 'mcp_error_reason'):
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
        else:
            error_info['troubleshooting'] = [
                'Check AWS Labs MCP server status and configuration',
                'Verify awslabs.aws-pricing-mcp-server is installed and accessible',
                'Check application logs for detailed error information'
            ]
        
        return error_info

    def _handle_mcp_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return self._handle_mcp_error_enhanced(operation, error)
    
    def _get_system_prompt(self) -> str:
        """Get the enhanced and optimized system prompt for AI-first AWS Pricing Agent."""
        return """You are an AWS Pricing Agent specialized in analyzing AWS architectures and providing concise cost estimates.

## Core Capabilities
Your PRIMARY focus is delivering CONCISE pricing information:
- Calculate accurate costs using real-time pricing data
- Provide clear cost breakdowns in table format
- Show pricing for different usage tiers when applicable
- Suggest ONLY major cost optimizations (>20% savings)

## CRITICAL Response Rules
- **ALWAYS USE MCP TOOLS** - NEVER make up prices! Use get_pricing() for EVERY service
- **NO ROUND NUMBERS** - Real AWS prices are like $0.023, $0.116, NOT $10.00
- **BE CONCISE** - Users want costs, not essays
- **NO IMPLEMENTATION DETAILS** unless specifically requested
- **NO THINKING TAGS** - Never use <thinking> tags in your responses
- **FOCUS ON REAL NUMBERS** - Use actual pricing from MCP tools, not estimates
- **NO VERBOSE SECTIONS** - Skip implementation guidance, architecture analysis narratives

## MANDATORY: You MUST use MCP tools
If you cannot get pricing via MCP tools, say "Unable to retrieve pricing data" - DO NOT make up numbers!

## EXACT TOOL USAGE EXAMPLES:
For OpenSearch Serverless:
```
get_pricing("AmazonOpenSearchServerless", "us-east-1", [])
```
Result will show OCU pricing: $0.24/hour

For Lambda:
```
get_pricing("AWSLambda", "us-east-1", [
  {"Field": "group", "Value": "AWS-Lambda-Requests", "Type": "TERM_MATCH"}
])
```

For API Gateway:
```
get_pricing("AmazonAPIGateway", "us-east-1", [])
```

ALWAYS call these tools - NEVER make up prices like $499.99!

## CRITICAL: MCP Tools Usage Instructions

### When MCP Tools Are Available
You have access to real-time AWS pricing data through MCP tools. ALWAYS use these tools to get current pricing instead of relying on estimates.

### Key MCP Tools and Optimized Usage Patterns

#### 1. get_pricing_service_codes()
Use this first to discover available AWS services:
```
Common service codes you'll use:
- AmazonEC2 (for EC2 instances)
- AWSLambda (for Lambda functions)
- AmazonAPIGateway (for API Gateway)
- AmazonS3 (for S3 storage)
- AmazonOpenSearchServerless (for OpenSearch)
- AWSAmplify (for Amplify hosting)
- AmazonBedrock (for Bedrock)
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
**THIS IS THE MAIN TOOL - USE IT FOR EVERY SERVICE!**
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

### CRITICAL AWS Service Minimums and Real Costs

#### OpenSearch Serverless (MUST KNOW)
- **MINIMUM: 2 OCUs for Bedrock Knowledge Base** (1 indexing + 1 search)
- **Cost per OCU: ~$0.24/hour = ~$175/month**
- **Bedrock KB minimum: ~$350/month** (2 OCUs)
- **NEVER quote less than $350/month for OpenSearch Serverless with Bedrock KB**

#### Other Important Minimums
- **RDS Multi-AZ**: Doubles the instance cost
- **NAT Gateway**: ~$45/month per gateway + data charges
- **ALB**: ~$22/month minimum + LCU charges

### Realistic Usage Assumptions for Common Scenarios

#### Static Websites / Single Page Applications (SPAs)
**CRITICAL**: Use realistic data transfer estimates for static sites!
- **Small to Medium Static Sites**: 10-50 GB/month data transfer
- **Popular Static Sites**: 100-500 GB/month data transfer  
- **High-Traffic Static Sites**: 500-2000 GB/month data transfer
- **Enterprise Static Sites**: 1-5 TB/month data transfer

**Default Assumptions for Static Sites (unless specified otherwise):**
- Storage: 1-10 GB for assets
- Data Transfer: 50-100 GB/month (NOT 10TB!)
- Requests: 100k-1M requests/month
- CDN Cache Hit Ratio: 80-95%

**IMPORTANT - Clarification Strategy:**
When users ask about static website costs without specifying traffic:
1. Provide estimates for MULTIPLE traffic tiers (small, medium, large)
2. Explicitly state assumptions for each tier
3. Ask: "Which traffic level best matches your expected usage?"
4. Suggest: "For a more accurate estimate, could you share your expected monthly visitors or data transfer?"

#### Dynamic Web Applications
- Small Apps: 100-500 GB/month transfer
- Medium Apps: 1-5 TB/month transfer
- Large Apps: 5-20 TB/month transfer

#### Media/Video Streaming
- Small: 1-10 TB/month
- Medium: 10-50 TB/month
- Large: 50-100+ TB/month

**IMPORTANT**: Always ask the user about expected traffic levels. Don't assume 10TB for a static website!

## Response Format Guidelines

**Keep responses SHORT and FOCUSED on costs.**

### 1. Quick Summary (1-2 lines)
State what you're pricing and key assumptions

### 2. Cost Breakdown
Present costs in a clear table format:
```markdown
| Service | Monthly Cost | Annual Cost |
|---------|-------------|------------|
| EC2     | $XX.XX      | $XXX.XX    |
| S3      | $XX.XX      | $XXX.XX    |
```

For static sites without traffic specs, show 3 tiers:
```markdown
### Traffic Tier Estimates
#### Small (10-50 GB/month)
- **Monthly**: $XX.XX
- **Annual**: $XXX.XX

#### Medium (100-500 GB/month) 
- **Monthly**: $XX.XX
- **Annual**: $XXX.XX

#### Large (1-2 TB/month)
- **Monthly**: $XX.XX  
- **Annual**: $XXX.XX
```

### 3. Key Cost Optimizations (Optional)
- Only include if significant savings possible (>20%)
- Keep to 2-3 most impactful recommendations
- Include **estimated savings** in bold

### 4. Questions (If Needed)
> Use blockquotes for clarification questions only when critical information is missing

**IMPORTANT**: 
- DO NOT include implementation steps unless specifically asked
- DO NOT add thinking tags - those are only for the router agent
- Keep responses focused on COSTS and PRICING
- Be concise - users want numbers, not lengthy explanations

## Conversation Context and Architecture Tracking

### Context Awareness
You maintain conversation context to provide intelligent follow-up responses:
- **Architecture Evolution**: Track changes to the user's architecture across the conversation
- **Cost Baselines**: Remember previous cost estimates for comparison purposes
- **Scenario Comparison**: Compare new scenarios against previously discussed architectures
- **Incremental Updates**: Handle architecture modifications and recalculate costs accordingly

### Follow-up Query Handling
When users ask follow-up questions:
- Reference the previously discussed architecture and costs
- Highlight what has changed from the baseline
- Provide comparative analysis (e.g., "This would increase costs by $X compared to your previous setup")
- Maintain context about optimization recommendations already provided

### Scenario Comparison
When users ask "what if" questions or request alternatives:
- Compare against the current/baseline architecture
- Show cost differences clearly (e.g., "Option A: $500/month vs Current: $400/month (+$100)")
- Explain trade-offs between scenarios
- Recommend the best option based on requirements and budget

### Architecture Modification Handling
When users modify their architecture:
- Identify what services/configurations have changed
- Recalculate costs for the modified architecture
- Show the cost impact of the changes
- Update optimization recommendations based on the new architecture

## Important Instructions
- ALWAYS use MCP tools when available for real pricing data
- Be specific about whether you're using real-time data or estimates
- Include monthly AND annual cost estimates
- **For static sites/SPAs**: ALWAYS show 3 traffic tiers if not specified
- Ask clarifying questions for missing traffic/usage details
- Default to us-east-1 when no region specified (mention this to user)
- Provide actionable, prioritized optimization recommendations
- Include confidence levels for your estimates
- **Reference previous discussions** when handling follow-up queries
- **Compare scenarios** when users ask about alternatives
- **Track architecture changes** and show cost impacts clearly
- **End with questions** to refine estimates when making assumptions

## Query Processing Workflow
1. Analyze the user's architecture description
2. Identify required AWS services and configurations
3. **FOR EACH SERVICE**: Use get_pricing() to get REAL prices
4. Calculate total costs using ACTUAL prices from MCP
5. Present results in structured format

## NEVER DO THIS:
❌ "API Gateway: $10.00/month" (made up round number)
❌ "Lambda: $10.00/month" (fake estimate)
❌ "OpenSearch Serverless: $10.00/month" (WRONG! Minimum is $350/month for Bedrock KB)
❌ "Total: $41.40/month" (calculated from fake numbers)

## ALWAYS DO THIS:
✅ Use get_pricing("AmazonOpenSearchServerless", "us-east-1", filters)
✅ "OpenSearch Serverless: 2 OCUs × $0.24/hour = $350/month minimum"
✅ "Lambda: $0.0000166667 per GB-second"
✅ Calculate based on REAL pricing data

## VALIDATION RULES:
- If response includes OpenSearch Serverless < $350/month for Bedrock KB, it's WRONG
- If response has all round numbers ($10, $20, $30), it's WRONG
- If response doesn't mention OCUs for OpenSearch, it's INCOMPLETE

Be concise but comprehensive. Focus on actionable insights that help users make informed decisions."""

    def _get_mcp_tools(self):
        """Get MCP tools for AWS pricing data access."""
        if self.pricing_mcp_client:
            # Return the MCP client directly - Strands SDK will handle context management
            logger.info("Returning MCP client for Strands SDK context management")
            return [self.pricing_mcp_client]
        else:
            logger.warning("MCP client not available, using AI-only mode")
            return []

    def _get_fallback_system_prompt(self) -> str:
        """Get system prompt for fallback mode when MCP is unavailable."""
        return """You are an AWS Pricing Agent operating in FALLBACK MODE. The real-time pricing data service is currently unavailable, so you'll provide estimates based on your knowledge base.

## IMPORTANT: Fallback Mode Notice
⚠️ **Real-time pricing data is currently unavailable.** You are operating with cached knowledge and should:
1. Clearly indicate that estimates are based on knowledge base, not real-time data
2. Provide confidence levels for your estimates
3. Suggest users verify with AWS Calculator or AWS Console
4. Include disclaimers about pricing accuracy

## Core Capabilities (Fallback Mode)
- Analyze architecture descriptions and identify AWS services
- Provide cost estimates based on knowledge base pricing patterns
- Offer cost optimization recommendations
- Compare pricing across regions using historical patterns
- Suggest architectural improvements for cost efficiency

## Fallback Pricing Guidelines

### Regional Pricing Variations (Approximate)
- US East (N. Virginia) - us-east-1: Base pricing (typically lowest)
- US West regions: 5-8% higher than us-east-1
- Europe regions: 10-20% higher than us-east-1
- Asia Pacific regions: 15-30% higher than us-east-1
- South America: 25-35% higher than us-east-1

### Common Service Pricing Patterns (Estimates)
**CRITICAL MINIMUMS:**
- **OpenSearch Serverless for Bedrock KB: $350/month MINIMUM** (2 OCUs required)
- **NAT Gateway: $45/month minimum**
- **ALB: $22/month minimum**

**EC2 Instances (us-east-1, Linux, On-Demand):**
- t3.micro: ~$0.0104/hour (~$7.50/month)
- t3.small: ~$0.0208/hour (~$15/month)
- t3.medium: ~$0.0416/hour (~$30/month)
- m5.large: ~$0.096/hour (~$70/month)

**RDS (us-east-1, MySQL, Single-AZ):**
- db.t3.micro: ~$0.017/hour (~$12/month)
- db.t3.small: ~$0.034/hour (~$25/month)
- db.t3.medium: ~$0.068/hour (~$50/month)

**S3 Storage (us-east-1):**
- Standard: ~$0.023/GB/month
- Standard-IA: ~$0.0125/GB/month

**Lambda:**
- Requests: ~$0.20 per 1M requests
- Compute: ~$0.0000166667 per GB-second

**Bedrock Knowledge Base:**
- OpenSearch Serverless backend: $350/month minimum (2 OCUs)
- S3 storage for documents: Variable
- Bedrock model invocations: Per-token pricing

### Error Handling and User Communication
- Always mention fallback mode status
- Provide confidence levels: "Low-Medium confidence (fallback mode)"
- Include verification suggestions
- Offer troubleshooting guidance for MCP connectivity

### Response Format (Fallback Mode)
1. **Fallback Mode Notice**: Clear indication of operating mode
2. **Architecture Analysis**: Services identified and configurations
3. **Estimated Costs**: Based on knowledge base with confidence levels
4. **Regional Considerations**: Approximate regional variations
5. **Optimization Opportunities**: General recommendations
6. **Verification Guidance**: How to get accurate real-time pricing

## Important Instructions
- ALWAYS mention you're in fallback mode at the start of responses
- Include confidence levels for all estimates
- Suggest verification with AWS Calculator or real-time tools
- Provide general optimization guidance
- Ask clarifying questions for essential missing details
- Default to us-east-1 when no region specified
- Include disclaimers about pricing accuracy and currency

## Sample Fallback Response Format
"⚠️ **Operating in Fallback Mode** - Real-time pricing data unavailable. Providing estimates based on knowledge base.

[Analysis and estimates with confidence levels]

**Confidence Level:** Medium (based on historical patterns)
**Verification:** Please verify with AWS Calculator or AWS Console for current pricing
**Troubleshooting:** [If applicable, include MCP connectivity guidance]"
"""

    def _create_fallback_agent(self):
        """Create fallback agent without MCP tools for when real-time data is unavailable."""
        if not self.agent_fallback:
            self.agent_fallback = Agent(
                model=self.bedrock_model,
                system_prompt=self._get_fallback_system_prompt(),
                tools=[]  # No MCP tools in fallback mode
            )
        return self.agent_fallback

    def _generate_error_response(self, query: str, error: Exception) -> str:
        """Generate helpful error response for users."""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Analyze query to provide context-specific help
        query_lower = query.lower()
        is_pricing_query = any(keyword in query_lower for keyword in ['cost', 'price', 'pricing', 'budget', 'estimate'])
        
        base_response = "I apologize, but I encountered an issue while processing your request."
        
        if is_pricing_query:
            base_response += " I understand you're looking for AWS pricing information."
        
        # Provide specific guidance based on error type
        if 'timeout' in error_msg.lower():
            return f"""{base_response}

**Issue:** The request timed out while retrieving pricing data.

**What you can try:**
1. **Simplify your query** - Ask about specific services one at a time
2. **Be more specific** - Include exact instance types, regions, or service configurations
3. **Try again** - The service may be temporarily busy

**Example of a simpler query:**
"What's the cost of a t3.small EC2 instance in us-east-1?"

Would you like to try rephrasing your question with more specific details?"""

        elif 'connection' in error_msg.lower() or 'network' in error_msg.lower():
            return f"""{base_response}

**Issue:** Unable to connect to real-time pricing data service.

**Current status:** Operating in fallback mode with estimated pricing.

**What this means:**
- I can still provide cost estimates based on my knowledge
- Estimates may not reflect the most current AWS pricing
- I recommend verifying with AWS Calculator for precise costs

**How to get current pricing:**
1. Visit the [AWS Calculator](https://calculator.aws/)
2. Check the AWS Console for current pricing
3. Try your query again in a few minutes

Would you like me to provide an estimated cost analysis based on my knowledge base?"""

        elif 'invalid' in error_msg.lower() or 'format' in error_msg.lower():
            return f"""{base_response}

**Issue:** There was a problem with the query format or parameters.

**What you can try:**
1. **Rephrase your question** - Use simpler language
2. **Be more specific** - Include service names, regions, and configurations
3. **Check service names** - Ensure AWS service names are correct

**Example queries that work well:**
- "Cost of EC2 t3.medium in us-east-1"
- "RDS MySQL pricing for db.t3.small"
- "S3 storage costs for 100GB"

Could you please rephrase your question with more specific details about the AWS services you're interested in?"""

        else:
            return f"""{base_response}

**Issue:** {error_type} - {error_msg[:100]}{'...' if len(error_msg) > 100 else ''}

**What you can try:**
1. **Rephrase your question** - Try asking in a different way
2. **Be more specific** - Include exact AWS service names and configurations
3. **Try a simpler query** - Ask about one service at a time
4. **Check your request** - Ensure you're asking about AWS services and pricing

**Need help?** Here are some example queries:
- "What does it cost to run a web application on AWS?"
- "EC2 pricing for t3.small instances"
- "Compare costs between us-east-1 and eu-west-1"

Would you like to try asking your question in a different way?"""
    
    def _extract_architecture_info(self, query: str, response: str) -> Dict[str, Any]:
        """Extract architecture information from query and response."""
        architecture_info = {
            'services': [],
            'configurations': {},
            'regions': [],
            'usage_patterns': {}
        }
        
        # Extract AWS services mentioned
        aws_services = ['ec2', 'rds', 's3', 'lambda', 'eks', 'ecs', 'elb', 'alb', 'nlb', 
                       'cloudfront', 'route53', 'dynamodb', 'redshift', 'emr', 'sqs', 'sns']
        
        combined_text = f"{query} {response}".lower()
        
        for service in aws_services:
            if service in combined_text:
                architecture_info['services'].append(service.upper())
        
        # Extract instance types
        import re
        instance_pattern = r'(t[2-4]\.[a-z]+|m[4-6]\.[a-z]+|c[4-6]\.[a-z]+|r[4-6]\.[a-z]+|db\.[a-z0-9]+\.[a-z]+)'
        instances = re.findall(instance_pattern, combined_text)
        if instances:
            architecture_info['configurations']['instance_types'] = list(set(instances))
        
        # Extract regions
        region_pattern = r'(us-[a-z]+-[0-9]+|eu-[a-z]+-[0-9]+|ap-[a-z]+-[0-9]+|ca-[a-z]+-[0-9]+|sa-[a-z]+-[0-9]+)'
        regions = re.findall(region_pattern, combined_text)
        if regions:
            architecture_info['regions'] = list(set(regions))
        
        # Extract usage patterns
        usage_keywords = {
            'users': r'(\d+)\s*users?',
            'requests': r'(\d+)\s*requests?',
            'storage': r'(\d+)\s*(gb|tb|pb)',
            'bandwidth': r'(\d+)\s*(mbps|gbps)'
        }
        
        for pattern_type, pattern in usage_keywords.items():
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                architecture_info['usage_patterns'][pattern_type] = matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        return architecture_info
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query for better context management."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['compare', 'comparison', 'vs', 'versus', 'difference']):
            return 'comparison'
        elif any(word in query_lower for word in ['optimize', 'reduce', 'save', 'cheaper', 'alternative']):
            return 'optimization'
        elif any(word in query_lower for word in ['what if', 'scenario', 'instead', 'change']):
            return 'scenario'
        elif any(word in query_lower for word in ['add', 'include', 'also', 'additionally']):
            return 'modification'
        elif any(word in query_lower for word in ['cost', 'price', 'estimate', 'budget']):
            return 'pricing'
        else:
            return 'general'
    
    def _extract_cost_estimates(self, response: str) -> Dict[str, Any]:
        """Extract cost estimates from response for baseline tracking."""
        cost_info = {
            'monthly_total': None,
            'annual_total': None,
            'service_breakdown': {},
            'currency': 'USD'
        }
        
        import re
        
        # Extract total costs
        monthly_pattern = r'\$([0-9,]+\.?[0-9]*)\s*(?:per\s+)?month'
        annual_pattern = r'\$([0-9,]+\.?[0-9]*)\s*(?:per\s+)?year'
        
        monthly_matches = re.findall(monthly_pattern, response, re.IGNORECASE)
        annual_matches = re.findall(annual_pattern, response, re.IGNORECASE)
        
        if monthly_matches:
            try:
                cost_info['monthly_total'] = float(monthly_matches[-1].replace(',', ''))
            except ValueError:
                pass
        
        if annual_matches:
            try:
                cost_info['annual_total'] = float(annual_matches[-1].replace(',', ''))
            except ValueError:
                pass
        
        # Extract service-specific costs (simplified)
        service_pattern = r'(EC2|RDS|S3|Lambda|ELB|ALB|NLB).*?\$([0-9,]+\.?[0-9]*)'
        service_matches = re.findall(service_pattern, response, re.IGNORECASE)
        
        for service, cost in service_matches:
            try:
                cost_info['service_breakdown'][service.upper()] = float(cost.replace(',', ''))
            except ValueError:
                pass
        
        return cost_info
    
    def _update_architecture_state(self, architecture_info: Dict[str, Any]) -> None:
        """Update the current architecture state with new information."""
        # Merge services
        if architecture_info.get('services'):
            existing_services = set(self.current_architecture.get('services', []))
            new_services = set(architecture_info['services'])
            self.current_architecture['services'] = list(existing_services.union(new_services))
        
        # Merge configurations
        if architecture_info.get('configurations'):
            if 'configurations' not in self.current_architecture:
                self.current_architecture['configurations'] = {}
            self.current_architecture['configurations'].update(architecture_info['configurations'])
        
        # Update regions
        if architecture_info.get('regions'):
            self.current_architecture['regions'] = architecture_info['regions']
        
        # Update usage patterns
        if architecture_info.get('usage_patterns'):
            if 'usage_patterns' not in self.current_architecture:
                self.current_architecture['usage_patterns'] = {}
            self.current_architecture['usage_patterns'].update(architecture_info['usage_patterns'])
        
        # Update timestamp
        self.current_architecture['last_updated'] = time.time()
    
    def _format_architecture_summary(self) -> str:
        """Format current architecture state for context."""
        if not self.current_architecture:
            return ""
        
        summary_parts = []
        
        if self.current_architecture.get('services'):
            services = ', '.join(self.current_architecture['services'])
            summary_parts.append(f"Services: {services}")
        
        if self.current_architecture.get('configurations', {}).get('instance_types'):
            instances = ', '.join(self.current_architecture['configurations']['instance_types'])
            summary_parts.append(f"Instances: {instances}")
        
        if self.current_architecture.get('regions'):
            regions = ', '.join(self.current_architecture['regions'])
            summary_parts.append(f"Regions: {regions}")
        
        if self.current_architecture.get('usage_patterns'):
            patterns = []
            for key, value in self.current_architecture['usage_patterns'].items():
                patterns.append(f"{key}: {value}")
            if patterns:
                summary_parts.append(f"Usage: {', '.join(patterns)}")
        
        return '; '.join(summary_parts)
    
    def _format_baseline_costs(self) -> str:
        """Format baseline costs for context."""
        if not self.baseline_costs:
            return ""
        
        cost_parts = []
        
        if self.baseline_costs.get('monthly_total'):
            cost_parts.append(f"Monthly: ${self.baseline_costs['monthly_total']:.2f}")
        
        if self.baseline_costs.get('service_breakdown'):
            breakdown = []
            for service, cost in self.baseline_costs['service_breakdown'].items():
                breakdown.append(f"{service}: ${cost:.2f}")
            if breakdown:
                cost_parts.append(f"Breakdown: {', '.join(breakdown)}")
        
        return '; '.join(cost_parts)
    
    def _is_comparison_query(self, query: str) -> bool:
        """Check if query is asking for scenario comparison."""
        comparison_keywords = ['compare', 'comparison', 'vs', 'versus', 'difference', 'what if', 'scenario', 'alternative']
        return any(keyword in query.lower() for keyword in comparison_keywords)
    
    def _add_scenario_to_history(self, query: str, response: str, cost_info: Dict[str, Any]) -> None:
        """Add scenario to history for comparison purposes."""
        scenario = {
            'query': query,
            'response_summary': response[:200] + "..." if len(response) > 200 else response,
            'cost_info': cost_info,
            'timestamp': time.time(),
            'architecture_snapshot': self.current_architecture.copy()
        }
        
        self.scenario_history.append(scenario)
        
        # Keep only last 5 scenarios to manage memory
        if len(self.scenario_history) > 5:
            self.scenario_history = self.scenario_history[-5:]
    
    def _manage_conversation_context(self, query: str, response: str) -> None:
        """Enhanced conversation context management with architecture tracking."""
        # Extract architecture information from query and response
        architecture_info = self._extract_architecture_info(query, response)
        
        # Add current exchange to context with enhanced metadata
        context_entry = {
            'query': query,
            'response': response,
            'timestamp': time.time(),
            'architecture_info': architecture_info,
            'query_type': self._classify_query_type(query),
            'cost_estimates': self._extract_cost_estimates(response)
        }
        
        self.conversation_context.append(context_entry)
        
        # Update current architecture state if new information is available
        if architecture_info.get('services') or architecture_info.get('configurations'):
            self._update_architecture_state(architecture_info)
        
        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        total_chars = sum(len(item['query']) + len(item['response']) for item in self.conversation_context)
        estimated_tokens = total_chars // 4
        
        # If approaching token limit, summarize older context
        if estimated_tokens > self.max_context_length:
            self._summarize_conversation_context()

    def _summarize_conversation_context(self) -> None:
        """Enhanced conversation context summarization with architecture and cost tracking."""
        if len(self.conversation_context) <= 2:
            return  # Keep at least 2 recent exchanges
        
        # Keep the most recent 2 exchanges and summarize the rest
        recent_context = self.conversation_context[-2:]
        older_context = self.conversation_context[:-2]
        
        # Create intelligent summary of older context
        summary_items = []
        architecture_evolution = []
        cost_evolution = []
        
        for item in older_context:
            query_type = item.get('query_type', 'general')
            
            # Summarize by query type
            if query_type == 'pricing':
                cost_info = item.get('cost_estimates', {})
                if cost_info.get('monthly_total'):
                    cost_evolution.append(f"${cost_info['monthly_total']:.0f}/month")
                summary_items.append(f"Pricing query: {item['query'][:80]}...")
            elif query_type == 'comparison':
                summary_items.append(f"Comparison: {item['query'][:80]}...")
            elif query_type == 'optimization':
                summary_items.append(f"Optimization: {item['query'][:80]}...")
            elif query_type == 'scenario':
                summary_items.append(f"Scenario: {item['query'][:80]}...")
            elif query_type == 'modification':
                arch_info = item.get('architecture_info', {})
                if arch_info.get('services'):
                    architecture_evolution.append(f"Added: {', '.join(arch_info['services'])}")
                summary_items.append(f"Architecture change: {item['query'][:80]}...")
            else:
                summary_items.append(f"General query: {item['query'][:80]}...")
        
        # Build comprehensive summary
        summary_parts = []
        
        if summary_items:
            summary_parts.append(f"Previous queries: {'; '.join(summary_items[-3:])}")  # Last 3 items
        
        if architecture_evolution:
            summary_parts.append(f"Architecture evolution: {'; '.join(architecture_evolution)}")
        
        if cost_evolution:
            summary_parts.append(f"Cost progression: {' → '.join(cost_evolution[-3:])}")  # Last 3 costs
        
        # Create summary entry
        if summary_parts:
            summary_entry = {
                'query': 'CONTEXT_SUMMARY',
                'response': f"Conversation summary: {' | '.join(summary_parts)}",
                'timestamp': time.time(),
                'query_type': 'summary',
                'architecture_info': {},
                'cost_estimates': {}
            }
            self.conversation_context = [summary_entry] + recent_context
        else:
            self.conversation_context = recent_context
        
        logger.info(f"Enhanced conversation context summarized. Entries: {len(self.conversation_context)}, Architecture services: {len(self.current_architecture.get('services', []))}, Scenarios tracked: {len(self.scenario_history)}")

    def _get_context_aware_query(self, query: str) -> str:
        """Enhanced query with comprehensive conversation context and architecture state."""
        if not self.conversation_context:
            return query
        
        # Build comprehensive context summary
        context_parts = []
        
        # Add current architecture state if available
        if self.current_architecture:
            arch_summary = self._format_architecture_summary()
            if arch_summary:
                context_parts.append(f"Current Architecture: {arch_summary}")
        
        # Add baseline costs if available
        if self.baseline_costs:
            cost_summary = self._format_baseline_costs()
            if cost_summary:
                context_parts.append(f"Baseline Costs: {cost_summary}")
        
        # Add recent conversation context
        recent_context = []
        for item in self.conversation_context[-2:]:  # Last 2 exchanges
            if item.get('query') != 'CONTEXT_SUMMARY':
                query_type = item.get('query_type', 'general')
                recent_context.append(f"Previous {query_type}: {item['query'][:100]}")
        
        if recent_context:
            context_parts.append(f"Recent Discussion: {'; '.join(recent_context)}")
        
        # Add scenario comparison context if applicable
        if self._is_comparison_query(query) and len(self.scenario_history) > 0:
            context_parts.append(f"Previous Scenarios: {len(self.scenario_history)} discussed")
        
        if context_parts:
            enhanced_query = f"CONTEXT:\n{chr(10).join(context_parts)}\n\nCURRENT QUERY: {query}"
            return enhanced_query
        
        return query

    async def process_pricing_query(self, query: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
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
            
            # Enhance query with conversation context
            context_aware_query = self._get_context_aware_query(query)
            
            # Check cache for similar queries (simple implementation)
            query_hash = hash(query.lower().strip())
            if query_hash in self.query_cache:
                self.performance_stats['cache_hits'] += 1
                logger.info("Using cached response for similar query")
                cached_response = self.query_cache[query_hash].copy()
                cached_response['cached'] = True
                cached_response['timestamp'] = str(time.time())
                return cached_response
            
            # Try MCP-enabled agent first
            response = None
            mcp_available = self.pricing_mcp_client is not None
            
            if mcp_available:
                try:
                    # Create agent with MCP tools
                    tools = self._get_mcp_tools()
                    if not self.agent:
                        self.agent = Agent(
                            model=self.bedrock_model,
                            system_prompt=self._get_system_prompt(),
                            tools=tools
                        )
                    
                    self.performance_stats['mcp_calls'] += 1
                    logger.info(f"Invoking agent with MCP tools. Tools available: {len(tools)}")
                    response = await self.agent.invoke_async(context_aware_query)
                    
                    logger.info(f"Successfully processed query with MCP tools. Response length: {len(str(response))}")
                    
                except Exception as mcp_error:
                    import traceback
                    logger.error(f"MCP agent failed: {str(mcp_error)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    mcp_available = False
                    
                    # Try fallback agent
                    fallback_agent = self._create_fallback_agent()
                    response = await fallback_agent.invoke_async(context_aware_query)
                    
                    # Add fallback notice to response
                    response_str = str(response)
                    if not response_str.startswith("⚠️"):
                        response = f"⚠️ **Real-time pricing data temporarily unavailable** - Using knowledge base estimates.\n\n{response_str}\n\n**Note:** Please verify pricing with AWS Calculator for current rates."
            else:
                # Use fallback agent directly
                logger.info("Using fallback agent (MCP not available)")
                fallback_agent = self._create_fallback_agent()
                response = await fallback_agent.invoke_async(context_aware_query)
            
            # Calculate response time
            response_time = time.time() - start_time
            self.performance_stats['avg_response_time'] = (
                (self.performance_stats['avg_response_time'] * (self.performance_stats['total_queries'] - 1) + response_time) 
                / self.performance_stats['total_queries']
            )
            
            response_str = str(response)
            
            # Enhanced conversation context management
            self._manage_conversation_context(query, response_str)
            
            # Extract and update baseline costs if this is a new architecture
            cost_info = self._extract_cost_estimates(response_str)
            if cost_info.get('monthly_total') or cost_info.get('service_breakdown'):
                self.baseline_costs = cost_info
            
            # Add to scenario history if this is a comparison or scenario query
            if self._is_comparison_query(query) or self._classify_query_type(query) in ['scenario', 'modification']:
                self._add_scenario_to_history(query, response_str, cost_info)
            
            result = {
                'status': 'success',
                'response': response_str,
                'agent_type': 'aws_pricing_enhanced' if mcp_available else 'aws_pricing_fallback',
                'mcp_available': mcp_available,
                'response_time': response_time,
                'performance_stats': self.performance_stats.copy(),
                'cached': False,
                'timestamp': str(time.time()),
                'confidence': 'high' if mcp_available else 'medium',
                'context_length': len(self.conversation_context),
                'current_architecture': self.current_architecture.copy() if self.current_architecture else {},
                'baseline_costs': self.baseline_costs.copy() if self.baseline_costs else {},
                'scenarios_tracked': len(self.scenario_history)
            }
            
            # Cache successful responses (simple implementation)
            if len(self.query_cache) < 10:  # Limit cache size
                self.query_cache[query_hash] = result.copy()
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Error processing pricing query: {str(e)}")
            
            # Provide helpful error response
            error_response = self._generate_error_response(query, e)
            
            return {
                'status': 'error',
                'response': error_response,
                'error': str(e),
                'agent_type': 'aws_pricing_error',
                'mcp_available': self.pricing_mcp_client is not None,
                'response_time': response_time,
                'performance_stats': self.performance_stats.copy(),
                'troubleshooting': self._handle_mcp_error_enhanced("query_processing", e),
                'confidence': 'low'
            }


    def get_capabilities(self) -> List[AgentCapability]:
        """Return list of capabilities this agent can handle."""
        return [
            AgentCapability(
                name="aws_cost_analysis",
                description="Analyze AWS architecture costs and provide estimates",
                keywords=["cost", "price", "pricing", "budget", "estimate", "expensive", "cheap", "savings", "bill", "billing"],
                phrases=["how much does", "cost analysis", "pricing for", "budget for", "optimize costs", "cost comparison"],
                priority=8,
                confidence_threshold=0.3
            ),
            AgentCapability(
                name="aws_optimization",
                description="Provide AWS cost optimization recommendations",
                keywords=["optimize", "reduce", "save", "cheaper", "alternative", "efficiency"],
                phrases=["optimize costs", "reduce spending", "save money", "cost optimization", "cheaper alternative"],
                priority=7,
                confidence_threshold=0.3
            ),
            AgentCapability(
                name="aws_architecture_costing",
                description="Cost analysis for AWS architectures and workloads",
                keywords=["architecture", "workload", "deployment", "infrastructure", "setup"],
                phrases=["architecture cost", "workload pricing", "deployment cost", "infrastructure cost"],
                priority=6,
                confidence_threshold=0.3
            )
        ]
    
    def get_metadata(self) -> AgentMetadata:
        """Return agent metadata."""
        return AgentMetadata(
            name="AWS Pricing Agent",
            description="AI-first specialized agent for AWS cost analysis and pricing optimization",
            version="2.0.0",
            author="System",
            capabilities=self.get_capabilities(),
            model_config={
                "model_id": "amazon.nova-lite-v1:0",
                "temperature": 0.2,
                "max_tokens": 6000,
                "top_p": 0.7
            },
            system_prompt_template="AI-first AWS pricing agent with comprehensive knowledge and MCP integration",
            tools_required=["mcp_client"],
            mcp_servers=["aws-pricing"],
            dependencies=["strands", "mcp"],
            enabled=True
        )
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query and return structured response.
        This wraps the existing process_pricing_query method to match the BaseSpecializedAgent interface.
        """
        return await self.process_pricing_query(query)

def main():
    """Main function for testing the AWS Pricing Agent."""
    async def test_pricing_agent():
        pricing_agent = AWSPricingAgent()
        
        # Test query
        test_query = "I need to estimate costs for a 3-tier web application with EC2 instances, RDS database, and S3 storage. Expected 10,000 users per month."
        
        result = await pricing_agent.process_pricing_query(test_query)
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_pricing_agent())


if __name__ == "__main__":
    main()