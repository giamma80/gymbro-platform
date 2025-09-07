# 📦 Supabase Client Template - pyproject.toml

```toml
[tool.poetry]
name = "nutrifit-{service-name}"
version = "1.0.0"
description = "NutriFit {Service Name} Microservice with Supabase Client"
authors = ["NutriFit Team <dev@nutrifit.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"

# 🔥 Core Framework
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"

# 🗄️ Supabase Integration
supabase = "^2.0.0"
python-dotenv = "^1.0.0"

# 🔐 Authentication & Security
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"

# 📊 Data Validation & Serialization
email-validator = "^2.1.0"
python-dateutil = "^2.8.2"

# 🔄 HTTP & External APIs
httpx = "^0.25.0"
aiofiles = "^23.2.1"

# 📝 Logging & Monitoring
structlog = "^23.2.0"
rich = "^13.7.0"

# 🧪 Testing (Optional)
pytest = {version = "^7.4.0", optional = true}
pytest-asyncio = {version = "^0.21.0", optional = true}
httpx = {version = "^0.25.0", optional = true}

[tool.poetry.extras]
test = ["pytest", "pytest-asyncio", "httpx"]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

# 🔧 Configuration Template - config.py

```python
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Configuration settings for Supabase-based microservice"""
    
    # 🔗 Supabase Configuration
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    # 🚀 FastAPI Configuration
    app_name: str = "NutriFit {Service Name} Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 🔐 Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 🌐 CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",  # Flutter dev
        "https://*.netlify.app",  # Frontend deployment
        "https://*.render.com"    # Backend services
    ]
    
    # 📊 Real-time Configuration
    realtime_enabled: bool = True
    realtime_heartbeat_interval: int = 30
    
    # 📝 Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
```

# 🗄️ Database Client Template - database.py

```python
from supabase import create_client, Client
from config import settings
from typing import Optional, Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)

class SupabaseClient:
    """Supabase client wrapper with enhanced functionality"""
    
    def __init__(self):
        self.url = settings.supabase_url
        self.anon_key = settings.supabase_anon_key
        self.service_key = settings.supabase_service_key
        
        # Public client (RLS enforced)
        self.client: Client = create_client(self.url, self.anon_key)
        
        # Service client (bypass RLS)
        self.admin_client: Client = create_client(self.url, self.service_key)
    
    def get_client(self, admin: bool = False) -> Client:
        """Get Supabase client"""
        return self.admin_client if admin else self.client
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Supabase connection health"""
        try:
            # Test basic connectivity
            result = self.client.table('health_check').select('*').limit(1).execute()
            return {
                "status": "healthy",
                "supabase_connected": True,
                "realtime_enabled": settings.realtime_enabled
            }
        except Exception as e:
            logger.error("Supabase health check failed", error=str(e))
            return {
                "status": "unhealthy", 
                "supabase_connected": False,
                "error": str(e)
            }
    
    def set_auth(self, access_token: str):
        """Set authentication token for RLS"""
        self.client.auth.set_session(access_token)
    
    async def create_record(self, table: str, data: Dict[str, Any], admin: bool = False) -> Optional[Dict[str, Any]]:
        """Create a new record"""
        try:
            client = self.get_client(admin)
            result = client.table(table).insert(data).execute()
            
            if result.data:
                logger.info("Record created", table=table, record_id=result.data[0].get('id'))
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error("Failed to create record", table=table, error=str(e))
            raise
    
    async def get_record(self, table: str, record_id: str, admin: bool = False) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        try:
            client = self.get_client(admin)
            result = client.table(table).select('*').eq('id', record_id).single().execute()
            return result.data if result.data else None
            
        except Exception as e:
            logger.error("Failed to get record", table=table, record_id=record_id, error=str(e))
            return None
    
    async def update_record(self, table: str, record_id: str, data: Dict[str, Any], admin: bool = False) -> Optional[Dict[str, Any]]:
        """Update a record"""
        try:
            client = self.get_client(admin)
            result = client.table(table).update(data).eq('id', record_id).execute()
            
            if result.data:
                logger.info("Record updated", table=table, record_id=record_id)
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error("Failed to update record", table=table, record_id=record_id, error=str(e))
            raise
    
    async def delete_record(self, table: str, record_id: str, admin: bool = False) -> bool:
        """Delete a record"""
        try:
            client = self.get_client(admin)
            result = client.table(table).delete().eq('id', record_id).execute()
            
            logger.info("Record deleted", table=table, record_id=record_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete record", table=table, record_id=record_id, error=str(e))
            return False
    
    async def list_records(self, table: str, filters: Optional[Dict[str, Any]] = None, 
                          limit: int = 100, offset: int = 0, admin: bool = False) -> List[Dict[str, Any]]:
        """List records with optional filtering"""
        try:
            client = self.get_client(admin)
            query = client.table(table).select('*')
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Apply pagination
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error("Failed to list records", table=table, error=str(e))
            return []
    
    def subscribe_to_changes(self, table: str, callback, filters: Optional[Dict[str, Any]] = None):
        """Subscribe to real-time changes"""
        if not settings.realtime_enabled:
            logger.warning("Real-time is disabled")
            return None
        
        try:
            subscription = self.client.table(table).on('*', callback)
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    subscription = subscription.filter(key, 'eq', value)
            
            subscription.subscribe()
            logger.info("Subscribed to real-time changes", table=table)
            return subscription
            
        except Exception as e:
            logger.error("Failed to subscribe to changes", table=table, error=str(e))
            return None

# Global database client instance
db = SupabaseClient()
```

# 🔐 Authentication Template - auth.py

```python
from supabase import Client
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import db
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger(__name__)
security = HTTPBearer()

class AuthService:
    """Authentication service using Supabase Auth"""
    
    def __init__(self):
        self.client = db.get_client()
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email/password"""
        try:
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                logger.info("User authenticated", user_id=auth_response.user.id)
                return {
                    "user": auth_response.user,
                    "session": auth_response.session,
                    "access_token": auth_response.session.access_token
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
                
        except Exception as e:
            logger.error("Authentication failed", email=email, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current user from JWT token"""
        try:
            # Verify token with Supabase
            user_response = self.client.auth.get_user(credentials.credentials)
            
            if user_response.user:
                # Set auth context for subsequent DB operations
                db.set_auth(credentials.credentials)
                return user_response.user
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
                
        except Exception as e:
            logger.error("Token validation failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

# Global auth service instance
auth_service = AuthService()

# Dependency for protected endpoints
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    return await auth_service.get_current_user(credentials)
```

# 🚀 Main App Template - main.py

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import db
from auth import get_current_user
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Supabase-powered microservice for NutriFit Platform",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": settings.app_name}

@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    health = await db.health_check()
    return health

@app.get("/health/live") 
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "service": settings.app_name}

# Example protected endpoint
@app.get("/api/v1/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "metadata": current_user.user_metadata
    }

# Example CRUD endpoints
@app.post("/api/v1/{table}")
async def create_item(table: str, data: dict, current_user = Depends(get_current_user)):
    """Create a new item"""
    # Add user context
    data["user_id"] = current_user.id
    
    result = await db.create_record(table, data)
    return {"success": True, "data": result}

@app.get("/api/v1/{table}/{item_id}")
async def get_item(table: str, item_id: str, current_user = Depends(get_current_user)):
    """Get an item by ID"""
    result = await db.get_record(table, item_id)
    return {"data": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
```

# 📦 Environment Template - .env.example

```bash
# 🔗 Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# 🔐 Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 🚀 FastAPI Configuration
APP_NAME=NutriFit Service Name Service
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# 🔄 Real-time Configuration
REALTIME_ENABLED=true
REALTIME_HEARTBEAT_INTERVAL=30

# 🌐 CORS Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://app.nutrifit.com
```
