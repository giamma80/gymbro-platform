#!/bin/bash
# Microservice Template Setup Script
# Creates a new microservice from the updated template

set -e

TEMPLATE_DIR="/Users/giamma/workspace/gymbro-platform/templates/microservice-template/supabase-client-template"
SERVICES_DIR="/Users/giamma/workspace/gymbro-platform/services"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}🏗️  NutriFit Microservice Generator${NC}"
echo "========================================="

# Get service name
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 <service-name>${NC}"
    echo "Example: $0 workout-tracking"
    exit 1
fi

SERVICE_NAME=$1
SERVICE_DIR="$SERVICES_DIR/$SERVICE_NAME"

# Validate service name
if [[ ! $SERVICE_NAME =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
    echo -e "${RED}❌ Error: Service name must be lowercase, alphanumeric with dashes${NC}"
    echo "Valid examples: user-management, workout-tracking, nutrition-analysis"
    exit 1
fi

# Check if service already exists
if [ -d "$SERVICE_DIR" ]; then
    echo -e "${RED}❌ Error: Service '$SERVICE_NAME' already exists${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Creating service: ${BOLD}$SERVICE_NAME${NC}"

# Create service directory
mkdir -p "$SERVICE_DIR"
echo -e "${GREEN}✅ Created directory: $SERVICE_DIR${NC}"

# Copy template files
echo -e "${CYAN}📋 Copying template files...${NC}"
cp -r "$TEMPLATE_DIR"/* "$SERVICE_DIR/"

# Replace placeholders in files
echo -e "${CYAN}🔧 Configuring service...${NC}"

# Convert service-name to different formats
SERVICE_NAME_UNDERSCORE=$(echo "$SERVICE_NAME" | tr '-' '_')
SERVICE_NAME_CAMEL=$(echo "$SERVICE_NAME" | sed -r 's/-(.)/\U\1/g' | sed 's/^./\U&/')

# Files to update
FILES_TO_UPDATE=(
    "$SERVICE_DIR/pyproject.toml"
    "$SERVICE_DIR/.env.example"
    "$SERVICE_DIR/app/main.py"
    "$SERVICE_DIR/app/core/config.py"
    "$SERVICE_DIR/app/core/database.py"
)

# Update pyproject.toml
sed -i '' "s/{service-name}/$SERVICE_NAME/g" "$SERVICE_DIR/pyproject.toml"
sed -i '' "s/nutrifit-{service-name}/nutrifit-$SERVICE_NAME/g" "$SERVICE_DIR/pyproject.toml"
sed -i '' "s/{service-name} microservice/$SERVICE_NAME microservice/g" "$SERVICE_DIR/pyproject.toml"

echo -e "${GREEN}✅ Updated pyproject.toml${NC}"

# Create basic environment file
cat > "$SERVICE_DIR/.env.example" << EOF
# NutriFit $SERVICE_NAME Service Configuration
# Copy this file to .env and fill in your values

# Service Configuration
SERVICE_NAME=$SERVICE_NAME
SERVICE_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=info

# Supabase Configuration (shared database approach)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
POSTGRES_SCHEMA=$SERVICE_NAME_UNDERSCORE

# Database Configuration (if using direct PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/nutrifit_platform

# API Configuration
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# GraphQL Configuration
GRAPHQL_ENDPOINT=/graphql
GRAPHQL_PLAYGROUND=true

# Background Tasks (optional)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EOF

echo -e "${GREEN}✅ Created .env.example${NC}"

# Update main.py
cat > "$SERVICE_DIR/app/main.py" << EOF
"""
NutriFit $SERVICE_NAME Service
============================
Main FastAPI application for $SERVICE_NAME microservice.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.core.config import get_settings
from app.core.database import get_supabase_client
from app.api.v1.router import api_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=f"NutriFit {SERVICE_NAME.replace('-', ' ').title()} Service",
        description=f"Microservice for {SERVICE_NAME.replace('-', ' ')} management",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    
    # Health check endpoints
    @app.get("/health")
    async def health_check():
        """Basic health check."""
        return {
            "status": "healthy",
            "service": "$SERVICE_NAME",
            "version": "1.0.0"
        }
    
    @app.get("/health/ready")
    async def readiness_check():
        """Readiness check including database connectivity."""
        try:
            client = get_supabase_client()
            # Test database connection
            result = client.from_("${SERVICE_NAME_UNDERSCORE}_health").select("1").limit(1).execute()
            database_status = "connected"
        except Exception as e:
            logger.error("Database connection failed", error=str(e))
            database_status = "disconnected"
        
        return {
            "status": "ready" if database_status == "connected" else "not_ready",
            "service": "$SERVICE_NAME",
            "checks": {
                "database": database_status
            }
        }
    
    @app.get("/health/live")
    async def liveness_check():
        """Liveness check."""
        return {
            "status": "alive",
            "service": "$SERVICE_NAME"
        }
    
    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None
    )
EOF

echo -e "${GREEN}✅ Updated main.py${NC}"

# Update config.py
cat > "$SERVICE_DIR/app/core/config.py" << EOF
"""
Configuration settings for $SERVICE_NAME service.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Service Configuration
    service_name: str = "$SERVICE_NAME"
    service_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="info", env="LOG_LEVEL")
    
    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"], 
        env="CORS_ORIGINS"
    )
    
    # Database Configuration
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    postgres_schema: str = Field(default="$SERVICE_NAME_UNDERSCORE", env="POSTGRES_SCHEMA")
    
    # GraphQL Configuration  
    graphql_endpoint: str = Field(default="/graphql", env="GRAPHQL_ENDPOINT")
    graphql_playground: bool = Field(default=True, env="GRAPHQL_PLAYGROUND")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


_settings: Settings = None


def get_settings() -> Settings:
    """Get application settings (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
EOF

echo -e "${GREEN}✅ Updated config.py${NC}"

# Create basic database.py
cat > "$SERVICE_DIR/app/core/database.py" << EOF
"""
Database configuration and connection for $SERVICE_NAME service.
"""

import os
from typing import Optional
from supabase import create_client, Client
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get Supabase client (singleton)."""
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        
        try:
            _supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key  # Use service role for backend
            )
            
            # Set the schema for this service
            if hasattr(_supabase_client, 'postgrest'):
                _supabase_client.postgrest.schema = settings.postgres_schema
            
            logger.info(
                "Supabase client initialized",
                schema=settings.postgres_schema,
                url=settings.supabase_url
            )
            
        except Exception as e:
            logger.error("Failed to initialize Supabase client", error=str(e))
            raise
    
    return _supabase_client


def test_connection() -> bool:
    """Test database connection."""
    try:
        client = get_supabase_client()
        # Try a simple query to test connection
        result = client.from_("${SERVICE_NAME_UNDERSCORE}_test").select("1").limit(1).execute()
        return True
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        return False
EOF

echo -e "${GREEN}✅ Updated database.py${NC}"

# Create README.md
cat > "$SERVICE_DIR/README.md" << EOF
# NutriFit $SERVICE_NAME Service

Microservice for $SERVICE_NAME management in the NutriFit platform.

## Features

- FastAPI REST API
- GraphQL Federation support
- Supabase integration with schema isolation
- Domain-driven design architecture
- Comprehensive testing suite
- Health check endpoints

## Quick Start

1. **Setup Environment**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   \`\`\`

2. **Install Dependencies**
   \`\`\`bash
   poetry install
   \`\`\`

3. **Run Development Server**
   \`\`\`bash
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   \`\`\`

4. **Run Tests**
   \`\`\`bash
   ./run_tests.sh
   \`\`\`

## API Endpoints

- \`GET /health\` - Health check
- \`GET /health/ready\` - Readiness check
- \`GET /health/live\` - Liveness check
- \`GET /docs\` - Interactive API documentation

## Architecture

This service follows Domain-Driven Design principles:

- **API Layer**: REST endpoints and GraphQL resolvers
- **Application Layer**: Use cases and business logic orchestration  
- **Domain Layer**: Business entities and domain services
- **Infrastructure Layer**: Database repositories and external services

## Database Schema

Uses dedicated PostgreSQL schema: \`$SERVICE_NAME_UNDERSCORE\`

## Development

See the main platform documentation for development guidelines and deployment instructions.
EOF

echo -e "${GREEN}✅ Created README.md${NC}"

# Create basic test script
cat > "$SERVICE_DIR/run_tests.sh" << 'EOF'
#!/bin/bash
# Basic test runner for new service

echo "🧪 Running tests for SERVICE_NAME service..."

# Check if service is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Service not running. Start with:"
    echo "poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

# Basic health check test
echo "✅ Service is running"
echo "🔍 Testing health endpoints..."

# Test health endpoint
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

echo "🎉 Basic tests passed!"
EOF

chmod +x "$SERVICE_DIR/run_tests.sh"
echo -e "${GREEN}✅ Created test runner${NC}"

# Create basic directory structure
mkdir -p "$SERVICE_DIR/app/domain/repositories"
mkdir -p "$SERVICE_DIR/app/application"
mkdir -p "$SERVICE_DIR/app/infrastructure/repositories"
mkdir -p "$SERVICE_DIR/tests"

# Create __init__.py files
touch "$SERVICE_DIR/app/domain/__init__.py"
touch "$SERVICE_DIR/app/domain/repositories/__init__.py"
touch "$SERVICE_DIR/app/application/__init__.py"
touch "$SERVICE_DIR/app/infrastructure/__init__.py"
touch "$SERVICE_DIR/app/infrastructure/repositories/__init__.py"
touch "$SERVICE_DIR/tests/__init__.py"

echo -e "${GREEN}✅ Created directory structure${NC}"

# Final setup
cd "$SERVICE_DIR"

echo ""
echo -e "${BOLD}🎉 Service '$SERVICE_NAME' created successfully!${NC}"
echo ""
echo -e "${CYAN}📋 Next steps:${NC}"
echo "1. cd $SERVICE_DIR"
echo "2. cp .env.example .env"
echo "3. Edit .env with your Supabase credentials"
echo "4. poetry install"
echo "5. Create your database schema in Supabase"
echo "6. poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo -e "${YELLOW}📚 Documentation:${NC}"
echo "- Service README: $SERVICE_DIR/README.md"
echo "- Template updates: /templates/microservice-template/TEMPLATE_UPDATES_20250909.md"
echo "- Platform docs: /docs/"
echo ""
echo -e "${PURPLE}🏗️  Happy coding!${NC}"
