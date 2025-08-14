"""
Test per config module
"""
import pytest
from config import (
    settings,
    ACTIVITY_MULTIPLIERS,
    DEFAULT_PREFERENCES,
    SUPPORTED_DEVICES,
)


class TestConfiguration:
    """Test per configurazione app."""

    def test_settings_exist(self):
        """Test che le settings esistano."""
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'JWT_SECRET')
        assert hasattr(settings, 'DATABASE_URL')

    def test_activity_multipliers(self):
        """Test moltiplicatori attività."""
        assert 'sedentary' in ACTIVITY_MULTIPLIERS
        assert 'very_active' in ACTIVITY_MULTIPLIERS
        assert ACTIVITY_MULTIPLIERS['sedentary'] == 1.2
        assert ACTIVITY_MULTIPLIERS['extra_active'] == 1.9

    def test_default_preferences(self):
        """Test preferenze default."""
        assert 'timezone' in DEFAULT_PREFERENCES
        assert 'language' in DEFAULT_PREFERENCES
        assert DEFAULT_PREFERENCES['language'] == 'it'
        assert DEFAULT_PREFERENCES['push_notifications'] is True

    def test_supported_devices(self):
        """Test dispositivi supportati."""
        assert 'apple_watch' in SUPPORTED_DEVICES
        assert 'manual_entry' in SUPPORTED_DEVICES
        assert len(SUPPORTED_DEVICES) >= 6
