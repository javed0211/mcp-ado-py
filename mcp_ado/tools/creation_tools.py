"""Tools for creating Azure DevOps work items and other entities"""

from typing import Dict, List, Optional, Any
import logging

from ..ado.client import AdoClient
from ..ado.models import WorkItem
from ..utils.field_mapper import FieldMapper

logger = logging.getLogger(__name__)


class CreationTools:
    """Tools for creating Azure DevOps entities"""
    
    def __init__(self):
        self.field_mapper = FieldMapper()
    
    async def create_work_item(self, connection: Dict[str, str], work_item_type: str, 
                             title: str, fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new work item"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                # Validate work item type
                valid_types = ['Bug', 'Task', 'User Story', 'Feature', 'Epic', 'Test Case', 'Issue']
                if work_item_type not in valid_types:
                    return {
                        "success": False,
                        "error": f"Invalid work item type '{work_item_type}'. Valid types: {', '.join(valid_types)}"
                    }
                
                # Map and validate fields
                mapped_fields = {}
                if fields:
                    mapped_fields = self.field_mapper.map_fields_for_creation(fields, work_item_type)
                
                # Create work item
                work_item = await client.create_work_item(
                    work_item_type, title, mapped_fields, connection.get('project')
                )
                
                return {
                    "success": True,
                    "work_item": work_item.to_dict(),
                    "message": f"Created {work_item_type} '{title}' with ID {work_item.id}"
                }
        
        except Exception as e:
            logger.error(f"Error creating work item: {e}")
            return {
                "success": False,
                "error": str(e),
                "work_item_type": work_item_type,
                "title": title
            }
    
    async def create_bug(self, connection: Dict[str, str], title: str, 
                        repro_steps: str, severity: Optional[str] = None,
                        priority: Optional[int] = None, assigned_to: Optional[str] = None,
                        additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a bug work item with bug-specific fields"""
        fields = {
            'Microsoft.VSTS.TCM.ReproSteps': repro_steps
        }
        
        if severity:
            fields['Microsoft.VSTS.Common.Severity'] = severity
        if priority:
            fields['Microsoft.VSTS.Common.Priority'] = priority
        if assigned_to:
            fields['System.AssignedTo'] = assigned_to
        
        if additional_fields:
            fields.update(additional_fields)
        
        return await self.create_work_item(connection, 'Bug', title, fields)
    
    async def create_task(self, connection: Dict[str, str], title: str,
                         remaining_work: Optional[float] = None, activity: Optional[str] = None,
                         assigned_to: Optional[str] = None, 
                         additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a task work item with task-specific fields"""
        fields = {}
        
        if remaining_work:
            fields['Microsoft.VSTS.Scheduling.RemainingWork'] = remaining_work
        if activity:
            fields['Microsoft.VSTS.Common.Activity'] = activity
        if assigned_to:
            fields['System.AssignedTo'] = assigned_to
        
        if additional_fields:
            fields.update(additional_fields)
        
        return await self.create_work_item(connection, 'Task', title, fields)
    
    async def create_user_story(self, connection: Dict[str, str], title: str,
                               story_points: Optional[float] = None, 
                               acceptance_criteria: Optional[str] = None,
                               priority: Optional[int] = None, assigned_to: Optional[str] = None,
                               additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a user story work item with story-specific fields"""
        fields = {}
        
        if story_points:
            fields['Microsoft.VSTS.Scheduling.StoryPoints'] = story_points
        if acceptance_criteria:
            fields['Microsoft.VSTS.Common.AcceptanceCriteria'] = acceptance_criteria
        if priority:
            fields['Microsoft.VSTS.Common.Priority'] = priority
        if assigned_to:
            fields['System.AssignedTo'] = assigned_to
        
        if additional_fields:
            fields.update(additional_fields)
        
        return await self.create_work_item(connection, 'User Story', title, fields)
    
    async def create_feature(self, connection: Dict[str, str], title: str,
                            business_value: Optional[int] = None, effort: Optional[float] = None,
                            target_date: Optional[str] = None, assigned_to: Optional[str] = None,
                            additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a feature work item with feature-specific fields"""
        fields = {}
        
        if business_value:
            fields['Microsoft.VSTS.Common.BusinessValue'] = business_value
        if effort:
            fields['Microsoft.VSTS.Scheduling.Effort'] = effort
        if target_date:
            fields['Microsoft.VSTS.Scheduling.TargetDate'] = target_date
        if assigned_to:
            fields['System.AssignedTo'] = assigned_to
        
        if additional_fields:
            fields.update(additional_fields)
        
        return await self.create_work_item(connection, 'Feature', title, fields)
    
    async def create_epic(self, connection: Dict[str, str], title: str,
                         business_value: Optional[int] = None, effort: Optional[float] = None,
                         start_date: Optional[str] = None, target_date: Optional[str] = None,
                         assigned_to: Optional[str] = None,
                         additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an epic work item with epic-specific fields"""
        fields = {}
        
        if business_value:
            fields['Microsoft.VSTS.Common.BusinessValue'] = business_value
        if effort:
            fields['Microsoft.VSTS.Scheduling.Effort'] = effort
        if start_date:
            fields['Microsoft.VSTS.Scheduling.StartDate'] = start_date
        if target_date:
            fields['Microsoft.VSTS.Scheduling.TargetDate'] = target_date
        if assigned_to:
            fields['System.AssignedTo'] = assigned_to
        
        if additional_fields:
            fields.update(additional_fields)
        
        return await self.create_work_item(connection, 'Epic', title, fields)
    
    async def create_test_case(self, connection: Dict[str, str], title: str,
                              steps: str, priority: Optional[int] = None,
                              assigned_to: Optional[str] = None,
                              additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a test case work item with test case-specific fields"""
        fields = {
            'Microsoft.VSTS.TCM.Steps': steps
        }
        
        if priority:
            fields['Microsoft.VSTS.Common.Priority'] = priority
        if assigned_to:
            fields['System.AssignedTo'] = assigned_to
        
        if additional_fields:
            fields.update(additional_fields)
        
        return await self.create_work_item(connection, 'Test Case', title, fields)
    
    async def create_multiple_work_items(self, connection: Dict[str, str], 
                                       work_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple work items in batch"""
        results = []
        errors = []
        
        for item_data in work_items:
            try:
                work_item_type = item_data.get('work_item_type', 'Task')
                title = item_data.get('title', 'Untitled')
                fields = item_data.get('fields', {})
                
                result = await self.create_work_item(connection, work_item_type, title, fields)
                results.append(result)
                
                if not result.get('success'):
                    errors.append(result)
                    
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "item_data": item_data
                }
                results.append(error_result)
                errors.append(error_result)
        
        return {
            "success": len(errors) == 0,
            "results": results,
            "created_count": len([r for r in results if r.get('success')]),
            "error_count": len(errors),
            "errors": errors
        }
    
    async def create_work_items_from_template(self, connection: Dict[str, str], 
                                            template_name: str, 
                                            template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create work items from a predefined template"""
        templates = {
            'sprint_planning': self._create_sprint_planning_items,
            'bug_investigation': self._create_bug_investigation_items,
            'feature_development': self._create_feature_development_items,
            'user_story_breakdown': self._create_user_story_breakdown_items
        }
        
        if template_name not in templates:
            return {
                "success": False,
                "error": f"Unknown template '{template_name}'. Available templates: {', '.join(templates.keys())}"
            }
        
        try:
            work_items_data = templates[template_name](template_data)
            return await self.create_multiple_work_items(connection, work_items_data)
        
        except Exception as e:
            logger.error(f"Error creating work items from template '{template_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "template_name": template_name
            }
    
    def _create_sprint_planning_items(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create work items for sprint planning"""
        sprint_name = data.get('sprint_name', 'Sprint')
        features = data.get('features', [])
        
        work_items = []
        
        # Create epic for the sprint
        work_items.append({
            'work_item_type': 'Epic',
            'title': f'{sprint_name} - Development Epic',
            'fields': {
                'System.Description': f'Epic for {sprint_name} development work'
            }
        })
        
        # Create features and their tasks
        for feature in features:
            feature_title = feature.get('title', 'Feature')
            tasks = feature.get('tasks', [])
            
            work_items.append({
                'work_item_type': 'Feature',
                'title': feature_title,
                'fields': {
                    'System.Description': feature.get('description', ''),
                    'Microsoft.VSTS.Common.BusinessValue': feature.get('business_value', 50)
                }
            })
            
            for task in tasks:
                work_items.append({
                    'work_item_type': 'Task',
                    'title': task.get('title', 'Task'),
                    'fields': {
                        'System.Description': task.get('description', ''),
                        'Microsoft.VSTS.Scheduling.RemainingWork': task.get('hours', 8),
                        'System.AssignedTo': task.get('assigned_to', '')
                    }
                })
        
        return work_items
    
    def _create_bug_investigation_items(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create work items for bug investigation"""
        bug_title = data.get('bug_title', 'Bug Investigation')
        severity = data.get('severity', 'Medium')
        
        work_items = [
            {
                'work_item_type': 'Bug',
                'title': bug_title,
                'fields': {
                    'Microsoft.VSTS.TCM.ReproSteps': data.get('repro_steps', 'Steps to reproduce the issue'),
                    'Microsoft.VSTS.Common.Severity': severity,
                    'Microsoft.VSTS.Common.Priority': data.get('priority', 2)
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Investigate: {bug_title}',
                'fields': {
                    'System.Description': 'Investigate the root cause of the bug',
                    'Microsoft.VSTS.Scheduling.RemainingWork': 4
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Fix: {bug_title}',
                'fields': {
                    'System.Description': 'Implement fix for the bug',
                    'Microsoft.VSTS.Scheduling.RemainingWork': 8
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Test: {bug_title}',
                'fields': {
                    'System.Description': 'Test the bug fix',
                    'Microsoft.VSTS.Scheduling.RemainingWork': 2
                }
            }
        ]
        
        return work_items
    
    def _create_feature_development_items(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create work items for feature development"""
        feature_title = data.get('feature_title', 'New Feature')
        
        work_items = [
            {
                'work_item_type': 'Feature',
                'title': feature_title,
                'fields': {
                    'System.Description': data.get('description', ''),
                    'Microsoft.VSTS.Common.BusinessValue': data.get('business_value', 100)
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Design: {feature_title}',
                'fields': {
                    'System.Description': 'Design the feature architecture and UI',
                    'Microsoft.VSTS.Scheduling.RemainingWork': 16
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Implement: {feature_title}',
                'fields': {
                    'System.Description': 'Implement the feature functionality',
                    'Microsoft.VSTS.Scheduling.RemainingWork': 32
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Test: {feature_title}',
                'fields': {
                    'System.Description': 'Create and execute tests for the feature',
                    'Microsoft.VSTS.Scheduling.RemainingWork': 16
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Documentation: {feature_title}',
                'fields': {
                    'System.Description': 'Create user and technical documentation',
                    'Microsoft.VSTS.Scheduling.RemainingWork': 8
                }
            }
        ]
        
        return work_items
    
    def _create_user_story_breakdown_items(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create work items for user story breakdown"""
        story_title = data.get('story_title', 'User Story')
        story_points = data.get('story_points', 5)
        
        # Estimate task hours based on story points (rough estimation)
        total_hours = story_points * 6  # 6 hours per story point
        
        work_items = [
            {
                'work_item_type': 'User Story',
                'title': story_title,
                'fields': {
                    'System.Description': data.get('description', ''),
                    'Microsoft.VSTS.Common.AcceptanceCriteria': data.get('acceptance_criteria', ''),
                    'Microsoft.VSTS.Scheduling.StoryPoints': story_points
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Analysis: {story_title}',
                'fields': {
                    'System.Description': 'Analyze requirements and create technical approach',
                    'Microsoft.VSTS.Scheduling.RemainingWork': total_hours * 0.2
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Development: {story_title}',
                'fields': {
                    'System.Description': 'Implement the user story functionality',
                    'Microsoft.VSTS.Scheduling.RemainingWork': total_hours * 0.6
                }
            },
            {
                'work_item_type': 'Task',
                'title': f'Testing: {story_title}',
                'fields': {
                    'System.Description': 'Test the user story implementation',
                    'Microsoft.VSTS.Scheduling.RemainingWork': total_hours * 0.2
                }
            }
        ]
        
        return work_items