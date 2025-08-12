#!/usr/bin/env python3
"""
Agent Factory for Easy Creation of Specialized Agents

This module provides utilities for quickly creating and registering new specialized agents
using templates and configuration-driven approaches.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Type
from .agent_registry import BaseSpecializedAgent, AgentCapability, AgentMetadata, get_agent_registry
from .templates.ai_first_agent_template import AIFirstAgentTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory for creating and registering specialized agents."""
    
    def __init__(self):
        """Initialize the agent factory."""
        self.agent_registry = get_agent_registry()
        self.templates = {
            'ai_first': AIFirstAgentTemplate
        }
    
    def create_agent_from_config(self, config: Dict[str, Any]) -> Optional[BaseSpecializedAgent]:
        """
        Create an agent from configuration dictionary.
        
        Args:
            config: Agent configuration dictionary
            
        Returns:
            Created agent instance or None if creation failed
        """
        try:
            agent_type = config.get('type', 'ai_first')
            template_class = self.templates.get(agent_type, AIFirstAgentTemplate)
            
            # Create dynamic agent class
            agent_class = self._create_dynamic_agent_class(config, template_class)
            
            # Create instance
            agent_instance = agent_class(config.get('agent_config', {}))
            
            logger.info(f"Created agent from config: {config.get('name', 'Unknown')}")
            return agent_instance
            
        except Exception as e:
            logger.error(f"Failed to create agent from config: {e}")
            return None
    
    def _create_dynamic_agent_class(self, config: Dict[str, Any], template_class: Type[BaseSpecializedAgent]) -> Type[BaseSpecializedAgent]:
        """Create a dynamic agent class from configuration."""
        
        class DynamicAgent(template_class):
            def __init__(self, agent_config: Dict[str, Any] = None):
                self._config = config
                super().__init__(agent_config)
            
            def _get_system_prompt(self) -> str:
                """Get system prompt from configuration."""
                return config.get('system_prompt', super()._get_system_prompt())
            
            def get_capabilities(self) -> List[AgentCapability]:
                """Get capabilities from configuration."""
                capabilities = []
                for cap_config in config.get('capabilities', []):
                    capability = AgentCapability(
                        name=cap_config['name'],
                        description=cap_config['description'],
                        keywords=cap_config.get('keywords', []),
                        phrases=cap_config.get('phrases', []),
                        priority=cap_config.get('priority', 5),
                        confidence_threshold=cap_config.get('confidence_threshold', 0.5)
                    )
                    capabilities.append(capability)
                return capabilities
            
            def get_metadata(self) -> AgentMetadata:
                """Get metadata from configuration."""
                return AgentMetadata(
                    name=config.get('name', 'Dynamic Agent'),
                    description=config.get('description', 'Dynamically created agent'),
                    version=config.get('version', '1.0.0'),
                    author=config.get('author', 'Agent Factory'),
                    capabilities=self.get_capabilities(),
                    model_config=config.get('model_config', {}),
                    system_prompt_template=config.get('system_prompt', ''),
                    tools_required=config.get('tools_required', []),
                    mcp_servers=config.get('mcp_servers', []),
                    dependencies=config.get('dependencies', []),
                    enabled=config.get('enabled', True)
                )
        
        # Set dynamic class name
        DynamicAgent.__name__ = config.get('class_name', 'DynamicAgent')
        DynamicAgent.__qualname__ = DynamicAgent.__name__
        
        return DynamicAgent
    
    def create_agent_from_template(self, 
                                 agent_id: str,
                                 name: str,
                                 description: str,
                                 domain_knowledge: str,
                                 capabilities: List[Dict[str, Any]],
                                 mcp_server: Optional[str] = None,
                                 template_type: str = 'ai_first') -> Optional[BaseSpecializedAgent]:
        """
        Create an agent from template with provided parameters.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name
            description: Agent description
            domain_knowledge: Domain-specific knowledge for system prompt
            capabilities: List of capability configurations
            mcp_server: Optional MCP server command
            template_type: Template type to use
            
        Returns:
            Created agent instance or None if creation failed
        """
        config = {
            'name': name,
            'description': description,
            'type': template_type,
            'system_prompt': self._generate_system_prompt(name, description, domain_knowledge, mcp_server),
            'capabilities': capabilities,
            'mcp_servers': [mcp_server] if mcp_server else [],
            'model_config': {
                'model_id': 'amazon.nova-lite-v1:0',
                'temperature': 0.3,
                'max_tokens': 4000,
                'top_p': 0.8
            },
            'enabled': True
        }
        
        agent = self.create_agent_from_config(config)
        if agent:
            # Register the agent
            self.agent_registry.register_agent_instance(agent_id, agent)
            logger.info(f"Created and registered agent: {agent_id}")
        
        return agent
    
    def _generate_system_prompt(self, name: str, description: str, domain_knowledge: str, mcp_server: Optional[str]) -> str:
        """Generate a system prompt from template."""
        mcp_section = ""
        if mcp_server:
            mcp_section = f"""
## CRITICAL: MCP Tools Usage Instructions

### When MCP Tools Are Available
You have access to real-time {name.lower()} data through MCP tools. ALWAYS use these tools to get current information instead of relying on estimates.

### MCP Server Integration
Connected to: {mcp_server}

### Error Handling for MCP Tools
- If MCP tools fail, acknowledge the failure and use knowledge base
- Always mention when using cached/estimated vs real-time data
- Provide troubleshooting guidance for connection issues
"""
        
        return f"""You are a {name} with comprehensive knowledge and real-time data access.

## Core Capabilities
{description}

{mcp_section}

## Domain Knowledge Context
{domain_knowledge}

## Response Format Guidelines
Structure your responses with:
1. **Analysis**: What you identify and assess
2. **Real-Time Data**: Use MCP tools when available for current information
3. **Recommendations**: Prioritized recommendations with specific guidance
4. **Implementation Guidance**: Next steps and considerations

## Important Instructions
- Be specific about whether you're using real-time data or estimates
- Ask clarifying questions only for essential missing details
- Provide actionable, prioritized recommendations
- Include confidence levels for your analysis
- Reference previous discussions when handling follow-up queries

Be concise but comprehensive. Focus on actionable insights that help users make informed decisions."""
    
    def register_agent_from_file(self, config_file: str) -> bool:
        """
        Register an agent from a configuration file.
        
        Args:
            config_file: Path to agent configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            agent_id = config.get('agent_id')
            if not agent_id:
                logger.error("Agent configuration missing 'agent_id'")
                return False
            
            agent = self.create_agent_from_config(config)
            if agent:
                self.agent_registry.register_agent_instance(agent_id, agent)
                logger.info(f"Registered agent from file: {config_file}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to register agent from file {config_file}: {e}")
            return False
    
    def create_security_agent(self) -> Optional[BaseSpecializedAgent]:
        """Create a pre-configured security agent."""
        return self.create_agent_from_template(
            agent_id='aws_security',
            name='AWS Security Agent',
            description='Specialized agent for AWS security analysis and compliance checking',
            domain_knowledge="""
