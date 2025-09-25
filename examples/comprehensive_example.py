#!/usr/bin/env python3
"""
Comprehensive example of using the Azure DevOps MCP Server

This example demonstrates various capabilities of the MCP ADO server including:
- Natural language queries
- Work item creation
- Batch operations
- Advanced reporting
"""

import asyncio
import json
from typing import Dict, Any

# Example connection configuration
CONNECTION = {
    "org": "https://dev.azure.com/your-organization",
    "pat": "your-personal-access-token",
    "project": "your-project-name"
}

class AdoMcpExample:
    """Example client for Azure DevOps MCP Server"""
    
    def __init__(self, connection: Dict[str, str]):
        self.connection = connection
    
    async def test_connection(self):
        """Test the connection to Azure DevOps"""
        print("Testing connection to Azure DevOps...")
        # In a real implementation, this would call the MCP server
        result = {
            "success": True,
            "message": f"Successfully connected to {self.connection['org']}",
            "project_count": 5
        }
        print(f"✓ {result['message']}")
        return result
    
    async def natural_language_queries(self):
        """Demonstrate natural language query capabilities"""
        print("\n=== Natural Language Query Examples ===")
        
        queries = [
            "Show all bugs assigned to me",
            "Find active user stories with high priority",
            "List tasks created this week",
            "Show completed work items in current iteration",
            "Find bugs with severity critical",
            "Show all features in backlog",
            "List work items tagged with 'urgent'",
            "Find unassigned tasks"
        ]
        
        for query in queries:
            print(f"\nQuery: '{query}'")
            # In a real implementation, this would call the MCP server
            result = {
                "success": True,
                "work_items": [
                    {"id": 123, "title": f"Sample item for: {query}", "type": "Bug", "state": "Active"},
                    {"id": 124, "title": f"Another item for: {query}", "type": "Task", "state": "New"}
                ],
                "count": 2,
                "wiql": f"SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.Title] CONTAINS '{query.split()[-1]}'"
            }
            print(f"  Found {result['count']} work items")
            print(f"  Generated WIQL: {result['wiql']}")
    
    async def create_work_items(self):
        """Demonstrate work item creation"""
        print("\n=== Work Item Creation Examples ===")
        
        # Create a bug
        print("\nCreating a bug...")
        bug_result = {
            "success": True,
            "work_item": {
                "id": 1001,
                "title": "Login page crashes on mobile devices",
                "work_item_type": "Bug",
                "state": "New"
            },
            "message": "Created Bug 'Login page crashes on mobile devices' with ID 1001"
        }
        print(f"✓ {bug_result['message']}")
        
        # Create a user story
        print("\nCreating a user story...")
        story_result = {
            "success": True,
            "work_item": {
                "id": 1002,
                "title": "As a user, I want to reset my password",
                "work_item_type": "User Story",
                "state": "New",
                "story_points": 5
            },
            "message": "Created User Story 'As a user, I want to reset my password' with ID 1002"
        }
        print(f"✓ {story_result['message']}")
        
        # Create multiple tasks
        print("\nCreating multiple tasks...")
        tasks = [
            {"work_item_type": "Task", "title": "Design password reset UI", "fields": {"remaining_work": 8}},
            {"work_item_type": "Task", "title": "Implement password reset API", "fields": {"remaining_work": 16}},
            {"work_item_type": "Task", "title": "Write unit tests", "fields": {"remaining_work": 4}},
            {"work_item_type": "Task", "title": "Update documentation", "fields": {"remaining_work": 2}}
        ]
        
        batch_result = {
            "success": True,
            "created_count": 4,
            "error_count": 0,
            "results": [
                {"success": True, "work_item": {"id": 1003, "title": task["title"]}}
                for task in tasks
            ]
        }
        print(f"✓ Created {batch_result['created_count']} tasks successfully")
    
    async def advanced_queries(self):
        """Demonstrate advanced query capabilities"""
        print("\n=== Advanced Query Examples ===")
        
        # Get work items by iteration
        print("\nGetting work items for current iteration...")
        iteration_result = {
            "success": True,
            "iteration_path": "MyProject\\Sprint 1",
            "summary": {
                "total_count": 15,
                "total_story_points": 45,
                "total_remaining_work": 120
            },
            "grouped_items": {
                "User Story": {"New": 2, "Active": 3, "Done": 1},
                "Task": {"New": 4, "Active": 3, "Done": 2},
                "Bug": {"Active": 1}
            }
        }
        print(f"✓ Found {iteration_result['summary']['total_count']} work items")
        print(f"  Total story points: {iteration_result['summary']['total_story_points']}")
        print(f"  Remaining work: {iteration_result['summary']['total_remaining_work']} hours")
        
        # Get burndown data
        print("\nGetting burndown data...")
        burndown_result = {
            "success": True,
            "summary": {
                "story_points_completion_percent": 67.5,
                "work_completion_percent": 72.3,
                "total_story_points": 45,
                "completed_story_points": 30.5
            }
        }
        print(f"✓ Sprint progress: {burndown_result['summary']['story_points_completion_percent']}% story points completed")
        print(f"  Work completion: {burndown_result['summary']['work_completion_percent']}%")
        
        # Get recent work items
        print("\nGetting recent work items (last 7 days)...")
        recent_result = {
            "success": True,
            "count": 8,
            "by_day": {
                "2024-01-15": 3,
                "2024-01-14": 2,
                "2024-01-13": 1,
                "2024-01-12": 2
            }
        }
        print(f"✓ Found {recent_result['count']} work items changed in the last 7 days")
    
    async def project_management(self):
        """Demonstrate project management capabilities"""
        print("\n=== Project Management Examples ===")
        
        # List projects
        print("\nListing all projects...")
        projects_result = {
            "success": True,
            "projects": [
                {"name": "Web Application", "id": "proj-1", "state": "wellFormed"},
                {"name": "Mobile App", "id": "proj-2", "state": "wellFormed"},
                {"name": "API Services", "id": "proj-3", "state": "wellFormed"}
            ],
            "count": 3
        }
        print(f"✓ Found {projects_result['count']} projects")
        for project in projects_result['projects']:
            print(f"  - {project['name']} ({project['state']})")
        
        # Get project details
        print(f"\nGetting details for project '{self.connection['project']}'...")
        project_result = {
            "success": True,
            "project": {
                "name": self.connection['project'],
                "description": "Main development project",
                "visibility": "private",
                "state": "wellFormed"
            }
        }
        print(f"✓ Project: {project_result['project']['name']}")
        print(f"  Description: {project_result['project']['description']}")
    
    async def query_suggestions(self):
        """Demonstrate query suggestion capabilities"""
        print("\n=== Query Suggestions ===")
        
        suggestions_result = {
            "success": True,
            "suggestions": [
                "Show all bugs assigned to me",
                "Find active tasks",
                "List all user stories in current iteration",
                "Show high priority items",
                "Find bugs created this week"
            ]
        }
        
        print("Available query suggestions:")
        for i, suggestion in enumerate(suggestions_result['suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    async def run_all_examples(self):
        """Run all example scenarios"""
        print("Azure DevOps MCP Server - Comprehensive Examples")
        print("=" * 50)
        
        await self.test_connection()
        await self.natural_language_queries()
        await self.create_work_items()
        await self.advanced_queries()
        await self.project_management()
        await self.query_suggestions()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("\nTo use this with a real Azure DevOps instance:")
        print("1. Update the CONNECTION dictionary with your organization URL and PAT")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the MCP server: python -m mcp_ado.server")
        print("4. Connect your MCP client to the server")

async def main():
    """Main function to run examples"""
    example = AdoMcpExample(CONNECTION)
    await example.run_all_examples()

if __name__ == "__main__":
    asyncio.run(main())