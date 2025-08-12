# AWS Pricing Agent Optimization Guidelines

## Overview

This document captures critical learnings from the successful MCP integration optimization of the AWS Pricing Agent. These guidelines should be followed for any future development or optimization work on this agent.

## 🎯 Key Success Factors

### 1. MCP Integration Best Practices

**System Prompt Optimization:**
- Always include comprehensive MCP tool usage instructions in system prompts
- Provide specific filter patterns for each AWS service (EC2, RDS, S3, Lambda)
- Include the complete workflow: analyze → identify → get attributes → get values → call pricing → calculate → optimize → present
- Add performance optimization guidelines (specific filters, batch queries, regional queries)

**Critical Filter Patterns:**
```python
# EC2 - Always include these filters
{"Field": "instanceType", "Value": "t3.small", "Type": "EQUALS"},
{"Field": "tenancy", "Value": "Shared", "Type": "EQUALS"},
{"Field": "operatingSystem", "Value": "Linux", "Type": "EQUALS"}

# RDS - Essential filters
{"Field": "instanceType", "Value": "db.t3.small", "Type": "EQUALS"},
{"Field": "engineCode", "Value": "mysql", "Type": "EQUALS"},
{"Field": "deploymentOption", "Value": "Single-AZ", "Type": "EQUALS"}

# Multi-region queries
get_pricing("AmazonEC2", ["us-east-1", "us-west-2", "eu-west-1"], filters)
```

### 2. Performance Optimization Strategies

**Model Configuration:**
- Temperature: 0.2 (for consistency)
- Max Tokens: 6000 (for complex queries)
- Top P: 0.7 (for focused responses)

**Caching Implementation:**
- Implement simple query caching with hash-based keys
- Limit cache size (10 entries max to prevent memory issues)
- Track performance stats: total_queries, cache_hits, mcp_calls, avg_response_time

**Connection Optimization:**
- Set MCP_TIMEOUT=30 and MCP_MAX_RETRIES=3 in environment
- Implement enhanced connection testing
- Add graceful degradation when MCP unavailable

### 3. Testing and Validation

**Comprehensive Test Coverage:**
- Simple queries (filter optimization)
- Multi-service architectures (complex query handling)
- Multi-region comparisons (regional optimization)
- Complex microservices (performance optimization)
- Cached queries (caching validation)

**Test Validation Criteria:**
- Success rate: Target >90%
- Response times: <5s simple, <10s complex
- Feature coverage: >80%
- MCP integration: Must be working
- Caching: Must show performance improvement

**Common Test Issues:**
- False negatives due to keyword detection logic being too strict
- Caching interference during comprehensive tests
- Response variation between test runs
- Always validate with isolated tests when comprehensive tests show issues

## 🚨 Critical Implementation Notes

### MCP Server Integration

**AWS Labs MCP Server:**
- Use: `uvx awslabs.aws-pricing-mcp-server@latest`
- Requires: uvx/uv installation
- Environment: Set FASTMCP_LOG_LEVEL=ERROR to reduce noise
- Connection: Test with simple queries first

**Error Handling Patterns:**
- uvx_not_installed: Guide user to install uv/uvx
- missing_dependencies: Install mcp and strands[mcp]
- server_unavailable: Provide fallback with knowledge base
- Always include troubleshooting steps in error responses

### System Prompt Structure

**Required Sections:**
1. Core Capabilities (with MCP emphasis)
2. MCP Tools Usage Instructions (detailed examples)
3. Optimized Filter Patterns (service-specific)
4. Performance Optimization Guidelines
5. Error Handling Instructions
6. AWS Pricing Knowledge Context (fallback)
7. Response Format Guidelines
8. Query Processing Workflow

**Critical Instructions:**
- "ALWAYS use MCP tools when available for real pricing data"
- "Be specific about whether you're using real-time data or estimates"
- "Include monthly AND annual cost estimates"
- "Default to us-east-1 when no region specified"

## 🔧 Technical Architecture

### Agent Structure
```python
class AWSPricingAgent:
    def __init__(self):
        # Optimized model configuration
        self.bedrock_model = BedrockModel(
            model_id="amazon.nova-lite-v1:0",
            temperature=0.2,
            max_tokens=6000,
            top_p=0.7
        )
        
        # Performance tracking
        self.query_cache = {}
        self.performance_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'mcp_calls': 0,
            'avg_response_time': 0
        }
```

### Response Structure
All responses should follow this format:
1. Architecture Analysis
2. Real-Time Pricing Data (using MCP tools)
3. Cost Breakdown (monthly/annual)
4. Regional Considerations
5. Optimization Opportunities
6. Implementation Guidance

## 🎯 Future Development Guidelines

### When Adding New Features:
1. Always test MCP integration first
2. Update system prompt with new service patterns
3. Add comprehensive test coverage
4. Validate performance impact
5. Update error handling for new scenarios

### When Debugging Issues:
1. Check MCP server connection first
2. Validate filter formats against AWS Labs server
3. Test with isolated queries before comprehensive tests
4. Check for caching interference
5. Verify keyword detection logic in tests

### When Optimizing Performance:
1. Profile response times by query complexity
2. Optimize system prompt length vs. completeness
3. Implement progressive caching strategies
4. Monitor MCP server response patterns
5. Balance accuracy vs. speed

## 📊 Success Metrics

### Production Readiness Criteria:
- ✅ Success Rate: >90%
- ✅ Response Time: <5s simple, <10s complex
- ✅ MCP Integration: Working with real-time data
- ✅ Caching: >20% hit rate for typical usage
- ✅ Feature Coverage: >80% comprehensive functionality
- ✅ Error Handling: Graceful degradation

### Monitoring in Production:
- Track response times and success rates
- Monitor MCP connection health
- Measure cache effectiveness
- Log error patterns for improvement
- Collect user feedback on accuracy

## 🚀 Deployment Checklist

Before deploying optimizations:
- [ ] MCP server connection tested and working
- [ ] System prompt includes all optimization patterns
- [ ] Caching implementation tested
- [ ] Error handling covers all known scenarios
- [ ] Comprehensive test suite passes >90%
- [ ] Performance metrics meet targets
- [ ] Documentation updated with new capabilities

## 💡 Key Learnings

1. **MCP Integration is Critical**: Real-time data significantly improves accuracy and user trust
2. **System Prompt Quality Matters**: Detailed instructions lead to better MCP tool usage
3. **Caching Provides Major Benefits**: 0.00s response times for repeated queries
4. **Testing Must Be Comprehensive**: False negatives can occur with insufficient test coverage
5. **Performance Optimization is Iterative**: Small improvements compound to significant gains
6. **Error Handling is User Experience**: Good error messages with troubleshooting improve adoption

## 🔄 Continuous Improvement

Regular optimization tasks:
- Review and update filter patterns as AWS services evolve
- Monitor MCP server updates and compatibility
- Analyze user query patterns for optimization opportunities
- Update system prompt based on real usage patterns
- Refine caching strategies based on hit rate analysis

This guidance ensures future development maintains the high quality and performance achieved through this optimization effort.