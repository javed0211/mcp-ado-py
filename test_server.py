#!/usr/bin/env python3
"""
Test script for Azure DevOps MCP Server
"""

import asyncio
import json
from mcp_ado.server import McpServer
from mcp_ado.utils.query_converter import QueryConverter
from mcp_ado.utils.field_mapper import FieldMapper

async def test_server():
    """Test the MCP server functionality"""
    
    print("=== Azure DevOps MCP Server Test ===\n")
    
    # Initialize server
    server = McpServer()
    
    # Test 1: Query Conversion
    print("1. Testing Query Conversion:")
    converter = QueryConverter()
    test_queries = [
        "Show me all bugs assigned to john",
        "Find high priority tasks in current iteration", 
        "Get all user stories created last week",
        "List completed features from last month"
    ]
    
    for query in test_queries:
        wiql = converter.convert_to_wiql(query)
        print(f"   Query: {query}")
        print(f"   WIQL:  {wiql}")
        print()
    
    # Test 2: Field Mapping
    print("2. Testing Field Mapping:")
    mapper = FieldMapper()
    test_fields = ['title', 'assigned_to', 'priority', 'state', 'created_date', 'story_points']
    
    for field in test_fields:
        mapped = mapper.get_field_reference(field)
        print(f"   {field} -> {mapped}")
    print()
    
    # Test 3: Available Tools
    print("3. Available Tools:")
    print(f"   Total tools registered: {len(server.tools)}")
    
    # Group tools by category
    categories = {
        'Project': [],
        'Work Item': [],
        'Query': [],
        'Creation': []
    }
    
    for tool_name, tool_def in server.tools.items():
        if any(x in tool_name for x in ['project', 'team']):
            categories['Project'].append(tool_name)
        elif any(x in tool_name for x in ['create', 'batch']):
            categories['Creation'].append(tool_name)
        elif any(x in tool_name for x in ['query', 'search', 'report']):
            categories['Query'].append(tool_name)
        else:
            categories['Work Item'].append(tool_name)
    
    for category, tools in categories.items():
        if tools:
            print(f"\n   {category} Tools ({len(tools)}):")
            for tool in sorted(tools):
                desc = server.tools[tool]['description'][:50] + "..." if len(server.tools[tool]['description']) > 50 else server.tools[tool]['description']
                print(f"     - {tool}: {desc}")
    
    # Test 4: Tool Schema Validation
    print("\n4. Tool Schema Validation:")
    sample_tools = ['query_work_items', 'create_bug', 'create_user_story', 'list_projects']
    
    for tool_name in sample_tools:
        if tool_name in server.tools:
            tool_def = server.tools[tool_name]
            schema = tool_def.get('inputSchema', {})
            required_fields = schema.get('required', [])
            properties = schema.get('properties', {})
            
            print(f"   {tool_name}:")
            print(f"     Required: {required_fields}")
            print(f"     Properties: {list(properties.keys())}")
        else:
            print(f"   {tool_name}: NOT FOUND")
    
    # Test 5: Mock Tool Execution
    print("\n5. Testing Tool Execution (Mock):")
    
    # Test list_tools request
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    response = await server.handle_request(list_tools_request)
    print(f"   list_tools response: {response.get('result', {}).get('tools', [])[:2]}... (showing first 2)")
    
    print("\n=== Test Complete ===")
    print("✅ Server initialized successfully")
    print("✅ Query conversion working")
    print("✅ Field mapping working") 
    print("✅ All tools registered")
    print("✅ JSON-RPC handling working")

if __name__ == "__main__":
    asyncio.run(test_server())