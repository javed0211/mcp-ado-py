#!/usr/bin/env python3
"""
Simple usage example for Azure DevOps MCP Server

This shows the most basic way to use the server.
"""

import json
import subprocess
import sys


def main():
    """Simple example of using the MCP server"""
    
    # UPDATE THESE VALUES WITH YOUR AZURE DEVOPS INFO
    ORG_URL = "https://dev.azure.com/your-organization/"
    PROJECT = "your-project" 
    PAT_TOKEN = "your-azure-devops-pat-token-here"
    
    if PAT_TOKEN == "your-azure-devops-pat-token-here":
        print("❌ Please update the configuration:")
        print("   ORG_URL = 'https://dev.azure.com/yourorg'")
        print("   PROJECT = 'YourProject'")
        print("   PAT_TOKEN = 'your-personal-access-token'")
        return
    
    # Start the server
    print("🚀 Starting server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "mcp_ado"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    
    try:
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "Simple Client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read initialization response
        init_response = json.loads(process.stdout.readline())
        print("✅ Server initialized")
        
        # List tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/list"
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        tools_response = json.loads(process.stdout.readline())
        tools = tools_response["result"]["tools"]
        print(f"📋 Found {len(tools)} tools")
        
        # Call a tool
        tool_request = {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "tools/call",
            "params": {
                "name": "core_list_projects",
                "arguments": {
                    "connection": {
                        "org": ORG_URL,
                        "project": PROJECT,
                        "pat": PAT_TOKEN
                    }
                }
            }
        }
        
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        tool_response = json.loads(process.stdout.readline())
        
        if "result" in tool_response:
            print("🎉 Tool call successful!")
            print("Projects:")
            for project in tool_response["result"].get("projects", []):
                print(f"  - {project.get('name', 'Unknown')}")
        else:
            print("❌ Tool call failed:")
            print(json.dumps(tool_response, indent=2))
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    main()