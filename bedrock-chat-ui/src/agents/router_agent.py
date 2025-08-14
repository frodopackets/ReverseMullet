#!/usr/bin/env python3
"""
Enhanced Router Agent with Extensible Agent Registry

This agent analyzes user queries and routes them to appropriate specialized agents
using the agent registry system for extensible agent management.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from strands import Agent, tool
from .agent_registry import get_agent_registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouterAgent:
    """
    Router Agent that analyzes user intent and routes to appropriate specialized agents.
    Uses Amazon Nova Lite model for intent analysis and general responses.
    """
    
    def __init__(self):
        """Initialize the Enhanced Router Agent with agent registry integration."""
        from strands.models import BedrockModel
        
        # Create BedrockModel with Nova Lite configuration
        bedrock_model = BedrockModel(
            model_id="amazon.nova-lite-v1:0",
            temperature=0.3,
            max_tokens=4000,
            top_p=0.8
        )
        
        # Initialize conversation context for sharing with specialized agents
        self.conversation_history = []
        self.max_history_length = 10
        
        # Get agent registry for dynamic agent management
        self.agent_registry = get_agent_registry()
        
        # Initialize the agent with enhanced system prompt and dynamic tools
        self.agent = Agent(
            model=bedrock_model,
            system_prompt=self._get_enhanced_system_prompt(),
            tools=self._get_dynamic_tools()
        )
    
    def _get_enhanced_system_prompt(self) -> str:
        """Get the enhanced system prompt for the Router Agent with dynamic agent awareness."""
        available_agents = self.agent_registry.get_available_agents()
        
        agent_descriptions = []
        for agent_id, metadata in available_agents.items():
            capabilities = [cap.name for cap in metadata.capabilities]
            agent_descriptions.append(f"- {metadata.name}: {metadata.description} (Capabilities: {', '.join(capabilities)})")
        
        agents_info = "\n".join(agent_descriptions) if agent_descriptions else "- AWS Pricing Agent: Cost analysis and pricing optimization"
        
        return f"""You are an Enhanced Router Agent that analyzes user queries and routes them to the most appropriate specialized agent.

<thinking>
Remember to put ALL your analysis logic inside thinking tags like this!
</thinking>

Your primary responsibilities:
1. Analyze user intent to determine which specialized agent can best handle their query
2. Route queries to appropriate specialized agents using dynamic tools
3. Handle general queries directly when no specialized agent is suitable
4. Maintain conversation context across different agent interactions

