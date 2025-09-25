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

from .tools.work_item_tools import WorkItemTools
from .tools.project_tools import ProjectTools
from .tools.query_tools import QueryTools
from .tools.creation_tools import CreationTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class McpServer:
    """Main MCP Server class"""
    
    def __init__(self):
        self.work_item_tools = WorkItemTools()
        self.project_tools = ProjectTools()
        self.query_tools = QueryTools()
        self.creation_tools = CreationTools()
        self.tools = self._register_tools()
        self.initialized = False
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register all available tools"""
        return {
            # Project tools
            "list_projects": {
                "name": "list_projects",
                "description": "List all projects in the Azure DevOps organization",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "object",
                            "properties": {
                                "org": {"type": "string", "description": "Azure DevOps organization URL"},
                                "pat": {"type": "string", "description": "Personal Access Token"}
                            },
                            "required": ["org", "pat"]
                        }
                    },
                    "required": ["connection"]
                }
            },
            "get_project": {
                "name": "get_project",
                "description": "Get specific project information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "object",
                            "properties": {
                                "org": {"type": "string", "description": "Azure DevOps organization URL"},
                                "pat": {"type": "string", "description": "Personal Access Token"}
                            },
                            "required": ["org", "pat"]
                        },
                        "project_name": {"type": "string", "description": "Name of the project"}
                    },
                    "required": ["connection", "project_name"]
                }
            },
            "test_connection": {
                "name": "test_connection",
                "description": "Test connection to Azure DevOps",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "object",
                            "properties": {
                                "org": {"type": "string", "description": "Azure DevOps organization URL"},
                                "pat": {"type": "string", "description": "Personal Access Token"}
                            },
                            "required": ["org", "pat"]
                        }
                    },
                    "required": ["connection"]
                }
            },
            
            # Work item query tools
            "search_work_items": {
                "name": "search_work_items",
                "description": "Search work items using natural language query",
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
                        "top": {"type": "integer", "description": "Number of items to return", "default": 50}
                    },
                    "required": ["connection", "query"]
                }
            },
            "query_work_items_wiql": {
                "name": "query_work_items_wiql",
                "description": "Execute WIQL query directly",
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
                        "wiql": {"type": "string", "description": "WIQL query string"},
                        "top": {"type": "integer", "description": "Number of items to return", "default": 100}
                    },
                    "required": ["connection", "wiql"]
                }
            },
            "get_work_item": {
                "name": "get_work_item",
                "description": "Get a specific work item by ID",
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
                        "work_item_id": {"type": "integer", "description": "Work item ID"}
                    },
                    "required": ["connection", "work_item_id"]
                }
            },
            "get_my_work_items": {
                "name": "get_my_work_items",
                "description": "Get work items assigned to the current user",
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
                        }
                    },
                    "required": ["connection"]
                }
            },
            
            # Work item creation tools
            "create_work_item": {
                "name": "create_work_item",
                "description": "Create a new work item",
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
                        "work_item_type": {"type": "string", "description": "Work item type (Bug, Task, User Story, Feature, Epic, Test Case)"},
                        "title": {"type": "string", "description": "Work item title"},
                        "fields": {
                            "type": "object",
                            "description": "Additional fields for the work item",
                            "additionalProperties": True
                        }
                    },
                    "required": ["connection", "work_item_type", "title"]
                }
            },
            "create_bug": {
                "name": "create_bug",
                "description": "Create a bug work item with bug-specific fields",
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
                        "title": {"type": "string", "description": "Bug title"},
                        "repro_steps": {"type": "string", "description": "Steps to reproduce the bug"},
                        "severity": {"type": "string", "description": "Bug severity"},
                        "priority": {"type": "integer", "description": "Bug priority (1-4)"},
                        "assigned_to": {"type": "string", "description": "Person to assign the bug to"},
                        "additional_fields": {
                            "type": "object",
                            "description": "Additional fields",
                            "additionalProperties": True
                        }
                    },
                    "required": ["connection", "title", "repro_steps"]
                }
            },
            "create_user_story": {
                "name": "create_user_story",
                "description": "Create a user story work item",
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
                        "title": {"type": "string", "description": "User story title"},
                        "story_points": {"type": "number", "description": "Story points estimate"},
                        "acceptance_criteria": {"type": "string", "description": "Acceptance criteria"},
                        "priority": {"type": "integer", "description": "Priority (1-4)"},
                        "assigned_to": {"type": "string", "description": "Person to assign to"},
                        "additional_fields": {
                            "type": "object",
                            "description": "Additional fields",
                            "additionalProperties": True
                        }
                    },
                    "required": ["connection", "title"]
                }
            },
            "create_task": {
                "name": "create_task",
                "description": "Create a task work item",
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
                        "title": {"type": "string", "description": "Task title"},
                        "remaining_work": {"type": "number", "description": "Remaining work in hours"},
                        "activity": {"type": "string", "description": "Activity type"},
                        "assigned_to": {"type": "string", "description": "Person to assign to"},
                        "additional_fields": {
                            "type": "object",
                            "description": "Additional fields",
                            "additionalProperties": True
                        }
                    },
                    "required": ["connection", "title"]
                }
            },
            "create_multiple_work_items": {
                "name": "create_multiple_work_items",
                "description": "Create multiple work items in batch",
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
                        "work_items": {
                            "type": "array",
                            "description": "Array of work items to create",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "work_item_type": {"type": "string"},
                                    "title": {"type": "string"},
                                    "fields": {"type": "object", "additionalProperties": True}
                                },
                                "required": ["work_item_type", "title"]
                            }
                        }
                    },
                    "required": ["connection", "work_items"]
                }
            },
            
            # Work item update tools
            "update_work_item": {
                "name": "update_work_item",
                "description": "Update an existing work item",
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
                        "work_item_id": {"type": "integer", "description": "Work item ID to update"},
                        "fields": {
                            "type": "object",
                            "description": "Fields to update",
                            "additionalProperties": True
                        }
                    },
                    "required": ["connection", "work_item_id", "fields"]
                }
            },
            
            # Advanced query tools
            "get_work_items_by_iteration": {
                "name": "get_work_items_by_iteration",
                "description": "Get all work items in a specific iteration",
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
                        "iteration_path": {"type": "string", "description": "Iteration path"}
                    },
                    "required": ["connection", "iteration_path"]
                }
            },
            "get_burndown_data": {
                "name": "get_burndown_data",
                "description": "Get burndown chart data for an iteration",
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
                        "iteration_path": {"type": "string", "description": "Iteration path"}
                    },
                    "required": ["connection", "iteration_path"]
                }
            },
            "get_recent_work_items": {
                "name": "get_recent_work_items",
                "description": "Get work items changed in the last N days",
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
                        "days": {"type": "integer", "description": "Number of days to look back", "default": 7}
                    },
                    "required": ["connection"]
                }
            },
            
            # Utility tools
            "get_query_suggestions": {
                "name": "get_query_suggestions",
                "description": "Get query suggestions for natural language search",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "partial_query": {"type": "string", "description": "Partial query to get suggestions for", "default": ""}
                    }
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
        try:
            # Project tools
            if tool_name == "list_projects":
                return await self.project_tools.list_projects(arguments["connection"])
            elif tool_name == "get_project":
                return await self.project_tools.get_project(arguments["connection"], arguments["project_name"])
            elif tool_name == "test_connection":
                return await self.project_tools.test_connection(arguments["connection"])
            
            # Work item query tools
            elif tool_name == "search_work_items":
                return await self.work_item_tools.search_work_items(
                    arguments["connection"], 
                    arguments["query"], 
                    arguments.get("top", 50)
                )
            elif tool_name == "query_work_items_wiql":
                return await self.work_item_tools.query_work_items_wiql(
                    arguments["connection"], 
                    arguments["wiql"], 
                    arguments.get("top", 100)
                )
            elif tool_name == "get_work_item":
                return await self.work_item_tools.get_work_item(
                    arguments["connection"], 
                    arguments["work_item_id"]
                )
            elif tool_name == "get_my_work_items":
                return await self.query_tools.get_my_work_items(arguments["connection"])
            
            # Work item creation tools
            elif tool_name == "create_work_item":
                return await self.creation_tools.create_work_item(
                    arguments["connection"],
                    arguments["work_item_type"],
                    arguments["title"],
                    arguments.get("fields")
                )
            elif tool_name == "create_bug":
                return await self.creation_tools.create_bug(
                    arguments["connection"],
                    arguments["title"],
                    arguments["repro_steps"],
                    arguments.get("severity"),
                    arguments.get("priority"),
                    arguments.get("assigned_to"),
                    arguments.get("additional_fields")
                )
            elif tool_name == "create_user_story":
                return await self.creation_tools.create_user_story(
                    arguments["connection"],
                    arguments["title"],
                    arguments.get("story_points"),
                    arguments.get("acceptance_criteria"),
                    arguments.get("priority"),
                    arguments.get("assigned_to"),
                    arguments.get("additional_fields")
                )
            elif tool_name == "create_task":
                return await self.creation_tools.create_task(
                    arguments["connection"],
                    arguments["title"],
                    arguments.get("remaining_work"),
                    arguments.get("activity"),
                    arguments.get("assigned_to"),
                    arguments.get("additional_fields")
                )
            elif tool_name == "create_multiple_work_items":
                return await self.creation_tools.create_multiple_work_items(
                    arguments["connection"],
                    arguments["work_items"]
                )
            
            # Work item update tools
            elif tool_name == "update_work_item":
                return await self.work_item_tools.update_work_item(
                    arguments["connection"],
                    arguments["work_item_id"],
                    arguments["fields"]
                )
            
            # Advanced query tools
            elif tool_name == "get_work_items_by_iteration":
                return await self.query_tools.get_work_items_by_iteration(
                    arguments["connection"],
                    arguments["iteration_path"]
                )
            elif tool_name == "get_burndown_data":
                return await self.query_tools.get_burndown_data(
                    arguments["connection"],
                    arguments["iteration_path"]
                )
            elif tool_name == "get_recent_work_items":
                return await self.query_tools.get_recent_work_items(
                    arguments["connection"],
                    arguments.get("days", 7)
                )
            
            # Utility tools
            elif tool_name == "get_query_suggestions":
                return self.work_item_tools.get_query_suggestions(
                    arguments.get("partial_query", "")
                )
            
            else:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not implemented"
                }
                
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "tool_name": tool_name
            }

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