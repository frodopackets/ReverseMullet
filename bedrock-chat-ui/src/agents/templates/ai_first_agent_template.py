#!/usr/bin/env python3
"""
AI-First Specialized Agent Template

This template provides a foundation for creating new AI-first specialized agents
following the proven patterns from the AWS Pricing Agent implementation.

Key Principles:
1. AI-first design with minimal helper code
2. Rich system prompts with comprehensive domain knowledge
3. MCP integration for real-time data access
4. Graceful fallback when external services unavailable
5. Performance optimization with caching
6. Comprehensive error handling
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from strands import Agent
from strands.tools.mcp import MCPClient
from ..agent_registry import BaseSpecializedAgent, AgentCapability, AgentMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIFirstAgentTemplate(BaseSpecializedAgent):
    """
    Template for AI-first specialized agents.
    
    Replace 'Template' with your specific domain (e.g., SecurityAgent, PerformanceAgent)
    and customize the system prompt, capabilities, and MCP integration.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the specialized agent with AI-first configuration."""
        from strands.models import BedrockModel
        
        self.config = config or {}
        
        # Create optimized BedrockModel configuration
        model_config = self.config.get('model_config', {
            "model_id": "amazon.nova-lite-v1:0",
            "temperature": 0.3,  # Adjust based on your domain needs
            "max_tokens": 4000,  # Adjust based on response complexity
            "top_p": 0.8
        })
        
        self.bedrock_model = BedrockModel(**model_config)
        
        # Initialize MCP client for real-time data (customize for your domain)
        self.mcp_client = self._initialize_mcp_client()
        
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
        
        # Conversation context management
        self.conversation_context = []
        self.max_context_length = 8000
    
    def _initialize_mcp_client(self) -> Optional[MCPClient]:
        """
        Initialize MCP client for your domain-specific data source.
        
        Customize this method to connect to your specific MCP server.
        Examples:
        - AWS documentation server
        - Security scanning services
        - Performance monitoring APIs
        - Compliance databases
        """
        try:
            from mcp import stdio_client, StdioServerParameters
            import os
            
            # Example MCP server configuration - customize for your domain
            # Replace with your specific MCP server
            mcp_server_command = self.config.get('mcp_server_command', 
                                                'uvx your-domain-mcp-server@latest')
            
            mcp_client = MCPClient(lambda: stdio_client(
                StdioServerParameters(
                    command="bash",
                    args=["-c", f"source ~/.local/bin/env && {mcp_server_command}"],
                    env={
                        **os.environ,
                        "FASTMCP_LOG_LEVEL": "ERROR",
                        # Add domain-specific environment variables
                        "MCP_TIMEOUT": "30",
                        "MCP_MAX_RETRIES": "3"
                    }
                )
            ))
            
            logger.info(f"MCP client initialized for {self.__class__.__name__}")
            
            # Test connection
            if self._test_mcp_connection(mcp_client):
                return mcp_client
            else:
                logger.warning("MCP server not available, using AI-only mode")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {str(e)}")
            return None
    
    def _test_mcp_connection(self, mcp_client) -> bool:
        """Test MCP server connection."""
        if not mcp_client:
            return False
        
        try:
            # Implement a simple test call to your MCP server
            # This is domain-specific - customize for your server
            logger.info("MCP server connection test: Ready for integration")
            return True
        except Exception as e:
            logger.warning(f"MCP server connection test failed: {str(e)}")
            return False
    
    def _get_system_prompt(self) -> str:
        """
        Get the comprehensive system prompt for your specialized agent.
        
        This is the heart of the AI-first approach. Customize this extensively
        for your domain with:
        1. Domain expertise and knowledge
        2. MCP tool usage instructions
        3. Response format guidelines
        4. Error handling instructions
        5. Optimization patterns
        """
        return """You are a [DOMAIN] Specialized Agent with comprehensive knowledge and real-time data access.

## Core Capabilities
You are an AI-first [domain] agent with extensive [domain] knowledge and access to real-time data via MCP tools. You use your reasoning abilities to:
- [Capability 1: e.g., Analyze security configurations and identify vulnerabilities]
- [Capability 2: e.g., Provide optimization recommendations with specific improvements]
- [Capability 3: e.g., Compare different approaches with detailed analysis]
- [Capability 4: e.g., Suggest best practices and implementation guidance]

