"""Work item management tools"""

from typing import Dict, List, Optional, Any
import logging

from ..ado.client import AdoClient
from ..ado.models import WorkItem, QueryResult
from ..utils.query_converter import QueryConverter
from ..utils.field_mapper import FieldMapper

logger = logging.getLogger(__name__)


class WorkItemTools:
    """Tools for work item operations"""
    
    def __init__(self):
        self.query_converter = QueryConverter()
        self.field_mapper = FieldMapper()
    
    async def get_work_item(self, connection: Dict[str, str], work_item_id: int) -> Dict[str, Any]:
        """Get a specific work item by ID"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                work_item = await client.get_work_item(work_item_id, connection.get('project'))
                
                if not work_item:
                    return {
                        "success": False,
                        "error": f"Work item {work_item_id} not found"
                    }
                
                return {
                    "success": True,
                    "work_item": work_item.to_dict()
                }
        
        except Exception as e:
            logger.error(f"Error getting work item {work_item_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_work_items(self, connection: Dict[str, str], work_item_ids: List[int]) -> Dict[str, Any]:
        """Get multiple work items by IDs"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                work_items = await client.get_work_items(work_item_ids, connection.get('project'))
                
                return {
                    "success": True,
                    "work_items": [wi.to_dict() for wi in work_items],
                    "count": len(work_items)
                }
        
        except Exception as e:
            logger.error(f"Error getting work items {work_item_ids}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_work_items(self, connection: Dict[str, str], query: str, top: int = 50) -> Dict[str, Any]:
        """Search work items using natural language query"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                # Convert natural language to WIQL
                wiql = self.query_converter.convert_to_wiql(query, connection.get('project'))
                
                # Execute query
                result = await client.query_work_items(wiql, connection.get('project'), top)
                
                return {
                    "success": True,
                    "work_items": [wi.to_dict() for wi in result.work_items],
                    "count": result.total_count,
                    "query": query,
                    "wiql": result.query_text,
                    "execution_time": result.execution_time
                }
        
        except Exception as e:
            logger.error(f"Error searching work items with query '{query}': {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def query_work_items_wiql(self, connection: Dict[str, str], wiql: str, top: int = 100) -> Dict[str, Any]:
        """Execute WIQL query directly"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                result = await client.query_work_items(wiql, connection.get('project'), top)
                
                return {
                    "success": True,
                    "work_items": [wi.to_dict() for wi in result.work_items],
                    "count": result.total_count,
                    "wiql": result.query_text,
                    "execution_time": result.execution_time
                }
        
        except Exception as e:
            logger.error(f"Error executing WIQL query: {e}")
            return {
                "success": False,
                "error": str(e),
                "wiql": wiql
            }
    
    async def update_work_item(self, connection: Dict[str, str], work_item_id: int, 
                             fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update a work item"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                # Map field names to Azure DevOps references
                mapped_fields = {}
                for field_name, field_value in fields.items():
                    field_ref = self.field_mapper.get_field_reference(field_name)
                    formatted_value = self.field_mapper.format_field_value(field_ref, field_value)
                    mapped_fields[field_ref] = formatted_value
                
                # Update work item
                updated_work_item = await client.update_work_item(
                    work_item_id, mapped_fields, connection.get('project')
                )
                
                return {
                    "success": True,
                    "work_item": updated_work_item.to_dict(),
                    "updated_fields": list(fields.keys())
                }
        
        except Exception as e:
            logger.error(f"Error updating work item {work_item_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "work_item_id": work_item_id
            }
    
    async def delete_work_item(self, connection: Dict[str, str], work_item_id: int) -> Dict[str, Any]:
        """Delete a work item (move to recycle bin)"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                success = await client.delete_work_item(work_item_id, connection.get('project'))
                
                return {
                    "success": success,
                    "work_item_id": work_item_id,
                    "message": f"Work item {work_item_id} {'deleted' if success else 'could not be deleted'}"
                }
        
        except Exception as e:
            logger.error(f"Error deleting work item {work_item_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "work_item_id": work_item_id
            }
    
    async def get_work_item_history(self, connection: Dict[str, str], work_item_id: int) -> Dict[str, Any]:
        """Get work item revision history"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                # Get work item revisions
                url = client._build_url(f"wit/workitems/{work_item_id}/revisions?api-version=7.1", 
                                      connection.get('project'))
                response = await client._make_request("GET", url)
                
                revisions = []
                for revision_data in response.get('value', []):
                    revision = {
                        'rev': revision_data.get('rev'),
                        'changed_date': revision_data.get('fields', {}).get('System.ChangedDate'),
                        'changed_by': revision_data.get('fields', {}).get('System.ChangedBy', {}).get('displayName'),
                        'state': revision_data.get('fields', {}).get('System.State'),
                        'title': revision_data.get('fields', {}).get('System.Title')
                    }
                    revisions.append(revision)
                
                return {
                    "success": True,
                    "work_item_id": work_item_id,
                    "revisions": revisions,
                    "revision_count": len(revisions)
                }
        
        except Exception as e:
            logger.error(f"Error getting work item history for {work_item_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "work_item_id": work_item_id
            }
    
    async def get_work_item_comments(self, connection: Dict[str, str], work_item_id: int) -> Dict[str, Any]:
        """Get work item comments"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                # Get work item comments
                url = client._build_url(f"wit/workitems/{work_item_id}/comments?api-version=7.1-preview.3", 
                                      connection.get('project'))
                response = await client._make_request("GET", url)
                
                comments = []
                for comment_data in response.get('value', []):
                    comment = {
                        'id': comment_data.get('id'),
                        'text': comment_data.get('text'),
                        'created_date': comment_data.get('createdDate'),
                        'created_by': comment_data.get('createdBy', {}).get('displayName'),
                        'modified_date': comment_data.get('modifiedDate'),
                        'modified_by': comment_data.get('modifiedBy', {}).get('displayName')
                    }
                    comments.append(comment)
                
                return {
                    "success": True,
                    "work_item_id": work_item_id,
                    "comments": comments,
                    "comment_count": len(comments)
                }
        
        except Exception as e:
            logger.error(f"Error getting work item comments for {work_item_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "work_item_id": work_item_id
            }
    
    async def add_work_item_comment(self, connection: Dict[str, str], work_item_id: int, 
                                  comment_text: str) -> Dict[str, Any]:
        """Add a comment to a work item"""
        try:
            async with AdoClient(
                organization=connection['org'],
                personal_access_token=connection['pat'],
                project=connection.get('project')
            ) as client:
                # Add comment
                url = client._build_url(f"wit/workitems/{work_item_id}/comments?api-version=7.1-preview.3", 
                                      connection.get('project'))
                comment_data = {"text": comment_text}
                
                response = await client._make_request("POST", url, json=comment_data)
                
                return {
                    "success": True,
                    "work_item_id": work_item_id,
                    "comment": {
                        'id': response.get('id'),
                        'text': response.get('text'),
                        'created_date': response.get('createdDate'),
                        'created_by': response.get('createdBy', {}).get('displayName')
                    }
                }
        
        except Exception as e:
            logger.error(f"Error adding comment to work item {work_item_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "work_item_id": work_item_id
            }
    
    def get_query_suggestions(self, partial_query: str = "") -> Dict[str, Any]:
        """Get query suggestions for natural language search"""
        suggestions = self.query_converter.get_query_suggestions(partial_query)
        
        return {
            "success": True,
            "suggestions": suggestions,
            "partial_query": partial_query
        }