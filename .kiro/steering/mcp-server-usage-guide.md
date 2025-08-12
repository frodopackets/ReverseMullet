# MCP Server Usage Guide for Kiro Agents

## Overview

This document provides guidance for Kiro agents on how to effectively use the configured MCP servers in this workspace. Always prioritize MCP data over knowledge base when available.

## 🔧 Available MCP Servers

### 1. AWS Pricing Server (aws-pricing)
**Purpose**: Real-time AWS pricing data and cost analysis
**Server**: `awslabs.aws-pricing-mcp-server@latest`
**Status**: ✅ Configured

**Key Tools Available:**
- `get_pricing_service_codes()` - Discover available AWS services
- `get_pricing_service_attributes(service_code)` - Find filterable attributes
- `get_pricing_attribute_values(service_code, attributes)` - Get valid filter values
- `get_pricing(service_code, region, filters)` - Get real-time pricing data

**Usage Trigger**: ALWAYS use when user asks for AWS pricing estimates, cost analysis, or cost optimization

**Optimized Usage Patterns:**
```python
# EC2 Pricing with optimized filters
get_pricing("AmazonEC2", "us-east-1", [
  {"Field": "instanceType", "Value": "t3.small", "Type": "EQUALS"},
  {"Field": "tenancy", "Value": "Shared", "Type": "EQUALS"},
  {"Field": "operatingSystem", "Value": "Linux", "Type": "EQUALS"}
])

# Multi-region comparison
get_pricing("AmazonEC2", ["us-east-1", "us-west-2", "eu-west-1"], [
  {"Field": "instanceType", "Value": "t3.medium", "Type": "EQUALS"}
])

# RDS with engine specification
get_pricing("AmazonRDS", "us-east-1", [
  {"Field": "instanceType", "Value": "db.t3.small", "Type": "EQUALS"},
  {"Field": "engineCode", "Value": "mysql", "Type": "EQUALS"},
  {"Field": "deploymentOption", "Value": "Single-AZ", "Type": "EQUALS"}
])
```

### 2. AWS Documentation Server (aws-docs)
**Purpose**: Access to official AWS documentation
**Server**: `awslabs.aws-documentation-mcp-server@latest`
**Status**: ✅ Configured

**Key Tools Available:**
- `search_documentation(search_phrase)` - Search AWS docs
- `read_documentation(url)` - Read specific AWS doc pages
- `recommend(url)` - Get related documentation recommendations

**Usage Trigger**: ALWAYS use when AWS-specific documentation, implementation guidance, or service information is needed

**Usage Patterns:**
```python
# Search for specific AWS service information
search_documentation("Lambda function URLs")

# Read specific documentation pages
read_documentation("https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html")

# Get related documentation
recommend("https://docs.aws.amazon.com/lambda/latest/dg/welcome.html")
```

### 3. Context7 Documentation Server (context7)
**Purpose**: Access to documentation for development frameworks and tools
**Server**: Context7 MCP server
**Status**: ✅ Configured

**Key Tools Available:**
- `mcp_context7_resolve_library_id(libraryName)` - Resolve library names to Context7 IDs
- `mcp_context7_get_library_docs(context7CompatibleLibraryID, topic, tokens)` - Get library documentation

**Usage Trigger**: ALWAYS use when documentation is needed for:
- **Next.js** - React framework documentation and examples
- **Strands Agents SDK** - AI agent development framework
- **Terraform** - Infrastructure as Code documentation
- Other development frameworks and libraries

**Usage Patterns:**
```python
# Get Next.js documentation
mcp_context7_resolve_library_id("Next.js")
mcp_context7_get_library_docs("/vercel/next.js", "routing", 5000)

# Get Strands Agents SDK documentation
mcp_context7_resolve_library_id("Strands Agents SDK")
mcp_context7_get_library_docs("/strands/agents", "tools", 8000)

# Get Terraform documentation
mcp_context7_resolve_library_id("Terraform")
mcp_context7_get_library_docs("/hashicorp/terraform", "aws-provider", 6000)
```

## 🎯 General MCP Usage Guidelines

### 1. Data Source Priority
1. **First Priority**: Use MCP servers for real-time, authoritative data
2. **Second Priority**: Use knowledge base only when MCP unavailable
3. **Always Indicate**: Mention data source and confidence level to users

### 2. Error Handling
- If MCP server unavailable, gracefully fall back to knowledge base
- Always mention when using fallback data vs. real-time MCP data
- Provide troubleshooting guidance for MCP connection issues
- Include confidence levels: "High" (MCP data) vs. "Medium" (knowledge base)

### 3. Performance Optimization
- Use specific filters to reduce response size and improve speed
- Batch queries when possible (e.g., multi-region comparisons)
- Cache results within conversation context
- Monitor response times and optimize accordingly