### AWS Security Best Practices
- **IAM Security**: Principle of least privilege, role-based access, MFA enforcement
- **Network Security**: VPC security groups, NACLs, VPC flow logs, private subnets
- **Data Protection**: Encryption at rest/transit, S3 bucket policies, KMS key management
- **Monitoring**: CloudTrail, GuardDuty, Security Hub, Config rules
- **Compliance**: CIS benchmarks, NIST frameworks, PCI DSS, SOC 2

### Common Security Issues
- Overly permissive IAM policies
- Public S3 buckets with sensitive data
- Security groups with 0.0.0.0/0 access
- Unencrypted data stores
- Missing security monitoring

### Security Assessment Framework
1. **Identity and Access Management**: Review IAM policies, roles, and permissions
2. **Network Security**: Analyze VPC configuration and network controls
3. **Data Protection**: Check encryption and access controls
4. **Monitoring and Logging**: Verify security monitoring setup
5. **Compliance**: Assess against relevant standards
            """,
            capabilities=[
                {
                    'name': 'security_analysis',
                    'description': 'Analyze AWS security configurations and identify vulnerabilities',
                    'keywords': ['security', 'vulnerability', 'risk', 'threat', 'compliance', 'audit'],
                    'phrases': ['security analysis', 'check security', 'security review', 'vulnerability assessment'],
                    'priority': 9,
                    'confidence_threshold': 0.7
                },
                {
                    'name': 'iam_analysis',
                    'description': 'Analyze IAM policies and permissions',
                    'keywords': ['iam', 'permissions', 'policy', 'role', 'access', 'authentication'],
                    'phrases': ['iam policy', 'permissions review', 'access control', 'role analysis'],
                    'priority': 8,
                    'confidence_threshold': 0.6
                },
                {
                    'name': 'compliance_check',
                    'description': 'Check compliance against security standards',
                    'keywords': ['compliance', 'standards', 'audit', 'regulation', 'cis', 'nist', 'pci'],
                    'phrases': ['compliance check', 'audit requirements', 'security standards'],
                    'priority': 7,
                    'confidence_threshold': 0.5
                }
            ]
        )
    
    def create_performance_agent(self) -> Optional[BaseSpecializedAgent]:
        """Create a pre-configured performance agent."""
        return self.create_agent_from_template(
            agent_id='aws_performance',
            name='AWS Performance Agent',
            description='Specialized agent for AWS performance optimization and monitoring',
            domain_knowledge="""
