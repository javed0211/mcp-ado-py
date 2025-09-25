"""Project management tools"""

from typing import Dict, List, Optional, Any
import logging

from ..ado.client import AdoClient
from ..ado.models import Project, Team

logger = logging.getLogger(__name__)


class ProjectTools:
    """Tools for project operations"""
    
    async def list_projects(self, connection: Dict[str, str]) -> Dict[str, Any]:
        """List all projects in the organization"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat']
            ) as client:
                projects = await client.list_projects()
                
                return {
                    "success": True,
                    "projects": [
                        {
                            "id": project.id,
                            "name": project.name,
                            "description": project.description,
                            "url": project.url,
                            "state": project.state,
                            "visibility": project.visibility
                        }
                        for project in projects
                    ],
                    "count": len(projects)
                }
        
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_project(self, connection: Dict[str, str], project_name: str) -> Dict[str, Any]:
        """Get specific project information"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat']
            ) as client:
                project = await client.get_project(project_name)
                
                if not project:
                    return {
                        "success": False,
                        "error": f"Project '{project_name}' not found"
                    }
                
                return {
                    "success": True,
                    "project": {
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "url": project.url,
                        "state": project.state,
                        "visibility": project.visibility
                    }
                }
        
        except Exception as e:
            logger.error(f"Error getting project '{project_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "project_name": project_name
            }
    
    async def get_project_teams(self, connection: Dict[str, str], project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get teams in a project"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                teams = await client.get_teams(project)
                
                return {
                    "success": True,
                    "project": project,
                    "teams": [
                        {
                            "id": team.id,
                            "name": team.name,
                            "description": team.description,
                            "project_id": team.project_id
                        }
                        for team in teams
                    ],
                    "count": len(teams)
                }
        
        except Exception as e:
            logger.error(f"Error getting teams for project '{project}': {e}")
            return {
                "success": False,
                "error": str(e),
                "project": project
            }
    
    async def get_project_areas(self, connection: Dict[str, str], project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get area paths in a project"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                # Get area paths
                url = client._build_url("wit/classificationnodes/areas?$depth=10&api-version=7.1", project)
                response = await client._make_request("GET", url)
                
                def extract_areas(node, path=""):
                    areas = []
                    current_path = f"{path}\\{node['name']}" if path else node['name']
                    areas.append({
                        "id": node.get('id'),
                        "name": node['name'],
                        "path": current_path,
                        "has_children": bool(node.get('children'))
                    })
                    
                    for child in node.get('children', []):
                        areas.extend(extract_areas(child, current_path))
                    
                    return areas
                
                areas = extract_areas(response)
                
                return {
                    "success": True,
                    "project": project,
                    "areas": areas,
                    "count": len(areas)
                }
        
        except Exception as e:
            logger.error(f"Error getting areas for project '{project}': {e}")
            return {
                "success": False,
                "error": str(e),
                "project": project
            }
    
    async def get_project_iterations(self, connection: Dict[str, str], project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get iteration paths in a project"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                # Get iteration paths
                url = client._build_url("wit/classificationnodes/iterations?$depth=10&api-version=7.1", project)
                response = await client._make_request("GET", url)
                
                def extract_iterations(node, path=""):
                    iterations = []
                    current_path = f"{path}\\{node['name']}" if path else node['name']
                    
                    iteration_data = {
                        "id": node.get('id'),
                        "name": node['name'],
                        "path": current_path,
                        "has_children": bool(node.get('children'))
                    }
                    
                    # Add iteration-specific attributes if available
                    attributes = node.get('attributes', {})
                    if 'startDate' in attributes:
                        iteration_data['start_date'] = attributes['startDate']
                    if 'finishDate' in attributes:
                        iteration_data['finish_date'] = attributes['finishDate']
                    
                    iterations.append(iteration_data)
                    
                    for child in node.get('children', []):
                        iterations.extend(extract_iterations(child, current_path))
                    
                    return iterations
                
                iterations = extract_iterations(response)
                
                return {
                    "success": True,
                    "project": project,
                    "iterations": iterations,
                    "count": len(iterations)
                }
        
        except Exception as e:
            logger.error(f"Error getting iterations for project '{project}': {e}")
            return {
                "success": False,
                "error": str(e),
                "project": project
            }
    
    async def get_project_work_item_types(self, connection: Dict[str, str], project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get available work item types in a project"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                # Get work item types
                url = client._build_url("wit/workitemtypes?api-version=7.1", project)
                response = await client._make_request("GET", url)
                
                work_item_types = []
                for wit_data in response.get('value', []):
                    work_item_types.append({
                        "name": wit_data['name'],
                        "description": wit_data.get('description', ''),
                        "icon": wit_data.get('icon', {}).get('url', ''),
                        "color": wit_data.get('color', ''),
                        "is_disabled": wit_data.get('isDisabled', False)
                    })
                
                return {
                    "success": True,
                    "project": project,
                    "work_item_types": work_item_types,
                    "count": len(work_item_types)
                }
        
        except Exception as e:
            logger.error(f"Error getting work item types for project '{project}': {e}")
            return {
                "success": False,
                "error": str(e),
                "project": project
            }
    
    async def get_project_fields(self, connection: Dict[str, str], project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get available fields in a project"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                # Get work item fields
                url = client._build_url("wit/fields?api-version=7.1", project)
                response = await client._make_request("GET", url)
                
                fields = []
                for field_data in response.get('value', []):
                    fields.append({
                        "name": field_data['name'],
                        "reference_name": field_data['referenceName'],
                        "description": field_data.get('description', ''),
                        "type": field_data.get('type', ''),
                        "usage": field_data.get('usage', ''),
                        "read_only": field_data.get('readOnly', False),
                        "can_sort_by": field_data.get('canSortBy', False),
                        "is_queryable": field_data.get('isQueryable', False),
                        "supported_operations": field_data.get('supportedOperations', [])
                    })
                
                return {
                    "success": True,
                    "project": project,
                    "fields": fields,
                    "count": len(fields)
                }
        
        except Exception as e:
            logger.error(f"Error getting fields for project '{project}': {e}")
            return {
                "success": False,
                "error": str(e),
                "project": project
            }
    
    async def test_connection(self, connection: Dict[str, str]) -> Dict[str, Any]:
        """Test connection to Azure DevOps"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat']
            ) as client:
                result = await client.test_connection()
                return result
        
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return {
                "success": False,
                "error": str(e)
            }