### 4. User Communication
**Always be transparent about data sources:**
- ✅ "Using real-time AWS pricing data via MCP server..."
- ✅ "Based on current AWS documentation (retrieved via MCP)..."
- ✅ "MCP server unavailable, using knowledge base (verify with AWS)..."
- ❌ Don't present knowledge base data as if it's real-time

## 🚨 Critical Usage Instructions

### For AWS Pricing Queries
- **ALWAYS** use aws-pricing MCP server when user asks for AWS pricing estimates
- Include comprehensive filter patterns for accurate results
- Provide both monthly and annual cost estimates
- Include optimization recommendations based on real pricing data
- Default to us-east-1 region when not specified

### For AWS Documentation Queries
- **ALWAYS** use aws-docs MCP server for AWS-specific documentation and implementation guidance
- Use specific technical terms in searches
- Read full documentation pages for comprehensive answers
- Provide direct links to official AWS documentation

### For Development Framework Documentation
- **ALWAYS** use context7 MCP server for:
  - **Next.js**: React framework, routing, API routes, deployment, etc.
  - **Strands Agents SDK**: AI agent development, tools, models, etc.
  - **Terraform**: Infrastructure as Code, providers, resources, etc.
- First resolve library ID, then get specific documentation
- Use topic parameter to focus on relevant sections
- Adjust tokens parameter based on complexity (5000-10000 typical)

### For Architecture and Cost Analysis
- **AWS Architecture**: Combine aws-pricing (for costs) + aws-docs (for implementation)
- **Development Architecture**: Combine context7 (for frameworks) + aws-docs (for AWS services)
- **Full Stack Solutions**: Use all three servers as appropriate for comprehensive guidance

## 🔧 Troubleshooting MCP Issues

### Common Issues and Solutions

**MCP Server Connection Failed:**
- Verify uvx/uv installation: `uvx --version`
- Check server status: `uvx awslabs.aws-pricing-mcp-server@latest`
- Fall back to knowledge base with clear disclaimer

**Invalid Filter Formats:**
- Use discovery tools first: `get_pricing_service_attributes()`
- Verify filter values: `get_pricing_attribute_values()`
- Follow exact filter patterns from this guide

**Slow Response Times:**
- Use more specific filters to reduce data volume
- Break complex queries into smaller parts
- Implement caching for repeated queries

## 📊 Success Metrics

### MCP Usage Quality Indicators
- **High Quality**: Real-time MCP data with proper attribution
- **Medium Quality**: Knowledge base with MCP unavailable disclaimer
- **Low Quality**: Knowledge base presented as current/real-time data

### Performance Targets
- Simple MCP queries: <5 seconds
- Complex MCP queries: <10 seconds
- Fallback responses: <3 seconds
- Cache hit responses: <1 second

## 🎯 MCP Server Selection Rules

### Quick Decision Matrix
| User Query Type | Primary MCP Server | Secondary Server | Fallback |
|-----------------|-------------------|------------------|----------|
| AWS pricing/costs | aws-pricing | aws-docs (for context) | Knowledge base |
| AWS implementation | aws-docs | aws-pricing (for costs) | Knowledge base |
| Next.js development | context7 | - | Knowledge base |
| Strands Agents SDK | context7 | - | Knowledge base |
| Terraform/IaC | context7 | aws-docs (for AWS resources) | Knowledge base |
| Full-stack AWS app | All three servers | - | Knowledge base |

### Selection Logic
1. **AWS Pricing**: If query mentions costs, pricing, estimates → aws-pricing
2. **AWS Services**: If query about AWS implementation, configuration → aws-docs  
3. **Development Frameworks**: If query about Next.js, Strands, Terraform → context7
4. **Complex Projects**: Use multiple servers for comprehensive answers

## 💡 Best Practices Summary

1. **Choose Right Server**: Use the decision matrix above for server selection
2. **Always Try MCP First**: Attempt appropriate MCP server before falling back
3. **Use Specific Filters**: Include relevant filters for accurate, fast results
4. **Be Transparent**: Always indicate data source and confidence level
5. **Combine When Appropriate**: Use multiple servers for comprehensive answers
6. **Handle Errors Gracefully**: Provide helpful troubleshooting when MCP fails
7. **Optimize Performance**: Use caching and efficient query patterns
8. **Stay Current**: MCP data is authoritative - prefer it over static knowledge

## 🔄 Continuous Improvement

### Regular Tasks
- Monitor MCP server health and performance
- Update filter patterns as AWS services evolve
- Refine error handling based on common failure modes
- Optimize query patterns based on usage analytics

This guide ensures consistent, high-quality use of MCP servers across all agent interactions in this workspace.