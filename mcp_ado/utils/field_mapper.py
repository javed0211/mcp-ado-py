"""Field mapping utilities for Azure DevOps work items"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class FieldMapper:
    """Maps common field names to Azure DevOps field references"""
    
    def __init__(self):
        self.field_mappings = {
            # System fields
            'id': 'System.Id',
            'title': 'System.Title',
            'description': 'System.Description',
            'state': 'System.State',
            'reason': 'System.Reason',
            'assigned_to': 'System.AssignedTo',
            'created_by': 'System.CreatedBy',
            'changed_by': 'System.ChangedBy',
            'created_date': 'System.CreatedDate',
            'changed_date': 'System.ChangedDate',
            'work_item_type': 'System.WorkItemType',
            'area_path': 'System.AreaPath',
            'iteration_path': 'System.IterationPath',
            'tags': 'System.Tags',
            'history': 'System.History',
            'rev': 'System.Rev',
            'authorized_date': 'System.AuthorizedDate',
            'watermark': 'System.Watermark',
            'comment_count': 'System.CommentCount',
            'hyperlink_count': 'System.HyperLinkCount',
            'attachment_count': 'System.AttachedFileCount',
            'external_link_count': 'System.ExternalLinkCount',
            'related_link_count': 'System.RelatedLinkCount',
            'node_name': 'System.NodeName',
            'area_id': 'System.AreaId',
            'area_level1': 'System.AreaLevel1',
            'area_level2': 'System.AreaLevel2',
            'area_level3': 'System.AreaLevel3',
            'area_level4': 'System.AreaLevel4',
            'iteration_id': 'System.IterationId',
            'iteration_level1': 'System.IterationLevel1',
            'iteration_level2': 'System.IterationLevel2',
            'iteration_level3': 'System.IterationLevel3',
            'iteration_level4': 'System.IterationLevel4',
            
            # Microsoft VSTS Common fields
            'priority': 'Microsoft.VSTS.Common.Priority',
            'severity': 'Microsoft.VSTS.Common.Severity',
            'value_area': 'Microsoft.VSTS.Common.ValueArea',
            'risk': 'Microsoft.VSTS.Common.Risk',
            'stack_rank': 'Microsoft.VSTS.Common.StackRank',
            'business_value': 'Microsoft.VSTS.Common.BusinessValue',
            'time_criticality': 'Microsoft.VSTS.Common.TimeCriticality',
            'triage': 'Microsoft.VSTS.Common.Triage',
            'acceptance_criteria': 'Microsoft.VSTS.Common.AcceptanceCriteria',
            'activity': 'Microsoft.VSTS.Common.Activity',
            'discipline': 'Microsoft.VSTS.Common.Discipline',
            'resolution': 'Microsoft.VSTS.Common.Resolution',
            'state_change_date': 'Microsoft.VSTS.Common.StateChangeDate',
            'activated_date': 'Microsoft.VSTS.Common.ActivatedDate',
            'activated_by': 'Microsoft.VSTS.Common.ActivatedBy',
            'resolved_date': 'Microsoft.VSTS.Common.ResolvedDate',
            'resolved_by': 'Microsoft.VSTS.Common.ResolvedBy',
            'resolved_reason': 'Microsoft.VSTS.Common.ResolvedReason',
            'closed_date': 'Microsoft.VSTS.Common.ClosedDate',
            'closed_by': 'Microsoft.VSTS.Common.ClosedBy',
            'rating': 'Microsoft.VSTS.Common.Rating',
            
            # Microsoft VSTS Scheduling fields
            'story_points': 'Microsoft.VSTS.Scheduling.StoryPoints',
            'effort': 'Microsoft.VSTS.Scheduling.Effort',
            'original_estimate': 'Microsoft.VSTS.Scheduling.OriginalEstimate',
            'remaining_work': 'Microsoft.VSTS.Scheduling.RemainingWork',
            'completed_work': 'Microsoft.VSTS.Scheduling.CompletedWork',
            'start_date': 'Microsoft.VSTS.Scheduling.StartDate',
            'finish_date': 'Microsoft.VSTS.Scheduling.FinishDate',
            'due_date': 'Microsoft.VSTS.Scheduling.DueDate',
            'target_date': 'Microsoft.VSTS.Scheduling.TargetDate',
            'baseline_work': 'Microsoft.VSTS.Scheduling.BaselineWork',
            'size': 'Microsoft.VSTS.Scheduling.Size',
            
            # Microsoft VSTS Build fields
            'integration_build': 'Microsoft.VSTS.Build.IntegrationBuild',
            'found_in': 'Microsoft.VSTS.Build.FoundIn',
            
            # Microsoft VSTS TCM (Test Case Management) fields
            'test_suite_type': 'Microsoft.VSTS.TCM.TestSuiteType',
            'test_suite_type_id': 'Microsoft.VSTS.TCM.TestSuiteTypeId',
            'query_text': 'Microsoft.VSTS.TCM.QueryText',
            'parameters': 'Microsoft.VSTS.TCM.Parameters',
            'local_data_source': 'Microsoft.VSTS.TCM.LocalDataSource',
            'automated_test_name': 'Microsoft.VSTS.TCM.AutomatedTestName',
            'automated_test_storage': 'Microsoft.VSTS.TCM.AutomatedTestStorage',
            'automated_test_id': 'Microsoft.VSTS.TCM.AutomatedTestId',
            'automated_test_type': 'Microsoft.VSTS.TCM.AutomatedTestType',
            'steps': 'Microsoft.VSTS.TCM.Steps',
            'repro_steps': 'Microsoft.VSTS.TCM.ReproSteps',
            'system_info': 'Microsoft.VSTS.TCM.SystemInfo'
        }
        
        # Reverse mapping for lookups
        self.reverse_mappings = {v: k for k, v in self.field_mappings.items()}
        
        # Work item type specific fields
        self.work_item_type_fields = {
            'Bug': [
                'Microsoft.VSTS.TCM.ReproSteps',
                'Microsoft.VSTS.TCM.SystemInfo',
                'Microsoft.VSTS.Common.Severity',
                'Microsoft.VSTS.Common.Priority',
                'Microsoft.VSTS.Build.FoundIn',
                'Microsoft.VSTS.Build.IntegrationBuild'
            ],
            'Task': [
                'Microsoft.VSTS.Scheduling.RemainingWork',
                'Microsoft.VSTS.Scheduling.CompletedWork',
                'Microsoft.VSTS.Scheduling.OriginalEstimate',
                'Microsoft.VSTS.Common.Activity',
                'Microsoft.VSTS.Common.Discipline'
            ],
            'User Story': [
                'Microsoft.VSTS.Scheduling.StoryPoints',
                'Microsoft.VSTS.Common.AcceptanceCriteria',
                'Microsoft.VSTS.Common.Priority',
                'Microsoft.VSTS.Common.ValueArea',
                'Microsoft.VSTS.Common.Risk',
                'Microsoft.VSTS.Common.BusinessValue'
            ],
            'Feature': [
                'Microsoft.VSTS.Scheduling.Effort',
                'Microsoft.VSTS.Common.BusinessValue',
                'Microsoft.VSTS.Common.TimeCriticality',
                'Microsoft.VSTS.Scheduling.TargetDate',
                'Microsoft.VSTS.Common.ValueArea'
            ],
            'Epic': [
                'Microsoft.VSTS.Scheduling.Effort',
                'Microsoft.VSTS.Common.BusinessValue',
                'Microsoft.VSTS.Scheduling.StartDate',
                'Microsoft.VSTS.Scheduling.TargetDate',
                'Microsoft.VSTS.Common.ValueArea'
            ],
            'Test Case': [
                'Microsoft.VSTS.TCM.Steps',
                'Microsoft.VSTS.TCM.Parameters',
                'Microsoft.VSTS.TCM.LocalDataSource',
                'Microsoft.VSTS.TCM.AutomatedTestName',
                'Microsoft.VSTS.TCM.AutomatedTestStorage',
                'Microsoft.VSTS.TCM.AutomatedTestType',
                'Microsoft.VSTS.Common.Priority'
            ]
        }
    
    def get_field_reference(self, field_name: str) -> str:
        """Get Azure DevOps field reference from common name"""
        return self.field_mappings.get(field_name.lower(), field_name)
    
    def get_field_name(self, field_reference: str) -> str:
        """Get common field name from Azure DevOps field reference"""
        return self.reverse_mappings.get(field_reference, field_reference)
    
    def get_work_item_type_fields(self, work_item_type: str) -> List[str]:
        """Get relevant fields for a specific work item type"""
        return self.work_item_type_fields.get(work_item_type, [])
    
    def map_fields_for_creation(self, fields: Dict[str, Any], work_item_type: str) -> Dict[str, Any]:
        """Map field names to Azure DevOps references for work item creation"""
        mapped_fields = {}
        
        for field_name, field_value in fields.items():
            # Skip None values
            if field_value is None:
                continue
            
            # Get the proper field reference
            field_ref = self.get_field_reference(field_name)
            
            # Handle special field types
            if field_ref in ['System.AssignedTo', 'System.CreatedBy', 'System.ChangedBy']:
                # For user fields, we might need to handle different formats
                if isinstance(field_value, str):
                    mapped_fields[field_ref] = field_value
                elif isinstance(field_value, dict) and 'displayName' in field_value:
                    mapped_fields[field_ref] = field_value['displayName']
            elif field_ref == 'System.Tags':
                # Handle tags - should be semicolon-separated string
                if isinstance(field_value, list):
                    mapped_fields[field_ref] = '; '.join(field_value)
                else:
                    mapped_fields[field_ref] = str(field_value)
            elif field_ref in ['System.CreatedDate', 'System.ChangedDate', 'Microsoft.VSTS.Scheduling.StartDate', 
                              'Microsoft.VSTS.Scheduling.FinishDate', 'Microsoft.VSTS.Scheduling.DueDate']:
                # Handle date fields
                if isinstance(field_value, datetime):
                    mapped_fields[field_ref] = field_value.isoformat()
                elif isinstance(field_value, str):
                    mapped_fields[field_ref] = field_value
            else:
                mapped_fields[field_ref] = field_value
        
        return mapped_fields
    
    def validate_field_for_work_item_type(self, field_reference: str, work_item_type: str) -> bool:
        """Check if a field is valid for a specific work item type"""
        # System fields are valid for all work item types
        if field_reference.startswith('System.'):
            return True
        
        # Check work item type specific fields
        type_fields = self.get_work_item_type_fields(work_item_type)
        return field_reference in type_fields
    
    def get_required_fields(self, work_item_type: str) -> List[str]:
        """Get required fields for a work item type"""
        # System.Title is required for all work item types
        required = ['System.Title']
        
        # Add work item type specific required fields
        if work_item_type == 'Bug':
            required.extend(['Microsoft.VSTS.TCM.ReproSteps'])
        elif work_item_type == 'Test Case':
            required.extend(['Microsoft.VSTS.TCM.Steps'])
        
        return required
    
    def get_field_type(self, field_reference: str) -> str:
        """Get the expected type for a field"""
        field_types = {
            'System.Id': 'integer',
            'System.Title': 'string',
            'System.Description': 'html',
            'System.State': 'string',
            'System.AssignedTo': 'identity',
            'System.CreatedBy': 'identity',
            'System.ChangedBy': 'identity',
            'System.CreatedDate': 'datetime',
            'System.ChangedDate': 'datetime',
            'System.WorkItemType': 'string',
            'System.AreaPath': 'treepath',
            'System.IterationPath': 'treepath',
            'System.Tags': 'plaintext',
            'Microsoft.VSTS.Common.Priority': 'integer',
            'Microsoft.VSTS.Common.Severity': 'string',
            'Microsoft.VSTS.Scheduling.StoryPoints': 'double',
            'Microsoft.VSTS.Scheduling.Effort': 'double',
            'Microsoft.VSTS.Scheduling.OriginalEstimate': 'double',
            'Microsoft.VSTS.Scheduling.RemainingWork': 'double',
            'Microsoft.VSTS.Scheduling.CompletedWork': 'double',
            'Microsoft.VSTS.Scheduling.StartDate': 'datetime',
            'Microsoft.VSTS.Scheduling.FinishDate': 'datetime',
            'Microsoft.VSTS.Scheduling.DueDate': 'datetime',
            'Microsoft.VSTS.Common.AcceptanceCriteria': 'html',
            'Microsoft.VSTS.TCM.ReproSteps': 'html',
            'Microsoft.VSTS.TCM.Steps': 'html',
            'Microsoft.VSTS.Common.BusinessValue': 'integer',
            'Microsoft.VSTS.Common.TimeCriticality': 'double',
            'Microsoft.VSTS.Common.StackRank': 'double'
        }
        
        return field_types.get(field_reference, 'string')
    
    def format_field_value(self, field_reference: str, value: Any) -> Any:
        """Format a field value according to its expected type"""
        field_type = self.get_field_type(field_reference)
        
        if value is None:
            return None
        
        try:
            if field_type == 'integer':
                return int(value)
            elif field_type == 'double':
                return float(value)
            elif field_type == 'datetime':
                if isinstance(value, datetime):
                    return value.isoformat()
                elif isinstance(value, str):
                    # Try to parse and reformat
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        return dt.isoformat()
                    except ValueError:
                        return value
            elif field_type in ['string', 'plaintext', 'html', 'treepath', 'identity']:
                return str(value)
            else:
                return value
        except (ValueError, TypeError):
            # If conversion fails, return original value
            return value