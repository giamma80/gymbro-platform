"""
Schema-aware database access for calorie-balance service.
Centralized schema management with configurable schema name.

⚠️  CRITICAL USAGE PATTERN:
   - In repositories: self.table = self.schema_manager.table_name
   - Then use: self.table.select() (NOT self.client.table())
   - See docs/databases/cross-schema-patterns.md for full guide
"""

from typing import Any
from supabase import Client

from app.core.database import get_supabase_client
from app.core.config import get_settings


class SchemaManager:
    """
    Centralized schema management for database operations.
    
    CRITICAL: This returns pre-configured table objects, not strings!
    
    Usage in repositories:
    ✅ CORRECT:
        self.table = self.schema_manager.calorie_events
        response = self.table.select("*").execute()
    
    ❌ WRONG:
        self.table = "calorie_events"  # Missing schema!
        response = self.client.table(self.table).execute()
    """
    
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
    
    # Core calorie-balance tables
    @property
    def users(self) -> Any:
        """Get users table."""
        return self.table('users')
    
    @property 
    def calorie_events(self) -> Any:
        """Get calorie_events table."""
        return self.table('calorie_events')
    
    @property
    def daily_balances(self) -> Any:
        """Get daily_balances table."""
        return self.table('daily_balances')
    
    @property
    def calorie_goals(self) -> Any:
        """Get calorie_goals table."""
        return self.table('calorie_goals')
        
    @property
    def metabolic_profiles(self) -> Any:
        """Get metabolic_profiles table."""
        return self.table('metabolic_profiles')

    # Analytics views
    @property
    def hourly_calorie_summary(self) -> Any:
        """Get hourly_calorie_summary view."""
        return self.table('hourly_calorie_summary')
        
    @property
    def daily_calorie_summary(self) -> Any:
        """Get daily_calorie_summary view."""
        return self.table('daily_calorie_summary')
        
    @property
    def weekly_calorie_summary(self) -> Any:
        """Get weekly_calorie_summary view."""
        return self.table('weekly_calorie_summary')
        
    @property
    def monthly_calorie_summary(self) -> Any:
        """Get monthly_calorie_summary view."""
        return self.table('monthly_calorie_summary')
        
    @property
    def daily_balance_summary(self) -> Any:
        """Get daily_balance_summary view."""
        return self.table('daily_balance_summary')


# Global schema manager instance
_schema_manager = None


def get_schema_manager(client: Client = None) -> SchemaManager:
    """Get or create global schema manager instance."""
    global _schema_manager
    if _schema_manager is None or client is not None:
        _schema_manager = SchemaManager(client)
    return _schema_manager


# Backward compatibility functions
def get_calorie_events_table(client: Client = None):
    """Get calorie_events table from configured schema."""
    return get_schema_manager(client).calorie_events


def get_daily_balances_table(client: Client = None):
    """Get daily_balances table from configured schema.""" 
    return get_schema_manager(client).daily_balances


def get_calorie_goals_table(client: Client = None):
    """Get calorie_goals table from configured schema."""
    return get_schema_manager(client).calorie_goals


def get_metabolic_profiles_table(client: Client = None):
    """Get metabolic_profiles table from configured schema."""
    return get_schema_manager(client).metabolic_profiles


def get_users_table(client: Client = None):
    """Get users table from configured schema."""
    return get_schema_manager(client).users
