"""
🏋️ GymBro Platform - Configuration Settings
===========================================

Configurazioni centralizzate per il servizio User Management.
Utilizza pydantic-settings per gestione environment variables.
"""

import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazioni dell'applicazione"""

    model_config = SettingsConfigDict(
        env_file=[".env", "../../.env"],  # Cerca prima locale, poi root
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignora variabili extra non definite nella classe
    )

    # ==========================================
    # 🔧 App Settings
    # ==========================================
    APP_NAME: str = "GymBro User Management"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment")

    # ==========================================
    # 🗄️ Database Settings
    # ==========================================
    DATABASE_URL: str = Field(default="", description="Database URL")
    DB_ECHO: bool = Field(default=False, description="Database echo")

    # ==========================================
    # 🔐 Security Settings
    # ==========================================
    JWT_SECRET: str = Field(default="test-secret", description="JWT Secret")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT Algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15, description="JWT Access token expire minutes"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=30, description="JWT Refresh token expire days"
    )

    # ==========================================
    # 🏢 Supabase Settings (FREE TIER)
    # ==========================================
    SUPABASE_URL: str = Field(default="", description="Supabase URL")
    SUPABASE_KEY: str = Field(default="", description="Supabase Key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default="", description="Supabase Service Role Key"
    )

    # ==========================================
    # 🧠 Cache Settings (In-Memory for MVP)
    # ==========================================
    CACHE_TTL: int = Field(default=3600, description="Cache TTL")  # 1 hour
    # Redis removed for MVP - using PostgreSQL sessions + in-memory cache

    # ==========================================
    # 🌐 CORS & Security
    # ==========================================
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
        ],
        description="CORS Origins",
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"], description="Allowed Hosts"
    )

    # ==========================================
    # 📊 Monitoring Settings
    # ==========================================
    SENTRY_DSN: str = Field(default="", description="Sentry DSN")
    LOG_LEVEL: str = Field(default="INFO", description="Log Level")

    # ==========================================
    # 🎯 Rate Limiting
    # ==========================================
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        default=60, description="Rate limit requests per minute"
    )
    RATE_LIMIT_BURST: int = Field(default=10, description="Rate limit burst")

    # ==========================================
    # 🔄 Background Tasks (PostgreSQL-based for MVP)
    # ==========================================
    # Celery Redis URLs removed - using database-based task queue for MVP
    # CELERY_BROKER_URL: Database-based tasks
    # CELERY_RESULT_BACKEND: Database-based results

    # ==========================================
    # 📧 Email Settings (SendGrid FREE)
    # ==========================================
    SENDGRID_API_KEY: str = Field(default="", description="SendGrid API Key")
    FROM_EMAIL: str = Field(default="noreply@gymbro.app", description="From Email")

    # ==========================================
    # 🚩 Feature Flags
    # ==========================================
    FLAGSMITH_ENVIRONMENT_KEY: str = Field(
        default="", description="Flagsmith Environment Key"
    )


# Istanza globale delle settings
settings = Settings()

# ==========================================
# 🛡️ Security Configuration
# ==========================================

# Password validation rules
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGITS = True
PASSWORD_REQUIRE_SPECIAL = True

# Session settings
SESSION_COOKIE_NAME = "gymbro_session"
SESSION_COOKIE_SECURE = settings.ENVIRONMENT == "production"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "lax"

# Account lockout settings
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# ==========================================
# 📊 BMR/TDEE Configuration
# ==========================================

# Moltiplicatori per livello di attività (per calcolo TDEE)
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,  # Poco/nessun esercizio
    "lightly_active": 1.375,  # Esercizio leggero 1-3 giorni/settimana
    "moderately_active": 1.55,  # Esercizio moderato 3-5 giorni/settimana
    "very_active": 1.725,  # Esercizio intenso 6-7 giorni/settimana
    "extra_active": 1.9,  # Esercizio molto intenso, lavoro fisico
}

# Limiti per validazione dati antropometrici
MIN_AGE = 13
MAX_AGE = 120
MIN_HEIGHT_CM = 100
MAX_HEIGHT_CM = 250
MIN_WEIGHT_KG = 30
MAX_WEIGHT_KG = 300

# ==========================================
# 🔄 Cache Keys
# ==========================================

CACHE_KEYS = {
    "user_profile": "user:{user_id}:profile",
    "user_stats": "user:{user_id}:stats",
    "user_preferences": "user:{user_id}:preferences",
    "user_session": "session:{session_id}",
    "rate_limit": "rate_limit:{user_id}:{endpoint}",
}

# ==========================================
# 📱 Device Integration
# ==========================================

# Supported device types
SUPPORTED_DEVICES = [
    "apple_watch",
    "fitbit",
    "garmin",
    "samsung_health",
    "google_fit",
    "android_health",
    "manual_entry",
]

# Data source priorities (higher = more trusted)
DATA_SOURCE_PRIORITY = {
    "manual_entry": 10,
    "apple_watch": 9,
    "garmin": 8,
    "fitbit": 7,
    "samsung_health": 6,
    "google_fit": 5,
    "android_health": 4,
}

# ==========================================
# 🎨 UI/UX Settings
# ==========================================

# Default user preferences
DEFAULT_PREFERENCES = {
    "timezone": "Europe/Rome",
    "language": "it",
    "weight_unit": "kg",
    "distance_unit": "km",
    "push_notifications": True,
    "email_notifications": True,
    "meal_reminders": True,
    "workout_reminders": True,
    "profile_public": False,
    "share_achievements": True,
}

# ==========================================
# 📊 Analytics Events
# ==========================================

ANALYTICS_EVENTS = {
    "user_registered": "user_registered",
    "user_login": "user_login",
    "profile_updated": "profile_updated",
    "preferences_updated": "preferences_updated",
    "password_changed": "password_changed",
    "account_deleted": "account_deleted",
}

# ==========================================
# 🚨 Error Codes
# ==========================================

ERROR_CODES = {
    "EMAIL_ALREADY_EXISTS": "EMAIL_ALREADY_EXISTS",
    "INVALID_CREDENTIALS": "INVALID_CREDENTIALS",
    "WEAK_PASSWORD": "WEAK_PASSWORD",
    "ACCOUNT_LOCKED": "ACCOUNT_LOCKED",
    "INVALID_TOKEN": "INVALID_TOKEN",
    "TOKEN_EXPIRED": "TOKEN_EXPIRED",
    "INSUFFICIENT_PERMISSIONS": "INSUFFICIENT_PERMISSIONS",
    "RATE_LIMIT_EXCEEDED": "RATE_LIMIT_EXCEEDED",
    "VALIDATION_ERROR": "VALIDATION_ERROR",
    "DATABASE_ERROR": "DATABASE_ERROR",
    "EXTERNAL_SERVICE_ERROR": "EXTERNAL_SERVICE_ERROR",
}

# ==========================================
# 🚀 Settings Instance
# ==========================================

# Crea l'istanza globale delle configurazioni
settings = Settings()
