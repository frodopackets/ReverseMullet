#!/usr/bin/env python3
"""
Agent Registry System for Extensible Specialized Agents

This module provides a centralized registry for managing specialized agents,
enabling easy addition of new agents without modifying the router core.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Type, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentCapability:
    """Defines a capability that an agent can handle."""
    name: str
    description: str
    keywords: List[str]
    phrases: List[str]
    priority: int = 1  # Higher priority agents are preferred for overlapping capabilities
    confidence_threshold: float = 0.5  # Minimum confidence to route to this agent

@dataclass
class AgentMetadata:
    """Metadata for a registered agent."""
    name: str
    description: str
    version: str
    author: str
    capabilities: List[AgentCapability]
    model_config: Dict[str, Any]
    system_prompt_template: str
    tools_required: List[str] = None
    mcp_servers: List[str] = None
    dependencies: List[str] = None
    enabled: bool = True

class BaseSpecializedAgent(ABC):
    """Base class for all specialized agents."""
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the agent with optional configuration."""
        pass
    
    @abstractmethod
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query and return structured response."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Return list of capabilities this agent can handle."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> AgentMetadata:
        """Return agent metadata."""
        pass
    
    def validate_query(self, query: str) -> bool:
        """Validate if this agent can handle the query."""
        return True
    
    def get_confidence_score(self, query: str) -> float:
        """Calculate confidence score for handling this query."""
        capabilities = self.get_capabilities()
        query_lower = query.lower()
        
        max_score = 0.0
        for capability in capabilities:
            score = 0.0
            
            # Enhanced keyword matching with diminishing returns
            keyword_matches = sum(1 for keyword in capability.keywords if keyword in query_lower)
            if capability.keywords and keyword_matches > 0:
                # Use logarithmic scaling for multiple matches to prevent oversaturation
                # 1 match = 0.6, 2 matches = 0.75, 3+ matches = 0.85+
                keyword_ratio = min(keyword_matches / len(capability.keywords), 1.0)
                keyword_score = 0.4 + (keyword_ratio * 0.4)  # Base 0.4 + up to 0.4 more
                score += keyword_score
            
            # Enhanced phrase matching with higher weight
            phrase_matches = sum(1 for phrase in capability.phrases if phrase in query_lower)
            if capability.phrases and phrase_matches > 0:
                # Phrases are more specific, give them higher weight
                phrase_score = min(phrase_matches * 0.5, 0.9)  # Up to 0.9 for phrases
                score += phrase_score
            
            # Bonus for high-priority capabilities
            if score > 0:
                priority_bonus = (capability.priority - 5) * 0.05  # Small bonus for priority 6+
                score += max(priority_bonus, 0)
                
                # Apply priority weighting
                score *= (capability.priority / 10.0)
                
                # Enhanced minimum score for any relevant match
                if keyword_matches > 0 or phrase_matches > 0:
                    score = max(score, 0.6)  # Higher minimum for AWS pricing agent
            
            max_score = max(max_score, score)
        
        return min(max_score, 1.0)

