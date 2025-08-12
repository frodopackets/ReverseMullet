#!/usr/bin/env python3
"""
Agent Management CLI Tool

Command-line interface for managing specialized agents, creating new agents,
and monitoring agent performance.
"""

import argparse
import json
import sys
import asyncio
from typing import Dict, Any
from .agent_registry import get_agent_registry
from .agent_factory import get_agent_factory

def list_agents():
    """List all registered agents."""
    registry = get_agent_registry()
    agents = registry.get_available_agents()
    
    if not agents:
        print("No agents registered.")
        return
    
    print("Registered Agents:")
    print("-" * 50)
    
    for agent_id, metadata in agents.items():
        status = "✓ Enabled" if metadata.enabled else "✗ Disabled"
        print(f"ID: {agent_id}")
        print(f"Name: {metadata.name}")
        print(f"Description: {metadata.description}")
        print(f"Version: {metadata.version}")
        print(f"Status: {status}")
        print(f"Capabilities: {len(metadata.capabilities)}")
        
        if metadata.capabilities:
            for cap in metadata.capabilities:
                print(f"  - {cap.name}: {cap.description}")
        
        print("-" * 50)

def agent_status():
    """Show detailed agent status."""
    registry = get_agent_registry()
    status = registry.get_agent_status()
    
    print("Agent Status Report:")
    print("=" * 60)
    
    for agent_id, agent_status in status.items():
        print(f"\nAgent: {agent_id}")
        print(f"Name: {agent_status['name']}")
        print(f"Description: {agent_status['description']}")
        print(f"Version: {agent_status['version']}")
        print(f"Enabled: {'Yes' if agent_status['enabled'] else 'No'}")
        print(f"Instance Loaded: {'Yes' if agent_status['instance_loaded'] else 'No'}")
        print(f"Instantiable: {'Yes' if agent_status.get('instantiable', False) else 'No'}")
        print(f"Capabilities: {agent_status['capabilities']}")
        
        if 'error' in agent_status:
            print(f"Error: {agent_status['error']}")

def test_agent(agent_id: str, query: str):
    """Test an agent with a query."""
    async def run_test():
        registry = get_agent_registry()
        agent = registry.get_agent(agent_id)
        
        if not agent:
            print(f"Agent '{agent_id}' not found.")
            return
        
        print(f"Testing agent '{agent_id}' with query: {query}")
        print("-" * 50)
        
        try:
            response = await agent.process_query(query)
            
            print(f"Status: {response.get('status', 'unknown')}")
            print(f"Agent Type: {response.get('agent_type', 'unknown')}")
            print(f"MCP Available: {response.get('mcp_available', False)}")
            print(f"Confidence: {response.get('confidence', 'unknown')}")
            print(f"Cached: {response.get('cached', False)}")
            print("\nResponse:")
            print(response.get('response', 'No response content'))
            
            if 'error' in response:
                print(f"\nError: {response['error']}")
                if 'troubleshooting' in response:
                    print("Troubleshooting:")
                    for tip in response['troubleshooting']:
                        print(f"  - {tip}")
        
        except Exception as e:
            print(f"Error testing agent: {e}")
    
    asyncio.run(run_test())

def create_agent_interactive():
    """Interactive agent creation."""
    print("Interactive Agent Creation")
    print("=" * 30)
    
    agent_id = input("Agent ID (e.g., 'my_agent'): ").strip()
    if not agent_id:
        print("Agent ID is required.")
        return
    
    name = input("Agent Name (e.g., 'My Specialized Agent'): ").strip()
    if not name:
        print("Agent name is required.")
        return
    
    description = input("Description: ").strip()
    if not description:
        print("Description is required.")
        return
    
    print("\nDomain Knowledge (enter multiple lines, end with empty line):")
    domain_knowledge_lines = []
    while True:
        line = input()
        if not line:
            break
        domain_knowledge_lines.append(line)
    
    domain_knowledge = "\n".join(domain_knowledge_lines)
    
    # Collect capabilities
    capabilities = []
    print("\nCapabilities (enter at least one):")
    
    while True:
        cap_name = input("Capability name (or press Enter to finish): ").strip()
        if not cap_name:
            break
        
        cap_desc = input("Capability description: ").strip()
        keywords = input("Keywords (comma-separated): ").strip().split(',')
        keywords = [k.strip() for k in keywords if k.strip()]
        
        phrases = input("Phrases (comma-separated): ").strip().split(',')
        phrases = [p.strip() for p in phrases if p.strip()]
        
        priority = input("Priority (1-10, default 5): ").strip()
        try:
            priority = int(priority) if priority else 5
        except ValueError:
            priority = 5
        
        confidence = input("Confidence threshold (0.0-1.0, default 0.5): ").strip()
        try:
            confidence = float(confidence) if confidence else 0.5
        except ValueError:
            confidence = 0.5
        
        capabilities.append({
            'name': cap_name,
            'description': cap_desc,
            'keywords': keywords,
            'phrases': phrases,
            'priority': priority,
            'confidence_threshold': confidence
        })
    
    if not capabilities:
        print("At least one capability is required.")
        return
    
    mcp_server = input("MCP server command (optional): ").strip()
    mcp_server = mcp_server if mcp_server else None
    
    # Create the agent
    factory = get_agent_factory()
    agent = factory.create_agent_from_template(
        agent_id=agent_id,
        name=name,
        description=description,
        domain_knowledge=domain_knowledge,
        capabilities=capabilities,
        mcp_server=mcp_server
    )
    
    if agent:
        print(f"\n✓ Successfully created and registered agent '{agent_id}'")
        print(f"Name: {name}")
        print(f"Capabilities: {len(capabilities)}")
    else:
        print(f"\n✗ Failed to create agent '{agent_id}'")

