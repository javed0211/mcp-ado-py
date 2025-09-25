"""Query and reporting tools"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta

from ..ado.client import AdoClient
from ..utils.query_converter import QueryConverter

logger = logging.getLogger(__name__)


class QueryTools:
    """Tools for advanced querying and reporting"""
    
    def __init__(self):
        self.query_converter = QueryConverter()
    
    async def get_work_items_by_iteration(self, connection: Dict[str, str], 
                                        iteration_path: str, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get all work items in a specific iteration"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            wiql = f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], 
                   [System.AssignedTo], [Microsoft.VSTS.Scheduling.StoryPoints], 
                   [Microsoft.VSTS.Scheduling.RemainingWork]
            FROM WorkItems
            WHERE [System.IterationPath] UNDER '{iteration_path}'
            ORDER BY [System.WorkItemType], [System.State]
            """
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                result = await client.query_work_items(wiql, project)
                
                # Group by work item type and state
                grouped_items = {}
                total_story_points = 0
                total_remaining_work = 0
                
                for work_item in result.work_items:
                    wit_type = work_item.work_item_type
                    state = work_item.state
                    
                    if wit_type not in grouped_items:
                        grouped_items[wit_type] = {}
                    if state not in grouped_items[wit_type]:
                        grouped_items[wit_type][state] = []
                    
                    grouped_items[wit_type][state].append(work_item.to_dict())
                    
                    # Sum up story points and remaining work
                    if work_item.story_points:
                        total_story_points += work_item.story_points
                    if work_item.fields.get('Microsoft.VSTS.Scheduling.RemainingWork'):
                        total_remaining_work += float(work_item.fields['Microsoft.VSTS.Scheduling.RemainingWork'])
                
                return {
                    "success": True,
                    "iteration_path": iteration_path,
                    "project": project,
                    "work_items": [wi.to_dict() for wi in result.work_items],
                    "grouped_items": grouped_items,
                    "summary": {
                        "total_count": result.total_count,
                        "total_story_points": total_story_points,
                        "total_remaining_work": total_remaining_work
                    }
                }
        
        except Exception as e:
            logger.error(f"Error getting work items for iteration '{iteration_path}': {e}")
            return {
                "success": False,
                "error": str(e),
                "iteration_path": iteration_path
            }
    
    async def get_work_items_by_area(self, connection: Dict[str, str], 
                                   area_path: str, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get all work items in a specific area"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            wiql = f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], 
                   [System.AssignedTo], [System.CreatedDate], [System.ChangedDate]
            FROM WorkItems
            WHERE [System.AreaPath] UNDER '{area_path}'
            ORDER BY [System.ChangedDate] DESC
            """
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                result = await client.query_work_items(wiql, project)
                
                return {
                    "success": True,
                    "area_path": area_path,
                    "project": project,
                    "work_items": [wi.to_dict() for wi in result.work_items],
                    "count": result.total_count
                }
        
        except Exception as e:
            logger.error(f"Error getting work items for area '{area_path}': {e}")
            return {
                "success": False,
                "error": str(e),
                "area_path": area_path
            }
    
    async def get_my_work_items(self, connection: Dict[str, str], 
                              project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get work items assigned to the current user"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            wiql = """
            SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], 
                   [System.CreatedDate], [System.ChangedDate], [Microsoft.VSTS.Common.Priority]
            FROM WorkItems
            WHERE [System.AssignedTo] = @Me
            ORDER BY [Microsoft.VSTS.Common.Priority] ASC, [System.ChangedDate] DESC
            """
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                result = await client.query_work_items(wiql, project)
                
                # Group by state
                by_state = {}
                for work_item in result.work_items:
                    state = work_item.state
                    if state not in by_state:
                        by_state[state] = []
                    by_state[state].append(work_item.to_dict())
                
                return {
                    "success": True,
                    "project": project,
                    "work_items": [wi.to_dict() for wi in result.work_items],
                    "by_state": by_state,
                    "count": result.total_count
                }
        
        except Exception as e:
            logger.error(f"Error getting my work items: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_recent_work_items(self, connection: Dict[str, str], 
                                  days: int = 7, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get work items changed in the last N days"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            wiql = f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], 
                   [System.AssignedTo], [System.ChangedDate], [System.ChangedBy]
            FROM WorkItems
            WHERE [System.ChangedDate] >= '{cutoff_date}'
            ORDER BY [System.ChangedDate] DESC
            """
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                result = await client.query_work_items(wiql, project)
                
                # Group by day
                by_day = {}
                for work_item in result.work_items:
                    if work_item.changed_date:
                        day = work_item.changed_date.strftime('%Y-%m-%d')
                        if day not in by_day:
                            by_day[day] = []
                        by_day[day].append(work_item.to_dict())
                
                return {
                    "success": True,
                    "project": project,
                    "days": days,
                    "cutoff_date": cutoff_date,
                    "work_items": [wi.to_dict() for wi in result.work_items],
                    "by_day": by_day,
                    "count": result.total_count
                }
        
        except Exception as e:
            logger.error(f"Error getting recent work items: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_work_items_by_tag(self, connection: Dict[str, str], 
                                  tag: str, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get work items with a specific tag"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            wiql = f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], 
                   [System.AssignedTo], [System.Tags]
            FROM WorkItems
            WHERE [System.Tags] CONTAINS '{tag}'
            ORDER BY [System.ChangedDate] DESC
            """
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                result = await client.query_work_items(wiql, project)
                
                return {
                    "success": True,
                    "project": project,
                    "tag": tag,
                    "work_items": [wi.to_dict() for wi in result.work_items],
                    "count": result.total_count
                }
        
        except Exception as e:
            logger.error(f"Error getting work items with tag '{tag}': {e}")
            return {
                "success": False,
                "error": str(e),
                "tag": tag
            }
    
    async def get_burndown_data(self, connection: Dict[str, str], 
                              iteration_path: str, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get burndown chart data for an iteration"""
        try:
            project = project_name or connection.get('project')
            if not project:
                return {
                    "success": False,
                    "error": "Project name must be specified"
                }
            
            # Get all work items in the iteration
            wiql = f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], 
                   [Microsoft.VSTS.Scheduling.StoryPoints], [Microsoft.VSTS.Scheduling.RemainingWork],
                   [Microsoft.VSTS.Scheduling.CompletedWork], [Microsoft.VSTS.Scheduling.OriginalEstimate]
            FROM WorkItems
            WHERE [System.IterationPath] UNDER '{iteration_path}'
            """
            
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=project
            ) as client:
                result = await client.query_work_items(wiql, project)
                
                # Calculate burndown metrics
                total_story_points = 0
                completed_story_points = 0
                total_remaining_work = 0
                total_completed_work = 0
                total_original_estimate = 0
                
                by_state = {}
                
                for work_item in result.work_items:
                    state = work_item.state
                    if state not in by_state:
                        by_state[state] = {"count": 0, "story_points": 0, "remaining_work": 0}
                    
                    by_state[state]["count"] += 1
                    
                    if work_item.story_points:
                        total_story_points += work_item.story_points
                        by_state[state]["story_points"] += work_item.story_points
                        
                        if state.lower() in ['done', 'closed', 'completed']:
                            completed_story_points += work_item.story_points
                    
                    remaining_work = work_item.fields.get('Microsoft.VSTS.Scheduling.RemainingWork', 0)
                    if remaining_work:
                        remaining_work = float(remaining_work)
                        total_remaining_work += remaining_work
                        by_state[state]["remaining_work"] += remaining_work
                    
                    completed_work = work_item.fields.get('Microsoft.VSTS.Scheduling.CompletedWork', 0)
                    if completed_work:
                        total_completed_work += float(completed_work)
                    
                    original_estimate = work_item.fields.get('Microsoft.VSTS.Scheduling.OriginalEstimate', 0)
                    if original_estimate:
                        total_original_estimate += float(original_estimate)
                
                # Calculate completion percentages
                story_points_completion = (completed_story_points / total_story_points * 100) if total_story_points > 0 else 0
                work_completion = (total_completed_work / (total_completed_work + total_remaining_work) * 100) if (total_completed_work + total_remaining_work) > 0 else 0
                
                return {
                    "success": True,
                    "iteration_path": iteration_path,
                    "project": project,
                    "summary": {
                        "total_work_items": result.total_count,
                        "total_story_points": total_story_points,
                        "completed_story_points": completed_story_points,
                        "story_points_completion_percent": round(story_points_completion, 2),
                        "total_remaining_work": total_remaining_work,
                        "total_completed_work": total_completed_work,
                        "total_original_estimate": total_original_estimate,
                        "work_completion_percent": round(work_completion, 2)
                    },
                    "by_state": by_state,
                    "work_items": [wi.to_dict() for wi in result.work_items]
                }
        
        except Exception as e:
            logger.error(f"Error getting burndown data for iteration '{iteration_path}': {e}")
            return {
                "success": False,
                "error": str(e),
                "iteration_path": iteration_path
            }
    
    async def get_team_velocity(self, connection: Dict[str, str], 
                              team_name: str, iterations: int = 5, 
                              project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get team velocity data over the last N iterations"""
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
                # Get recent iterations
                url = client._build_url("wit/classificationnodes/iterations?$depth=2&api-version=7.1", project)
                response = await client._make_request("GET", url)
                
                # Extract iteration paths (simplified - would need more logic for proper iteration selection)
                iteration_paths = []
                def extract_iterations(node, path=""):
                    current_path = f"{path}\\{node['name']}" if path else node['name']
                    if node.get('attributes', {}).get('startDate'):
                        iteration_paths.append(current_path)
                    for child in node.get('children', []):
                        extract_iterations(child, current_path)
                
                extract_iterations(response)
                
                # Get velocity data for each iteration
                velocity_data = []
                for iteration_path in iteration_paths[-iterations:]:  # Last N iterations
                    burndown = await self.get_burndown_data(connection, iteration_path, project)
                    if burndown.get('success'):
                        velocity_data.append({
                            "iteration": iteration_path,
                            "completed_story_points": burndown['summary']['completed_story_points'],
                            "total_story_points": burndown['summary']['total_story_points'],
                            "completion_percent": burndown['summary']['story_points_completion_percent']
                        })
                
                # Calculate average velocity
                avg_velocity = sum(v['completed_story_points'] for v in velocity_data) / len(velocity_data) if velocity_data else 0
                
                return {
                    "success": True,
                    "team_name": team_name,
                    "project": project,
                    "iterations_analyzed": len(velocity_data),
                    "average_velocity": round(avg_velocity, 2),
                    "velocity_data": velocity_data
                }
        
        except Exception as e:
            logger.error(f"Error getting team velocity for '{team_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "team_name": team_name
            }