## CRITICAL: MCP Tools Usage Instructions

### When MCP Tools Are Available
You have access to real-time [domain] data through MCP tools. ALWAYS use these tools to get current information instead of relying on estimates.

### Key MCP Tools and Usage Patterns

#### 1. [tool_name_1]()
Use this to [purpose]:
```
Call [tool_name_1]() to [specific use case]
```

#### 2. [tool_name_2](parameter)
[Description of tool and usage]:
```
[tool_name_2]("specific_parameter_example")
```

#### 3. [tool_name_3](param1, param2, filters)
Get [type of data] with optimized parameters:
```
[tool_name_3]("param1_value", "param2_value", [
  {"Field": "field_name", "Value": "field_value", "Type": "EQUALS"}
])
```

### Optimized Usage Patterns for Common Scenarios

#### [Scenario 1] (Most Important)
- [parameter1]: "value1", "value2", "value3"
- [parameter2]: "option1", "option2"
- [parameter3]: Use [specific format]

#### [Scenario 2]
- [parameter1]: "different_value1", "different_value2"
- [parameter2]: "different_option1", "different_option2"

### Performance Optimization Guidelines

1. **Use Specific Parameters**: Always include relevant parameters to reduce response size
2. **Batch Queries**: When comparing multiple options, use batch operations
3. **Cache Results**: Remember data within the same conversation
4. **Handle Errors Gracefully**: Provide fallback responses when MCP unavailable

### Error Handling for MCP Tools
- If MCP tools fail, acknowledge the failure and use knowledge base
- Always mention when using cached/estimated vs real-time data
- Provide troubleshooting guidance for connection issues

## [Domain] Knowledge Context (Fallback)

### [Knowledge Area 1]
- [Key concept 1]: [Description and best practices]
- [Key concept 2]: [Description and implementation guidance]
- [Key concept 3]: [Description and optimization strategies]

### [Knowledge Area 2]
- [Important pattern 1]: [When to use and how to implement]
- [Important pattern 2]: [Benefits and considerations]
- [Important pattern 3]: [Common pitfalls and solutions]

### Common [Domain] Strategies
1. **[Strategy 1]**: [Description and benefits]
2. **[Strategy 2]**: [Use cases and implementation]
3. **[Strategy 3]**: [Best practices and considerations]

## Response Format Guidelines

Structure your responses with:
1. **[Analysis Type] Analysis**: [What you identify and assess]
2. **Real-Time Data**: Use MCP tools to get current information
3. **[Output Type] Breakdown**: [Detailed breakdown format]
4. **[Consideration Type] Considerations**: [Important factors to consider]
5. **[Recommendation Type] Opportunities**: Prioritized recommendations with specific guidance
6. **Implementation Guidance**: Next steps and considerations

## Conversation Context and [Domain] Tracking

### Context Awareness
You maintain conversation context to provide intelligent follow-up responses:
- **[Context Type 1]**: Track [what to track] across the conversation
- **[Context Type 2]**: Remember [what to remember] for comparison purposes
- **[Context Type 3]**: Compare [what to compare] against previously discussed [items]
- **[Context Type 4]**: Handle [what modifications] and recalculate [what to recalculate] accordingly

### Follow-up Query Handling
When users ask follow-up questions:
- Reference the previously discussed [context items]
- Highlight what has changed from the baseline
- Provide comparative analysis (e.g., "This would [change description] compared to your previous [setup/configuration]")
- Maintain context about [recommendations/analysis] already provided

## Important Instructions
- ALWAYS use MCP tools when available for real [data type] data
- Be specific about whether you're using real-time data or estimates
- Include [specific output requirements]
- Ask clarifying questions only for essential missing details
- Default to [default settings] when not specified (mention this to user)
- Provide actionable, prioritized [recommendation type] recommendations
- Include confidence levels for your [analysis/estimates]
- **Reference previous discussions** when handling follow-up queries
- **Compare scenarios** when users ask about alternatives
- **Track [domain] changes** and show [impact type] impacts clearly

## Query Processing Workflow
1. Analyze the user's [input type] description
2. Identify required [domain elements] and configurations
3. Use [mcp_tool_discovery]() to understand available options
4. Use [mcp_tool_values]() to get valid parameter values
5. Call [mcp_tool_main]() with optimized parameters for each [element]
6. Calculate [results] and provide breakdown
7. Identify [optimization/improvement] opportunities
8. Present results in structured format

