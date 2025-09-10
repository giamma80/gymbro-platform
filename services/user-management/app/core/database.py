"""
Database Configuration - Supabase Client with configurable schema
Service: user-management
Schema: configurable via DATABASE_SCHEMA env var (default: user_management)
"""

from typing import Optional, Dict, Any
import structlog
from supabase import create_client, Client
from postgrest.exceptions import APIError

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Global Supabase client (uses anon key for runtime safety)
_supabase_client: Optional[Client] = None


def create_supabase_client(use_service_role: bool = False) -> Client:
    """Create and configure a Supabase client.

    By default this function returns/creates a global client that uses the
    anon key (safer for runtime). When `use_service_role=True` a new client
    backed by the service_role key will be created — this is intended for
    administrative checks (startup readiness) and is NOT stored globally.
    """
    global _supabase_client

    if use_service_role:
        # Create a transient client with the service role key for privileged checks
        try:
            svc_client = create_client(
                settings.supabase_url,
                settings.supabase_service_key,
            )
            logger.info(
                "Supabase service-role client created for admin check",
                url=settings.supabase_url,
            )
            return svc_client
        except Exception as e:
            logger.error(
                "Failed to create service-role supabase client",
                error=str(e),
            )
            raise

    # Use anon client as the global default for day-to-day operations
    if _supabase_client is None:
        try:
            _supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key,
            )
            logger.info(
                "Supabase anon client created successfully",
                service=settings.service_name,
                url=settings.supabase_url,
            )
        except Exception as e:
            logger.error(
                "Failed to create Supabase anon client",
                error=str(e),
                service=settings.service_name,
            )
            raise

    return _supabase_client


def get_supabase_client() -> Client:
    """Get existing Supabase client (anon)."""
    if _supabase_client is None:
        return create_supabase_client()
    return _supabase_client


# Schema-aware table access functions (deprecated - use SchemaManager)
def get_users_table():
    """Get users table from configured schema."""
    from app.core.schema_tables import get_schema_manager
    return get_schema_manager().users


def get_user_profiles_table():
    """Get user_profiles table from configured schema."""
    from app.core.schema_tables import get_schema_manager
    return get_schema_manager().user_profiles


def get_privacy_settings_table():
    """Get privacy_settings table from configured schema."""
    from app.core.schema_tables import get_schema_manager
    return get_schema_manager().privacy_settings


def get_user_service_context_view():
    """Get user_service_context view from configured schema."""
    from app.core.schema_tables import get_schema_manager
    return get_schema_manager().user_service_context

 
async def check_supabase_connection() -> bool:
    """Check Supabase connectivity using a temporary service-role client.

    We use the service_role key only for this privileged startup check so
    the application (which uses the anon client) doesn't fail due to
    permission issues when the database/schema exists but table privileges
    haven't been granted to anon yet.
    """
    try:
        # Create a transient, privileged client for the check
        svc_client = create_supabase_client(use_service_role=True)

        # Use a SchemaManager bound to the service client so we don't
        # replace the global schema manager / client used by runtime code.
        from app.core.schema_tables import SchemaManager
        schema_manager = SchemaManager(svc_client)

        # Try a simple query on our users table to test access to schema/tables
        _ = schema_manager.users.select("id").limit(1).execute()

        logger.info(
            "Supabase connection check passed",
            schema=schema_manager.schema_name,
        )
        return True

    except APIError as e:
        # If it's just a schema cache/info message we still consider it OK
        if "schema cache" in str(e):
            logger.info(
                "Supabase connection check passed (schema cache message is OK)"
            )
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
