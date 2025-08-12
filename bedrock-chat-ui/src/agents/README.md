# Extensible Agent System

## Overview

This directory contains a comprehensive, extensible agent system built on AI-first principles. The system enables easy creation, registration, and management of specialized agents that can handle domain-specific queries with intelligent routing and real-time data integration.

## Architecture

### Core Components

```
src/agents/
├── agent_registry.py          # Central registry for agent management
├── agent_factory.py           # Factory for creating agents from templates/config
├── agent_cli.py              # Command-line interface for agent management
├── router_agent.py           # Enhanced router with dynamic agent routing
├── aws_pricing_agent.py      # Example specialized agent (AWS pricing)
├── agent_config.json         # Agent configuration file
├── templates/
│   ├── ai_first_agent_template.py    # Template for AI-first agents
│   └── AI_FIRST_AGENT_GUIDE.md       # Comprehensive creation guide
└── examples/
    └── example_agent_config.json     # Example configuration file
```

### Key Features

- **AI-First Design**: Prioritizes intelligent reasoning over complex helper code
- **Dynamic Agent Registration**: Automatic discovery and routing of specialized agents
- **MCP Integration**: Real-time data access with graceful fallback
- **Performance Optimization**: Caching, metrics tracking, and response optimization
- **Extensible Architecture**: Easy addition of new agents without core modifications
- **Comprehensive Error Handling**: User-friendly error messages with troubleshooting
- **CLI Management**: Command-line tools for agent creation and management

## Quick Start

### 1. Using Existing Agents

The system comes with a pre-configured AWS Pricing Agent:

```python
from .agent_registry import get_agent_registry

registry = get_agent_registry()
agent = registry.get_agent('aws_pricing')
response = await agent.process_query("What's the cost of a t3.small EC2 instance?")
```

### 2. Creating a New Agent

#### Option A: Using the CLI (Recommended)

```bash
# Interactive creation
python -m src.agents.agent_cli create interactive

# Create predefined agents
python -m src.agents.agent_cli create predefined security
python -m src.agents.agent_cli create predefined performance
```

#### Option B: Using the Factory

```python
from .agent_factory import get_agent_factory

factory = get_agent_factory()
agent = factory.create_agent_from_template(
    agent_id='my_agent',
    name='My Specialized Agent',
    description='Agent for my specific domain',
    domain_knowledge='Comprehensive domain knowledge here...',
    capabilities=[
        {
            'name': 'domain_analysis',
            'description': 'Analyze domain-specific configurations',
            'keywords': ['analyze', 'review', 'assess'],
            'phrases': ['analyze my setup', 'review configuration'],
            'priority': 8,
            'confidence_threshold': 0.6
        }
    ]
)
```

#### Option C: From Configuration File

```python
factory = get_agent_factory()
success = factory.register_agent_from_file('path/to/agent_config.json')
```

### 3. Using the Router

The router automatically selects the best agent for each query:

```python
from .router_agent import RouterAgent

router = RouterAgent()
response = await router.process_query("Analyze my AWS security configuration")
# Automatically routes to security agent if available
```

## Agent Management

### CLI Commands

```bash
# List all agents
python -m src.agents.agent_cli list

# Show detailed status
python -m src.agents.agent_cli status

# Test an agent
python -m src.agents.agent_cli test aws_pricing "Cost of t3.small in us-east-1"

# Enable/disable agents
python -m src.agents.agent_cli enable my_agent
python -m src.agents.agent_cli disable my_agent

# Find best agent for a query
python -m src.agents.agent_cli find "optimize my database performance"

# Export configuration
python -m src.agents.agent_cli export agents_backup.json
```

### Programmatic Management

```python
from .agent_registry import get_agent_registry

registry = get_agent_registry()

# List available agents
agents = registry.get_available_agents()

# Find best agent for query
best_agent_id = registry.find_best_agent("security analysis query")

# Get agent status
status = registry.get_agent_status()

# Enable/disable agents
registry.enable_agent('agent_id')
registry.disable_agent('agent_id')
```

## Creating Specialized Agents

### AI-First Approach

The system follows an AI-first philosophy:

