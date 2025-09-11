"""
Schema-aware database access for user_management service.
Centralized schema management with configurable schema name.
"""

from typing import Any

from supabase import Client

from app.core.config import get_settings
from app.core.database import get_supabase_client


class SchemaManager:
    """Centralized schema management for database operations."""

    def __init__(self, client: Client = None):
        """Initialize schema manager with optional client."""
        self._client = client or get_supabase_client()
        self._settings = get_settings()
        self._schema_name = self._settings.database_schema

    @property
    def schema_name(self) -> str:
        """Get the configured schema name."""
        return self._schema_name

    def table(self, table_name: str) -> Any:
        """Get a table from the configured schema."""
        return self._client.schema(self._schema_name).table(table_name)

    # Core user tables
    @property
    def users(self) -> Any:
        """Get users table."""
        return self.table("users")

    @property
    def user_profiles(self) -> Any:
        """Get user_profiles table."""
        return self.table("user_profiles")

    @property
    def privacy_settings(self) -> Any:
        """Get privacy_settings table."""
        return self.table("privacy_settings")

    @property
    def user_service_context(self) -> Any:
        """Get user_service_context view."""
        return self.table("user_service_context")

    # Auth tables
    @property
    def auth_credentials(self) -> Any:
        """Get auth_credentials table."""
        return self.table("auth_credentials")

    @property
    def auth_sessions(self) -> Any:
        """Get auth_sessions table."""
        return self.table("auth_sessions")

    @property
    def password_reset_tokens(self) -> Any:
        """Get password_reset_tokens table."""
        return self.table("password_reset_tokens")

    @property
    def email_verification_tokens(self) -> Any:
        """Get email_verification_tokens table."""
        return self.table("email_verification_tokens")

    @property
    def social_auth_profiles(self) -> Any:
        """Get social_auth_profiles table."""
        return self.table("social_auth_profiles")

    @property
    def audit_logs(self) -> Any:
        """Get audit_logs table."""
        return self.table("audit_logs")


# Global schema manager instance
_schema_manager = None


def get_schema_manager(client: Client = None) -> SchemaManager:
    """Get or create global schema manager instance."""
    global _schema_manager
    if _schema_manager is None or client is not None:
        _schema_manager = SchemaManager(client)
    return _schema_manager


# Backward compatibility functions
def get_auth_credentials_table(client: Client = None):
    """Get auth_credentials table from configured schema."""
    return get_schema_manager(client).auth_credentials


def get_auth_sessions_table(client: Client = None):
    """Get auth_sessions table from configured schema."""
    return get_schema_manager(client).auth_sessions


def get_password_reset_tokens_table(client: Client = None):
    """Get password_reset_tokens table from configured schema."""
    return get_schema_manager(client).password_reset_tokens


def get_email_verification_tokens_table(client: Client = None):
    """Get email_verification_tokens table from configured schema."""
    return get_schema_manager(client).email_verification_tokens


def get_social_auth_profiles_table(client: Client = None):
    """Get social_auth_profiles table from configured schema."""
    return get_schema_manager(client).social_auth_profiles


def get_audit_logs_table(client: Client = None):
    """Get audit_logs table from configured schema."""
    return get_schema_manager(client).audit_logs
