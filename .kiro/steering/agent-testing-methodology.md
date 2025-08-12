# Agent Testing Methodology and Best Practices

## Overview

This document establishes proven testing methodologies for AI agents, particularly those with external integrations like MCP servers. Based on successful optimization of the AWS Pricing Agent.

## 🎯 Testing Philosophy

### Core Principles

1. **Test Real Scenarios**: Use actual user queries, not artificial test cases
2. **Validate End-to-End**: Test complete user workflows, not just individual functions
3. **Expect Variability**: AI responses vary - test for patterns, not exact matches
4. **Isolate When Debugging**: Use targeted tests to debug specific issues
5. **Monitor Performance**: Always track response times and success rates

### Testing Pyramid for AI Agents

```
    /\
   /  \     E2E Integration Tests (Few, High Value)
  /____\    
 /      \    Component Tests (Some, Focused)
/________\   Unit Tests (Many, Fast)
```

## 🧪 Test Categories and Patterns

### 1. Functional Testing

**Simple Query Tests (Filter Optimization)**
```python
{
    "name": "Simple Query Test",
    "query": "What's the cost of a t3.small EC2 instance in us-east-1?",
    "expected_features": ["real-time data", "monthly cost", "annual cost"],
    "success_criteria": {
        "response_time": "<5s",
        "feature_coverage": ">80%",
        "mcp_integration": "working"
    }
}
```

**Complex Query Tests (Performance Optimization)**
```python
{
    "name": "Multi-Service Architecture Test",
    "query": "I need pricing for a 3-tier web app with EC2, RDS, and S3 for 10,000 users",
    "expected_features": ["multiple services", "cost breakdown", "optimization suggestions"],
    "success_criteria": {
        "response_time": "<10s",
        "services_analyzed": ">=3",
        "optimization_provided": True
    }
}
```

### 2. Integration Testing

**MCP Server Integration**
```python
async def test_mcp_integration():
    """Test MCP server connectivity and data retrieval."""
    agent = AWSPricingAgent()
    
    # Test connection
    assert agent.pricing_mcp_client is not None
    
    # Test data retrieval
    result = await agent.process_pricing_query("Simple pricing query")
    assert result['mcp_available'] == True
    assert result['status'] == 'success'
    
    # Test error handling
    # Simulate MCP failure and verify graceful degradation
```

**Multi-Region Testing**
```python
{
    "name": "Multi-Region Comparison",
    "query": "Compare costs for t3.medium across us-east-1, us-west-2, and eu-west-1",
    "expected_features": ["multi-region", "cost comparison", "regional differences"],
    "validation_logic": {
        "regions_mentioned": ["us-east-1", "us-west-2", "eu-west-1"],
        "comparison_language": ["compare", "comparison", "breakdown"],
        "regional_analysis": ["region", "difference", "considerations"]
    }
}
```

### 3. Performance Testing

**Response Time Benchmarks**
```python
performance_targets = {
    "simple_queries": {"target": 5.0, "acceptable": 8.0},
    "complex_queries": {"target": 10.0, "acceptable": 15.0},
    "cached_queries": {"target": 1.0, "acceptable": 2.0},
    "error_scenarios": {"target": 3.0, "acceptable": 5.0}
}
```

**Caching Effectiveness**
```python
async def test_caching_performance():
    """Test caching system effectiveness."""
    agent = AWSPricingAgent()
    
    # First query - should be slow
    start_time = time.time()
    result1 = await agent.process_pricing_query("Test query")
    first_response_time = time.time() - start_time
    
    # Second identical query - should be fast (cached)
    start_time = time.time()
    result2 = await agent.process_pricing_query("Test query")
    cached_response_time = time.time() - start_time
    
    assert result2.get('cached') == True
    assert cached_response_time < 1.0  # Should be nearly instant
    assert first_response_time > cached_response_time * 2  # Significant improvement
```

### 4. Error Handling Testing

**MCP Server Unavailable**
```python
async def test_mcp_server_unavailable():
    """Test behavior when MCP server is unavailable."""
    agent = AWSPricingAgent()
    
    # Simulate MCP server failure
    agent.pricing_mcp_client = None
    
    result = await agent.process_pricing_query("Pricing query")
    
    # Should still provide response using knowledge base
    assert result['status'] == 'success'
    assert result['mcp_available'] == False
    assert 'fallback' in result.get('note', '').lower()
    assert 'troubleshooting' in result
```

**Invalid Query Handling**
```python
error_test_scenarios = [
    {
        "name": "Invalid Service",
        "query": "Get pricing for InvalidServiceXYZ",
        "expected_behavior": "graceful_error_with_suggestions"
    },
    {
        "name": "Invalid Region",
        "query": "What's the cost in invalid-region-123?",
        "expected_behavior": "region_validation_error_with_valid_options"
    }
]
```

## 🔍 Feature Detection Patterns

### Flexible Keyword Matching

**Avoid overly strict keyword detection:**
```python
# BAD: Too strict
def check_feature_strict(response, feature):
    return feature.lower() in response.lower()

# GOOD: Flexible with synonyms
feature_keywords = {
    "cost_comparison": ["compare", "comparison", "breakdown", "cost breakdown", "versus", "vs"],
    "optimization": ["optimization", "optimize", "savings", "recommend", "improve", "reduce cost"],
    "real_time_data": ["real-time", "current", "latest", "mcp", "up-to-date", "live data"]
}

def check_feature_flexible(response, feature):
    keywords = feature_keywords.get(feature, [feature])
    return any(keyword in response.lower() for keyword in keywords)
```