def create_predefined_agent(agent_type: str):
    """Create a predefined agent."""
    factory = get_agent_factory()
    
    if agent_type == 'security':
        agent = factory.create_security_agent()
        if agent:
            print("✓ Successfully created AWS Security Agent")
        else:
            print("✗ Failed to create AWS Security Agent")
    
    elif agent_type == 'performance':
        agent = factory.create_performance_agent()
        if agent:
            print("✓ Successfully created AWS Performance Agent")
        else:
            print("✗ Failed to create AWS Performance Agent")
    
    else:
        print(f"Unknown predefined agent type: {agent_type}")
        print("Available types: security, performance")

def enable_agent(agent_id: str):
    """Enable an agent."""
    registry = get_agent_registry()
    registry.enable_agent(agent_id)
    print(f"✓ Enabled agent '{agent_id}'")

def disable_agent(agent_id: str):
    """Disable an agent."""
    registry = get_agent_registry()
    registry.disable_agent(agent_id)
    print(f"✓ Disabled agent '{agent_id}'")

def export_config(filepath: str):
    """Export agent configuration."""
    registry = get_agent_registry()
    registry.export_configuration(filepath)
    print(f"✓ Exported configuration to {filepath}")

def find_agent_for_query(query: str):
    """Find the best agent for a query."""
    registry = get_agent_registry()
    best_agent_id = registry.find_best_agent(query)
    
    if best_agent_id:
        metadata = registry.agent_metadata.get(best_agent_id)
        agent = registry.get_agent(best_agent_id)
        confidence = agent.get_confidence_score(query) if agent else 0.0
        
        print(f"Best agent for query: '{query}'")
        print(f"Agent ID: {best_agent_id}")
        print(f"Name: {metadata.name if metadata else 'Unknown'}")
        print(f"Confidence Score: {confidence:.2f}")
        
        if metadata:
            print(f"Capabilities: {[cap.name for cap in metadata.capabilities]}")
    else:
        print(f"No suitable agent found for query: '{query}'")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Agent Management CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List agents
    subparsers.add_parser('list', help='List all registered agents')
    
    # Agent status
    subparsers.add_parser('status', help='Show detailed agent status')
    
    # Test agent
    test_parser = subparsers.add_parser('test', help='Test an agent with a query')
    test_parser.add_argument('agent_id', help='Agent ID to test')
    test_parser.add_argument('query', help='Query to test with')
    
    # Create agent
    create_parser = subparsers.add_parser('create', help='Create a new agent')
    create_subparsers = create_parser.add_subparsers(dest='create_type', help='Creation methods')
    
    create_subparsers.add_parser('interactive', help='Interactive agent creation')
    
    predefined_parser = create_subparsers.add_parser('predefined', help='Create predefined agent')
    predefined_parser.add_argument('type', choices=['security', 'performance'], help='Predefined agent type')
    
    # Enable/disable agents
    enable_parser = subparsers.add_parser('enable', help='Enable an agent')
    enable_parser.add_argument('agent_id', help='Agent ID to enable')
    
    disable_parser = subparsers.add_parser('disable', help='Disable an agent')
    disable_parser.add_argument('agent_id', help='Agent ID to disable')
    
    # Export configuration
    export_parser = subparsers.add_parser('export', help='Export agent configuration')
    export_parser.add_argument('filepath', help='File path to export to')
    
    # Find agent for query
    find_parser = subparsers.add_parser('find', help='Find best agent for a query')
    find_parser.add_argument('query', help='Query to find agent for')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_agents()
        elif args.command == 'status':
            agent_status()
        elif args.command == 'test':
            test_agent(args.agent_id, args.query)
        elif args.command == 'create':
            if args.create_type == 'interactive':
                create_agent_interactive()
            elif args.create_type == 'predefined':
                create_predefined_agent(args.type)
            else:
                print("Please specify creation type: interactive or predefined")
        elif args.command == 'enable':
            enable_agent(args.agent_id)
        elif args.command == 'disable':
            disable_agent(args.agent_id)
        elif args.command == 'export':
            export_config(args.filepath)
        elif args.command == 'find':
            find_agent_for_query(args.query)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()