Be concise but comprehensive. Focus on actionable insights that help users make informed decisions."""

    def _get_mcp_tools(self):
        """Get MCP tools for real-time data access."""
        if self.mcp_client:
            logger.info("Returning MCP client for Strands SDK context management")
            return [self.mcp_client]
        else:
            logger.warning("MCP client not available, using AI-only mode")
            return []
    
    def _get_fallback_system_prompt(self) -> str:
        """Get system prompt for fallback mode when MCP is unavailable."""
        return """You are a [DOMAIN] Specialized Agent operating in FALLBACK MODE. The real-time data service is currently unavailable, so you'll provide analysis based on your knowledge base.

## IMPORTANT: Fallback Mode Notice
⚠️ **Real-time [domain] data is currently unavailable.** You are operating with cached knowledge and should:
1. Clearly indicate that analysis is based on knowledge base, not real-time data
2. Provide confidence levels for your analysis
3. Suggest users verify with [authoritative sources]
4. Include disclaimers about [data accuracy/currency]

## Core Capabilities (Fallback Mode)
- Analyze [domain elements] and identify [key components]
- Provide [analysis type] based on knowledge base patterns
- Offer [recommendation type] recommendations
- Compare [comparison elements] using historical patterns
- Suggest [improvement type] improvements for [optimization goals]

## Fallback [Domain] Guidelines

### [Knowledge Area] Patterns (Approximate)
- [Pattern 1]: [Description and typical values/approaches]
- [Pattern 2]: [Description and typical values/approaches]
- [Pattern 3]: [Description and typical values/approaches]

### Common [Domain Element] Patterns (Estimates)
**[Category 1]:**
- [Item 1]: [Typical characteristics/values]
- [Item 2]: [Typical characteristics/values]
- [Item 3]: [Typical characteristics/values]

**[Category 2]:**
- [Item 1]: [Typical characteristics/values]
- [Item 2]: [Typical characteristics/values]

### Error Handling and User Communication
- Always mention fallback mode status
- Provide confidence levels: "Low-Medium confidence (fallback mode)"
- Include verification suggestions
- Offer troubleshooting guidance for MCP connectivity

### Response Format (Fallback Mode)
1. **Fallback Mode Notice**: Clear indication of operating mode
2. **[Analysis Type] Analysis**: [Elements] identified and configurations
3. **Estimated [Results]**: Based on knowledge base with confidence levels
4. **[Consideration Type] Considerations**: Approximate [variations/factors]
5. **[Recommendation Type] Opportunities**: General recommendations
6. **Verification Guidance**: How to get accurate real-time [data/analysis]

## Important Instructions
- ALWAYS mention you're in fallback mode at the start of responses
- Include confidence levels for all analysis
- Suggest verification with [authoritative sources]
- Provide general [recommendation type] guidance
- Ask clarifying questions for essential missing details
- Default to [default values] when not specified
- Include disclaimers about [accuracy aspects]

## Sample Fallback Response Format
"⚠️ **Operating in Fallback Mode** - Real-time [domain] data unavailable. Providing analysis based on knowledge base.

[Analysis and recommendations with confidence levels]

