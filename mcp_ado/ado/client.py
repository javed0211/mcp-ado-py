"""Azure DevOps API client"""

import asyncio
import base64
import json
import logging
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, quote
import aiohttp
from datetime import datetime

from .models import WorkItem, Project, User, Team, QueryResult

logger = logging.getLogger(__name__)


class AdoClient:
    """Azure DevOps REST API client"""
    
    def __init__(self, organization: str, personal_access_token: str, project: Optional[str] = None):
        """
        Initialize Azure DevOps client
        
        Args:
            organization: Azure DevOps organization URL or name
            personal_access_token: Personal Access Token for authentication
            project: Default project name (optional)
        """
        self.organization = organization.rstrip('/')
        if not self.organization.startswith('https://'):
            self.organization = f"https://dev.azure.com/{self.organization}"
        
        self.pat = personal_access_token
        self.project = project
        
        # Create authorization header
        auth_string = f":{self.pat}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create session"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Azure DevOps API"""
        session = self._get_session()
        
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise Exception("Authentication failed. Check your Personal Access Token.")
                elif response.status == 403:
                    raise Exception("Access denied. Check your permissions.")
                elif response.status == 404:
                    raise Exception("Resource not found.")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")
                
                return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {str(e)}")
    
    def _build_url(self, path: str, project: Optional[str] = None) -> str:
        """Build API URL"""
        base_url = f"{self.organization}/_apis"
        if project:
            base_url = f"{self.organization}/{quote(project)}/_apis"
        return urljoin(base_url, path)
    
    # Project operations
    async def list_projects(self) -> List[Project]:
        """List all projects in the organization"""
        url = self._build_url("projects?api-version=7.1")
        response = await self._make_request("GET", url)
        
        projects = []
        for project_data in response.get('value', []):
            project = Project(
                id=project_data['id'],
                name=project_data['name'],
                description=project_data.get('description'),
                url=project_data.get('url'),
                state=project_data.get('state'),
                visibility=project_data.get('visibility')
            )
            projects.append(project)
        
        return projects
    
    async def get_project(self, project_name: str) -> Optional[Project]:
        """Get specific project by name"""
        url = self._build_url(f"projects/{quote(project_name)}?api-version=7.1")
        try:
            response = await self._make_request("GET", url)
            return Project(
                id=response['id'],
                name=response['name'],
                description=response.get('description'),
                url=response.get('url'),
                state=response.get('state'),
                visibility=response.get('visibility')
            )
        except Exception:
            return None
    
    # Work Item operations
    async def get_work_item(self, work_item_id: int, project: Optional[str] = None) -> Optional[WorkItem]:
        """Get a specific work item by ID"""
        project = project or self.project
        if not project:
            raise ValueError("Project must be specified")
        
        url = self._build_url(f"wit/workitems/{work_item_id}?api-version=7.1", project)
        try:
            response = await self._make_request("GET", url)
            return WorkItem.from_ado_response(response)
        except Exception:
            return None
    
    async def get_work_items(self, work_item_ids: List[int], project: Optional[str] = None) -> List[WorkItem]:
        """Get multiple work items by IDs"""
        project = project or self.project
        if not project:
            raise ValueError("Project must be specified")
        
        if not work_item_ids:
            return []
        
        ids_str = ','.join(map(str, work_item_ids))
        url = self._build_url(f"wit/workitems?ids={ids_str}&api-version=7.1", project)
        
        response = await self._make_request("GET", url)
        work_items = []
        for item_data in response.get('value', []):
            work_items.append(WorkItem.from_ado_response(item_data))
        
        return work_items
    
    async def query_work_items(self, wiql: str, project: Optional[str] = None, top: int = 100) -> QueryResult:
        """Execute WIQL query to get work items"""
        project = project or self.project
        if not project:
            raise ValueError("Project must be specified")
        
        start_time = datetime.now()
        
        # Execute query
        query_url = self._build_url("wit/wiql?api-version=7.1", project)
        query_data = {"query": wiql}
        
        query_response = await self._make_request("POST", query_url, json=query_data)
        
        work_item_refs = query_response.get('workItems', [])
        if not work_item_refs:
            return QueryResult(work_items=[], total_count=0, query_text=wiql)
        
        # Limit results
        work_item_refs = work_item_refs[:top]
        work_item_ids = [ref['id'] for ref in work_item_refs]
        
        # Get full work item details
        work_items = await self.get_work_items(work_item_ids, project)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return QueryResult(
            work_items=work_items,
            total_count=len(work_items),
            query_text=wiql,
            execution_time=execution_time
        )
    
    async def create_work_item(self, work_item_type: str, title: str, fields: Optional[Dict[str, Any]] = None, 
                             project: Optional[str] = None) -> WorkItem:
        """Create a new work item"""
        project = project or self.project
        if not project:
            raise ValueError("Project must be specified")
        
        url = self._build_url(f"wit/workitems/${quote(work_item_type)}?api-version=7.1", project)
        
        # Build patch document
        patch_document = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": title
            }
        ]
        
        # Add additional fields
        if fields:
            for field_name, field_value in fields.items():
                if not field_name.startswith('/fields/'):
                    field_name = f"/fields/{field_name}"
                patch_document.append({
                    "op": "add",
                    "path": field_name,
                    "value": field_value
                })
        
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json-patch+json'
        
        response = await self._make_request("POST", url, json=patch_document, headers=headers)
        return WorkItem.from_ado_response(response)
    
    async def update_work_item(self, work_item_id: int, fields: Dict[str, Any], 
                             project: Optional[str] = None) -> WorkItem:
        """Update an existing work item"""
        project = project or self.project
        if not project:
            raise ValueError("Project must be specified")
        
        url = self._build_url(f"wit/workitems/{work_item_id}?api-version=7.1", project)
        
        # Build patch document
        patch_document = []
        for field_name, field_value in fields.items():
            if not field_name.startswith('/fields/'):
                field_name = f"/fields/{field_name}"
            patch_document.append({
                "op": "replace",
                "path": field_name,
                "value": field_value
            })
        
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json-patch+json'
        
        response = await self._make_request("PATCH", url, json=patch_document, headers=headers)
        return WorkItem.from_ado_response(response)
    
    async def delete_work_item(self, work_item_id: int, project: Optional[str] = None) -> bool:
        """Delete a work item (move to recycle bin)"""
        project = project or self.project
        if not project:
            raise ValueError("Project must be specified")
        
        url = self._build_url(f"wit/workitems/{work_item_id}?api-version=7.1", project)
        
        try:
            await self._make_request("DELETE", url)
            return True
        except Exception:
            return False
    
    # Team operations
    async def get_teams(self, project: Optional[str] = None) -> List[Team]:
        """Get teams in a project"""
        project = project or self.project
        if not project:
            raise ValueError("Project must be specified")
        
        url = self._build_url(f"projects/{quote(project)}/teams?api-version=7.1")
        response = await self._make_request("GET", url)
        
        teams = []
        for team_data in response.get('value', []):
            team = Team(
                id=team_data['id'],
                name=team_data['name'],
                description=team_data.get('description'),
                project_id=team_data.get('projectId')
            )
            teams.append(team)
        
        return teams
    
    # Utility methods
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Azure DevOps"""
        try:
            projects = await self.list_projects()
            return {
                "success": True,
                "message": f"Successfully connected to {self.organization}",
                "project_count": len(projects)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
            self.session = None