### Semantic Feature Detection

**Use semantic understanding for complex features:**
```python
def check_multi_service_analysis(response):
    """Check if response analyzes multiple AWS services."""
    services = ["ec2", "rds", "s3", "lambda", "eks", "emr", "redshift"]
    services_mentioned = sum(1 for service in services if service in response.lower())
    return services_mentioned >= 2

def check_cost_breakdown_provided(response):
    """Check if response provides detailed cost breakdown."""
    breakdown_indicators = [
        "monthly cost" in response.lower(),
        "annual cost" in response.lower(),
        "breakdown" in response.lower(),
        "$" in response and ("month" in response.lower() or "year" in response.lower())
    ]
    return sum(breakdown_indicators) >= 2
```

## 📊 Test Execution Patterns

### Comprehensive Test Suite

**Structure for complete agent testing:**
```python
class AgentTestSuite:
    def __init__(self, agent_class):
        self.agent_class = agent_class
        self.results = []
    
    async def run_all_tests(self):
        """Run complete test suite."""
        # Functional tests
        await self.run_functional_tests()
        
        # Integration tests
        await self.run_integration_tests()
        
        # Performance tests
        await self.run_performance_tests()
        
        # Error handling tests
        await self.run_error_handling_tests()
        
        # Generate comprehensive report
        return self.generate_report()
    
    def generate_report(self):
        """Generate detailed test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'])
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': (passed_tests / total_tests) * 100,
                'avg_response_time': self.calculate_avg_response_time()
            },
            'detailed_results': self.results,
            'recommendations': self.generate_recommendations()
        }
```

### Isolated Testing for Debugging

**When comprehensive tests show issues:**
```python
async def debug_specific_feature(agent, feature_name, test_query):
    """Debug specific feature in isolation."""
    print(f"🔍 Debugging: {feature_name}")
    
    # Clear any caches to ensure fresh response
    if hasattr(agent, 'query_cache'):
        agent.query_cache = {}
    
    # Run isolated test
    result = await agent.process_pricing_query(test_query)
    
    # Detailed analysis
    response_text = result.get('response', '').lower()
    
    print(f"Response length: {len(response_text)} characters")
    print(f"MCP available: {result.get('mcp_available', False)}")
    print(f"Status: {result.get('status', 'unknown')}")
    
    # Show response sample
    print(f"Response sample: {response_text[:500]}...")
    
    return result
```

## 🚨 Common Testing Pitfalls

### 1. False Negatives from Strict Matching

**Problem**: Test fails even though functionality works
```python
# BAD: Too strict
assert "cost comparison" in response.lower()

# GOOD: Flexible matching
comparison_indicators = ["compare", "comparison", "breakdown", "versus"]
assert any(indicator in response.lower() for indicator in comparison_indicators)
```

### 2. Caching Interference

**Problem**: Cached responses affect test results
```python
# SOLUTION: Clear cache between tests
def setup_test(agent):
    if hasattr(agent, 'query_cache'):
        agent.query_cache = {}
    if hasattr(agent, 'performance_stats'):
        agent.performance_stats = {'total_queries': 0, 'cache_hits': 0}
```

### 3. Timing-Dependent Tests

**Problem**: Tests fail due to response time variations
```python
# BAD: Hard timeout
assert response_time < 5.0

# GOOD: Reasonable ranges with context
if query_complexity == "simple":
    assert response_time < 8.0, f"Simple query took {response_time}s (expected <8s)"
elif query_complexity == "complex":
    assert response_time < 15.0, f"Complex query took {response_time}s (expected <15s)"
```

### 4. Ignoring AI Response Variability

**Problem**: Tests expect identical responses
```python
# BAD: Exact string matching
assert response == expected_response

# GOOD: Pattern and feature matching
assert check_required_features(response, expected_features)
assert response_quality_score(response) > 0.8
```

## 📈 Test Metrics and KPIs

### Success Criteria

**Production Readiness Thresholds:**
```python
production_readiness = {
    'functional_tests': {'pass_rate': 0.95, 'min_tests': 10},
    'integration_tests': {'pass_rate': 0.90, 'min_tests': 5},
    'performance_tests': {'pass_rate': 0.85, 'response_time_p95': 10.0},
    'error_handling_tests': {'pass_rate': 0.90, 'graceful_degradation': True}
}
```

### Continuous Monitoring

**Key metrics to track in production:**
```python
production_metrics = {
    'success_rate': 'percentage_of_successful_queries',
    'response_times': 'p50_p95_p99_response_times',
    'feature_coverage': 'percentage_of_expected_features_present',
    'user_satisfaction': 'feedback_scores_and_ratings',
    'error_patterns': 'categorized_error_frequency'
}
```

## 🔄 Test Maintenance

### Regular Test Updates

**Monthly maintenance tasks:**
1. Review and update test scenarios based on user feedback
2. Adjust performance thresholds based on production data
3. Add new test cases for edge cases discovered in production
4. Update feature detection logic for improved accuracy

### Test Data Management

**Keep test queries relevant:**
```python
# Rotate test queries to match real usage patterns
test_query_rotation = {
    'simple_queries': ['current_popular_queries'],
    'complex_queries': ['real_user_scenarios'],
    'edge_cases': ['discovered_failure_modes']
}
```

This testing methodology ensures robust, reliable AI agents that perform well in production environments while maintaining high quality standards.