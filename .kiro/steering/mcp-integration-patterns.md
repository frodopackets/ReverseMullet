# MCP Integration Patterns and Best Practices

## Overview

This document captures proven patterns for integrating Model Context Protocol (MCP) servers with AI agents, based on successful implementation with the AWS Labs aws-pricing-mcp-server.

## 🔧 MCP Server Setup Patterns

### Standard MCP Server Configuration

**Kiro MCP Configuration (.kiro/settings/mcp.json):**
```json
{
  "mcpServers": {
    "aws-pricing": {
      "command": "uvx",
      "args": ["awslabs.aws-pricing-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "MCP_TIMEOUT": "30",
        "MCP_MAX_RETRIES": "3"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Agent MCP Client Initialization:**
```python
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

pricing_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="bash",
        args=["-c", "source ~/.local/bin/env && uvx awslabs.aws-pricing-mcp-server@latest"],
        env={
            **os.environ,
            "FASTMCP_LOG_LEVEL": "ERROR",
            "AWS_REGION": "us-east-1",
            "MCP_TIMEOUT": "30",
            "MCP_MAX_RETRIES": "3"
        }
    )
))
```

### Connection Testing Pattern

**Always test MCP connections before use:**
```python
def _test_mcp_connection_enhanced(self, mcp_client):
    """Enhanced MCP server connection test with performance metrics."""
    if not mcp_client:
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
```

## 🎯 System Prompt Integration Patterns

### MCP Tool Usage Instructions Template

**Always include in system prompts:**
```markdown
## CRITICAL: MCP Tools Usage Instructions

### When MCP Tools Are Available
You have access to real-time data through MCP tools. ALWAYS use these tools instead of relying on estimates.

### Key MCP Tools and Usage Patterns

#### 1. Discovery Tools
- get_service_codes() - Discover available services
- get_service_attributes(service_code) - Find available filters
- get_attribute_values(service_code, attributes) - Get valid filter values

#### 2. Data Retrieval Tools
- get_data(service_code, region, filters) - Get real-time data

### Optimized Usage Patterns

**Service-Specific Filter Examples:**
[Include specific examples for your domain]

**Performance Guidelines:**
1. Use specific filters to reduce response size
2. Batch queries when possible
3. Cache results within conversations
4. Handle errors gracefully with fallbacks
```

### Error Handling Instructions

**Include comprehensive error handling guidance:**
```markdown
### Error Handling for MCP Tools
- If MCP tools fail, acknowledge the failure and use knowledge base
- Always mention when using cached/estimated vs real-time data
- Provide troubleshooting guidance for connection issues
- Include confidence levels for estimates
```

## 🚀 Performance Optimization Patterns

### Caching Implementation

**Simple but effective caching pattern:**
```python
# Performance tracking and caching
self.query_cache = {}
self.performance_stats = {
    'total_queries': 0,
    'cache_hits': 0,
    'mcp_calls': 0,
    'avg_response_time': 0
}

# In query processing
query_hash = hash(query.lower().strip())
if query_hash in self.query_cache:
    self.performance_stats['cache_hits'] += 1
    logger.info("Using cached response for similar query")
    cached_response = self.query_cache[query_hash].copy()
    cached_response['cached'] = True
    return cached_response

# Cache successful responses (limit size)
if len(self.query_cache) < 10:
    self.query_cache[query_hash] = result.copy()
```

### Response Time Tracking

**Always track performance metrics:**
```python
import time
start_time = time.time()

# Process query...

response_time = time.time() - start_time
self.performance_stats['avg_response_time'] = (
    (self.performance_stats['avg_response_time'] * (self.performance_stats['total_queries'] - 1) + response_time) 
    / self.performance_stats['total_queries']
)
```

## 🛡️ Error Handling Patterns

### Comprehensive Error Analysis

**Pattern for analyzing and handling MCP errors:**
```python
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
    elif 'invalid' in error_str or 'format' in error_str:
        error_info['optimization_suggestions'] = [
            'Verify filter field names using discovery tools',
            'Check filter values using attribute value tools',
            'Use exact field names and values from MCP server'
        ]
    
    return error_info
