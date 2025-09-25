#!/usr/bin/env python3
"""
Example usage of Azure DevOps MCP Server

This script demonstrates how to use the MCP server to interact with Azure DevOps
through natural language queries and programmatic API calls.
"""

import asyncio
import json
from mcp_ado.server import McpServer

async def demonstrate_mcp_server():
    """Demonstrate various MCP server capabilities"""
    
    print("🚀 Azure DevOps MCP Server Demo")
    print("=" * 50)
    
    # Initialize the server
    server = McpServer()
    
    # Example connection configuration (replace with your actual values)
    connection_config = {
        "org": "https://dev.azure.com/your-organization",
        "pat": "your-personal-access-token",
        "project": "your-project-name"
    }
    
    print("\n📋 Available Tools:")
    print("-" * 20)
    
    # Initialize the server first
    init_request = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "example-client",
                "version": "1.0.0"
            }
        }
    }
    
    await server.handle_request(init_request)
    
    # List all available tools
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    response = await server.handle_request(list_tools_request)
    tools = response.get('result', {}).get('tools', [])
    
    # Group tools by category for better display
    categories = {
        'Project Management': [],
        'Work Item Operations': [],
        'Query & Search': [],
        'Creation & Batch': []
    }
    
    for tool in tools:
        name = tool['name']
        if any(x in name for x in ['project', 'connection']):
            categories['Project Management'].append(tool)
        elif any(x in name for x in ['create', 'batch', 'multiple']):
            categories['Creation & Batch'].append(tool)
        elif any(x in name for x in ['search', 'query', 'suggestions']):
            categories['Query & Search'].append(tool)
        else:
            categories['Work Item Operations'].append(tool)
    
    for category, tools_list in categories.items():
        if tools_list:
            print(f"\n{category} ({len(tools_list)} tools):")
            for tool in tools_list:
                print(f"  • {tool['name']}: {tool['description'][:60]}...")
    
    print(f"\nTotal: {len(tools)} tools available")
    
    print("\n🔍 Natural Language Query Examples:")
    print("-" * 35)
    
    # Example natural language queries
    example_queries = [
        "Show me all bugs assigned to john.doe@company.com",
        "Find high priority user stories in current sprint",
        "Get all completed tasks from last week",
        "List features created by sarah in the last month",
        "Show me all test cases with priority 1",
        "Find all work items tagged with 'urgent'",
        "Get user stories with more than 8 story points"
    ]
    
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
        
        # Simulate search request
        search_request = {
            "jsonrpc": "2.0",
            "id": i,
            "method": "tools/call",
            "params": {
                "name": "search_work_items",
                "arguments": {
                    "connection": connection_config,
                    "query": query
                }
            }
        }
        
        print(f"   → Would execute: search_work_items with query: '{query}'")
        print()
    
    print("\n🛠️ Work Item Creation Examples:")
    print("-" * 32)
    
    # Example work item creation scenarios
    creation_examples = [
        {
            "type": "Bug",
            "tool": "create_bug",
            "data": {
                "title": "Login page crashes on mobile devices",
                "repro_steps": "1. Open app on mobile\n2. Navigate to login\n3. Enter credentials\n4. App crashes",
                "severity": "2 - High",
                "priority": 2,
                "assigned_to": "developer@company.com"
            }
        },
        {
            "type": "User Story",
            "tool": "create_user_story",
            "data": {
                "title": "As a user, I want to reset my password via email",
                "story_points": 5,
                "acceptance_criteria": "Given I forgot my password\nWhen I click 'Forgot Password'\nThen I receive a reset email",
                "priority": 2
            }
        },
        {
            "type": "Task",
            "tool": "create_task",
            "data": {
                "title": "Update API documentation for v2.0",
                "assigned_to": "tech.writer@company.com",
                "remaining_work": 8,
                "original_estimate": 8
            }
        }
    ]
    
    for i, example in enumerate(creation_examples, 1):
        print(f"{i}. Creating {example['type']}: {example['data']['title']}")
        
        create_request = {
            "jsonrpc": "2.0",
            "id": f"create_{i}",
            "method": "tools/call",
            "params": {
                "name": example['tool'],
                "arguments": {
                    "connection": connection_config,
                    **example['data']
                }
            }
        }
        
        print(f"   → Would call: {example['tool']}")
        print(f"   → With data: {json.dumps(example['data'], indent=6)}")
        print()
    
    print("\n📊 Advanced Query Examples:")
    print("-" * 27)
    
    # Example advanced operations
    advanced_examples = [
        {
            "name": "Get Burndown Data",
            "tool": "get_burndown_data",
            "description": "Retrieve burndown chart data for current iteration",
            "params": {
                "connection": connection_config,
                "iteration_path": "Project\\Sprint 1"
            }
        },
        {
            "name": "Batch Create Work Items",
            "tool": "create_multiple_work_items",
            "description": "Create multiple work items at once",
            "params": {
                "connection": connection_config,
                "work_items": [
                    {
                        "work_item_type": "Task",
                        "title": "Setup CI/CD pipeline",
                        "assigned_to": "devops@company.com"
                    },
                    {
                        "work_item_type": "Task", 
                        "title": "Configure monitoring",
                        "assigned_to": "devops@company.com"
                    }
                ]
            }
        },
        {
            "name": "Get Recent Activity",
            "tool": "get_recent_work_items",
            "description": "Get work items changed in the last 7 days",
            "params": {
                "connection": connection_config,
                "days": 7
            }
        }
    ]
    
    for i, example in enumerate(advanced_examples, 1):
        print(f"{i}. {example['name']}")
        print(f"   Description: {example['description']}")
        print(f"   Tool: {example['tool']}")
        print(f"   Key params: {list(example['params'].keys())}")
        print()
    
    print("\n🔧 Configuration & Setup:")
    print("-" * 24)
    print("To use this MCP server, you need:")
    print("1. Azure DevOps organization URL")
    print("2. Personal Access Token (PAT) with appropriate permissions")
    print("3. Project name you want to work with")
    print()
    print("Example connection configuration:")
    print(json.dumps({
        "org": "https://dev.azure.com/your-organization",
        "pat": "your-personal-access-token-here",
        "project": "your-project-name"
    }, indent=2))
    
    print("\n✨ Key Features:")
    print("-" * 15)
    features = [
        "🔍 Natural language to WIQL query conversion",
        "📝 Comprehensive work item CRUD operations", 
        "🚀 Batch creation and bulk operations",
        "📊 Advanced reporting and analytics",
        "🔗 Project and team management",
        "🏷️ Smart field mapping and validation",
        "⚡ Async/await for high performance",
        "🛡️ Robust error handling and logging"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n🎯 Ready to use! Start the server with:")
    print("   python -m mcp_ado.server")
    print("\nOr integrate with your MCP client using the JSON-RPC protocol.")

if __name__ == "__main__":
    asyncio.run(demonstrate_mcp_server())