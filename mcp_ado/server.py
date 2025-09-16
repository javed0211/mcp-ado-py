#!/usr/bin/env python3
"""
Azure DevOps MCP Server

A Model Context Protocol server that provides tools for interacting with Azure DevOps.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class McpServer:
    """Main MCP Server class"""
    
    def __init__(self):
        self.tools = self._register_tools()
        self.initialized = False
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register all available tools"""
        return {
            "core_list_projects": {
                "name": "core_list_projects",
                "description": "List all projects in the Azure DevOps organization",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "object",
                            "properties": {
                                "org": {"type": "string", "description": "Azure DevOps organization URL"},
                                "pat": {"type": "string", "description": "Personal Access Token"},
                                "project": {"type": "string", "description": "Project name (optional)"}
                            },
                            "required": ["org", "pat"]
                        }
                    },
                    "required": ["connection"]
                }
            },
            "wit_get_work_items": {
                "name": "wit_get_work_items",
                "description": "Get work items from Azure DevOps",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "object",
                            "properties": {
                                "org": {"type": "string", "description": "Azure DevOps organization URL"},
                                "pat": {"type": "string", "description": "Personal Access Token"},
                                "project": {"type": "string", "description": "Project name"}
                            },
                            "required": ["org", "pat", "project"]
                        },
                        "filters": {
                            "type": "object",
                            "properties": {
                                "state": {"type": "string", "description": "Work item state"},
                                "work_item_type": {"type": "string", "description": "Work item type"},
                                "top": {"type": "integer", "description": "Number of items to return"}
                            }
                        }
                    },
                    "required": ["connection"]
                }
            },
            "smart_work_item_search": {
                "name": "smart_work_item_search",
                "description": "Smart search for work items using natural language",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "object",
                            "properties": {
                                "org": {"type": "string", "description": "Azure DevOps organization URL"},
                                "pat": {"type": "string", "description": "Personal Access Token"},
                                "project": {"type": "string", "description": "Project name"}
                            },
                            "required": ["org", "pat", "project"]
                        },
                        "query": {"type": "string", "description": "Natural language search query"},
                        "top": {"type": "integer", "description": "Number of items to return", "default": 10}
                    },
                    "required": ["connection", "query"]
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                return await self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return await self._handle_list_tools(request_id)
            elif method == "tools/call":
                return await self._handle_tool_call(request_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _handle_initialize(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request"""
        self.initialized = True
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "azure-devops-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def _handle_list_tools(self, request_id: str) -> Dict[str, Any]:
        """Handle tools list request"""
        if not self.initialized:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32002,
                    "message": "Server not initialized"
                }
            }
        
        tools_list = [
            {
                "name": tool_info["name"],
                "description": tool_info["description"],
                "inputSchema": tool_info["inputSchema"]
            }
            for tool_info in self.tools.values()
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools_list
            }
        }
    
    async def _handle_tool_call(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request"""
        if not self.initialized:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32002,
                    "message": "Server not initialized"
                }
            }
        
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            }
        
        try:
            result = await self._execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool"""
        connection = arguments.get("connection", {})
        
        # Mock implementation - in a real server, this would call Azure DevOps APIs
        if tool_name == "core_list_projects":
            return {
                "projects": [
                    {"name": "Sample Project 1", "id": "proj-1"},
                    {"name": "Sample Project 2", "id": "proj-2"}
                ],
                "message": "This is a mock response. Configure with real Azure DevOps credentials."
            }
        elif tool_name == "wit_get_work_items":
            return {
                "work_items": [
                    {"id": 1, "title": "Sample Bug", "state": "Active", "type": "Bug"},
                    {"id": 2, "title": "Sample Task", "state": "New", "type": "Task"}
                ],
                "message": "This is a mock response. Configure with real Azure DevOps credentials."
            }
        elif tool_name == "smart_work_item_search":
            query = arguments.get("query", "")
            return {
                "work_items": [
                    {"id": 3, "title": f"Work item matching: {query}", "state": "Active", "type": "Bug"}
                ],
                "message": "This is a mock response. Configure with real Azure DevOps credentials."
            }
        
        return {"error": "Tool not implemented"}

async def main():
    """Main server loop"""
    server = McpServer()
    
    logger.info("Azure DevOps MCP Server starting...")
    
    try:
        while True:
            # Read JSON-RPC request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                
                # Write response to stdout
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())