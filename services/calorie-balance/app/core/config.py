from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "NutriFit Calorie Balance Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str
    
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External Services
    meal_tracking_service_url: str = "http://localhost:8002"
    health_monitor_service_url: str = "http://localhost:8003"
    ai_coach_service_url: str = "http://localhost:8005"
    
    # N8N Integration
    n8n_webhook_url: Optional[str] = None
    n8n_api_key: Optional[str] = None
    
    # OpenAI (for potential AI features)
    openai_api_key: Optional[str] = None
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"
    
    # Business Logic
    default_bmr_formula: str = "mifflin_st_jeor"  # or "harris_benedict"
    calorie_precision_grams: int = 20  # ±20g precision requirement
    confidence_threshold: float = 0.8
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()
