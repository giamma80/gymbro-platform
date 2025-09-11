"""
Supabase repository implementations for {service-name} service.

This module contains concrete implementations of repository interfaces
using Supabase as the database provider.
"""

from typing import List, Optional, Any, Dict
from app.domain.interfaces import I{ServiceName}Repository
from app.domain.entities import {ServiceName}Entity
from app.core.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


class Supabase{ServiceName}Repository(I{ServiceName}Repository):
    """
    Supabase implementation of the {ServiceName} repository.
    
    This class handles all database operations for {service-name} entities
    using Supabase as the backend.
    """
    
    def __init__(self):
        """Initialize the repository with Supabase client."""
        self.client = get_supabase_client()
        self.table_name = "{service_name}_data"  # Adjust table name as needed
    
    async def create(self, entity_data: Dict[str, Any]) -> {ServiceName}Entity:
        """
        Create a new {service-name} entity in the database.
        
        Args:
            entity_data: Dictionary containing the entity data
            
        Returns:
            Created {ServiceName}Entity
            
        Raises:
            Exception: If creation fails
        """
        try:
            response = self.client.table(self.table_name).insert(entity_data).execute()
            
            if response.data:
                return {ServiceName}Entity.from_dict(response.data[0])
            else:
                raise Exception(f"Failed to create {service-name} entity")
                
        except Exception as e:
            logger.error(f"Error creating {service-name} entity: {{e}}")
            raise
    
    async def get_by_id(self, entity_id: str) -> Optional[{ServiceName}Entity]:
        """
        Retrieve a {service-name} entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            {ServiceName}Entity if found, None otherwise
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("id", entity_id).execute()
            
            if response.data:
                return {ServiceName}Entity.from_dict(response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving {service-name} entity {{entity_id}}: {{e}}")
            return None
    
    async def get_by_user_id(self, user_id: str) -> List[{ServiceName}Entity]:
        """
        Retrieve all {service-name} entities for a specific user.
        
        Args:
            user_id: The user ID to filter by
            
        Returns:
            List of {ServiceName}Entity objects
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("user_id", user_id).execute()
            
            return [{ServiceName}Entity.from_dict(row) for row in response.data]
            
        except Exception as e:
            logger.error(f"Error retrieving {service-name} entities for user {{user_id}}: {{e}}")
            return []
    
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[{ServiceName}Entity]:
        """
        Update a {service-name} entity.
        
        Args:
            entity_id: The ID of the entity to update
            update_data: Dictionary containing the fields to update
            
        Returns:
            Updated {ServiceName}Entity if successful, None otherwise
        """
        try:
            response = self.client.table(self.table_name).update(update_data).eq("id", entity_id).execute()
            
            if response.data:
                return {ServiceName}Entity.from_dict(response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error updating {service-name} entity {{entity_id}}: {{e}}")
            return None
    
    async def delete(self, entity_id: str) -> bool:
        """
        Delete a {service-name} entity.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            response = self.client.table(self.table_name).delete().eq("id", entity_id).execute()
            return response.data is not None
            
        except Exception as e:
            logger.error(f"Error deleting {service-name} entity {{entity_id}}: {{e}}")
            return False
    
    async def list_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[{ServiceName}Entity]:
        """
        List all {service-name} entities with optional pagination.
        
        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of {ServiceName}Entity objects
        """
        try:
            query = self.client.table(self.table_name).select("*")
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
                
            response = query.execute()
            return [{ServiceName}Entity.from_dict(row) for row in response.data]
            
        except Exception as e:
            logger.error(f"Error listing {service-name} entities: {{e}}")
            return []
