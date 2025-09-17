"""
Database Configuration - Supabase Client
Service: calorie-balance
"""

from typing import Any, Dict, Optional

import structlog
from postgrest.exceptions import APIError
from supabase import Client, create_client

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
            _supabase_client = create_client(
                settings.supabase_url, settings.supabase_service_key
            )

            logger.info(
                "Supabase client created",
                service=settings.service_name,
                url=settings.supabase_url,
            )

        except Exception as e:
            logger.error(
                "Failed to create Supabase client",
                error=str(e),
                service=settings.service_name,
            )
            raise

    return _supabase_client


def get_supabase_client() -> Client:
    """Get existing Supabase client."""
    if _supabase_client is None:
        return create_supabase_client()
    # Disable database interceptor for now due to logging conflicts
    # from app.graphql.interceptors import DatabaseQueryLoggingInterceptor
    # interceptor = DatabaseQueryLoggingInterceptor(_supabase_client)
    return _supabase_client


async def check_supabase_connection() -> bool:
    """Check Supabase connectivity."""
    try:
        # Try a simple query to test connection using schema manager
        # Test with calorie_events table from calorie_balance schema
        from app.core.schema_tables import get_schema_manager

        schema_manager = get_schema_manager()
        schema_manager.calorie_events.select("*").limit(1).execute()

        logger.info("Supabase connection check passed")
        return True

    except APIError as e:
        # Check for common error patterns that still indicate connectivity
        error_msg = str(e).lower()
        if any(
            pattern in error_msg
            for pattern in [
                "relation",
                "table",
                "schema",
                "does not exist",
                "permission denied",
                "role",
            ]
        ):
            # Database is reachable, just configuration/permission issue
            logger.warning(
                "Supabase accessible but schema/permissions issue", error=str(e)
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
                    record_id=result.data[0].get("id") if result.data else None,
                )
                return result.data[0]
            else:
                raise Exception("No data returned from insert")

        except Exception as e:
            logger.error("Failed to create record", table=self.table_name, error=str(e))
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
                error=str(e),
            )
            raise

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Dict[str, Any]]:
        """Get all records with pagination."""
        try:
            result = self.table.select("*").range(offset, offset + limit - 1).execute()

            return result.data or []

        except Exception as e:
            logger.error(
                "Failed to get all records", table=self.table_name, error=str(e)
            )
            raise

    async def update(
        self, record_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update record by ID."""
        try:
            result = self.table.update(data).eq("id", record_id).execute()

            if result.data:
                logger.info(
                    "Record updated", table=self.table_name, record_id=record_id
                )
                return result.data[0]
            return None

        except Exception as e:
            logger.error(
                "Failed to update record",
                table=self.table_name,
                record_id=record_id,
                error=str(e),
            )
            raise

    async def delete(self, record_id: str) -> bool:
        """Delete record by ID."""
        try:
            result = self.table.delete().eq("id", record_id).execute()

            logger.info("Record deleted", table=self.table_name, record_id=record_id)
            return True

        except Exception as e:
            logger.error(
                "Failed to delete record",
                table=self.table_name,
                record_id=record_id,
                error=str(e),
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
                error=str(e),
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