**Confidence Level:** Medium (based on historical patterns)
**Verification:** Please verify with [authoritative source] for current [data/information]
**Troubleshooting:** [If applicable, include MCP connectivity guidance]"
"""
    
    def _create_fallback_agent(self):
        """Create fallback agent without MCP tools."""
        if not self.agent_fallback:
            self.agent_fallback = Agent(
                model=self.bedrock_model,
                system_prompt=self._get_fallback_system_prompt(),
                tools=[]  # No MCP tools in fallback mode
            )
        return self.agent_fallback
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query and return structured response.
        
        This is the main entry point for the agent. Customize the response
        structure for your domain needs.
        """
        start_time = time.time()
        self.performance_stats['total_queries'] += 1
        
        try:
            # Check cache first
            query_hash = hash(query.lower().strip())
            if query_hash in self.query_cache:
                self.performance_stats['cache_hits'] += 1
                logger.info("Using cached response for similar query")
                cached_response = self.query_cache[query_hash].copy()
                cached_response['cached'] = True
                return cached_response
            
            # Create agent with MCP tools if available
            if not self.agent:
                if self.mcp_client:
                    self.agent = Agent(
                        model=self.bedrock_model,
                        system_prompt=self._get_system_prompt(),
                        tools=self._get_mcp_tools()
                    )
                else:
                    self.agent = self._create_fallback_agent()
            
            # Process query
            try:
                response_content = ""
                async for event in self.agent.stream_async(query):
                    if "data" in event:
                        response_content += event["data"]
                
                result = {
                    'status': 'success',
                    'response': response_content,
                    'agent_type': self.__class__.__name__,
                    'mcp_available': self.mcp_client is not None,
                    'confidence': 'high' if self.mcp_client else 'medium',
                    'timestamp': time.time(),
                    'cached': False
                }
                
                # Track performance
                response_time = time.time() - start_time
                self.performance_stats['avg_response_time'] = (
                    (self.performance_stats['avg_response_time'] * (self.performance_stats['total_queries'] - 1) + response_time) 
                    / self.performance_stats['total_queries']
                )
                
                # Cache successful responses (limit cache size)
                if len(self.query_cache) < 10:
                    self.query_cache[query_hash] = result.copy()
                
                return result
                
            except Exception as e:
                logger.error(f"Agent processing error: {str(e)}")
                return {
                    'status': 'error',
                    'error': str(e),
                    'agent_type': self.__class__.__name__,
                    'mcp_available': self.mcp_client is not None,
                    'troubleshooting': self._get_troubleshooting_guidance(e),
                    'timestamp': time.time()
                }
        
        except Exception as e:
            logger.error(f"Query processing error: {str(e)}")
            return {
                'status': 'error',
                'error': f"Failed to process query: {str(e)}",
                'agent_type': self.__class__.__name__,
                'timestamp': time.time()
            }
    
    def _get_troubleshooting_guidance(self, error: Exception) -> List[str]:
        """Get troubleshooting guidance based on error type."""
        error_str = str(error).lower()
        guidance = []
        
        if 'timeout' in error_str:
            guidance.extend([
                'Reduce query complexity by being more specific',
                'Break complex queries into smaller parts',
                'Try again in a few moments'
            ])
        elif 'connection' in error_str:
            guidance.extend([
                'Check network connectivity',
                'Verify MCP server is running',
                'Try again later - service may be temporarily unavailable'
            ])
        else:
            guidance.extend([
                'Rephrase your question to be more specific',
                'Check that you\'re asking about supported [domain] topics',
                'Try a simpler query first'
            ])
        
        return guidance
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Return list of capabilities this agent can handle."""
        # Customize these capabilities for your domain
        return [
            AgentCapability(
                name="domain_analysis",
                description="Analyze [domain] configurations and provide insights",
                keywords=["analyze", "review", "assess", "evaluate"],
                phrases=["analyze my", "review the", "assess this", "evaluate the"],
                priority=8,
                confidence_threshold=0.6
            ),
            AgentCapability(
                name="domain_optimization",
                description="Provide [domain] optimization recommendations",
                keywords=["optimize", "improve", "enhance", "better"],
                phrases=["optimize for", "improve the", "make it better", "enhance performance"],
                priority=7,
                confidence_threshold=0.5
            ),
            AgentCapability(
                name="domain_comparison",
                description="Compare different [domain] approaches",
                keywords=["compare", "versus", "vs", "difference", "better"],
                phrases=["compare with", "versus", "what's better", "difference between"],
                priority=6,
                confidence_threshold=0.4
            )
        ]
    
    def get_metadata(self) -> AgentMetadata:
        """Return agent metadata."""
        return AgentMetadata(
            name="[Domain] Specialized Agent",
            description="AI-first specialized agent for [domain] analysis and optimization",
            version="1.0.0",
            author="Template",
            capabilities=self.get_capabilities(),
            model_config={
                "model_id": "amazon.nova-lite-v1:0",
                "temperature": 0.3,
                "max_tokens": 4000,
                "top_p": 0.8
            },
            system_prompt_template="AI-first [domain] agent with comprehensive knowledge and MCP integration",
            tools_required=["mcp_client"],
            mcp_servers=["domain-specific-server"],
            dependencies=["strands", "mcp"],
            enabled=True
        )

# Example implementation for a Security Agent
class SecurityAgent(AIFirstAgentTemplate):
    """Example Security Agent implementation using the AI-first template."""
    
    def _get_system_prompt(self) -> str:
        """Security-specific system prompt."""
        return """You are an AWS Security Specialized Agent with comprehensive security knowledge and real-time data access.

