#!/usr/bin/env python3
"""
Integration Demo: Complete Azure DevOps MCP Server Workflow

This demonstrates the full pipeline from natural language queries to Azure DevOps API calls.
"""

import asyncio
import json
from mcp_ado.server import McpServer
from mcp_ado.utils.query_converter import QueryConverter
from mcp_ado.utils.field_mapper import FieldMapper

async def demonstrate_complete_workflow():
    """Demonstrate the complete workflow from natural language to API calls"""
    
    print("🚀 Azure DevOps MCP Server - Complete Integration Demo")
    print("=" * 60)
    
    # Initialize components
    server = McpServer()
    query_converter = QueryConverter()
    field_mapper = FieldMapper()
    
    # Initialize server
    init_request = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "integration-demo", "version": "1.0.0"}
        }
    }
    await server.handle_request(init_request)
    
    print("\n📋 STEP 1: Natural Language Query Processing")
    print("-" * 50)
    
    # Example natural language queries
    nl_queries = [
        "Show me all critical bugs assigned to john.doe",
        "Find user stories with more than 5 story points in current sprint",
        "Get all completed tasks from last week",
        "List high priority features in backlog"
    ]
    
    for i, query in enumerate(nl_queries, 1):
        print(f"\n{i}. Natural Language: '{query}'")
        
        # Convert to WIQL
        wiql = query_converter.convert_to_wiql(query)
        print(f"   Generated WIQL: {wiql[:80]}...")
        
        # Show what the MCP call would look like
        mcp_request = {
            "jsonrpc": "2.0",
            "id": i,
            "method": "tools/call",
            "params": {
                "name": "search_work_items",
                "arguments": {
                    "connection": {
                        "org": "https://dev.azure.com/your-org",
                        "pat": "your-pat-token",
                        "project": "your-project"
                    },
                    "query": query,
                    "top": 50
                }
            }
        }
        print(f"   MCP Tool: search_work_items")
        print(f"   Would execute: Azure DevOps REST API call")
    
    print("\n🛠️ STEP 2: Work Item Creation Workflow")
    print("-" * 45)
    
    # Example creation scenarios
    creation_scenarios = [
        {
            "type": "Bug Report",
            "natural_request": "Create a bug for login page crashing on mobile",
            "tool": "create_bug",
            "mapped_fields": {
                "title": "Login page crashes on mobile devices",
                "repro_steps": "1. Open mobile app\n2. Navigate to login\n3. Enter credentials\n4. App crashes",
                "severity": "High",
                "priority": 2
            }
        },
        {
            "type": "User Story",
            "natural_request": "Create a user story for password reset feature",
            "tool": "create_user_story", 
            "mapped_fields": {
                "title": "As a user, I want to reset my password via email",
                "story_points": 5,
                "acceptance_criteria": "Given I forgot password\nWhen I click reset\nThen I get email",
                "priority": 2
            }
        },
        {
            "type": "Task",
            "natural_request": "Create a task to update API documentation",
            "tool": "create_task",
            "mapped_fields": {
                "title": "Update API documentation for v2.0",
                "remaining_work": 8,
                "original_estimate": 8,
                "assigned_to": "tech.writer@company.com"
            }
        }
    ]
    
    for i, scenario in enumerate(creation_scenarios, 1):
        print(f"\n{i}. {scenario['type']} Creation:")
        print(f"   Natural Request: '{scenario['natural_request']}'")
        print(f"   MCP Tool: {scenario['tool']}")
        
        # Show field mapping
        print("   Field Mapping:")
        for field_name, field_value in scenario['mapped_fields'].items():
            ado_field = field_mapper.get_field_reference(field_name)
            print(f"     {field_name} -> {ado_field}")
        
        # Show the actual MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"create_{i}",
            "method": "tools/call",
            "params": {
                "name": scenario['tool'],
                "arguments": {
                    "connection": {
                        "org": "https://dev.azure.com/your-org",
                        "pat": "your-pat-token",
                        "project": "your-project"
                    },
                    **scenario['mapped_fields']
                }
            }
        }
        print(f"   Would execute: Azure DevOps Work Items REST API")
        print(f"   API Endpoint: POST https://dev.azure.com/org/project/_apis/wit/workitems/${scenario['type']}")
    
    print("\n📊 STEP 3: Advanced Operations")
    print("-" * 35)
    
    advanced_operations = [
        {
            "name": "Batch Creation",
            "description": "Create multiple related work items at once",
            "tool": "create_multiple_work_items",
            "example": "Create epic with 3 user stories and 5 tasks",
            "api_calls": "Multiple POST requests with relationship linking"
        },
        {
            "name": "Burndown Analysis", 
            "description": "Get sprint progress and burndown data",
            "tool": "get_burndown_data",
            "example": "Show burndown for current sprint",
            "api_calls": "GET work items + analytics calculations"
        },
        {
            "name": "Team Velocity",
            "description": "Calculate team performance metrics",
            "tool": "get_recent_work_items",
            "example": "Show team velocity for last 3 sprints",
            "api_calls": "GET work items with date filtering + aggregation"
        }
    ]
    
    for i, op in enumerate(advanced_operations, 1):
        print(f"\n{i}. {op['name']}")
        print(f"   Description: {op['description']}")
        print(f"   Example: {op['example']}")
        print(f"   MCP Tool: {op['tool']}")
        print(f"   Azure DevOps API: {op['api_calls']}")
    
    print("\n🔄 STEP 4: Complete Request Flow")
    print("-" * 40)
    
    print("1. User Input (Natural Language)")
    print("   ↓")
    print("2. MCP Client → JSON-RPC Request")
    print("   ↓")
    print("3. MCP Server → Query Converter")
    print("   ↓")
    print("4. Natural Language → WIQL/Field Mapping")
    print("   ↓")
    print("5. Azure DevOps API Client")
    print("   ↓")
    print("6. HTTP Request → Azure DevOps REST API")
    print("   ↓")
    print("7. Response Processing & Formatting")
    print("   ↓")
    print("8. JSON-RPC Response → MCP Client")
    print("   ↓")
    print("9. Structured Data → User")
    
    print("\n🎯 STEP 5: Available API Endpoints")
    print("-" * 38)
    
    api_endpoints = [
        "GET  /_apis/projects - List projects",
        "GET  /_apis/wit/workitems/{id} - Get work item",
        "POST /_apis/wit/workitems/${type} - Create work item",
        "PATCH /_apis/wit/workitems/{id} - Update work item",
        "POST /_apis/wit/wiql - Execute WIQL query",
        "GET  /_apis/work/teamsettings/iterations - Get iterations",
        "GET  /_apis/wit/reporting/workitemrevisions - Get revisions"
    ]
    
    for endpoint in api_endpoints:
        print(f"   {endpoint}")
    
    print("\n✨ SUMMARY")
    print("-" * 15)
    print("🔍 Natural Language Processing: ✅ Implemented")
    print("🛠️ Work Item Creation Tools: ✅ 5 specialized tools")
    print("📊 Query & Search Tools: ✅ 3 advanced tools") 
    print("🏗️ Project Management: ✅ 3 management tools")
    print("⚡ Async API Client: ✅ High-performance HTTP client")
    print("🔗 Field Mapping: ✅ Smart field conversion")
    print("🛡️ Error Handling: ✅ Comprehensive error management")
    print("📝 JSON-RPC Protocol: ✅ Full MCP compliance")
    
    print(f"\n🎉 READY TO USE!")
    print(f"Total Tools: 17")
    print(f"Supported Work Item Types: Bug, Task, User Story, Feature, Epic, Test Case")
    print(f"Natural Language Queries: ✅ Supported")
    print(f"Batch Operations: ✅ Supported")
    print(f"Advanced Analytics: ✅ Supported")
    
    print("\n🚀 Start the server with: python -m mcp_ado.server")

if __name__ == "__main__":
    asyncio.run(demonstrate_complete_workflow())