1. **Rich System Prompts**: Embed comprehensive domain knowledge in system prompts
2. **Minimal Helper Code**: Let AI handle complexity through reasoning
3. **Real-Time Data**: Use MCP servers for current, authoritative data
4. **Graceful Degradation**: Fallback to knowledge base when external services unavailable

### Template Structure

```python
from .templates.ai_first_agent_template import AIFirstAgentTemplate

class MySpecializedAgent(AIFirstAgentTemplate):
    def _get_system_prompt(self) -> str:
        return """You are a [Domain] Specialized Agent...
        
        ## Core Capabilities
        [Define what your agent does]
        
        ## MCP Tools Usage Instructions
        [Detailed MCP integration instructions]
        
        ## Domain Knowledge Context
        [Comprehensive domain knowledge]
        
        ## Response Format Guidelines
        [Structure for consistent responses]
        """
    
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="capability_name",
                description="What this capability does",
                keywords=["key", "words"],
                phrases=["specific phrases"],
                priority=8,
                confidence_threshold=0.6
            )
        ]
```

### System Prompt Best Practices

1. **Be Comprehensive**: Include extensive domain knowledge
2. **Be Specific**: Provide exact examples and patterns
3. **Be Structured**: Use clear sections and formatting
4. **Include Examples**: Show proper tool usage patterns
5. **Handle Errors**: Provide fallback instructions

See `templates/AI_FIRST_AGENT_GUIDE.md` for detailed guidance.

## MCP Integration

### Setting Up MCP Tools

```python
def _initialize_mcp_client(self) -> Optional[MCPClient]:
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

### MCP Tools in System Prompts

```markdown
## CRITICAL: MCP Tools Usage Instructions

### When MCP Tools Are Available
You have access to real-time data through MCP tools. ALWAYS use these tools instead of estimates.

### Key MCP Tools and Usage Patterns

#### 1. get_data(service, parameters)
Get real-time data:
```
get_data("service_name", {"param1": "value1", "param2": "value2"})
```

### Error Handling for MCP Tools
- If MCP tools fail, acknowledge failure and use knowledge base
- Always mention when using cached/estimated vs real-time data
- Provide troubleshooting guidance for connection issues
```

## Performance Optimization

### Caching Implementation

```python
# In agent __init__
self.query_cache = {}
self.performance_stats = {
    'total_queries': 0,
    'cache_hits': 0,
    'avg_response_time': 0
}

# In process_query
query_hash = hash(query.lower().strip())
if query_hash in self.query_cache:
    self.performance_stats['cache_hits'] += 1
    return self.query_cache[query_hash].copy()

# Cache successful responses (limit size)
if len(self.query_cache) < 10:
    self.query_cache[query_hash] = result.copy()
```

### Performance Monitoring

```python
start_time = time.time()
# ... process query
response_time = time.time() - start_time

self.performance_stats['avg_response_time'] = (
    (self.performance_stats['avg_response_time'] * (self.performance_stats['total_queries'] - 1) + response_time) 
    / self.performance_stats['total_queries']
)
```

## Configuration

### Agent Configuration Format

```json
{
  "agent_id": "unique_agent_id",
  "name": "Human Readable Name",
  "description": "What this agent does",
  "version": "1.0.0",
  "author": "Your Name",
  "type": "ai_first",
  "enabled": true,
  "system_prompt": "Comprehensive system prompt...",
  "capabilities": [
    {
      "name": "capability_name",
      "description": "What this capability does",
      "keywords": ["keyword1", "keyword2"],
      "phrases": ["phrase1", "phrase2"],
      "priority": 8,
      "confidence_threshold": 0.6
    }
  ],
  "model_config": {
    "model_id": "amazon.nova-lite-v1:0",
    "temperature": 0.3,
    "max_tokens": 4000,
    "top_p": 0.8
  },
  "agent_config": {
    "mcp_server_command": "uvx domain-mcp-server@latest",
    "enable_caching": true,
    "cache_size": 10
  },
  "tools_required": ["mcp_client"],
  "mcp_servers": ["domain-server"],
  "dependencies": ["strands", "mcp"]
}
```

### Global Configuration (agent_config.json)

```json
{
  "default_model": {
    "model_id": "amazon.nova-lite-v1:0",
    "temperature": 0.3,
    "max_tokens": 4000,
    "top_p": 0.8
  },
  "agent_settings": {
    "max_conversation_history": 10,
    "enable_caching": true,
    "cache_size": 10,
    "timeout_seconds": 30
  },
  "mcp_settings": {
    "timeout": 30,
    "max_retries": 3,
    "log_level": "ERROR"
  }
}
```

## Testing

### Unit Testing

```python
import pytest
from your_agent import YourAgent

