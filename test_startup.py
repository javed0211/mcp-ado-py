#!/usr/bin/env python3
"""
Simple startup test for Azure DevOps MCP Server
"""

import asyncio
import json
import sys
from mcp_ado.server import McpServer

async def test_server_startup():
    """Test that the server can start and respond to basic requests"""
    
    print("🧪 Testing Azure DevOps MCP Server Startup")
    print("=" * 45)
    
    try:
        # Initialize server
        server = McpServer()
        print("✅ Server initialized successfully")
        
        # Test initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        init_response = await server.handle_request(init_request)
        if init_response.get("result"):
            print("✅ Server initialization request handled")
        else:
            print("❌ Server initialization failed")
            return False
        
        # Test tools list request
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        list_response = await server.handle_request(list_request)
        tools = list_response.get("result", {}).get("tools", [])
        
        if tools:
            print(f"✅ Tools list retrieved: {len(tools)} tools available")
        else:
            print("❌ No tools found")
            return False
        
        # Test invalid request handling
        invalid_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "invalid_method"
        }
        
        invalid_response = await server.handle_request(invalid_request)
        if invalid_response.get("error"):
            print("✅ Invalid request properly handled with error response")
        else:
            print("❌ Invalid request not properly handled")
            return False
        
        print("\n🎉 All startup tests passed!")
        print(f"📊 Server ready with {len(tools)} tools:")
        
        # Show first few tools as examples
        for i, tool in enumerate(tools[:5]):
            print(f"   {i+1}. {tool['name']}")
        
        if len(tools) > 5:
            print(f"   ... and {len(tools) - 5} more tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server_startup())
    sys.exit(0 if success else 1)