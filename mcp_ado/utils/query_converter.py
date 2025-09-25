"""Natural language to WIQL query converter"""

import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class QueryConverter:
    """Converts natural language queries to WIQL (Work Item Query Language)"""
    
    def __init__(self):
        self.work_item_types = {
            'bug': 'Bug',
            'bugs': 'Bug',
            'task': 'Task',
            'tasks': 'Task',
            'story': 'User Story',
            'stories': 'User Story',
            'user story': 'User Story',
            'user stories': 'User Story',
            'feature': 'Feature',
            'features': 'Feature',
            'epic': 'Epic',
            'epics': 'Epic',
            'issue': 'Issue',
            'issues': 'Issue',
            'test case': 'Test Case',
            'test cases': 'Test Case'
        }
        
        self.states = {
            'new': 'New',
            'active': 'Active',
            'resolved': 'Resolved',
            'closed': 'Closed',
            'done': 'Done',
            'completed': 'Done',
            'in progress': 'Active',
            'todo': 'To Do',
            'to do': 'To Do',
            'removed': 'Removed'
        }
        
        self.priorities = {
            'critical': '1',
            'high': '2',
            'medium': '3',
            'low': '4',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }
        
        self.time_patterns = {
            r'today': lambda: datetime.now().strftime('%Y-%m-%d'),
            r'yesterday': lambda: (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            r'this week': lambda: (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            r'last week': lambda: (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
            r'this month': lambda: (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            r'last month': lambda: (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
            r'(\d+)\s+days?\s+ago': lambda m: (datetime.now() - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d'),
            r'(\d+)\s+weeks?\s+ago': lambda m: (datetime.now() - timedelta(weeks=int(m.group(1)))).strftime('%Y-%m-%d'),
            r'(\d+)\s+months?\s+ago': lambda m: (datetime.now() - timedelta(days=int(m.group(1)) * 30)).strftime('%Y-%m-%d')
        }
    
    def convert_to_wiql(self, natural_query: str, project: Optional[str] = None) -> str:
        """
        Convert natural language query to WIQL
        
        Args:
            natural_query: Natural language query string
            project: Project name (optional)
            
        Returns:
            WIQL query string
        """
        query = natural_query.lower().strip()
        
        # Start building WIQL
        select_clause = "SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], [System.AssignedTo], [System.CreatedDate], [System.ChangedDate]"
        from_clause = "FROM WorkItems"
        where_conditions = []
        order_clause = "ORDER BY [System.ChangedDate] DESC"
        
        # Parse different query patterns
        conditions = self._parse_query_conditions(query)
        
        # Build WHERE conditions
        for condition in conditions:
            where_conditions.append(condition)
        
        # Construct final query
        wiql_parts = [select_clause, from_clause]
        
        if where_conditions:
            where_clause = f"WHERE {' AND '.join(where_conditions)}"
            wiql_parts.append(where_clause)
        
        wiql_parts.append(order_clause)
        
        wiql = ' '.join(wiql_parts)
        
        logger.info(f"Converted '{natural_query}' to WIQL: {wiql}")
        return wiql
    
    def _parse_query_conditions(self, query: str) -> List[str]:
        """Parse natural language query into WIQL conditions"""
        conditions = []
        
        # Work item type detection
        work_item_type = self._extract_work_item_type(query)
        if work_item_type:
            conditions.append(f"[System.WorkItemType] = '{work_item_type}'")
        
        # State detection
        state = self._extract_state(query)
        if state:
            conditions.append(f"[System.State] = '{state}'")
        
        # Priority detection
        priority = self._extract_priority(query)
        if priority:
            conditions.append(f"[Microsoft.VSTS.Common.Priority] = {priority}")
        
        # Assigned to detection
        assigned_to = self._extract_assigned_to(query)
        if assigned_to:
            if assigned_to.lower() in ['me', 'myself']:
                conditions.append("[System.AssignedTo] = @Me")
            elif assigned_to.lower() in ['unassigned', 'nobody', 'no one']:
                conditions.append("[System.AssignedTo] = ''")
            else:
                conditions.append(f"[System.AssignedTo] CONTAINS '{assigned_to}'")
        
        # Created by detection
        created_by = self._extract_created_by(query)
        if created_by:
            if created_by.lower() in ['me', 'myself']:
                conditions.append("[System.CreatedBy] = @Me")
            else:
                conditions.append(f"[System.CreatedBy] CONTAINS '{created_by}'")
        
        # Time-based conditions
        time_conditions = self._extract_time_conditions(query)
        conditions.extend(time_conditions)
        
        # Title/description search
        search_terms = self._extract_search_terms(query)
        if search_terms:
            search_conditions = []
            for term in search_terms:
                search_conditions.append(f"[System.Title] CONTAINS '{term}'")
                search_conditions.append(f"[System.Description] CONTAINS '{term}'")
            if search_conditions:
                conditions.append(f"({' OR '.join(search_conditions)})")
        
        # Tags detection
        tags = self._extract_tags(query)
        if tags:
            for tag in tags:
                conditions.append(f"[System.Tags] CONTAINS '{tag}'")
        
        # Area path detection
        area_path = self._extract_area_path(query)
        if area_path:
            conditions.append(f"[System.AreaPath] UNDER '{area_path}'")
        
        # Iteration path detection
        iteration_path = self._extract_iteration_path(query)
        if iteration_path:
            conditions.append(f"[System.IterationPath] UNDER '{iteration_path}'")
        
        return conditions
    
    def _extract_work_item_type(self, query: str) -> Optional[str]:
        """Extract work item type from query"""
        for key, value in self.work_item_types.items():
            if key in query:
                return value
        return None
    
    def _extract_state(self, query: str) -> Optional[str]:
        """Extract state from query"""
        for key, value in self.states.items():
            if key in query:
                return value
        return None
    
    def _extract_priority(self, query: str) -> Optional[str]:
        """Extract priority from query"""
        # Look for priority patterns
        priority_patterns = [
            r'priority\s+(\d+)',
            r'priority\s+(critical|high|medium|low)',
            r'(critical|high|medium|low)\s+priority'
        ]
        
        for pattern in priority_patterns:
            match = re.search(pattern, query)
            if match:
                priority_value = match.group(1).lower()
                return self.priorities.get(priority_value)
        
        return None
    
    def _extract_assigned_to(self, query: str) -> Optional[str]:
        """Extract assigned to information from query"""
        patterns = [
            r'assigned\s+to\s+([^\s,]+(?:\s+[^\s,]+)*)',
            r'assigned\s+([^\s,]+(?:\s+[^\s,]+)*)',
            r'by\s+([^\s,]+(?:\s+[^\s,]+)*)',
            r'for\s+([^\s,]+(?:\s+[^\s,]+)*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        # Check for special keywords
        if any(word in query for word in ['my', 'mine', 'me']):
            return 'me'
        if any(word in query for word in ['unassigned', 'nobody', 'no one']):
            return 'unassigned'
        
        return None
    
    def _extract_created_by(self, query: str) -> Optional[str]:
        """Extract created by information from query"""
        patterns = [
            r'created\s+by\s+([^\s,]+(?:\s+[^\s,]+)*)',
            r'authored\s+by\s+([^\s,]+(?:\s+[^\s,]+)*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_time_conditions(self, query: str) -> List[str]:
        """Extract time-based conditions from query"""
        conditions = []
        
        # Check for time patterns
        for pattern, date_func in self.time_patterns.items():
            if callable(date_func):
                # Simple patterns
                if re.search(pattern, query):
                    if 'created' in query:
                        date_value = date_func()
                        conditions.append(f"[System.CreatedDate] >= '{date_value}'")
                    elif 'changed' in query or 'updated' in query or 'modified' in query:
                        date_value = date_func()
                        conditions.append(f"[System.ChangedDate] >= '{date_value}'")
            else:
                # Patterns with groups
                match = re.search(pattern, query)
                if match:
                    if 'created' in query:
                        date_value = date_func(match)
                        conditions.append(f"[System.CreatedDate] >= '{date_value}'")
                    elif 'changed' in query or 'updated' in query or 'modified' in query:
                        date_value = date_func(match)
                        conditions.append(f"[System.ChangedDate] >= '{date_value}'")
        
        return conditions
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query"""
        # Remove common query words and extract meaningful terms
        stop_words = {
            'show', 'find', 'get', 'list', 'all', 'my', 'the', 'a', 'an', 'and', 'or', 'but',
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'that', 'which',
            'work', 'item', 'items', 'assigned', 'created', 'changed', 'updated', 'modified',
            'priority', 'state', 'type', 'title', 'description', 'tag', 'tags', 'area', 'iteration'
        }
        
        # Remove work item types, states, and other parsed elements
        cleaned_query = query
        for key in self.work_item_types.keys():
            cleaned_query = cleaned_query.replace(key, '')
        for key in self.states.keys():
            cleaned_query = cleaned_query.replace(key, '')
        
        # Extract quoted strings first
        quoted_terms = re.findall(r'"([^"]+)"', cleaned_query)
        cleaned_query = re.sub(r'"[^"]+"', '', cleaned_query)
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', cleaned_query)
        meaningful_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        return quoted_terms + meaningful_words
    
    def _extract_tags(self, query: str) -> List[str]:
        """Extract tags from query"""
        patterns = [
            r'tag[ged]*\s+([^\s,]+)',
            r'with\s+tag\s+([^\s,]+)',
            r'#([^\s,]+)'
        ]
        
        tags = []
        for pattern in patterns:
            matches = re.findall(pattern, query)
            tags.extend(matches)
        
        return tags
    
    def _extract_area_path(self, query: str) -> Optional[str]:
        """Extract area path from query"""
        patterns = [
            r'in\s+area\s+([^\s,]+(?:\s+[^\s,]+)*)',
            r'area\s+([^\s,]+(?:\s+[^\s,]+)*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_iteration_path(self, query: str) -> Optional[str]:
        """Extract iteration path from query"""
        patterns = [
            r'in\s+iteration\s+([^\s,]+(?:\s+[^\s,]+)*)',
            r'iteration\s+([^\s,]+(?:\s+[^\s,]+)*)',
            r'in\s+sprint\s+([^\s,]+(?:\s+[^\s,]+)*)',
            r'sprint\s+([^\s,]+(?:\s+[^\s,]+)*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        return None
    
    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions based on partial input"""
        suggestions = []
        
        # Basic query templates
        templates = [
            "Show all bugs assigned to me",
            "Find active tasks",
            "List all user stories in current iteration",
            "Show high priority items",
            "Find bugs created this week",
            "Show my work items",
            "List completed tasks",
            "Find items with tag 'urgent'",
            "Show all features",
            "Find unassigned bugs"
        ]
        
        # Filter suggestions based on partial query
        if partial_query:
            query_lower = partial_query.lower()
            suggestions = [t for t in templates if query_lower in t.lower()]
        else:
            suggestions = templates[:5]  # Show first 5 by default
        
        return suggestions