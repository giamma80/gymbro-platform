"""
🏋️ GymBro Platform - Test Configuration
======================================

Configurazione specifica per i test per evitare problemi di
connessione database durante CI/CD.
"""

from config import Settings
import tempfile


class TestSettings(Settings):
    """Configurazioni specifiche per i test."""

    def __init__(self, **kwargs):
        # Create a temporary in-memory SQLite database for tests
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db.close()

        # Override settings for testing
        db_url = f"sqlite+aiosqlite:///{temp_db.name}"
        kwargs.setdefault("DATABASE_URL", db_url)
        kwargs.setdefault("REDIS_URL", "redis://localhost:6379/0")
        kwargs.setdefault("JWT_SECRET", "test-secret-key-for-testing")
        kwargs.setdefault("ENVIRONMENT", "test")
        kwargs.setdefault("DEBUG", True)

        super().__init__(**kwargs)


def get_test_settings():
    """Get test settings instance."""
    return TestSettings()