@pytest.fixture
def agent():
    return YourAgent()

def test_capabilities(agent):
    capabilities = agent.get_capabilities()
    assert len(capabilities) > 0

def test_confidence_scoring(agent):
    high_score = agent.get_confidence_score("relevant query")
    low_score = agent.get_confidence_score("irrelevant query")
    assert high_score > low_score

async def test_query_processing(agent):
    response = await agent.process_query("test query")
    assert response['status'] == 'success'
```

### Integration Testing

```python
async def test_router_integration():
    from .router_agent import RouterAgent
    
    router = RouterAgent()
    response = await router.process_query("domain-specific query")
    
    # Should route to appropriate specialized agent
    assert 'specialized' in response.get('intent_analysis', {}).get('intent', '')
```

## Examples

### Security Agent

```python
class SecurityAgent(AIFirstAgentTemplate):
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="security_analysis",
                description="Analyze security configurations",
                keywords=["security", "vulnerability", "risk"],
                phrases=["security analysis", "check security"],
                priority=9,
                confidence_threshold=0.7
            )
        ]
```

### Performance Agent

```python
class PerformanceAgent(AIFirstAgentTemplate):
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="performance_analysis",
                description="Analyze performance metrics",
                keywords=["performance", "latency", "optimization"],
                phrases=["performance analysis", "optimize performance"],
                priority=8,
                confidence_threshold=0.6
            )
        ]
```

## Best Practices

### 1. System Prompt Design
- Include comprehensive domain knowledge
- Provide specific examples and patterns
- Structure with clear sections
- Handle error scenarios

### 2. Capability Definition
- Use specific, relevant keywords
- Set appropriate priority levels
- Define reasonable confidence thresholds
- Provide clear descriptions

### 3. MCP Integration
- Test connections thoroughly
- Implement graceful fallbacks
- Optimize query parameters
- Monitor performance

### 4. Error Handling
- Provide user-friendly messages
- Include troubleshooting guidance
- Implement fallback strategies
- Log errors for debugging

### 5. Performance
- Implement caching
- Track metrics
- Optimize prompts
- Use async processing

## Troubleshooting

### Common Issues

1. **Agent Not Found**
   - Check agent registration
   - Verify agent_config.json
   - Ensure agent is enabled

2. **MCP Connection Failures**
   - Verify MCP server installation
   - Check network connectivity
   - Review environment variables

3. **Low Confidence Scores**
   - Review capability keywords/phrases
   - Adjust confidence thresholds
   - Improve system prompt specificity

4. **Performance Issues**
   - Enable caching
   - Optimize system prompts
   - Monitor response times
   - Use specific MCP queries

### Debug Commands

```bash
# Check agent status
python -m src.agents.agent_cli status

# Test specific agent
python -m src.agents.agent_cli test agent_id "test query"

# Find routing for query
python -m src.agents.agent_cli find "your query here"
```

## Contributing

### Adding New Agents

1. Create agent class using template
2. Define capabilities clearly
3. Write comprehensive system prompt
4. Implement MCP integration if needed
5. Add tests
6. Register in agent_config.json
7. Update documentation

### Extending the System

1. Follow AI-first principles
2. Maintain backward compatibility
3. Add comprehensive tests
4. Update CLI tools
5. Document new features

## Future Enhancements

- Multi-agent collaboration
- Dynamic capability adjustment
- Learning from interactions
- Advanced routing strategies
- Performance analytics dashboard
- Agent marketplace/sharing

## Support

For questions, issues, or contributions:

1. Check existing documentation
2. Review examples and templates
3. Use CLI tools for debugging
4. Create detailed issue reports
5. Follow contribution guidelines

This extensible agent system provides a solid foundation for building intelligent, specialized agents that can grow and adapt to new requirements while maintaining high performance and user experience.