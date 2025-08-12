# AI-First Agent Creation Guide

## Overview

This guide provides comprehensive instructions for creating new AI-first specialized agents using the proven patterns from the AWS Pricing Agent implementation. The AI-first approach prioritizes intelligent reasoning over complex helper code, resulting in more maintainable, flexible, and adaptable agents.

## Core Principles

### 1. AI-First Design Philosophy
- **Rich System Prompts**: Comprehensive domain knowledge embedded in system prompts
- **Minimal Helper Code**: Let AI handle complexity through reasoning rather than hardcoded logic
- **Real-Time Data Integration**: Use MCP servers for current, authoritative data
- **Graceful Degradation**: Fallback to knowledge base when external services unavailable
- **Performance Optimization**: Caching and intelligent query handling

### 2. Proven Architecture Patterns
- **Agent Registry Integration**: Automatic discovery and routing
- **MCP Client Integration**: Real-time data access with error handling
- **Conversation Context**: Maintain state across interactions
- **Performance Tracking**: Monitor and optimize response times
- **Comprehensive Error Handling**: User-friendly error messages with troubleshooting

## Quick Start Guide

### Step 1: Create Your Agent Class

```python
from .templates.ai_first_agent_template import AIFirstAgentTemplate
from .agent_registry import AgentCapability, AgentMetadata

class YourDomainAgent(AIFirstAgentTemplate):
    """Your specialized agent for [domain] analysis."""
    
    def _get_system_prompt(self) -> str:
        """Customize system prompt for your domain."""
        return """You are a [Domain] Specialized Agent...
        
        [Include comprehensive domain knowledge here]
        """
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Define what your agent can handle."""
        return [
            AgentCapability(
                name="domain_analysis",
                description="Analyze [domain] configurations",
                keywords=["analyze", "review", "assess"],
                phrases=["analyze my", "review the"],
                priority=8,
                confidence_threshold=0.6
            )
        ]
    
    def get_metadata(self) -> AgentMetadata:
        """Provide agent metadata."""
        return AgentMetadata(
            name="Your Domain Agent",
            description="Specialized agent for [domain] analysis",
            version="1.0.0",
            author="Your Name",
            capabilities=self.get_capabilities(),
            # ... other metadata
        )
```

### Step 2: Register Your Agent

```python
# In agent_registry.py or your initialization code
from .your_domain_agent import YourDomainAgent

agent_registry.register_agent_class("your_domain", YourDomainAgent)
```

### Step 3: Update Configuration

Add your agent to `agent_config.json`:

```json
{
  "agents": {
    "your_domain": {
      "name": "Your Domain Agent",
      "description": "Specialized agent for [domain] analysis",
      "enabled": true,
      "capabilities": [
        {
          "name": "domain_analysis",
          "keywords": ["analyze", "review", "assess"],
          "priority": 8
        }
      ]
    }
  }
}
```

## Detailed Implementation Guide

### System Prompt Design

The system prompt is the heart of your AI-first agent. Follow this structure:

```markdown
## Core Capabilities
[Define what your agent does and its reasoning abilities]

## CRITICAL: MCP Tools Usage Instructions
[Detailed instructions for using real-time data tools]

### Key MCP Tools and Usage Patterns
[Specific examples of tool usage with proper parameters]

### Optimized Usage Patterns
[Domain-specific optimization patterns]

## [Domain] Knowledge Context (Fallback)
[Comprehensive domain knowledge for fallback mode]

## Response Format Guidelines
[Structure for consistent responses]

## Conversation Context and [Domain] Tracking
[How to maintain context across interactions]

## Important Instructions
[Critical guidelines for behavior and responses]
```

### MCP Integration Patterns

#### 1. Initialize MCP Client

```python
def _initialize_mcp_client(self) -> Optional[MCPClient]:
    """Initialize domain-specific MCP client."""
    try:
        from mcp import stdio_client, StdioServerParameters
        
        mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="bash",
                args=["-c", "uvx your-domain-mcp-server@latest"],
                env={
                    **os.environ,
                    "FASTMCP_LOG_LEVEL": "ERROR",
                    "MCP_TIMEOUT": "30"
                }
            )
        ))
        
        return mcp_client if self._test_mcp_connection(mcp_client) else None
    except Exception as e:
        logger.error(f"MCP initialization failed: {e}")
        return None
```

#### 2. Provide MCP Tools to Agent

```python
def _get_mcp_tools(self):
    """Provide MCP tools to Strands SDK."""
    if self.mcp_client:
        return [self.mcp_client]  # Let Strands SDK handle context
    return []
```

#### 3. Handle MCP Errors Gracefully

```python
# In your system prompt
### Error Handling for MCP Tools
- If MCP tools fail, acknowledge the failure and use knowledge base
- Always mention when using cached/estimated vs real-time data
- Provide troubleshooting guidance for connection issues
```

### Capability Definition

Define clear capabilities for your agent:

```python
def get_capabilities(self) -> List[AgentCapability]:
    return [
        AgentCapability(
            name="primary_capability",
            description="Main function of your agent",
            keywords=["key", "words", "that", "trigger"],
            phrases=["specific phrases", "that indicate", "this capability"],
            priority=8,  # Higher = preferred for overlapping capabilities
            confidence_threshold=0.6  # Minimum confidence to route here
        ),
        AgentCapability(
            name="secondary_capability",
            description="Additional function",
            keywords=["other", "keywords"],
            phrases=["other phrases"],
            priority=6,
            confidence_threshold=0.5
        )
    ]
```

### Performance Optimization

#### 1. Implement Caching

```python
def __init__(self, config: Dict[str, Any] = None):
    # ... other initialization
    
    self.query_cache = {}
    self.performance_stats = {
        'total_queries': 0,
        'cache_hits': 0,
        'mcp_calls': 0,
        'avg_response_time': 0
    }

async def process_query(self, query: str, context: Dict[str, Any] = None):
    # Check cache first
    query_hash = hash(query.lower().strip())
    if query_hash in self.query_cache:
        self.performance_stats['cache_hits'] += 1
        return self.query_cache[query_hash].copy()
    
    # Process query...
    
    # Cache successful responses (limit size)
    if len(self.query_cache) < 10:
        self.query_cache[query_hash] = result.copy()
```

#### 2. Track Performance Metrics

```python
start_time = time.time()
# ... process query
response_time = time.time() - start_time

self.performance_stats['avg_response_time'] = (
    (self.performance_stats['avg_response_time'] * (self.performance_stats['total_queries'] - 1) + response_time) 
    / self.performance_stats['total_queries']
)
```

### Error Handling Patterns

#### 1. Comprehensive Error Analysis

```python
def _get_troubleshooting_guidance(self, error: Exception) -> List[str]:
    error_str = str(error).lower()
    guidance = []
    
    if 'timeout' in error_str:
        guidance.extend([
            'Reduce query complexity',
            'Break into smaller parts',
            'Try again later'
        ])
    elif 'connection' in error_str:
        guidance.extend([
            'Check network connectivity',
            'Verify MCP server status',
            'Service may be temporarily unavailable'
        ])
    
    return guidance
```

#### 2. User-Friendly Error Messages

```python
return {
    'status': 'error',
    'error': str(e),
    'troubleshooting': self._get_troubleshooting_guidance(e),
    'fallback_available': self.agent_fallback is not None
}
```

## Domain-Specific Examples

### Security Agent Example

```python
class SecurityAgent(AIFirstAgentTemplate):
    def _get_system_prompt(self) -> str:
        return """You are an AWS Security Specialized Agent...
        
        ## Core Capabilities
        - Analyze AWS security configurations and identify vulnerabilities
        - Provide security optimization recommendations
        - Check compliance against security standards
        
        ## MCP Tools for Security Analysis
        - get_security_findings(): Current security issues
        - analyze_iam_policies(policy): IAM policy analysis
        - check_compliance(service, standards): Compliance checking
        
        ## Security Knowledge Context
        - IAM Best Practices: Principle of least privilege, role-based access
        - Network Security: VPC security groups, NACLs, flow logs
        - Data Protection: Encryption at rest/transit, S3 policies
        """
    
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="security_analysis",
                description="Analyze security configurations",
                keywords=["security", "vulnerability", "risk", "compliance"],
                phrases=["security analysis", "check security", "vulnerability assessment"],
                priority=9,
                confidence_threshold=0.7
            )
        ]
```

### Performance Agent Example

```python
class PerformanceAgent(AIFirstAgentTemplate):
    def _get_system_prompt(self) -> str:
        return """You are an AWS Performance Specialized Agent...
        
        ## Core Capabilities
        - Analyze AWS performance metrics and identify bottlenecks
        - Provide performance optimization recommendations
        - Monitor and alert on performance issues
        
        ## MCP Tools for Performance Analysis
        - get_performance_metrics(service, timeframe): Current metrics
        - analyze_bottlenecks(architecture): Bottleneck analysis
        - get_optimization_recommendations(metrics): Performance tuning
        
        ## Performance Knowledge Context
        - EC2 Performance: Instance types, CPU/memory optimization
        - Database Performance: RDS tuning, connection pooling
        - Network Performance: Latency optimization, CDN usage
        """
```

## Testing Your Agent

### 1. Unit Testing

```python
import pytest
from your_domain_agent import YourDomainAgent

@pytest.fixture
def agent():
    return YourDomainAgent()

def test_capabilities(agent):
    capabilities = agent.get_capabilities()
    assert len(capabilities) > 0
    assert all(cap.name for cap in capabilities)

def test_confidence_scoring(agent):
    high_confidence_query = "analyze my security configuration"
    low_confidence_query = "what's the weather like"
    
    high_score = agent.get_confidence_score(high_confidence_query)
    low_score = agent.get_confidence_score(low_confidence_query)
    
    assert high_score > low_score
```

