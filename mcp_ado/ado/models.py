"""Azure DevOps data models"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class Project:
    """Azure DevOps Project model"""
    id: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    state: Optional[str] = None
    visibility: Optional[str] = None
    last_update_time: Optional[datetime] = None


@dataclass
class User:
    """Azure DevOps User model"""
    id: str
    display_name: str
    unique_name: str
    email: Optional[str] = None
    image_url: Optional[str] = None


@dataclass
class Team:
    """Azure DevOps Team model"""
    id: str
    name: str
    description: Optional[str] = None
    project_id: Optional[str] = None


@dataclass
class WorkItemField:
    """Work item field model"""
    name: str
    value: Any
    field_type: Optional[str] = None


@dataclass
class WorkItem:
    """Azure DevOps Work Item model"""
    id: int
    title: str
    work_item_type: str
    state: str
    fields: Dict[str, Any] = field(default_factory=dict)
    url: Optional[str] = None
    assigned_to: Optional[User] = None
    created_by: Optional[User] = None
    created_date: Optional[datetime] = None
    changed_date: Optional[datetime] = None
    area_path: Optional[str] = None
    iteration_path: Optional[str] = None
    description: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: Optional[int] = None
    severity: Optional[str] = None
    effort: Optional[float] = None
    story_points: Optional[float] = None
    
    @classmethod
    def from_ado_response(cls, data: Dict[str, Any]) -> 'WorkItem':
        """Create WorkItem from Azure DevOps API response"""
        fields = data.get('fields', {})
        
        # Extract common fields
        assigned_to = None
        if 'System.AssignedTo' in fields and fields['System.AssignedTo']:
            assigned_to_data = fields['System.AssignedTo']
            assigned_to = User(
                id=assigned_to_data.get('id', ''),
                display_name=assigned_to_data.get('displayName', ''),
                unique_name=assigned_to_data.get('uniqueName', ''),
                email=assigned_to_data.get('uniqueName', '')
            )
        
        created_by = None
        if 'System.CreatedBy' in fields and fields['System.CreatedBy']:
            created_by_data = fields['System.CreatedBy']
            created_by = User(
                id=created_by_data.get('id', ''),
                display_name=created_by_data.get('displayName', ''),
                unique_name=created_by_data.get('uniqueName', ''),
                email=created_by_data.get('uniqueName', '')
            )
        
        # Parse dates
        created_date = None
        if 'System.CreatedDate' in fields:
            try:
                created_date = datetime.fromisoformat(fields['System.CreatedDate'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        changed_date = None
        if 'System.ChangedDate' in fields:
            try:
                changed_date = datetime.fromisoformat(fields['System.ChangedDate'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        # Extract tags
        tags = []
        if 'System.Tags' in fields and fields['System.Tags']:
            tags = [tag.strip() for tag in fields['System.Tags'].split(';') if tag.strip()]
        
        return cls(
            id=data.get('id', 0),
            title=fields.get('System.Title', ''),
            work_item_type=fields.get('System.WorkItemType', ''),
            state=fields.get('System.State', ''),
            fields=fields,
            url=data.get('url', ''),
            assigned_to=assigned_to,
            created_by=created_by,
            created_date=created_date,
            changed_date=changed_date,
            area_path=fields.get('System.AreaPath', ''),
            iteration_path=fields.get('System.IterationPath', ''),
            description=fields.get('System.Description', ''),
            acceptance_criteria=fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', ''),
            tags=tags,
            priority=fields.get('Microsoft.VSTS.Common.Priority'),
            severity=fields.get('Microsoft.VSTS.Common.Severity'),
            effort=fields.get('Microsoft.VSTS.Scheduling.Effort'),
            story_points=fields.get('Microsoft.VSTS.Scheduling.StoryPoints')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert WorkItem to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'work_item_type': self.work_item_type,
            'state': self.state,
            'url': self.url,
            'assigned_to': self.assigned_to.display_name if self.assigned_to else None,
            'created_by': self.created_by.display_name if self.created_by else None,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'changed_date': self.changed_date.isoformat() if self.changed_date else None,
            'area_path': self.area_path,
            'iteration_path': self.iteration_path,
            'description': self.description,
            'acceptance_criteria': self.acceptance_criteria,
            'tags': self.tags,
            'priority': self.priority,
            'severity': self.severity,
            'effort': self.effort,
            'story_points': self.story_points
        }


@dataclass
class QueryResult:
    """Query result model"""
    work_items: List[WorkItem]
    total_count: int
    query_text: Optional[str] = None
    execution_time: Optional[float] = None