## Core Capabilities
You are an AI-first security agent with extensive AWS security knowledge and access to real-time security data via MCP tools. You use your reasoning abilities to:
- Analyze AWS security configurations and identify vulnerabilities
- Provide security optimization recommendations with specific improvements
- Compare different security approaches with detailed risk analysis
- Suggest security best practices and implementation guidance

## CRITICAL: MCP Tools Usage Instructions

### When MCP Tools Are Available
You have access to real-time AWS security data through MCP tools. ALWAYS use these tools to get current security information instead of relying on estimates.

### Key MCP Tools and Usage Patterns

#### 1. get_security_findings()
Use this to get current security findings:
```
Call get_security_findings() to retrieve active security issues
```

#### 2. analyze_iam_policies(policy_document)
Analyze IAM policies for security issues:
```
analyze_iam_policies(policy_json_document)
```

#### 3. check_compliance(service, standards)
Check compliance against security standards:
```
check_compliance("ec2", ["cis", "nist", "pci"])
```

### AWS Security Knowledge Context (Fallback)

### IAM Security Patterns
- Principle of Least Privilege: Grant minimum necessary permissions
- Role-based Access: Use roles instead of users for applications
- MFA Enforcement: Require multi-factor authentication for sensitive operations

### Network Security
- VPC Security Groups: Implement defense in depth
- NACLs: Use as additional layer of security
- VPC Flow Logs: Enable for network monitoring

### Data Protection
- Encryption at Rest: Use AWS KMS for data encryption
- Encryption in Transit: Use TLS/SSL for data transmission
- S3 Bucket Policies: Implement proper access controls

## Response Format Guidelines

Structure your responses with:
1. **Security Analysis**: Configurations and vulnerabilities identified
2. **Real-Time Security Data**: Use MCP tools to get current security status
3. **Risk Assessment**: Detailed risk breakdown by severity
4. **Compliance Considerations**: Relevant compliance requirements
5. **Security Recommendations**: Prioritized recommendations with risk mitigation
6. **Implementation Guidance**: Step-by-step security improvements

Be concise but comprehensive. Focus on actionable security insights that help users improve their security posture."""
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Security-specific capabilities."""
        return [
            AgentCapability(
                name="security_analysis",
                description="Analyze AWS security configurations and identify vulnerabilities",
                keywords=["security", "vulnerability", "risk", "threat", "compliance"],
                phrases=["security analysis", "check security", "security review", "vulnerability assessment"],
                priority=9,
                confidence_threshold=0.7
            ),
            AgentCapability(
                name="iam_analysis",
                description="Analyze IAM policies and permissions",
                keywords=["iam", "permissions", "policy", "role", "access"],
                phrases=["iam policy", "permissions review", "access control", "role analysis"],
                priority=8,
                confidence_threshold=0.6
            ),
            AgentCapability(
                name="compliance_check",
                description="Check compliance against security standards",
                keywords=["compliance", "standards", "audit", "regulation", "cis", "nist"],
                phrases=["compliance check", "audit requirements", "security standards", "regulatory compliance"],
                priority=7,
                confidence_threshold=0.5
            )
        ]
    
    def get_metadata(self) -> AgentMetadata:
        """Security agent metadata."""
        return AgentMetadata(
            name="AWS Security Agent",
            description="AI-first specialized agent for AWS security analysis and compliance",
            version="1.0.0",
            author="Template Example",
            capabilities=self.get_capabilities(),
            model_config={
                "model_id": "amazon.nova-lite-v1:0",
                "temperature": 0.2,  # Lower temperature for security analysis
                "max_tokens": 5000,
                "top_p": 0.7
            },
            system_prompt_template="AI-first security agent with comprehensive AWS security knowledge",
            tools_required=["mcp_client"],
            mcp_servers=["aws-security"],
            dependencies=["strands", "mcp"],
            enabled=True
        )