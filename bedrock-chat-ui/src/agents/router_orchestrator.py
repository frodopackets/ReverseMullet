#!/usr/bin/env python3
"""
Router Orchestrator - Manages agent coordination and conversation context

This module handles the orchestration of different agents, manages conversation
context across agent invocations, and implements fallback strategies.
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationContext:
    """Manages conversation context across different agent invocations."""
    
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.current_architecture: Optional[Dict[str, Any]] = None
        self.last_agent_used: Optional[str] = None
        self.session_metadata: Dict[str, Any] = {}
        self.context_summary: Optional[str] = None
        
    def add_message(self, message: Dict[str, Any]):
        """Add a message to the conversation context."""
        self.messages.append({
            **message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 messages to manage memory
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]
    
    def update_architecture(self, architecture_data: Dict[str, Any]):
        """Update the current architecture being discussed."""
        self.current_architecture = architecture_data
        self.session_metadata['last_architecture_update'] = datetime.now().isoformat()
    
    def get_relevant_context(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """Get relevant context for the current conversation."""
        return self.messages[-max_messages:] if self.messages else []
    
    def get_context_summary(self) -> str:
        """Generate a summary of the current conversation context."""
        if not self.messages:
            return "No previous conversation context."
        
        recent_messages = self.get_relevant_context(5)
        
        # Extract key information
        topics = []
        if self.current_architecture:
            services = self.current_architecture.get('identified_services', {})
            if services:
                topics.append(f"Architecture with services: {', '.join(services.keys())}")
        
        if self.last_agent_used:
            topics.append(f"Last agent used: {self.last_agent_used}")
        
        user_queries = [msg['content'][:100] for msg in recent_messages if msg.get('role') == 'user']
        if user_queries:
            topics.append(f"Recent topics: {'; '.join(user_queries[-2:])}")
        
        return "; ".join(topics) if topics else "General conversation in progress."


class RouterOrchestrator:
    """
    Orchestrates routing between different agents and manages conversation context.
    Implements fallback strategies and agent coordination logic.
    """
    
    def __init__(self):
        """Initialize the Router Orchestrator."""
        self.conversation_context = ConversationContext()
        self.router_agent = None
        self.specialized_agents = {}
        self.fallback_strategies = {
            'uncertain_intent': self._handle_uncertain_intent,
            'agent_failure': self._handle_agent_failure,
            'context_overflow': self._handle_context_overflow
        }
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize router and specialized agents."""
        try:
            # Import and initialize Router Agent
            from .router_agent import RouterAgent
            self.router_agent = RouterAgent()
            logger.info("Router Agent initialized successfully")
            
            # Register specialized agents
            self.specialized_agents['aws_pricing'] = 'aws_pricing_agent_tool'
            logger.info("Specialized agents registered")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    async def process_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user query through the router orchestration system.
        
        Args:
            query: User query to process
            user_id: Optional user identifier for context management
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Add user message to context
            user_message = {
                'role': 'user',
                'content': query,
                'user_id': user_id
            }
            self.conversation_context.add_message(user_message)
            
            # Get conversation context for the router
            context_summary = self.conversation_context.get_context_summary()
            
            # Enhance query with context if available
            enhanced_query = self._enhance_query_with_context(query, context_summary)
            
            # Process through router agent
            response = await self._route_query(enhanced_query)
            
            # Add assistant response to context
            assistant_message = {
                'role': 'assistant',
                'content': response['content'],
                'agent_type': response.get('agent_type', 'router'),
                'intent_analysis': response.get('intent_analysis', {})
            }
            self.conversation_context.add_message(assistant_message)
            
            # Update context based on response
            await self._update_context_from_response(response)
            
            # Add orchestration metadata
            response['orchestration_metadata'] = {
                'context_messages_count': len(self.conversation_context.messages),
                'current_architecture_available': self.conversation_context.current_architecture is not None,
                'last_agent_used': self.conversation_context.last_agent_used,
                'context_summary': context_summary
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error in router orchestration: {str(e)}")
            return await self._handle_orchestration_error(query, str(e))
    
    def _enhance_query_with_context(self, query: str, context_summary: str) -> str:
        """Enhance query with relevant conversation context."""
        if not context_summary or context_summary == "No previous conversation context.":
            return query
        
        # Add context prefix for the router to understand conversation flow
        enhanced_query = f"""[CONTEXT: {context_summary}]

User Query: {query}"""
        
        return enhanced_query
    
    async def _route_query(self, query: str) -> Dict[str, Any]:
        """Route query through the router agent with fallback handling."""
        try:
            # Get conversation history for context
            conversation_history = self.conversation_context.get_relevant_context()
            
            # Process query through router agent
            response = await self.router_agent.process_query(query, conversation_history)
            
            # Update last agent used
            intent_analysis = response.get('intent_analysis', {})
            if intent_analysis.get('intent') == 'aws_pricing':
                self.conversation_context.last_agent_used = 'aws_pricing_agent'
            else:
                self.conversation_context.last_agent_used = 'router_agent'
            
            # Handle uncertain intent with fallback strategy
            if intent_analysis.get('confidence') == 'low':
                logger.info("Uncertain intent detected, applying fallback strategy")
                return await self.fallback_strategies['uncertain_intent'](query, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error routing query: {str(e)}")
            return await self.fallback_strategies['agent_failure'](query, str(e))
    
    async def _update_context_from_response(self, response: Dict[str, Any]):
        """Update conversation context based on agent response."""
        try:
            # Check if response contains architecture information
            content = response.get('content', '')
            
            # Look for architecture analysis in the response
            if 'identified_services' in content or 'architecture' in content.lower():
                # Try to extract architecture information
                try:
                    # This would be enhanced to parse actual architecture data from responses
                    # For now, we'll update metadata
                    self.conversation_context.session_metadata['contains_architecture'] = True
                    self.conversation_context.session_metadata['last_architecture_mention'] = datetime.now().isoformat()
                except Exception as e:
                    logger.debug(f"Could not extract architecture data: {str(e)}")
            
            # Update context summary periodically
            if len(self.conversation_context.messages) % 5 == 0:
                self.conversation_context.context_summary = self.conversation_context.get_context_summary()
                
        except Exception as e:
            logger.debug(f"Error updating context from response: {str(e)}")
    
    async def _handle_uncertain_intent(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Handle uncertain intent classification with fallback strategy."""
        try:
            # Analyze query for AWS-related keywords as secondary check
            aws_keywords = ['aws', 'amazon', 'ec2', 'rds', 's3', 'lambda', 'cost', 'price', 'pricing']
            query_lower = query.lower()
            
            has_aws_keywords = any(keyword in query_lower for keyword in aws_keywords)
            
            if has_aws_keywords:
                # Bias towards AWS pricing agent for AWS-related queries
                logger.info("Uncertain intent but AWS keywords detected, routing to pricing agent")
                # Don't add any note - just route to the appropriate agent
                response['intent_analysis']['fallback_suggestion'] = 'aws_pricing'
            else:
                # Provide general assistance without adding notes
                response['intent_analysis']['fallback_suggestion'] = 'clarification_needed'
            
            response['intent_analysis']['fallback_applied'] = True
            return response
            
        except Exception as e:
            logger.error(f"Error in uncertain intent fallback: {str(e)}")
            return response
    
    async def _handle_agent_failure(self, query: str, error: str) -> Dict[str, Any]:
        """Handle agent failure with graceful degradation."""
        try:
            # Provide helpful error response with troubleshooting
            error_response = {
                'content': f"""I encountered an issue while processing your request. Here's what happened:

**Error**: {error}

**What you can try**:
- Rephrase your question with more specific details
- If asking about AWS costs, mention specific services (EC2, RDS, S3, etc.)
- Try breaking complex questions into smaller parts
- Check if you're asking about supported AWS services

**I'm still here to help!** Please try again with a different approach.""",
                'agent_type': 'orchestrator_fallback',
                'intent_analysis': {
                    'intent': 'error_fallback',
                    'confidence': 'high',
                    'error_handled': True
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return error_response
            
        except Exception as e:
            logger.error(f"Error in agent failure fallback: {str(e)}")
            return {
                'content': 'I apologize, but I encountered multiple errors while processing your request. Please try again.',
                'agent_type': 'orchestrator_fallback',
                'intent_analysis': {'intent': 'critical_error', 'confidence': 'high'},
                'timestamp': datetime.now().isoformat()
            }
    
    async def _handle_context_overflow(self, query: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle context overflow by summarizing and truncating."""
        try:
            # Summarize older context and keep recent messages
            self.conversation_context.messages = self.conversation_context.messages[-10:]
            
            # Create context summary
            summary = self.conversation_context.get_context_summary()
            self.conversation_context.context_summary = summary
            
            logger.info("Context overflow handled, conversation history summarized")
            
            # Continue with normal processing
            return await self._route_query(query)
            
        except Exception as e:
            logger.error(f"Error handling context overflow: {str(e)}")
            return await self._handle_agent_failure(query, f"Context overflow error: {str(e)}")
    
    async def _handle_orchestration_error(self, query: str, error: str) -> Dict[str, Any]:
        """Handle orchestration-level errors."""
        return {
            'content': f"""I encountered an orchestration error while processing your request.

**Error**: {error}

This appears to be a system-level issue. Please try again, and if the problem persists, the system may need attention.

**You can still try**:
- Asking simpler questions
- Being more specific about what you need
- Trying again in a few moments""",
            'agent_type': 'orchestrator_error',
            'intent_analysis': {
                'intent': 'orchestration_error',
                'confidence': 'high',
                'error_type': 'orchestration_failure'
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status and health."""
        return {
            'router_agent_available': self.router_agent is not None,
            'specialized_agents_count': len(self.specialized_agents),
            'conversation_messages_count': len(self.conversation_context.messages),
            'current_architecture_available': self.conversation_context.current_architecture is not None,
            'last_agent_used': self.conversation_context.last_agent_used,
            'session_metadata': self.conversation_context.session_metadata,
            'fallback_strategies_available': list(self.fallback_strategies.keys())
        }
    
    def reset_conversation_context(self):
        """Reset conversation context for new session."""
        self.conversation_context = ConversationContext()
        logger.info("Conversation context reset")


# Test function for the orchestrator
async def test_router_orchestrator():
    """Test the router orchestrator with sample queries."""
    orchestrator = RouterOrchestrator()
    
    test_queries = [
        "How much does an EC2 t3.medium instance cost?",
        "What's the difference between ECS and EKS?",
        "I need a cost estimate for a web application with EC2, RDS, and S3",
        "Help me optimize costs for my current architecture",
        "This is a very ambiguous query that might be hard to classify"
    ]
    
    print("=== Router Orchestrator Test ===")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i} ---")
        print(f"Query: {query}")
        
        try:
            response = await orchestrator.process_query(query, user_id="test_user")
            print(f"Agent Type: {response.get('agent_type', 'unknown')}")
            print(f"Intent: {response.get('intent_analysis', {}).get('intent', 'unknown')}")
            print(f"Response: {response.get('content', 'No content')[:200]}...")
            
            if response.get('orchestration_metadata'):
                metadata = response['orchestration_metadata']
                print(f"Context Messages: {metadata.get('context_messages_count', 0)}")
                print(f"Last Agent: {metadata.get('last_agent_used', 'none')}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Test orchestration status
    print(f"\n--- Orchestration Status ---")
    status = orchestrator.get_orchestration_status()
    for key, value in status.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(test_router_orchestrator())