### 2. Integration Testing

```python
async def test_query_processing(agent):
    query = "Test query for your domain"
    response = await agent.process_query(query)
    
    assert response['status'] == 'success'
    assert 'response' in response
    assert response['agent_type'] == 'YourDomainAgent'
```

### 3. MCP Integration Testing

```python
def test_mcp_integration(agent):
    if agent.mcp_client:
        # Test MCP tools are available
        tools = agent._get_mcp_tools()
        assert len(tools) > 0
    else:
        # Test fallback mode works
        assert agent._create_fallback_agent() is not None
```

## Best Practices

### 1. System Prompt Guidelines
- **Be Comprehensive**: Include extensive domain knowledge
- **Be Specific**: Provide exact examples and patterns
- **Be Structured**: Use clear sections and formatting
- **Include Examples**: Show proper tool usage patterns
- **Handle Errors**: Provide fallback instructions

### 2. MCP Integration Guidelines
- **Test Connections**: Always verify MCP server availability
- **Handle Failures**: Graceful degradation to knowledge base
- **Optimize Queries**: Use specific parameters to reduce response size
- **Cache Results**: Avoid repeated calls for same data
- **Monitor Performance**: Track response times and success rates

### 3. Performance Guidelines
- **Implement Caching**: Cache successful responses
- **Track Metrics**: Monitor performance statistics
- **Optimize Prompts**: Balance comprehensiveness with token limits
- **Batch Operations**: Combine related queries when possible
- **Async Processing**: Use async/await for better performance

### 4. Error Handling Guidelines
- **User-Friendly Messages**: Provide clear, actionable error messages
- **Troubleshooting Guidance**: Include specific steps to resolve issues
- **Fallback Strategies**: Always have a backup plan
- **Confidence Levels**: Indicate reliability of responses
- **Logging**: Log errors for debugging and improvement

## Common Pitfalls to Avoid

### 1. Over-Engineering Helper Methods
- **Problem**: Creating complex helper methods instead of using AI reasoning
- **Solution**: Trust the AI with comprehensive system prompts

### 2. Insufficient Error Handling
- **Problem**: Not handling MCP server failures gracefully
- **Solution**: Always implement fallback modes and user guidance

### 3. Poor System Prompt Design
- **Problem**: Vague or incomplete system prompts
- **Solution**: Include comprehensive domain knowledge and specific examples

### 4. Ignoring Performance
- **Problem**: Not implementing caching or performance tracking
- **Solution**: Add caching and monitor response times from the start

### 5. Inadequate Testing
- **Problem**: Not testing MCP integration and error scenarios
- **Solution**: Test both happy paths and failure modes

## Advanced Patterns

### 1. Multi-Agent Collaboration

```python
async def collaborate_with_agent(self, other_agent_id: str, query: str):
    """Collaborate with another specialized agent."""
    other_agent = agent_registry.get_agent(other_agent_id)
    if other_agent:
        other_response = await other_agent.process_query(query)
        # Combine insights from both agents
        return self._combine_agent_responses(other_response)
```

### 2. Dynamic Capability Adjustment

```python
def adjust_capabilities_based_on_context(self, context: Dict[str, Any]):
    """Dynamically adjust capabilities based on context."""
    if context.get('user_expertise') == 'expert':
        # Increase confidence thresholds for expert users
        for cap in self.get_capabilities():
            cap.confidence_threshold *= 1.2
```

### 3. Learning from Interactions

```python
def learn_from_interaction(self, query: str, response: Dict[str, Any], feedback: str):
    """Learn from user feedback to improve future responses."""
    # Store interaction data for analysis
    self.interaction_history.append({
        'query': query,
        'response': response,
        'feedback': feedback,
        'timestamp': time.time()
    })
```

## Deployment Checklist

Before deploying your new agent:

- [ ] System prompt is comprehensive and domain-specific
- [ ] MCP integration tested and working
- [ ] Fallback mode implemented and tested
- [ ] Capabilities clearly defined with appropriate keywords
- [ ] Error handling covers all known scenarios
- [ ] Performance optimization implemented (caching, metrics)
- [ ] Unit and integration tests passing
- [ ] Agent registered in agent registry
- [ ] Configuration updated in agent_config.json
- [ ] Documentation updated with new capabilities

## Conclusion

The AI-first approach to specialized agents provides a powerful, maintainable, and scalable foundation for building intelligent systems. By following these patterns and guidelines, you can create specialized agents that:

- Leverage AI reasoning instead of complex code
- Integrate seamlessly with real-time data sources
- Provide excellent user experiences with graceful error handling
- Scale efficiently with performance optimization
- Maintain high quality through comprehensive testing

The key is to trust the AI with comprehensive domain knowledge while providing the right infrastructure for data access, error handling, and performance optimization.