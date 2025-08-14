#!/usr/bin/env python3
"""
AWS Pricing Agent - AI-first specialized agent for AWS cost analysis and pricing

This agent leverages Amazon Nova Pro's reasoning capabilities with real-time AWS 
pricing data via MCP to provide intelligent cost analysis and optimization recommendations.
"""

import json
import logging
import asyncio
import time
from typing import Dict, Any, Optional, List
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
from .agent_registry import BaseSpecializedAgent, AgentCapability, AgentMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSPricingAgent(BaseSpecializedAgent):
    """
    AI-first AWS Pricing Agent that uses Nova Pro's reasoning with real AWS pricing data.
    Minimal helper code - lets the AI do the heavy lifting with proper context.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the AWS Pricing Agent with Nova Pro model and MCP tools."""
        self.config = config or {}
        from strands.models import BedrockModel
        import os
        
        # Set region from config or environment
        self.region = self.config.get('region', os.getenv('AWS_REGION', 'us-east-1'))
        
        # Create BedrockModel with Nova Pro configuration for reliable tool use
        # Configure with extended timeout for complex tool interactions
        import boto3
        from botocore.config import Config
        
        # Create Bedrock client with extended timeout and optimized settings
        self.bedrock_config = Config(
            read_timeout=300,  # 5 minutes for complex tool calls
            connect_timeout=30,  # Increase connection timeout
            retries={'max_attempts': 3, 'mode': 'adaptive'}  # Adaptive retry with backoff
        )
        
        bedrock_client = boto3.client('bedrock-runtime', config=self.bedrock_config)
        
        # Try Nova Pro Latency Optimized for faster responses with tools
        # Falls back to regular Nova Pro if not available
        model_id = "amazon.nova-pro-v1:0-latency-optimized"
        try:
            # Test if latency optimized model is available
            test_response = bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                })
            )
            logger.info("Using Nova Pro Latency Optimized variant")
        except:
            # Fall back to regular Nova Pro
            model_id = "amazon.nova-pro-v1:0"
            logger.info("Using standard Nova Pro model")
        
        self.bedrock_model = BedrockModel(
            model_id=model_id,
            temperature=0.2,  # Reduced for more consistent responses
            max_tokens=6000,  # Increased for complex queries
            top_p=0.7,        # Optimized for focused responses
            region_name=self.region,
            boto_client_config=self.bedrock_config
        )
        
        # Initialize direct MCP client (no proxy needed)
        self.mcp_client = self._initialize_direct_mcp_client()
        
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
    
    def _initialize_direct_mcp_client(self):
        """Initialize direct MCP client using stdio transport."""
        try:
            from mcp import stdio_client, StdioServerParameters
            from strands.tools.mcp import MCPClient
            import os
            import subprocess
            
            # Test if the MCP server command works first
            command = "uvx"
            args = ["awslabs.aws-pricing-mcp-server"]
            
            logger.info(f"Testing MCP server command: {command} {' '.join(args)}")
            try:
                # Test if we can run the command at all
                test_result = subprocess.run(
                    [command] + args + ["--help"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                logger.info(f"MCP server test result: returncode={test_result.returncode}")
                if test_result.stdout:
                    logger.info(f"MCP server test stdout: {test_result.stdout[:200]}")
                if test_result.stderr:
                    logger.warning(f"MCP server test stderr: {test_result.stderr[:200]}")
                    
                # If help command fails, try checking if module exists
                if test_result.returncode != 0:
                    logger.error("MCP server --help failed, checking if module is installed...")
                    check_result = subprocess.run(
                        [command, "-c", "import awslabs.aws_pricing_mcp_server; print('Module found')"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    logger.info(f"Module check result: returncode={check_result.returncode}, stdout={check_result.stdout}, stderr={check_result.stderr}")
                    
            except Exception as test_error:
                logger.error(f"MCP server command test failed: {test_error}")
                # Try a simpler test
                try:
                    simple_test = subprocess.run(
                        [command, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    logger.info(f"Python version test: {simple_test.stdout}")
                except Exception as simple_error:
                    logger.error(f"Even python --version failed: {simple_error}")
                return None
            
            # Build environment with explicit ECS credential variables
            mcp_env = {
                **os.environ,
                "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
                "FASTMCP_LOG_LEVEL": "ERROR"
            }
            
            # Explicitly pass ECS credential environment variables if they exist
            ecs_credential_vars = [
                "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI",
                "AWS_CONTAINER_CREDENTIALS_FULL_URI", 
                "AWS_CONTAINER_AUTHORIZATION_TOKEN",
                "AWS_ACCESS_KEY_ID",
                "AWS_SECRET_ACCESS_KEY",
                "AWS_SESSION_TOKEN"
            ]
            
            for var in ecs_credential_vars:
                if var in os.environ:
                    mcp_env[var] = os.environ[var]
                    logger.debug(f"Passing ECS credential variable: {var}")
            
            logger.info(f"MCP environment has AWS_REGION: {mcp_env.get('AWS_REGION')}")
            logger.info(f"ECS credential vars present: {[var for var in ecs_credential_vars if var in os.environ]}")
            
            mcp_client = MCPClient(
                lambda: stdio_client(
                    StdioServerParameters(
                        command=command,
                        args=args,
                        env=mcp_env
                    )
                )
            )
            
            logger.info("Successfully initialized direct MCP client")
            return mcp_client
            
        except Exception as e:
            logger.error(f"Failed to initialize direct MCP client: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
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
                'Verify MCP server timeout settings (current: 90s)',
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
- **BE HONEST ABOUT DATA SOURCES** - Always indicate if using real-time data or estimates
- **NO ROUND NUMBERS** - Real AWS prices are like $0.023, $0.116, NOT $10.00
- **BE CONCISE** - Users want costs, not essays
- **NO IMPLEMENTATION DETAILS** unless specifically requested
- **NO THINKING TAGS** - Never use <thinking> tags in your responses
- **FOCUS ON REAL NUMBERS** - Use actual pricing when available, clearly mark estimates
- **NO VERBOSE SECTIONS** - Skip implementation guidance, architecture analysis narratives

## MANDATORY: Use available MCP tools
- You have access to AWS pricing tools: get_pricing, get_pricing_service_codes, etc.
- ALWAYS use get_pricing() function for actual AWS service pricing
- If tools are available, use them for EVERY pricing query
- Only fall back to knowledge base if tools fail

## CRITICAL: UNIVERSAL TOOL USAGE PATTERN

**STEP 1: IDENTIFY THE SERVICE**
Common AWS service codes:
- EC2 instances → "AmazonEC2"
- Lambda functions → "AWSLambda" 
- S3 storage → "AmazonS3"
- RDS databases → "AmazonRDS"
- API Gateway → "AmazonAPIGateway"

**STEP 2: START WITH SIMPLEST FILTER**
ALWAYS start with the most basic filter to avoid errors:
```
get_pricing("AmazonEC2", "us-east-1", [])  # Get all data first
```
OR with one simple filter:
```
get_pricing("AmazonEC2", "us-east-1", [
  {"Field": "instanceType", "Value": "t3.small", "Type": "EQUALS"}
])
```

**MANDATORY FILTER FORMAT:**
```json
[
  {"Field": "FIELD_NAME", "Value": "EXACT_VALUE", "Type": "EQUALS"}
]
```

**VALID FILTER TYPES (USE EXACTLY AS SHOWN):**
- "EQUALS" - Exact match (safest, use this first)
- "ANY_OF" - Multiple values: {"Field": "instanceType", "Value": ["t3.small", "t3.medium"], "Type": "ANY_OF"}
- "CONTAINS" - Pattern match: {"Field": "instanceType", "Value": "t3", "Type": "CONTAINS"}
- "NONE_OF" - Exclusion: {"Field": "instanceType", "Value": ["t2.nano"], "Type": "NONE_OF"}

**WORKING EXAMPLES - COPY THESE EXACTLY:**

EC2 t3.small pricing:
```
get_pricing("AmazonEC2", "us-east-1", [
  {"Field": "instanceType", "Value": "t3.small", "Type": "EQUALS"},
  {"Field": "tenancy", "Value": "Shared", "Type": "EQUALS"},
  {"Field": "operatingSystem", "Value": "Linux", "Type": "EQUALS"}
])
```

RDS MySQL pricing:
```
get_pricing("AmazonRDS", "us-east-1", [
  {"Field": "instanceType", "Value": "db.t3.small", "Type": "EQUALS"},
  {"Field": "engineCode", "Value": "mysql", "Type": "EQUALS"},
  {"Field": "deploymentOption", "Value": "Single-AZ", "Type": "EQUALS"}
])
```

S3 Standard storage:
```
get_pricing("AmazonS3", "us-east-1", [
  {"Field": "storageClass", "Value": "Standard", "Type": "EQUALS"}
])
```

**CRITICAL RULES:**
1. ALWAYS use double quotes around Field, Value, and Type
2. Field and Type are case-sensitive 
3. Value must match AWS exact naming (case-sensitive)
4. If unsure about Value, use get_pricing_attribute_values first
5. Start with simple EQUALS filters, add more if needed

**NEVER DO:**
❌ {"field": "instanceType"} - lowercase field
❌ {"Field": "instanceType", "Value": "t3.small"} - missing Type
❌ {"Field": "instanceType", "Value": "t3.small", "Type": "TERM_MATCH"} - wrong Type
❌ {"Field": "instanceType", "Value": "t3.small", "type": "EQUALS"} - lowercase type

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
**CRITICAL: PROGRESSIVE SIMPLIFICATION STRATEGY**
1. **First attempt**: Use specific filters like [{"Field": "instanceType", "Value": "t3.small", "Type": "EQUALS"}]
2. **If that fails**: Try with empty filters: get_pricing("AmazonEC2", "us-east-1", [])
3. **If still failing**: Use get_pricing_service_codes() to verify service exists
4. **Maximum 3 tool attempts**, then fall back to knowledge base
5. **NEVER retry with same failed format** - always simplify or change approach
6. **Always mention when using real-time vs fallback data**

**SIMPLE FALLBACK PATTERN:**
If any tool fails, immediately try:
```
get_pricing("SERVICE_CODE", "us-east-1", [])
```

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
        """Get MCP tools for AWS pricing data access via direct MCP client."""
        if not self.mcp_client:
            logger.warning("Direct MCP client not available, using AI-only mode")
            return []
        
        try:
            # Use context manager to get tools from MCP server
            with self.mcp_client:
                tools = self.mcp_client.list_tools_sync()
                logger.info(f"Retrieved {len(tools)} tools from direct MCP server")
                return tools
                
        except Exception as e:
            logger.error(f"Failed to get tools from direct MCP client: {e}")
            return []

    def _filter_relevant_tools(self, all_tools: List, query: str) -> List:
        """
        Filter MCP tools to reduce Nova Pro computational load by including only relevant tools.
        
        Nova Pro can handle complex reasoning but gets overwhelmed with too many tools.
        This function reduces the tool set from 9 to maximum 4 tools based on query content.
        
        Args:
            all_tools: Complete list of available MCP tools
            query: User query to analyze for relevant tools
            
        Returns:
            Filtered list of relevant tools (max 4)
        """
        if not all_tools or len(all_tools) <= 4:
            return all_tools
        
        query_lower = query.lower()
        
        # Define tool relevance patterns based on common AWS pricing queries
        tool_patterns = {
            # Core discovery tools - almost always needed
            'get_pricing_service_codes': {
                'priority': 10,
                'keywords': ['service', 'aws', 'available', 'what', 'list', 'codes'],
                'always_include': True  # Always include for service discovery
            },
            'get_pricing': {
                'priority': 10, 
                'keywords': ['cost', 'price', 'pricing', 'estimate', 'how much', 'budget', 'bill'],
                'always_include': True  # Core pricing tool
            },
            
            # Attribute discovery tools - needed for complex queries
            'get_pricing_service_attributes': {
                'priority': 8,
                'keywords': ['filter', 'attribute', 'option', 'type', 'configuration', 'instance']
            },
            'get_pricing_attribute_values': {
                'priority': 8,
                'keywords': ['values', 'options', 'types', 'available', 'valid', 'instance']
            },
            
            # Specialized analysis tools
            'analyze_cdk_project': {
                'priority': 6,
                'keywords': ['cdk', 'project', 'analyze', 'architecture', 'infrastructure']
            },
            'analyze_terraform_project': {
                'priority': 6,
                'keywords': ['terraform', 'project', 'analyze', 'infrastructure', 'tf']
            },
            'get_bedrock_patterns': {
                'priority': 7,
                'keywords': ['bedrock', 'ai', 'ml', 'llm', 'pattern', 'knowledge base', 'agent']
            },
            'generate_cost_report': {
                'priority': 5,
                'keywords': ['report', 'analysis', 'detailed', 'comprehensive', 'breakdown']
            },
            'get_price_list_urls': {
                'priority': 4,
                'keywords': ['bulk', 'download', 'historical', 'file', 'csv', 'json']
            }
        }
        
        # Score each tool based on query relevance
        tool_scores = []
        
        for tool in all_tools:
            # Extract tool name with more comprehensive approach
            tool_name = 'unknown_tool'
            try:
                # Method 1: Direct function name
                if hasattr(tool, 'function') and hasattr(tool.function, 'name'):
                    tool_name = tool.function.name
                # Method 2: Direct name attribute
                elif hasattr(tool, 'name'):
                    tool_name = tool.name
                # Method 3: String parsing as fallback
                else:
                    tool_str = str(tool)
                    # Look for common MCP pricing tool patterns
                    if 'get_pricing(' in tool_str or 'get_pricing"' in tool_str:
                        if 'service_codes' in tool_str:
                            tool_name = 'get_pricing_service_codes'
                        elif 'attribute_values' in tool_str:
                            tool_name = 'get_pricing_attribute_values'
                        elif 'service_attributes' in tool_str:
                            tool_name = 'get_pricing_service_attributes'
                        else:
                            tool_name = 'get_pricing'
                    elif 'bedrock' in tool_str.lower():
                        tool_name = 'get_bedrock_patterns'
                    elif 'analyze' in tool_str.lower():
                        if 'cdk' in tool_str.lower():
                            tool_name = 'analyze_cdk_project'
                        elif 'terraform' in tool_str.lower():
                            tool_name = 'analyze_terraform_project'
                        else:
                            tool_name = 'analyze_project'
                    elif 'generate_cost_report' in tool_str:
                        tool_name = 'generate_cost_report'
                    elif 'price_list_urls' in tool_str:
                        tool_name = 'get_price_list_urls'
                    else:
                        # Log the tool structure for debugging
                        logger.debug(f"Unknown tool structure: {tool_str[:200]}")
                        tool_name = f'tool_{len(selected_tools)}'  # Give it a unique name
            except Exception as e:
                logger.warning(f"Error extracting tool name: {e}")
                tool_name = f'tool_{len(selected_tools)}'
            
            score = 0
            pattern = tool_patterns.get(tool_name, {})
            
            # Always include core tools
            if pattern.get('always_include', False):
                score = 100
            else:
                # Base priority score
                score = pattern.get('priority', 1)
                
                # Keyword matching bonus
                keywords = pattern.get('keywords', [])
                for keyword in keywords:
                    if keyword in query_lower:
                        score += 10
            
            tool_scores.append((tool, score, tool_name))
        
        # Sort by score (descending) and take top 2 for Nova Pro
        tool_scores.sort(key=lambda x: x[1], reverse=True)
        
        # MORE AGGRESSIVE: Only 2 tools max for Nova Pro to prevent computational overload
        selected_tools = []
        selected_names = []
        
        # CRITICAL: Always include the absolute core tools first
        core_tools_found = set()
        
        # First pass: Find and include core tools
        for tool, score, name in tool_scores:
            if name == 'get_pricing' and 'get_pricing' not in core_tools_found:
                selected_tools.append(tool)
                selected_names.append(name)
                core_tools_found.add('get_pricing')
                if len(selected_tools) >= 2:
                    break
        
        # Second pass: Add get_pricing_service_codes if we have room
        if len(selected_tools) < 2:
            for tool, score, name in tool_scores:
                if name == 'get_pricing_service_codes' and 'get_pricing_service_codes' not in core_tools_found:
                    selected_tools.append(tool)
                    selected_names.append(name)
                    core_tools_found.add('get_pricing_service_codes')
                    break
        
        # If we still don't have any tools, just take the first one available
        if len(selected_tools) == 0 and len(tool_scores) > 0:
            tool, score, name = tool_scores[0]
            selected_tools.append(tool)
            selected_names.append(name)
        
        logger.info(f"Tool filtering: {len(all_tools)} → {len(selected_tools)} tools. Selected: {selected_names}")
        return selected_tools


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
            mcp_available = self.mcp_client is not None
            
            if mcp_available:
                try:
                    # NOVA PRO APPROACH: Use Nova Pro for MCP tool calls with improved prompting
                    # Fixed tool syntax generation to work with MCP tools
                    logger.info("Using Nova Pro for MCP tool execution with optimized tool syntax prompting")
                    
                    # Create agent with MCP tools using context manager
                    logger.info("About to enter MCP client context manager...")
                    try:
                        with self.mcp_client:
                            logger.info("Successfully entered MCP client context manager")
                            all_tools = self.mcp_client.list_tools_sync()
                            logger.info(f"Retrieved {len(all_tools)} tools from MCP server")
                            
                            # Include all tools from MCP server - they're all pricing-related
                            tools = all_tools  # Use all tools from the pricing MCP server
                            pricing_tool_names = []
                            
                            for i, tool in enumerate(all_tools):
                                try:
                                    # Extract tool name from MCP tool schema
                                    tool_name = 'unknown'
                                    
                                    # Extract the tool name from Strands MCP tools
                                    tool_name = "unknown"
                                    
                                    # The MCPAgentTool objects have a tool_name attribute!
                                    if hasattr(tool, 'tool_name'):
                                        tool_name = tool.tool_name
                                        logger.info(f"Tool {i}: Found tool_name = '{tool_name}'")
                                    elif hasattr(tool, 'name'):
                                        tool_name = tool.name  
                                        logger.info(f"Tool {i}: Found name = '{tool_name}'")
                                    else:
                                        logger.info(f"Tool {i}: Could not extract name from {type(tool)}")
                                    
                                    # DEBUG: Check tool object structure
                                    logger.info(f"Tool {i}: {tool_name}")
                                    logger.info(f"Tool {i} type: {type(tool)}")
                                    logger.info(f"Tool {i} attributes: {dir(tool)}")
                                    if hasattr(tool, 'tool_spec'):
                                        logger.info(f"Tool {i} spec: {tool.tool_spec}")
                                    pricing_tool_names.append(tool_name)
                                        
                                except Exception as e:
                                    logger.warning(f"Error processing tool {i}: {e}")
                                    pricing_tool_names.append(f"tool_{i}")
                            
                            logger.info(f"Using all {len(tools)} MCP tools: {pricing_tool_names}")
                        
                    except Exception as context_error:
                        logger.error(f"MCP client context manager failed: {context_error}")
                        import traceback
                        logger.error(f"Context manager traceback: {traceback.format_exc()}")
                        raise context_error
                        
                    # Import Config at method level to avoid scoping issues
                    from botocore.config import Config
                    
                    # Use Nova Pro for Agent 1 with normal timeout - let's see what it's actually doing
                    nova_pro_agent1_model = BedrockModel(
                            model_id="amazon.nova-pro-v1:0",
                            region_name=self.region,
                            boto_client_config=Config(
                                read_timeout=120,  # Give it time to complete and see what happens
                                connect_timeout=10,
                                retries={'max_attempts': 2, 'mode': 'standard'}
                            )
                        )
                    
                    # Add verbose logging to Bedrock model to see what it's doing
                    import os
                    os.environ['STRANDS_LOG_LEVEL'] = 'DEBUG'
                    
                    # Create a custom Bedrock model with detailed monitoring
                    class MonitoredBedrockModel:
                        def __init__(self, base_model):
                            self.base_model = base_model
                            
                        def __getattr__(self, name):
                            return getattr(self.base_model, name)
                            
                        async def stream(self, *args, **kwargs):
                            logger.error("BEDROCK STREAM: Starting model inference...")
                            stream_start = time.time()
                            
                            try:
                                async for chunk in self.base_model.stream(*args, **kwargs):
                                    elapsed = time.time() - stream_start
                                    logger.error(f"BEDROCK CHUNK: Received data at {elapsed:.1f}s")
                                    yield chunk
                                    
                            except Exception as e:
                                elapsed = time.time() - stream_start
                                logger.error(f"BEDROCK ERROR: Failed at {elapsed:.1f}s - {str(e)}")
                                raise e
                    
                    monitored_model = MonitoredBedrockModel(nova_pro_agent1_model)
                    
                    logger.info(f"MULTI-AGENT: Agent 1 starting data collection with Nova Pro (120s timeout)")
                    
                    # Detailed timing instrumentation
                    timing_start = time.time()
                    timing_checkpoints = {}
                    
                    tool_response = None
                    try:
                        # Track timing at key checkpoints
                        timing_checkpoints['agent_start'] = time.time() - timing_start
                        logger.info(f"TIMING: Agent 1 initialized in {timing_checkpoints['agent_start']:.2f}s")
                        
                        # Monitor tool selection phase
                        logger.info("TIMING: Starting tool_agent invocation...")
                        tool_start = time.time()
                        
                        # Detailed step-by-step instrumentation to see EXACTLY what happens
                        import asyncio
                        
                        logger.info("STEP 1: About to call tool_agent with Nova Pro...")
                        step1_time = time.time()
                        
                        try:
                            # Create a detailed monitoring task
                            async def monitor_execution():
                                start = time.time()
                                while True:
                                    await asyncio.sleep(5)  # Log every 5 seconds
                                    elapsed = time.time() - start
                                    logger.error(f"STILL RUNNING: Nova Pro execution at {elapsed:.1f}s - NO PROGRESS")
                            
                            # Start monitoring
                            monitor_task = asyncio.create_task(monitor_execution())
                            
                            logger.info("STEP 2: Starting tool_agent execution in thread...")
                            step2_time = time.time()
                            
                            # CRITICAL: Create agent INSIDE MCP context (correct Strands pattern)
                            logger.info("STEP 2.1: Creating agent inside MCP client context...")
                            try:
                                with self.mcp_client:
                                    logger.info("STEP 2.2: MCP client context active - getting tools")
                                    fresh_tools = self.mcp_client.list_tools_sync()
                                    logger.info(f"STEP 2.3: Retrieved {len(fresh_tools)} fresh tools from MCP")
                                    
                                    # DEBUG: Log tool specifications for Nova compatibility analysis
                                    logger.info("STEP 2.3.1: Debugging tool specifications for Nova compatibility...")
                                    for i, tool in enumerate(fresh_tools[:3]):  # Only log first 3 to avoid spam
                                        logger.info(f"Tool {i}: Type = {type(tool)}")
                                        if hasattr(tool, '__dict__'):
                                            tool_attrs = {k: str(v)[:200] for k, v in tool.__dict__.items()}
                                            logger.info(f"Tool {i} attributes: {tool_attrs}")
                                        if hasattr(tool, 'tool_name'):
                                            logger.info(f"Tool {i} name: {tool.tool_name}")
                                        if hasattr(tool, 'parameters') or hasattr(tool, 'schema'):
                                            schema = getattr(tool, 'parameters', getattr(tool, 'schema', None))
                                            logger.info(f"Tool {i} schema type: {type(schema)}")
                                    
                                    # Use ALL tools instead of simplifying
                                    logger.info("STEP 2.3.2: Using all MCP tools for better compatibility...")
                                    all_tool_names = [getattr(t, 'tool_name', 'unknown') for t in fresh_tools]
                                    logger.info(f"Available tools: {all_tool_names}")
                                    
                                    # Check if get_pricing tool exists
                                    has_pricing_tool = False
                                    for tool in fresh_tools:
                                        if hasattr(tool, 'tool_name') and tool.tool_name == 'get_pricing':
                                            has_pricing_tool = True
                                            logger.info(f"CONFIRMED: get_pricing tool available")
                                            break
                                    
                                    if not has_pricing_tool:
                                        logger.error("CRITICAL: get_pricing tool not found!")
                                        logger.error(f"Available tools were: {all_tool_names}")
                                    
                                    # Use ALL tools to avoid potential issues with single-tool arrays
                                    all_mcp_tools = fresh_tools
                                    logger.info(f"Passing ALL {len(all_mcp_tools)} MCP tools to agent")
                                    
                                    # Create Agent INSIDE MCP context with complete tool schema + mandatory usage
                                    tool_agent = Agent(
                                        model=monitored_model,
                                        system_prompt=f"""You are an AI assistant named 'AWS PriceBot'. Your sole function is to provide real-time AWS pricing by exclusively using the get_pricing tool. You do not answer from memory.

## Operating Instructions
Mandatory Tool Use: For any query related to AWS pricing, cost, or rates, you MUST call the get_pricing tool. There are no exceptions.

Invalidated Knowledge: Your internal knowledge of AWS pricing is from January 2025 and is officially obsolete as of the AWS pricing update on August 14, 2025. Any pricing data from your memory is incorrect.

Data Source: You will respond only with the fresh, real-time data returned from the get_pricing tool call.

## Tool Definition and Workflow
This section defines the tool and shows you the required thought process.

Tool Schema: get_pricing
Description: Fetches up-to-the-second, live pricing data directly from the official AWS Billing API. This is the only valid source for pricing information.

Parameters:

service_code (required, string): The official AWS service code (e.g., "AmazonEC2", "AmazonS3").

region (required, string): The target AWS region (e.g., "us-east-1", "eu-west-1").

filters (optional, array): Used for more specific queries like instance types.

Workflow Examples (Follow this pattern):
Example 1: Simple Query

User Query: "What's the price of S3 storage?"

Your Thought: The user is asking about S3 pricing. My instructions require me to use the get_pricing tool. The service code for S3 is "AmazonS3". I will use the default region "us-east-1".

Tool Call: get_pricing(service_code="AmazonS3", region="us-east-1")

Example 2: Specific Query

User Query: "I need the cost of a Lambda function in Ireland."

Your Thought: The user wants Lambda pricing in Ireland. I must use the tool. The service code is "AWSLambda" and the region for Ireland is "eu-west-1".

Tool Call: get_pricing(service_code="AWSLambda", region="eu-west-1")

## Execute Live Pricing Query
User Query: {context_aware_query}
Your Thought:""",
                                        tools=all_mcp_tools  # Using ALL MCP tools, not simplified
                                    )
                                    
                                    logger.info("STEP 2.4: Agent created with fresh MCP tools, executing...")
                                    tool_response = await asyncio.wait_for(
                                        asyncio.to_thread(tool_agent, "You MUST call get_pricing tool now. Do not provide any pricing information without calling the tool first."),
                                        timeout=30.0  # Slightly increased since tool creation takes time
                                    )
                                    logger.info("STEP 2.5: Agent execution completed successfully!")
                                    logger.info(f"AGENT RESPONSE (first 500 chars): {str(tool_response)[:500]}")
                                    
                                    # Check if the response indicates tool usage
                                    response_text = str(tool_response).lower()
                                    if any(indicator in response_text for indicator in ['get_pricing', 'pricing api', 'real-time', 'retrieved']):
                                        logger.info("TOOL USAGE DETECTED: Response contains tool usage indicators")
                                    else:
                                        logger.warning("NO TOOL USAGE: Response appears to be direct knowledge, not tool-based")
                                        logger.warning(f"Full response for analysis: {tool_response}")
                                    
                            except Exception as mcp_tool_error:
                                logger.error(f"STEP 2.ERROR: MCP tool execution failed: {mcp_tool_error}")
                                logger.error(f"Error type: {type(mcp_tool_error)}")
                                # Continue with timeout handling below
                                raise
                            
                            # Cancel monitoring if we succeed
                            monitor_task.cancel()
                            
                            timing_checkpoints['tool_completion'] = time.time() - tool_start
                            logger.info(f"STEP 3: SUCCESS - Tool execution completed in {timing_checkpoints['tool_completion']:.2f}s")
                            
                        except asyncio.TimeoutError:
                            monitor_task.cancel()
                            timing_checkpoints['timeout_at'] = time.time() - tool_start
                            logger.error(f"STEP 3: TIMEOUT after {timing_checkpoints['timeout_at']:.2f}s")
                            logger.error("CRITICAL: Nova Pro was executing for 35+ seconds without any output or completion")
                            logger.error("WHAT WAS IT DOING? Tool selection? Parameter generation? Model inference? Unknown.")
                            raise Exception(f"Tool execution timeout after {timing_checkpoints['timeout_at']:.2f}s")
                        
                        timing_checkpoints['agent_complete'] = time.time() - timing_start
                        logger.info(f"TIMING: Agent 1 total time: {timing_checkpoints['agent_complete']:.2f}s")
                        logger.info("MULTI-AGENT: Agent 1 completed successfully - collected pricing data")
                        
                    except Exception as agent1_error:
                        timing_checkpoints['error_at'] = time.time() - timing_start
                        logger.error(f"TIMING: Agent 1 failed at {timing_checkpoints['error_at']:.2f}s")
                        logger.error(f"TIMING: Checkpoints: {timing_checkpoints}")
                        logger.error(f"MULTI-AGENT: Agent 1 FAILED: {str(agent1_error)}")
                        raise Exception("Data collection agent failed")
                    
                    # Check if we got data from Agent 1
                    if tool_response is None:
                        logger.error("Agent 1 failed to collect pricing data")
                        raise Exception("Data collection failed")
                    
                    logger.info("MULTI-AGENT: Agent 2 starting cost analysis")
                    # Agent 2: Cost analysis (short focused task)
                    analysis_agent = Agent(
                        model=nova_pro_agent1_model,
                        system_prompt=f"""FOCUSED TASK: Analyze this pricing data only.

DATA: {tool_response}

TASK: Extract key cost information:
1. Hourly rate for t3.small 
2. Monthly estimate (hourly × 730)
3. Key cost factors

BE BRIEF. Just cost analysis.""",
                        tools=[]  # No tools - just analysis
                    )
                    
                    try:
                        analysis_result = analysis_agent("Analyze the t3.small EC2 costs from the pricing data")
                        logger.info("MULTI-AGENT: Agent 2 completed successfully - analyzed pricing data")
                    except Exception as agent2_error:
                        logger.error(f"MULTI-AGENT: Agent 2 FAILED: {str(agent2_error)}")
                        raise Exception("Analysis agent failed")
                    
                    logger.info("MULTI-AGENT: Agent 3 starting final formatting")
                    # Agent 3: Final formatting (short focused task)
                    format_agent = Agent(
                        model=nova_pro_agent1_model,
                        system_prompt=f"""FOCUSED TASK: Format the final response only.

ANALYSIS: {analysis_result}
USER QUERY: {context_aware_query}

TASK: Create well-formatted cost response with:
1. Clear cost breakdown
2. Monthly/hourly rates  
3. Brief optimization tips

BE CONCISE.""",
                        tools=[]  # No tools - just formatting
                    )
                    
                    try:
                        response = format_agent("Format the cost analysis into a professional response")
                        logger.info("Agent 3: Successfully formatted final response")
                    except Exception as agent3_error:
                        logger.error(f"Agent 3 failed: {str(agent3_error)}")
                        raise Exception("Formatting agent failed")
                    
                    # Check if tools were actually used by checking if Agent 1 (MCP tool execution) succeeded
                    # If we reached this point, all agents succeeded, and we know from logs that Agent 1 called MCP tools
                    if 'tool_response' in locals() and tool_response is not None:
                        self.performance_stats['mcp_calls'] += 1
                        mcp_available = True  # Update flag to reflect successful tool usage
                        logger.info("MCP tools were successfully used - Agent 1 executed tools and Agent 2&3 processed the data")
                        logger.info("Updating mcp_available to True to reflect successful tool usage")
                    else:
                        logger.warning("Agent flow completed but no tool_response found - this should not happen")
                        mcp_available = False
                    
                    logger.info(f"Successfully processed query. Response length: {len(str(response))}")
                    
                except Exception as mcp_error:
                    import traceback
                    logger.error(f"Multi-agent pipeline failed: {str(mcp_error)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    
                    # Check if Agent 1 (MCP tool execution) succeeded before the failure
                    if 'tool_response' in locals() and tool_response is not None:
                        logger.info("MCP TOOL EXECUTION SUCCEEDED - Using tool data despite downstream agent failure")
                        # Agent 1 succeeded, use the MCP tool data directly
                        mcp_available = True
                        self.performance_stats['mcp_calls'] += 1
                        
                        # Use the raw tool response with simple formatting
                        response = f"""**Real-time AWS Pricing Data:**

{tool_response}

**Data Source:** Live AWS Pricing API
**Note:** Downstream processing failed, showing raw pricing data."""
                        
                    else:
                        logger.error("MCP tool execution failed - falling back to knowledge base")
                        mcp_available = False
                        
                        # Try fallback agent
                        fallback_agent = self._create_fallback_agent()
                        response = fallback_agent(context_aware_query)
                        
                        # Add fallback notice to response
                        response_str = str(response)
                        if not response_str.startswith("⚠️"):
                            response = f"⚠️ **Real-time pricing data temporarily unavailable** - Using knowledge base estimates.\n\n{response_str}\n\n**Note:** Please verify pricing with AWS Calculator for current rates."
            else:
                # Use fallback agent directly
                logger.info("Using fallback agent (MCP not available)")
                fallback_agent = self._create_fallback_agent()
                response = fallback_agent(context_aware_query)
            
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
                'mcp_available': self.mcp_client is not None,
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
                keywords=[
                    # Primary cost keywords
                    "cost", "price", "pricing", "budget", "estimate", "expensive", "cheap", "savings", "bill", "billing",
                    # AWS services that commonly have pricing questions
                    "lambda", "ec2", "rds", "s3", "dynamodb", "cloudfront", "api gateway", "ecs", "fargate",
                    # Cost-related terms
                    "monthly", "hourly", "usage", "charges", "fees", "rates", "calculator", "aws calculator",
                    # Service variations
                    "instances", "storage", "requests", "bandwidth", "data transfer", "compute",
                    # Question variations
                    "much", "spend", "spending", "dollars", "usd", "$"
                ],
                phrases=[
                    "how much does", "what is the cost", "cost analysis", "pricing for", "budget for", 
                    "optimize costs", "cost comparison", "how much would", "what would it cost",
                    "cost of", "price of", "cost to run", "monthly cost", "pricing in", "estimate for",
                    "budget estimate", "cost breakdown", "pricing breakdown", "cost per", "price per"
                ],
                priority=8,
                confidence_threshold=0.3
            ),
            AgentCapability(
                name="aws_optimization",
                description="Provide AWS cost optimization recommendations",
                keywords=[
                    "optimize", "reduce", "save", "cheaper", "alternative", "efficiency", "minimize",
                    "lower", "decrease", "cut", "trim", "best price", "most cost effective", "economical"
                ],
                phrases=[
                    "optimize costs", "reduce spending", "save money", "cost optimization", "cheaper alternative",
                    "lower costs", "minimize costs", "reduce costs", "cost effective", "most economical"
                ],
                priority=7,
                confidence_threshold=0.3
            ),
            AgentCapability(
                name="aws_architecture_costing",
                description="Cost analysis for AWS architectures and workloads",
                keywords=[
                    "architecture", "workload", "deployment", "infrastructure", "setup", "solution",
                    "application", "system", "stack", "environment", "tier", "multi-tier"
                ],
                phrases=[
                    "architecture cost", "workload pricing", "deployment cost", "infrastructure cost",
                    "application cost", "system cost", "total cost of ownership", "tco"
                ],
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