class AgentRegistry:
    """Central registry for managing specialized agents."""
    
    def __init__(self):
        """Initialize the agent registry."""
        self.agents: Dict[str, Type[BaseSpecializedAgent]] = {}
        self.agent_metadata: Dict[str, AgentMetadata] = {}
        self.agent_instances: Dict[str, BaseSpecializedAgent] = {}
        self.configuration: Dict[str, Any] = {}
        
        # Load configuration
        self._load_configuration()
        
        # Register built-in agents
        self._register_builtin_agents()
    
    def _load_configuration(self):
        """Load agent registry configuration."""
        try:
            with open('src/agents/agent_config.json', 'r') as f:
                self.configuration = json.load(f)
        except FileNotFoundError:
            logger.info("No agent configuration file found, using defaults")
            self.configuration = {
                "default_model": {
                    "model_id": "amazon.nova-lite-v1:0",
                    "temperature": 0.3,
                    "max_tokens": 4000,
                    "top_p": 0.8
                },
                "agent_settings": {
                    "max_conversation_history": 10,
                    "enable_caching": True,
                    "cache_size": 10,
                    "timeout_seconds": 30
                }
            }
    
    def _register_builtin_agents(self):
        """Register built-in agents."""
        # Register AWS Pricing Agent
        try:
            from .aws_pricing_agent import AWSPricingAgent
            self.register_agent_class("aws_pricing", AWSPricingAgent)
            logger.info("Registered built-in AWS Pricing Agent")
        except ImportError as e:
            logger.warning(f"Could not register AWS Pricing Agent: {e}")
    
    def register_agent_class(self, agent_id: str, agent_class: Type[BaseSpecializedAgent]):
        """Register a new agent class."""
        if not issubclass(agent_class, BaseSpecializedAgent):
            raise ValueError(f"Agent class must inherit from BaseSpecializedAgent")
        
        self.agents[agent_id] = agent_class
        
        # Create temporary instance to get metadata
        try:
            temp_instance = agent_class()
            metadata = temp_instance.get_metadata()
            self.agent_metadata[agent_id] = metadata
            logger.info(f"Registered agent: {agent_id} - {metadata.description}")
        except Exception as e:
            logger.error(f"Failed to get metadata for agent {agent_id}: {e}")
    
    def register_agent_instance(self, agent_id: str, agent_instance: BaseSpecializedAgent):
        """Register a pre-configured agent instance."""
        if not isinstance(agent_instance, BaseSpecializedAgent):
            raise ValueError(f"Agent must inherit from BaseSpecializedAgent")
        
        self.agent_instances[agent_id] = agent_instance
        metadata = agent_instance.get_metadata()
        self.agent_metadata[agent_id] = metadata
        logger.info(f"Registered agent instance: {agent_id} - {metadata.description}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseSpecializedAgent]:
        """Get an agent instance by ID."""
        # Check if we have a pre-configured instance
        if agent_id in self.agent_instances:
            return self.agent_instances[agent_id]
        
        # Create new instance from class
        if agent_id in self.agents:
            try:
                agent_config = self.configuration.get("agent_settings", {})
                agent_instance = self.agents[agent_id](agent_config)
                self.agent_instances[agent_id] = agent_instance
                return agent_instance
            except Exception as e:
                logger.error(f"Failed to create agent instance {agent_id}: {e}")
                return None
        
        return None
    
    def find_best_agent(self, query: str, exclude_agents: List[str] = None) -> Optional[str]:
        """Find the best agent to handle a query based on capabilities and confidence."""
        exclude_agents = exclude_agents or []
        best_agent = None
        best_score = 0.0
        
        for agent_id, metadata in self.agent_metadata.items():
            if agent_id in exclude_agents or not metadata.enabled:
                continue
            
            agent = self.get_agent(agent_id)
            if not agent:
                continue
            
            try:
                confidence = agent.get_confidence_score(query)
                
                # Check if confidence meets threshold
                min_confidence = min(cap.confidence_threshold for cap in metadata.capabilities)
                if confidence < min_confidence:
                    continue
                
                # Weight by priority
                max_priority = max(cap.priority for cap in metadata.capabilities)
                weighted_score = confidence * (max_priority / 10.0)
                
                if weighted_score > best_score:
                    best_score = weighted_score
                    best_agent = agent_id
                    
            except Exception as e:
                logger.error(f"Error evaluating agent {agent_id}: {e}")
                continue
        
        if best_agent:
            logger.info(f"Selected agent {best_agent} with confidence {best_score:.2f}")
        
        return best_agent
    
    def get_available_agents(self) -> Dict[str, AgentMetadata]:
        """Get all available agents and their metadata."""
        return {aid: meta for aid, meta in self.agent_metadata.items() if meta.enabled}
    
    def get_agent_capabilities(self, agent_id: str) -> List[AgentCapability]:
        """Get capabilities for a specific agent."""
        if agent_id in self.agent_metadata:
            return self.agent_metadata[agent_id].capabilities
        return []
    
    def enable_agent(self, agent_id: str):
        """Enable an agent."""
        if agent_id in self.agent_metadata:
            self.agent_metadata[agent_id].enabled = True
            logger.info(f"Enabled agent: {agent_id}")
    
    def disable_agent(self, agent_id: str):
        """Disable an agent."""
        if agent_id in self.agent_metadata:
            self.agent_metadata[agent_id].enabled = False
            logger.info(f"Disabled agent: {agent_id}")
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered agents."""
        status = {}
        
        for agent_id, metadata in self.agent_metadata.items():
            agent_status = {
                "name": metadata.name,
                "description": metadata.description,
                "version": metadata.version,
                "enabled": metadata.enabled,
                "capabilities": len(metadata.capabilities),
                "instance_loaded": agent_id in self.agent_instances
            }
            
            # Check if agent can be instantiated
            if agent_id in self.agents and agent_id not in self.agent_instances:
                try:
                    test_instance = self.agents[agent_id]({})
                    agent_status["instantiable"] = True
                except Exception as e:
                    agent_status["instantiable"] = False
                    agent_status["error"] = str(e)
            else:
                agent_status["instantiable"] = True
            
            status[agent_id] = agent_status
        
        return status
    
    def reload_configuration(self):
        """Reload agent configuration from file."""
        self._load_configuration()
        logger.info("Reloaded agent registry configuration")
    
    def export_configuration(self, filepath: str):
        """Export current configuration to file."""
        config = {
            "agents": {},
            "configuration": self.configuration
        }
        
        for agent_id, metadata in self.agent_metadata.items():
            config["agents"][agent_id] = {
                "name": metadata.name,
                "description": metadata.description,
                "version": metadata.version,
                "author": metadata.author,
                "enabled": metadata.enabled,
                "capabilities": [
                    {
                        "name": cap.name,
                        "description": cap.description,
                        "keywords": cap.keywords,
                        "phrases": cap.phrases,
                        "priority": cap.priority,
                        "confidence_threshold": cap.confidence_threshold
                    }
                    for cap in metadata.capabilities
                ],
                "model_config": metadata.model_config,
                "tools_required": metadata.tools_required,
                "mcp_servers": metadata.mcp_servers,
                "dependencies": metadata.dependencies
            }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Exported agent configuration to {filepath}")

# Global registry instance
agent_registry = AgentRegistry()

def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    return agent_registry