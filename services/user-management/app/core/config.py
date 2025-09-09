"""
Configuration Template - Supabase Client
Service: user-management
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Settings for user-management service using Supabase Client."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Service identification
    service_name: str = Field(default="user-management", description="Service name")
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Supabase configuration
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_anon_key: str = Field(..., description="Supabase anon key for client operations")
    supabase_service_key: str = Field(..., description="Supabase service key for server operations")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT signing")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, description="JWT token expiration")
    
    # CORS configuration
    allowed_origins: str = Field(
        default="http://localhost:3000,capacitor://localhost,https://localhost,http://localhost:8080",
        description="Comma-separated list of allowed CORS origins"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    # Rate limiting
    rate_limit_requests_per_minute: int = Field(default=60, description="Rate limit per user")
    
    # External services (if needed)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    log_level: str = Field(default="INFO", description="Logging level")
    structured_logging: bool = Field(default=True, description="Use structured logging")
    
    # Feature flags
    enable_real_time: bool = Field(default=True, description="Enable Supabase real-time")
    enable_auth: bool = Field(default=True, description="Enable Supabase auth")
    enable_storage: bool = Field(default=False, description="Enable Supabase storage")
    
    # Performance
    request_timeout_seconds: int = Field(default=30, description="Request timeout")
    max_connections: int = Field(default=100, description="Max concurrent connections")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