## IMPORTANT: Response Formatting
- **ALWAYS use Markdown formatting** for all responses
- Use headers (##, ###) to organize information
- Use **bold** for emphasis and important points
- Use bullet points (- or *) for lists
- Use code blocks with ``` for technical content
- Use tables when presenting comparative data
- Format your responses for optimal readability

## CRITICAL: Thinking Tags Usage
- **ALWAYS wrap your analysis logic in <thinking> tags**
- The thinking section should include:
  - Analysis of user query
  - Intent classification
  - Agent selection reasoning
  - Any routing decisions
- **NEVER include routing logic in the main response**
- The main response should ONLY contain the specialized agent's response or your direct answer

## Available Specialized Agents:
{agents_info}

## Intent Classification Guidelines:
Use the agent registry to dynamically determine the best agent for each query based on:
- Agent capabilities and confidence scores
- Keyword and phrase matching
- Agent priority levels
- Query complexity and requirements

## Routing Strategy:
<thinking>
1. **Analyze Query**: Identify key topics, keywords, and intent
2. **Find Best Agent**: Use agent registry to find the highest-confidence match
3. **Route or Handle**: Either route to specialized agent or handle directly
4. **Context Management**: Share relevant conversation context with specialized agents
</thinking>

When routing, follow this pattern:
1. Put ALL analysis in <thinking> tags
2. Route to the appropriate agent
3. Return ONLY the specialized agent's response
4. Do NOT include your routing explanation in the visible response

## Fallback Strategy:
- If no specialized agent has sufficient confidence, handle the query directly
- For uncertain classifications, provide helpful general responses
- Always maintain a professional and helpful tone

## Agent Tool Usage:
- Use specialized agent tools when confidence threshold is met
- Include conversation context when routing to specialized agents
- Handle agent errors gracefully with user-friendly messages

## OUTPUT RULES:
1. **ALWAYS start with <thinking>** for your analysis
2. **NEVER show routing logic** in the visible response
3. When using a tool, **ONLY return the tool's output**
4. Do NOT add preambles like "I'll route this to..." or "Let me analyze..."
5. The user should ONLY see the final answer, not your decision process

Always be helpful, accurate, and leverage the most appropriate specialized knowledge available."""

    def _get_dynamic_tools(self):
        """Get dynamic tools based on available agents in the registry."""
        tools = []
        
        # Add tools for each available agent
        available_agents = self.agent_registry.get_available_agents()
        for agent_id, metadata in available_agents.items():
            if metadata.enabled:
                # Create a tool for this agent
                tool_func = self._create_agent_tool(agent_id, metadata)
                tools.append(tool_func)
        
        return tools
    
    def _create_agent_tool(self, agent_id: str, metadata):
        """Create a tool function for a specific agent."""
        @tool
        async def specialized_agent_tool(query: str) -> str:
            f"""
            Route query to {metadata.name} for specialized analysis.
            
            Args:
                query: User query related to {metadata.description.lower()}
                
            Returns:
                Specialized analysis and recommendations from {metadata.name}
            """
            return await self._route_to_agent(agent_id, query)
        
        # Set the tool name dynamically
        specialized_agent_tool.__name__ = f"{agent_id}_agent_tool"
        specialized_agent_tool.__doc__ = f"""
        Route query to {metadata.name} for specialized analysis.
        
        Use this tool when the user query relates to: {', '.join([cap.name for cap in metadata.capabilities])}
        
        Args:
            query: User query related to {metadata.description.lower()}
            
        Returns:
            Specialized analysis and recommendations from {metadata.name}
        """
        
        return specialized_agent_tool
    
    async def _route_to_agent(self, agent_id: str, query: str) -> str:
        """Route a query to a specific specialized agent."""
        try:
            logger.info(f"Routing query to {agent_id}: {query[:100]}...")
            
            # Get the agent from registry
            agent = self.agent_registry.get_agent(agent_id)
            if not agent:
                return f"The {agent_id} agent is not available. Please try your query again or rephrase it for general assistance."
            
            # Prepare context for the specialized agent
            context = {
                'conversation_history': self.conversation_history[-3:],  # Share last 3 exchanges
                'router_context': True,
                'timestamp': time.time()
            }
            
            # Process the query with the specialized agent
            response = await agent.process_query(query, context)
            
            # Handle different response statuses
            if response.get('status') == 'success':
                response_content = str(response.get('response', 'No response content available'))
                
                # Add metadata about data source and confidence
                confidence = response.get('confidence', 'medium')
                mcp_available = response.get('mcp_available', False)
                
                # Check if MCP tools were actually used by looking at reliable signals from the agent
                mcp_calls_made = response.get('performance_stats', {}).get('mcp_calls', 0) > 0
                
                # Use the reliable mcp_available flag and mcp_calls count from the specialized agent
                # These are set by the agent itself when it successfully uses MCP tools
                tools_actually_used = mcp_available and mcp_calls_made
                
                if tools_actually_used:
                    response_content += f"\n\n**Data Source:** Real-time AWS pricing data"
                    response_content += f"\n**Confidence Level:** {confidence.title()}"
                else:
                    response_content += f"\n\n**Data Source:** Knowledge base estimates - verify with AWS Calculator"
                    response_content += f"\n**Confidence Level:** Medium (fallback mode)"
                
                return response_content
                
            elif response.get('status') == 'error':
                error_msg = response.get('error', 'Unknown error occurred')
                troubleshooting = response.get('troubleshooting', [])
                
                # Generate user-friendly error response
                error_response = f"""I encountered an issue while processing your request with the specialized agent.

**Issue:** {error_msg}

**What you can try:**
1. **Rephrase your question** - Be more specific about what you need
2. **Try a simpler query** - Break complex requests into smaller parts
3. **Check your request** - Ensure you're asking about supported topics
"""
                
                # Add troubleshooting guidance if available
                if troubleshooting:
                    error_response += f"\n**Technical Details:**\n"
                    for tip in troubleshooting[:3]:  # Limit to 3 tips
                        error_response += f"- {tip}\n"
                
                error_response += f"\nWould you like to try rephrasing your question?"
                
                return error_response
            else:
                return "I received an unexpected response format from the specialized agent. Please try your query again."
            
        except Exception as e:
            logger.error(f"Error routing to agent {agent_id}: {str(e)}")
            error_type = type(e).__name__
            
            return f"""I encountered an unexpected error while processing your request.

**Error Type:** {error_type}
**Issue:** The specialized agent is temporarily unavailable.

**What you can try:**
1. **Rephrase your question** to be more specific
2. **Try your query again** in a few minutes
3. **Ask for general guidance** - I can still help with general questions

Would you like me to help with general guidance instead?"""

    @tool
    async def aws_pricing_agent_tool(self, query: str) -> str:
        """
        Enhanced AWS pricing tool with conversation context sharing and comprehensive error handling.
        
        Args:
            query: User query related to AWS costs, pricing, or architecture cost analysis
            
        Returns:
            Detailed cost analysis, pricing breakdown, and optimization recommendations
        """
        try:
            # Import and initialize the AWS Pricing Agent
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from aws_pricing_agent import AWSPricingAgent
            import asyncio
            
            logger.info(f"Processing AWS pricing query: {query[:100]}...")
            
            # Create or reuse pricing agent instance with conversation context sharing
            if not hasattr(self, '_pricing_agent'):
                self._pricing_agent = AWSPricingAgent()
            
            pricing_agent = self._pricing_agent
            
            # Share router conversation context with pricing agent if available
            if hasattr(self, 'conversation_history') and self.conversation_history:
                # Convert router context to pricing agent format
                for item in self.conversation_history[-3:]:  # Share last 3 exchanges
                    if item.get('role') == 'user' and item.get('content'):
                        # Add context about previous user queries
                        pricing_agent.conversation_context.append({
                            'query': f"[ROUTER_CONTEXT] {item['content']}",
                            'response': "[Context from router conversation]",
                            'timestamp': time.time(),
                            'query_type': 'context_sharing',
                            'architecture_info': {},
                            'cost_estimates': {}
                        })
            
            # Process the query using the specialized pricing agent
            response = await pricing_agent.process_pricing_query(query)
            
            # Handle different response statuses
            if response.get('status') == 'success':
                response_content = str(response.get('response', 'No response content available'))
                
                # Add metadata about data source and confidence
                confidence = response.get('confidence', 'medium')
                mcp_available = response.get('mcp_available', False)
                
                if not mcp_available:
                    response_content += f"\n\n**Data Source:** Knowledge base (real-time data unavailable)"
                    response_content += f"\n**Confidence Level:** {confidence.title()}"
                    response_content += f"\n**Recommendation:** Verify with AWS Calculator for current pricing"
                else:
                    response_content += f"\n\n**Data Source:** Real-time AWS pricing data"
                    response_content += f"\n**Confidence Level:** {confidence.title()}"
                
                return response_content
                
            elif response.get('status') == 'error':
                error_msg = response.get('error', 'Unknown error occurred')
                troubleshooting = response.get('troubleshooting', {})
                
                # Generate user-friendly error response
                error_response = f"""I encountered an issue while retrieving AWS pricing data.

**Issue:** {error_msg}

**What you can try:**
1. **Rephrase your question** - Be more specific about AWS services and configurations
2. **Try a simpler query** - Ask about one service at a time
3. **Check your request** - Ensure you're asking about valid AWS services

**Example queries that work well:**
- "What's the cost of an EC2 t3.small instance in us-east-1?"
- "RDS MySQL pricing for db.t3.medium"
- "S3 storage costs for 100GB of data"
"""
                
                # Add troubleshooting guidance if available
                if troubleshooting.get('troubleshooting'):
                    error_response += f"\n**Technical Details:**\n"
                    for tip in troubleshooting['troubleshooting'][:3]:  # Limit to 3 tips
                        error_response += f"- {tip}\n"
                
                error_response += f"\nWould you like to try rephrasing your pricing question?"
                
                return error_response
            else:
                return "I received an unexpected response format from the pricing agent. Please try your query again."
            
        except ImportError as e:
            logger.error(f"Import error for AWS Pricing Agent: {str(e)}")
            return """The AWS Pricing Agent is not properly configured.

**Issue:** Missing required components for pricing analysis.

**What this means:**
- The specialized pricing agent cannot be loaded
- I can still provide general AWS guidance

**What you can try:**
1. **Ask general AWS questions** - I can help with service information and best practices
2. **Use AWS Calculator** - Visit https://calculator.aws/ for official pricing
3. **Try again later** - The pricing service may be restored

Would you like me to help with general AWS questions instead?"""
            
        except Exception as e:
            logger.error(f"Unexpected error calling AWS Pricing Agent: {str(e)}")
            error_type = type(e).__name__
            
            return f"""I encountered an unexpected error while processing your AWS pricing query.

**Error Type:** {error_type}
**Issue:** The pricing analysis system is temporarily unavailable.

**Alternative options:**
1. **AWS Calculator** - Visit https://calculator.aws/ for official pricing
2. **AWS Console** - Check current pricing in your AWS account  
3. **General guidance** - I can still help with AWS architecture questions

**What you can try:**
- Rephrase your question to be more specific
- Ask about individual AWS services one at a time
- Try your query again in a few minutes

Would you like me to help with general AWS architecture guidance instead?"""

    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        Enhanced intent analysis using agent registry for dynamic agent selection.
        
        Args:
            query: User query to analyze
            
        Returns:
            Dictionary containing intent analysis results
        """
        # Use agent registry to find the best agent for this query
        best_agent_id = self.agent_registry.find_best_agent(query)
        
        if best_agent_id:
            # Get the agent and its confidence score
            agent = self.agent_registry.get_agent(best_agent_id)
            confidence_score = agent.get_confidence_score(query) if agent else 0.0
            metadata = self.agent_registry.agent_metadata.get(best_agent_id)
            
            # Determine confidence level (adjusted thresholds)
            if confidence_score >= 0.7:
                confidence = 'high'
            elif confidence_score >= 0.4:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            return {
                'intent': 'specialized_agent',
                'selected_agent': best_agent_id,
                'agent_name': metadata.name if metadata else best_agent_id,
                'confidence': confidence,
                'confidence_score': confidence_score,
                'reasoning': f"Best match: {metadata.name if metadata else best_agent_id} (score: {confidence_score:.2f})",
                'fallback_to_general': False,
                'uncertainty_handled': False,
                'capabilities': [cap.name for cap in metadata.capabilities] if metadata else []
            }
        else:
            # No specialized agent found, handle as general query
            return {
                'intent': 'general',
                'selected_agent': 'general_response',
                'agent_name': 'General Response',
                'confidence': 'medium',
                'confidence_score': 0.0,
                'reasoning': "No specialized agent found with sufficient confidence",
                'fallback_to_general': True,
                'uncertainty_handled': True,
                'capabilities': []
            }

    async def process_query(self, query: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Enhanced query processing with conversation context management and comprehensive error handling.
        
        Args:
            query: User query to process
            conversation_history: Optional conversation history for context
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Update conversation history
            if conversation_history:
                self.conversation_history = conversation_history[-self.max_history_length:]
            
            # Add current query to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': query,
                'timestamp': time.time()
            })
            
            # Analyze intent with enhanced logic
            intent_analysis = self.analyze_intent(query)
            
            logger.info(f"Intent analysis: {intent_analysis}")
            
            # Handle uncertain intent with user guidance
            if intent_analysis.get('uncertainty_handled'):
                uncertainty_guidance = self._generate_uncertainty_guidance(query, intent_analysis)
                if uncertainty_guidance:
                    intent_analysis['uncertainty_guidance'] = uncertainty_guidance
            
            # Get response from agent using stream_async and collect the full response
            response_content = ""
            try:
                async for event in self.agent.stream_async(query):
                    if "data" in event:
                        response_content += event["data"]
                
                # Add uncertainty guidance if applicable
                if intent_analysis.get('uncertainty_guidance'):
                    response_content += f"\n\n{intent_analysis['uncertainty_guidance']}"
                
            except Exception as agent_error:
                logger.error(f"Agent processing error: {str(agent_error)}")
                response_content = self._generate_agent_error_response(query, agent_error, intent_analysis)
            
            # Add response to conversation history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response_content,
                'timestamp': time.time(),
                'intent_analysis': intent_analysis
            })
            
            # Trim conversation history if too long
            if len(self.conversation_history) > self.max_history_length:
                self.conversation_history = self.conversation_history[-self.max_history_length:]
            
            return {
                'content': response_content,
                'agent_type': 'router_enhanced',
                'intent_analysis': intent_analysis,
                'timestamp': None,  # Will be set by the calling code
                'error_handled': True if 'Agent processing error' in response_content else False,
                'conversation_context_length': len(self.conversation_history)
            }
            
        except Exception as e:
            logger.error(f"Router error processing query: {str(e)}")
            
            # Generate helpful error response based on query type
            error_response = self._generate_router_error_response(query, e)
            
            return {
                'content': error_response,
                'agent_type': 'router_error',
                'intent_analysis': {
                    'intent': 'error', 
                    'confidence': 'high',
                    'error_type': type(e).__name__,
                    'fallback_used': True
                },
                'timestamp': None,
                'error_handled': True
            }

    def _generate_uncertainty_guidance(self, query: str, intent_analysis: Dict[str, Any]) -> Optional[str]:
        """Generate guidance for uncertain intent classification."""
        if not intent_analysis.get('fallback_to_general'):
            return None
        
        return """

💡 **Tip:** If you're looking for AWS pricing information, try being more specific:
- "What's the cost of running [specific service]?"
- "How much does [instance type] cost per month?"
- "Compare pricing between [service A] and [service B]"

I can provide detailed AWS cost analysis and optimization recommendations!"""

    def _generate_agent_error_response(self, query: str, error: Exception, intent_analysis: Dict[str, Any]) -> str:
        """Generate helpful response when agent processing fails."""
        error_type = type(error).__name__
        
        if intent_analysis.get('intent') == 'aws_pricing':
            return f"""I apologize, but I encountered an issue while processing your AWS pricing query.

**What happened:** {error_type} - The specialized pricing agent is temporarily unavailable.

**What you can try:**
1. **Rephrase your question** - Try asking about specific AWS services
2. **Be more specific** - Include service names, instance types, or regions
3. **Try again** - The service may be temporarily busy

**Example queries that work well:**
- "Cost of EC2 t3.medium in us-east-1"
- "RDS pricing for MySQL database"
- "S3 storage costs for 100GB"

Would you like to try rephrasing your pricing question?"""
        else:
            return f"""I encountered a temporary issue while processing your request.

**Error:** {error_type}

**What you can try:**
1. **Rephrase your question** - Try asking in a different way
2. **Be more specific** - Provide more details about what you're looking for
3. **Try again** - This may be a temporary issue

I'm here to help with AWS questions, pricing analysis, and general technical guidance. Please try asking your question again!"""

    def _generate_router_error_response(self, query: str, error: Exception) -> str:
        """Generate comprehensive error response for router failures."""
        error_type = type(error).__name__
        
        # Check if query seems to be pricing-related
        is_pricing_query = any(keyword in query.lower() for keyword in ['cost', 'price', 'pricing', 'budget'])
        
        base_response = f"""I apologize, but I encountered a system error while processing your request.

**Error Type:** {error_type}
**Status:** Routing system temporarily unavailable"""

        if is_pricing_query:
            base_response += """

**For AWS Pricing Questions:**
Since you appear to be asking about AWS costs, here are some alternatives:
1. **AWS Calculator:** Visit https://calculator.aws/ for official pricing
2. **AWS Console:** Check current pricing in your AWS account
3. **Try again:** The pricing service may be temporarily unavailable

**Example pricing queries to try:**
- "What's the monthly cost of a t3.small EC2 instance?"
- "Compare RDS pricing between MySQL and PostgreSQL"
- "S3 storage costs for different storage classes"
"""
        else:
            base_response += """

**What you can try:**
1. **Rephrase your question** - Try asking in a simpler way
2. **Be more specific** - Include more details about what you need
3. **Try again** - This may be a temporary system issue

**I can help with:**
- AWS service questions and best practices
- Cost analysis and pricing information
- Architecture recommendations
- Technical guidance and troubleshooting
"""

        base_response += """

Please try your question again, and I'll do my best to help!"""
        
        return base_response

    def test_intent_classification(self) -> Dict[str, Any]:
        """
        Test the intent classification with sample queries.
        
        Returns:
            Dictionary containing test results
        """
        test_queries = [
            # AWS Pricing queries
            "How much does an EC2 t3.medium instance cost per month?",
            "I need a cost estimate for a 3-tier web application on AWS",
            "What's the pricing for S3 storage in us-east-1?",
            "Can you help me optimize costs for my AWS architecture?",
            "Budget analysis for running a microservices architecture",
            
            # General queries  
            "How do I configure an EC2 security group?",
            "What's the difference between ECS and EKS?",
            "Help me set up a Lambda function",
            "Best practices for AWS IAM roles",
            "How to deploy a Next.js app on AWS?"
        ]
        
        results = {
            'aws_pricing_queries': [],
            'general_queries': [],
            'accuracy_summary': {}
        }
        
        for query in test_queries:
            intent_result = self.analyze_intent(query)
            
            # Categorize based on expected intent
            if any(keyword in query.lower() for keyword in ['cost', 'price', 'pricing', 'budget', 'estimate', 'optimize costs']):
                expected_intent = 'aws_pricing'
                results['aws_pricing_queries'].append({
                    'query': query,
                    'detected_intent': intent_result['intent'],
                    'confidence': intent_result['confidence'],
                    'correct': intent_result['intent'] == expected_intent
                })
            else:
                expected_intent = 'general'
                results['general_queries'].append({
                    'query': query,
                    'detected_intent': intent_result['intent'],
                    'confidence': intent_result['confidence'],
                    'correct': intent_result['intent'] == expected_intent
                })
        
        # Calculate accuracy
        total_correct = sum(1 for q in results['aws_pricing_queries'] if q['correct']) + \
                       sum(1 for q in results['general_queries'] if q['correct'])
        total_queries = len(test_queries)
        accuracy = (total_correct / total_queries) * 100
        
        results['accuracy_summary'] = {
            'total_queries': total_queries,
            'correct_classifications': total_correct,
            'accuracy_percentage': accuracy
        }
        
        return results


def main():
    """Main function for testing the Router Agent."""
    import asyncio
    
    async def test_router():
        router = RouterAgent()
        
        print("=== Router Agent Intent Classification Test ===")
        test_results = router.test_intent_classification()
        
        print(f"\nAccuracy: {test_results['accuracy_summary']['accuracy_percentage']:.1f}%")
        print(f"Correct: {test_results['accuracy_summary']['correct_classifications']}/{test_results['accuracy_summary']['total_queries']}")
        
        print("\n=== AWS Pricing Queries ===")
        for result in test_results['aws_pricing_queries']:
            status = "✓" if result['correct'] else "✗"
            print(f"{status} {result['query']}")
            print(f"   Detected: {result['detected_intent']} ({result['confidence']} confidence)")
        
        print("\n=== General Queries ===")
        for result in test_results['general_queries']:
            status = "✓" if result['correct'] else "✗"
            print(f"{status} {result['query']}")
            print(f"   Detected: {result['detected_intent']} ({result['confidence']} confidence)")
        
        print("\n=== Sample Query Processing ===")
        sample_query = "How much would it cost to run a web application with EC2, RDS, and S3?"
        response = await router.process_query(sample_query)
        
        print(f"Query: {sample_query}")
        print(f"Intent: {response['intent_analysis']['intent']}")
        print(f"Response: {response['content'][:200]}...")

    # Run the test
    asyncio.run(test_router())


if __name__ == "__main__":
    main()