```

### Graceful Degradation

**Always provide fallback when MCP unavailable:**
```python
try:
    # Use MCP tools for real-time data
    response = await self.agent.invoke_async(query)
    result['mcp_available'] = True
    result['confidence'] = 'high'
except Exception as e:
    # Fallback to knowledge base
    logger.warning(f"MCP unavailable, using knowledge base: {str(e)}")
    response = await self.agent_fallback.invoke_async(query)
    result['mcp_available'] = False
    result['confidence'] = 'medium'
    result['note'] = 'Using knowledge base - verify with official sources'
```

## 🧪 Testing Patterns

### Comprehensive Test Coverage

**Test categories for MCP integration:**
```python
test_scenarios = [
    {
        "name": "Simple Query (Filter Optimization)",
        "query": "Basic query with standard filters",
        "expected_features": ["real-time data", "specific results"]
    },
    {
        "name": "Complex Query (Performance Optimization)", 
        "query": "Multi-parameter complex query",
        "expected_features": ["multiple data points", "comprehensive analysis"]
    },
    {
        "name": "Error Handling (Robustness)",
        "query": "Query designed to trigger errors",
        "expected_features": ["graceful error handling", "troubleshooting guidance"]
    },
    {
        "name": "Cached Query (Performance)",
        "query": "Repeat of previous query",
        "expected_features": ["cached response", "fast response time"]
    }
]
```

### Test Validation Logic

**Robust feature detection:**
```python
feature_keywords = {
    "real-time data": ["real-time", "current", "latest", "mcp"],
    "error handling": ["error", "unavailable", "fallback", "troubleshooting"],
    "performance": ["cached", "fast", "optimized"],
    "comprehensive": ["breakdown", "analysis", "detailed"]
}

# Use flexible keyword matching
def check_feature(response_text, feature):
    keywords = feature_keywords.get(feature, [feature])
    return any(keyword in response_text.lower() for keyword in keywords)
```

## 📊 Monitoring and Observability

### Production Monitoring

**Key metrics to track:**
```python
production_metrics = {
    'mcp_connection_health': 'percentage_uptime',
    'response_times': 'p50, p95, p99',
    'success_rates': 'percentage_successful_queries',
    'cache_effectiveness': 'hit_rate_percentage',
    'error_patterns': 'categorized_error_counts'
}
```

### Health Check Pattern

**Regular health checks for MCP servers:**
```python
async def health_check_mcp(self):
    """Perform health check on MCP server connection."""
    try:
        # Simple test query
        test_result = await self.simple_mcp_query()
        return {
            'status': 'healthy',
            'response_time': test_result.get('response_time', 0),
            'timestamp': time.time()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }
```

## 🔄 Maintenance Patterns

### Regular Optimization Tasks

**Scheduled maintenance activities:**
1. **Weekly**: Review error logs and update error handling
2. **Monthly**: Analyze performance metrics and optimize bottlenecks
3. **Quarterly**: Update MCP server versions and test compatibility
4. **As needed**: Update system prompts based on usage patterns

### Version Management

**Track MCP server versions:**
```python
mcp_server_info = {
    'server_name': 'awslabs.aws-pricing-mcp-server',
    'version': 'latest',  # or specific version
    'last_updated': '2024-01-15',
    'compatibility_tested': True,
    'performance_baseline': {
        'avg_response_time': 3.5,
        'success_rate': 0.95
    }
}
```

## 💡 Key Success Factors

1. **Comprehensive System Prompts**: Include detailed MCP usage instructions
2. **Robust Error Handling**: Plan for MCP server unavailability
3. **Performance Optimization**: Implement caching and monitoring
4. **Thorough Testing**: Cover all integration scenarios
5. **Graceful Degradation**: Always have fallback strategies
6. **Continuous Monitoring**: Track health and performance metrics

## 🚨 Common Pitfalls to Avoid

1. **Assuming MCP Always Available**: Always implement fallbacks
2. **Insufficient Error Context**: Provide actionable troubleshooting
3. **Ignoring Performance**: Monitor and optimize response times
4. **Inadequate Testing**: Test error scenarios, not just happy paths
5. **Static Integration**: Plan for MCP server updates and changes
6. **Poor User Communication**: Always indicate data source and confidence

This pattern guide ensures consistent, high-quality MCP integrations across all agent implementations.