### AWS Performance Optimization
- **EC2 Performance**: Instance types, CPU/memory optimization, placement groups
- **Database Performance**: RDS tuning, connection pooling, read replicas
- **Storage Performance**: EBS optimization, S3 performance patterns
- **Network Performance**: Latency optimization, CDN usage, VPC design
- **Application Performance**: Auto Scaling, Load Balancing, caching strategies

### Performance Monitoring
- **CloudWatch Metrics**: CPU, memory, disk, network utilization
- **Application Insights**: X-Ray tracing, custom metrics
- **Database Monitoring**: Performance Insights, slow query analysis
- **Network Monitoring**: VPC Flow Logs, latency measurements

### Optimization Strategies
1. **Right-sizing**: Match resources to actual workload requirements
2. **Caching**: Implement appropriate caching layers (ElastiCache, CloudFront)
3. **Auto Scaling**: Scale resources based on demand patterns
4. **Load Distribution**: Use load balancers and multiple AZs
5. **Database Optimization**: Query optimization, indexing, connection pooling
            """,
            capabilities=[
                {
                    'name': 'performance_analysis',
                    'description': 'Analyze AWS performance metrics and identify bottlenecks',
                    'keywords': ['performance', 'latency', 'throughput', 'bottleneck', 'optimization'],
                    'phrases': ['performance analysis', 'optimize performance', 'slow response', 'bottleneck analysis'],
                    'priority': 8,
                    'confidence_threshold': 0.6
                },
                {
                    'name': 'monitoring_setup',
                    'description': 'Set up performance monitoring and alerting',
                    'keywords': ['monitoring', 'metrics', 'alerts', 'cloudwatch', 'dashboard'],
                    'phrases': ['set up monitoring', 'performance metrics', 'create alerts'],
                    'priority': 7,
                    'confidence_threshold': 0.5
                },
                {
                    'name': 'scaling_optimization',
                    'description': 'Optimize auto scaling and load balancing',
                    'keywords': ['scaling', 'auto scaling', 'load balancer', 'capacity', 'elasticity'],
                    'phrases': ['auto scaling', 'load balancing', 'scale up', 'scale down'],
                    'priority': 6,
                    'confidence_threshold': 0.4
                }
            ]
        )
    
    def list_available_templates(self) -> Dict[str, str]:
        """List available agent templates."""
        return {
            'ai_first': 'AI-first template with comprehensive system prompts and MCP integration'
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents managed by the factory."""
        return self.agent_registry.get_agent_status()

# Global factory instance
agent_factory = AgentFactory()

def get_agent_factory() -> AgentFactory:
    """Get the global agent factory instance."""
    return agent_factory