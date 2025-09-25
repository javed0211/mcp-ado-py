# Azure DevOps MCP Server

A comprehensive Model Context Protocol (MCP) server for Azure DevOps integration. This server provides intelligent tools for querying, creating, and managing Azure DevOps work items using natural language and structured APIs.

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/your-username/mcp-ado-py.git
cd mcp-ado-py
pip install -r requirements.txt

# Run the server
python -m mcp_ado.server

# Or run the demo
python example_usage.py
```

## ✨ Key Features

### 🔍 Smart Query Capabilities
- **Natural Language Search**: Convert plain English queries into WIQL (Work Item Query Language)
- **Advanced Filtering**: Search by work item type, state, assignee, dates, tags, and more
- **Query Suggestions**: Get intelligent suggestions for common queries
- **WIQL Support**: Execute raw WIQL queries directly

### 📝 Work Item Management
- **Create Work Items**: Support for all work item types (Bug, Task, User Story, Feature, Epic, Test Case)
- **Batch Operations**: Create multiple work items at once
- **Template-based Creation**: Use predefined templates for common scenarios
- **Update & Modify**: Edit existing work items with field validation
- **Smart Field Mapping**: Automatic mapping between common names and Azure DevOps field references

### 📊 Reporting & Analytics
- **Burndown Charts**: Get sprint progress and burndown data
- **Team Velocity**: Track team performance over iterations
- **Recent Activity**: Monitor recent changes and updates
- **Iteration Reports**: Comprehensive iteration summaries
- **Custom Analytics**: Build custom reports using flexible query tools

### 🏗️ Project Management
- **Project Discovery**: List and explore available projects
- **Team Management**: Access team information and structure
- **Area & Iteration Paths**: Navigate project hierarchies
- **Connection Testing**: Validate Azure DevOps connectivity

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/mcp-ado-py.git
cd mcp-ado-py
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Azure DevOps connection (see Configuration section)

## Configuration

Create a connection configuration with your Azure DevOps details:

```python
connection = {
    "org": "https://dev.azure.com/your-organization",
    "pat": "your-personal-access-token",
    "project": "your-project-name"  # optional, can be specified per request
}
```

### Getting a Personal Access Token (PAT)

1. Go to your Azure DevOps organization
2. Click on your profile picture → Personal access tokens
3. Create a new token with the following scopes:
   - Work Items: Read & Write
   - Project and Team: Read
   - Build: Read (optional, for build-related queries)

## Usage

### Starting the MCP Server

```bash
python -m mcp_ado.server
```

The server will start and listen for JSON-RPC requests on stdin/stdout.

### Natural Language Queries

The server can understand and convert natural language queries into WIQL:

```python
# Examples of natural language queries:
"Show all bugs assigned to me"
"Find active user stories with high priority"
"List tasks created this week"
"Show completed work items in current iteration"
"Find bugs with severity critical"
"Show all features in backlog"
"List work items tagged with 'urgent'"
"Find unassigned tasks"
```

## 🛠️ Available Tools (17 Total)

### Project Management (3 tools)
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_projects` | List all projects in the organization | `connection` |
| `get_project` | Get specific project information | `connection`, `project_name` |
| `test_connection` | Test connection to Azure DevOps | `connection` |

### Query & Search (3 tools)
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `search_work_items` | Search using natural language queries | `connection`, `query`, `top` |
| `query_work_items_wiql` | Execute WIQL queries directly | `connection`, `wiql`, `top` |
| `get_query_suggestions` | Get intelligent query suggestions | `connection`, `partial_query` |

### Work Item Operations (6 tools)
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_work_item` | Get specific work item by ID | `connection`, `work_item_id` |
| `get_my_work_items` | Get work items assigned to current user | `connection`, `state`, `work_item_type` |
| `update_work_item` | Update existing work item fields | `connection`, `work_item_id`, `fields` |
| `get_work_items_by_iteration` | Get work items in specific iteration | `connection`, `iteration_path` |
| `get_burndown_data` | Get burndown chart data for iteration | `connection`, `iteration_path` |
| `get_recent_work_items` | Get recently changed work items | `connection`, `days` |

### Creation & Batch (5 tools)
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `create_work_item` | Create any type of work item | `connection`, `work_item_type`, `title`, `fields` |
| `create_bug` | Create bug with bug-specific fields | `connection`, `title`, `repro_steps`, `severity` |
| `create_user_story` | Create user story with story fields | `connection`, `title`, `story_points`, `acceptance_criteria` |
| `create_task` | Create task with task-specific fields | `connection`, `title`, `remaining_work`, `original_estimate` |
| `create_multiple_work_items` | Batch create multiple work items | `connection`, `work_items[]` |

## Examples

### Basic Work Item Search

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_work_items",
    "arguments": {
      "connection": {
        "org": "https://dev.azure.com/myorg",
        "pat": "my-pat-token",
        "project": "MyProject"
      },
      "query": "Show all bugs assigned to me",
      "top": 20
    }
  }
}
```

### Creating a Bug

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "create_bug",
    "arguments": {
      "connection": {
        "org": "https://dev.azure.com/myorg",
        "pat": "my-pat-token",
        "project": "MyProject"
      },
      "title": "Login page crashes on mobile devices",
      "repro_steps": "1. Open app on mobile\n2. Navigate to login\n3. Enter credentials\n4. App crashes",
      "severity": "High",
      "priority": 2
    }
  }
}
```

### Batch Creating Work Items

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "create_multiple_work_items",
    "arguments": {
      "connection": {
        "org": "https://dev.azure.com/myorg",
        "pat": "my-pat-token",
        "project": "MyProject"
      },
      "work_items": [
        {
          "work_item_type": "Task",
          "title": "Design password reset UI",
          "fields": {
            "remaining_work": 8,
            "assigned_to": "john.doe@company.com"
          }
        },
        {
          "work_item_type": "Task",
          "title": "Implement password reset API",
          "fields": {
            "remaining_work": 16,
            "assigned_to": "jane.smith@company.com"
          }
        }
      ]
    }
  }
}
```

## Natural Language Query Examples

The query converter can understand various natural language patterns:

| Query | Generated WIQL |
|-------|----------------|
| "Show all bugs assigned to me" | `SELECT ... WHERE [System.WorkItemType] = 'Bug' AND [System.AssignedTo] = @Me` |
| "Find high priority tasks" | `SELECT ... WHERE [System.WorkItemType] = 'Task' AND [Microsoft.VSTS.Common.Priority] = 2` |
| "List items created this week" | `SELECT ... WHERE [System.CreatedDate] >= '2024-01-08'` |
| "Show completed user stories" | `SELECT ... WHERE [System.WorkItemType] = 'User Story' AND [System.State] = 'Done'` |

## Architecture

The server is built with a modular architecture:

```
mcp_ado/
├── server.py              # Main MCP server
├── ado/
│   ├── client.py          # Azure DevOps REST API client
│   └── models.py          # Data models
├── tools/
│   ├── work_item_tools.py # Work item operations
│   ├── creation_tools.py  # Work item creation
│   ├── project_tools.py   # Project operations
│   └── query_tools.py     # Advanced queries
└── utils/
    ├── query_converter.py # Natural language to WIQL
    └── field_mapper.py    # Field mapping utilities
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Formatting

```bash
# Install formatting tools
pip install black flake8

# Format code
black mcp_ado/
flake8 mcp_ado/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the examples directory for usage patterns
- Review the comprehensive example in `examples/comprehensive_example.py`