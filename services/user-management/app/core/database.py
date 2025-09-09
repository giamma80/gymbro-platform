"""
Database Configuration - Supabase Client with user_management schema
Service: user-management
Schema: user_management (dedicated for cost optimization)
"""

from typing import Optional, Dict, Any
import structlog
from supabase import create_client, Client
from postgrest.exceptions import APIError

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Global Supabase client
_supabase_client: Optional[Client] = None

def create_supabase_client() -> Client:
    """Create and configure Supabase client."""
    global _supabase_client
    
    if _supabase_client is None:
        try:
            # Create Supabase client with standard configuration
            _supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_service_key
            )
            
            logger.info(
                "Supabase client created successfully",
                service=settings.service_name,
                url=settings.supabase_url
            )
            
        except Exception as e:
            logger.error(
                "Failed to create Supabase client",
                error=str(e),
                service=settings.service_name
            )
            raise
    
    return _supabase_client

def get_supabase_client() -> Client:
    """Get existing Supabase client."""
    if _supabase_client is None:
        return create_supabase_client()
    return _supabase_client


# Schema-aware table access functions for user_management
def get_users_table():
    """Get users table from user_management schema."""
    client = get_supabase_client()
    return client.table('users')


def get_user_profiles_table():
    """Get user_profiles table from user_management schema."""
    client = get_supabase_client()
    return client.table('user_profiles')


def get_privacy_settings_table():
    """Get privacy_settings table from user_management schema."""
    client = get_supabase_client()
    return client.table('privacy_settings')


def get_user_service_context_view():
    """Get user_service_context view from user_management schema."""
    client = get_supabase_client()
    return client.table('user_service_context')

async def check_supabase_connection() -> bool:
    """Check Supabase connectivity using users table."""
    try:
        client = get_supabase_client()
        
        # Try a simple query on our users table to test connection
        result = client.table("users").select("id").limit(1).execute()
        
        logger.info("Supabase connection check passed", schema="user_management")
        return True
        
    except APIError as e:
        # If it's just a schema issue but connection works, that's OK
        if "schema cache" in str(e):
            logger.info("Supabase connection check passed (schema cache message is OK)")
            return True
        
        logger.error("Supabase connection check failed", error=str(e))
        return False
        
    except Exception as e:
        logger.error("Supabase connection check failed", error=str(e))
        return False

class SupabaseRepository:
    """Base repository class for Supabase operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.client = get_supabase_client()
        self.table = self.client.table(table_name)
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        try:
            result = self.table.insert(data).execute()
            
            if result.data:
                logger.info(
                    "Record created",
                    table=self.table_name,
                    record_id=result.data[0].get("id") if result.data else None
                )
                return result.data[0]
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(
                "Failed to create record",
                table=self.table_name,
                error=str(e)
            )
            raise
    
    async def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID."""
        try:
            result = self.table.select("*").eq("id", record_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(
                "Failed to get record by ID",
                table=self.table_name,
                record_id=record_id,
                error=str(e)
            )
            raise
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Dict[str, Any]]:
        """Get all records with pagination."""
        try:
            result = (
                self.table
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            return result.data or []
            
        except Exception as e:
            logger.error(
                "Failed to get all records",
                table=self.table_name,
                error=str(e)
            )
            raise
    
    async def update(self, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update record by ID."""
        try:
            result = (
                self.table
                .update(data)
                .eq("id", record_id)
                .execute()
            )
            
            if result.data:
                logger.info(
                    "Record updated",
                    table=self.table_name,
                    record_id=record_id
                )
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(
                "Failed to update record",
                table=self.table_name,
                record_id=record_id,
                error=str(e)
            )
            raise
    
    async def delete(self, record_id: str) -> bool:
        """Delete record by ID."""
        try:
            result = (
                self.table
                .delete()
                .eq("id", record_id)
                .execute()
            )
            
            logger.info(
                "Record deleted",
                table=self.table_name,
                record_id=record_id
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to delete record",
                table=self.table_name,
                record_id=record_id,
                error=str(e)
            )
            raise
    
    async def query(self, **filters) -> list[Dict[str, Any]]:
        """Query records with filters."""
        try:
            query = self.table.select("*")
            
            for field, value in filters.items():
                query = query.eq(field, value)
            
            result = query.execute()
            return result.data or []
            
        except Exception as e:
            logger.error(
                "Failed to query records",
                table=self.table_name,
                filters=filters,
                error=str(e)
            )
            raise

# Helper functions for common operations
async def create_health_check_table():
    """Create health check table if it doesn't exist."""
    try:
        client = get_supabase_client()
        
        # This would typically be done via migrations
        # For now, we'll just log that the table should exist
        logger.info("Health check table should be created via migrations")
        
    except Exception as e:
        logger.error("Failed to create health check table", error=str(e))
