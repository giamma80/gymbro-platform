"""
Configuration for Analytics Service
Standard configuration following GymBro template
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings following standard template"""
    
    # Service Info
    SERVICE_NAME: str = "analytics-service"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    
    # Database Configuration - STANDARD POSTGRESQL
    DATABASE_URL: Optional[str] = None
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "gymbro_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres123"
    
    # Redis Configuration - STANDARD CACHE LAYER
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Security - STANDARD JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    CORS_ORIGINS: str = "*"  # Comma-separated origins
    
    # External Services - FEDERATION
    USER_MANAGEMENT_URL: str = "http://localhost:8001"
    GRAPHQL_GATEWAY_URL: str = "http://localhost:4000"
    
    # Monitoring - STANDARD OBSERVABILITY
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Analytics Specific Settings
    TIME_SERIES_RETENTION_DAYS: int = 365
    ANALYTICS_CACHE_TTL: int = 3600  # 1 hour
    MAX_DASHBOARD_DAYS: int = 90
    
    # Service URLs - for microservice communication
    USER_MANAGEMENT_URL: str = "http://gymbro_user_service:8000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Construct database URL if not provided directly"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL if not provided directly"""
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
