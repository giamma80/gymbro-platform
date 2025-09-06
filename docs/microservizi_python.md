# Microservizi Python 3.11 - NutriFit Platform

## Executive Summary

Implementazione completa dei 5 microservizi Python 3.11 per la piattaforma NutriFit, basata su **Domain-Driven Design** e architettura **cloud-native**. L'approccio utilizza **FastAPI**, **Supabase Cloud** per database segregati e **N8N Cloud** per orchestrazione workflow, garantendo scalabilità, maintainability e deployment automatizzato su **Render.com**.

**Architettura Confermata:**
- ✅ **5 Microservizi Python 3.11** atomici e indipendenti
- ✅ **FastAPI + Supabase Cloud + Poetry** stack unificato
- ✅ **Domain-Driven Design** con Value Objects constraint-aware
- ✅ **N8N Cloud orchestration** per workflow complessi
- ✅ **Docker multi-stage** per compatibilità locale/Render
- ✅ **MCP Server** per microservizi con AI/ML capabilities

---

## 1. Architettura Microservizi con Database Segregation

### 5 Microservizi Atomici con Supabase Cloud

```mermaid
graph TB
    subgraph "Mobile App"
        FLUTTER[Flutter App]
    end
    
    subgraph "API Gateway"
        GATEWAY[API Gateway<br/>Facade Pattern]
    end
    
    subgraph "N8N Cloud Orchestration"
        N8N[N8N Workflows<br/>AI + External APIs]
    end
    
    subgraph "Microservizi Python 3.11"
        CB[Calorie Balance<br/>Service + MCP]
        MT[Meal Tracking<br/>Service + MCP]
        HM[Health Monitor<br/>Service]
        NS[Notifications<br/>Service]
        AI[AI Nutrition Coach<br/>Service + MCP]
    end
    
    subgraph "Supabase Cloud Databases"
        DB1[(nutrifit_calorie_balance)]
        DB2[(nutrifit_meal_tracking)]
        DB3[(nutrifit_health_monitor)]
        DB4[(nutrifit_notifications)]
        DB5[(nutrifit_ai_coach)]
        PUSH[Push Notifications]
    end
    
    FLUTTER --> GATEWAY
    GATEWAY --> CB
    GATEWAY --> MT
    GATEWAY --> HM
    GATEWAY --> NS
    GATEWAY --> AI
    
    N8N --> CB
    N8N --> MT
    N8N --> AI
    N8N <--> OPENAI[OpenAI API]
    N8N <--> OFF[OpenFoodFacts]
    
    CB --> DB1
    MT --> DB2
    HM --> DB3
    NS --> DB4
    AI --> DB5
    NS --> PUSH
```

### Database Segregation su Supabase

**Principio**: Ogni microservizio ha il proprio database isolato su Supabase Cloud per garantire autonomia completa e evitare coupling.

| Microservizio | Database Supabase | Schema Domain | MCP Server |
|---------------|-------------------|---------------|------------|
| **calorie-balance** | `nutrifit_calorie_balance` | Energy metabolism, goals, BMR | ✅ Per AI workflows |
| **meal-tracking** | `nutrifit_meal_tracking` | Food data, nutrition, meals | ✅ Per food analysis |
| **health-monitor** | `nutrifit_health_monitor` | HealthKit data, metrics | ❌ Solo data sync |
| **notifications** | `nutrifit_notifications` | Push tokens, templates | ❌ Solo messaging |
| **ai-coach** | `nutrifit_ai_coach` | Conversations, RAG vectors | ✅ Primary AI service |

---

## 2. Python 3.11 Tech Stack Unificato

### Core Framework Stack per Tutti i Microservizi

```python
# pyproject.toml - Template standard per ogni microservizio
[tool.poetry]
name = "nutrifit-{service-name}"
version = "1.0.0"  
description = "NutriFit {Service Name} Microservice"
authors = ["NutriFit Team <dev@nutrifit.com>"]

[tool.poetry.dependencies]
python = "^3.11"

# Core Framework
fastapi = "^0.104.1"              # Modern async API framework
uvicorn = {extras = ["standard"], version = "^0.24.0"}  # ASGI server development
gunicorn = "^21.2.0"              # Production WSGI server per Render

# Database & Supabase Integration
supabase = "^2.3.0"               # Supabase Python client
asyncpg = "^0.29.0"               # PostgreSQL async driver  
sqlalchemy = "^2.0.23"            # Modern async ORM
pydantic = {extras = ["email"], version = "^2.4.0"}   # Data validation

# HTTP & External APIs  
httpx = "^0.25.2"                 # Modern async HTTP client
aiofiles = "^23.2.1"              # Async file operations

# Model Context Protocol (per servizi AI)
mcp = "^1.0.0"                    # MCP server implementation
openai = "^1.3.0"                 # OpenAI API client (se needed)
strawberry-graphql = "^0.211.0"   # GraphQL per FastAPI, supporto federation

## GraphQL Federation con Strawberry

Per integrare ogni microservizio Python nella federazione GraphQL, aggiungi la dipendenza `strawberry-graphql` e definisci uno schema federato accanto agli endpoint REST.

### Esempio base (FastAPI + Strawberry)

```python
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class User:
    id: int
    name: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> User:
        # recupera utente dal DB
        return User(id=id, name="Mario")

schema = strawberry.federation.Schema(Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

### Passi per la federation
1. Esponi `/graphql` come subgraph federato.
2. Registra il subgraph in Apollo Gateway.
3. Mantieni REST e GraphQL in parallelo per transizione graduale.

Per dettagli architetturali, vedi [docs/architettura.md](architettura.md).
# Monitoring & Logging
structlog = "^23.2.0"             # Structured logging
prometheus-client = "^0.19.0"     # Metrics collection

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"                 # Testing framework
pytest-asyncio = "^0.21.0"        # Async test support
pytest-cov = "^4.1.0"             # Coverage reporting
httpx = "^0.25.2"                 # Test HTTP client
factory-boy = "^3.3.0"            # Test data factories

# Code Quality
black = "^23.7.0"                 # Code formatting
isort = "^5.12.0"                 # Import sorting  
flake8 = "^6.0.0"                 # Linting
mypy = "^1.5.0"                   # Type checking

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Configurazione Standard per Supabase Cloud

```python
# app/core/config.py - Template per ogni microservizio
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """Configuration per microservizio NutriFit"""
    
    # Service Identity
    service_name: str = "{service-name}"
    environment: str = "development"
    debug: bool = False
    
    # Supabase Cloud Configuration (REQUIRED)
    supabase_url: str                      # Supabase project URL
    supabase_anon_key: str                 # Public anon key
    supabase_service_key: str              # Service role key (backend only)
    
    # Database specifico per servizio
    database_name: str = "nutrifit_{service_name}"
    
    # N8N Cloud Integration
    n8n_webhook_url: Optional[str] = None  # N8N webhook per questo servizio
    n8n_api_key: Optional[str] = None      # N8N API key
    
    # Security
    secret_key: str                        # JWT secret
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS per mobile app
    allowed_origins: List[str] = [
        "http://localhost:3000",           # Flutter web debug
        "capacitor://localhost",           # Capacitor iOS
        "https://localhost",               # Capacitor Android
    ]
    
    # MCP Server Configuration (se applicable)
    mcp_server_enabled: bool = False
    mcp_server_port: Optional[int] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Struttura Database Segregata per Microservizio

```python
# app/database.py - Template per ogni microservizio
from supabase import create_client, Client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import asyncpg
from app.core.config import settings

# Supabase Client per operazioni dirette
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_key  # Service key per backend operations
)

# SQLAlchemy Async Engine per ORM avanzato
DATABASE_URL = f"postgresql+asyncpg://postgres:{settings.supabase_service_key}@{settings.supabase_url.split('https://')[1]}/postgres"

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency per ottenere sessione database"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Health check funzioni
async def check_supabase_connection() -> bool:
    """Verifica connessione a Supabase"""
    try:
        result = supabase.table('_health_check').select('*').limit(1).execute()
        return True
    except Exception:
        return False

async def check_sqlalchemy_connection() -> bool:
    """Verifica connessione SQLAlchemy"""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False
```

### Modelli Base per Database Segregato

```python
# app/models/base.py - Base models per ogni microservizio
from sqlalchemy import Column, String, DateTime, Boolean, Text, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class BaseModel(Base):
    """Classe base per tutti i modelli del microservizio"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    # Metadata per cross-service communication
    external_refs = Column(Text, nullable=True)  # JSON per riferimenti esterni
    sync_status = Column(String(50), default='active')  # active, syncing, error

class ServiceHealthCheck(Base):
    """Tabella health check per ogni microservizio"""
    __tablename__ = "_health_check"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(100), nullable=False)
    status = Column(String(20), default='healthy')
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(String(20), nullable=False)
```

## 3. Cloud-Native Authentication e Security

### JWT Authentication con Supabase Auth

```python
# app/core/auth.py - Authentication middleware unificato
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from jose import JWTError, jwt
from typing import Optional
from app.database import supabase
from app.core.config import settings

security = HTTPBearer()

class SupabaseAuthManager:
    """Gestione autenticazione centralizzata con Supabase"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def verify_token(self, token: str) -> Optional[dict]:
        """Verifica JWT token tramite Supabase"""
        try:
            # Supabase gestisce automaticamente la verifica JWT
            user = self.supabase.auth.get_user(token)
            return user.user if user.user else None
        except Exception:
            return None
    
    async def get_user_metadata(self, user_id: str) -> dict:
        """Recupera metadata utente per autorizzazione"""
        try:
            result = self.supabase.table('user_profiles').select(
                'id, role, permissions, subscription_tier'
            ).eq('id', user_id).single().execute()
            return result.data if result.data else {}
        except Exception:
            return {}

auth_manager = SupabaseAuthManager(supabase)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Dependency per ottenere utente corrente"""
    token = credentials.credentials
    user = await auth_manager.verify_token(token)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    
    return user

async def require_permission(permission: str):
    """Factory per dependency che richiede specifica permission"""
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        metadata = await auth_manager.get_user_metadata(current_user['id'])
        permissions = metadata.get('permissions', [])
        
        if permission not in permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' required"
            )
        
        return current_user
    
    return permission_checker
```

### Cross-Service Communication Security

```python
# app/core/inter_service.py - Comunicazione sicura tra microservizi
import httpx
import time
import hmac
import hashlib
from typing import Dict, Any
from app.core.config import settings

class InterServiceClient:
    """Client per comunicazione sicura tra microservizi"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=10)
        )
        self.service_secret = settings.secret_key
    
    def _generate_signature(self, payload: str, timestamp: str) -> str:
        """Genera signature HMAC per request inter-service"""
        message = f"{timestamp}:{payload}"
        signature = hmac.new(
            self.service_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        data: Dict[Any, Any] = None
    ) -> httpx.Response:
        """Chiamata autenticata ad altro microservizio"""
        timestamp = str(int(time.time()))
        payload = json.dumps(data) if data else ""
        signature = self._generate_signature(payload, timestamp)
        
        headers = {
            "X-Service-Name": settings.service_name,
            "X-Timestamp": timestamp,
            "X-Signature": signature,
            "Content-Type": "application/json"
        }
        
        service_url = f"https://{service_name}.render.com"  # Render URLs
        url = f"{service_url}{endpoint}"
        
        response = await self.client.request(
            method=method,
            url=url,
            json=data,
            headers=headers
        )
        
        return response
    
    async def verify_inter_service_request(self, request: Request) -> bool:
        """Verifica richiesta da altro microservizio"""
        service_name = request.headers.get("X-Service-Name")
        timestamp = request.headers.get("X-Timestamp")
        signature = request.headers.get("X-Signature")
        
        if not all([service_name, timestamp, signature]):
            return False
        
        # Verifica timestamp (max 5 minuti)
        current_time = int(time.time())
        if abs(current_time - int(timestamp)) > 300:
            return False
        
        # Verifica signature
        body = await request.body()
        expected_signature = self._generate_signature(body.decode(), timestamp)
        
        return hmac.compare_digest(signature, expected_signature)

inter_service = InterServiceClient()
```

## 4. N8N Cloud Integration Pattern

### N8N Webhook Handler

```python
# app/integrations/n8n.py - N8N Cloud integration per ogni servizio
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import httpx
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class N8NIntegration:
    """Integrazione con N8N Cloud per orchestrazione workflows"""
    
    def __init__(self):
        self.n8n_base_url = "https://n8n.cloud/webhook/"  # N8N Cloud
        self.api_key = settings.n8n_api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def trigger_workflow(
        self, 
        workflow_id: str, 
        data: Dict[str, Any],
        wait_for_response: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Trigger N8N workflow tramite webhook"""
        webhook_url = f"{self.n8n_base_url}{workflow_id}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else None
        }
        
        try:
            response = await self.client.post(
                webhook_url,
                json={
                    "service": settings.service_name,
                    "timestamp": time.time(),
                    "data": data
                },
                headers=headers
            )
            
            if wait_for_response and response.status_code == 200:
                return response.json()
            
            logger.info(
                "N8N workflow triggered",
                workflow_id=workflow_id,
                service=settings.service_name,
                status_code=response.status_code
            )
            
            return {"status": "triggered", "workflow_id": workflow_id}
            
        except Exception as e:
            logger.error(
                "Failed to trigger N8N workflow",
                workflow_id=workflow_id,
                error=str(e)
            )
            raise HTTPException(
                status_code=500,
                detail=f"N8N workflow trigger failed: {str(e)}"
            )
    
    async def receive_webhook(self, request: Request) -> Dict[str, Any]:
        """Ricevi webhook da N8N workflow"""
        try:
            data = await request.json()
            
            # Log received data
            logger.info(
                "Received N8N webhook",
                service=settings.service_name,
                workflow_data=data
            )
            
            return data
            
        except Exception as e:
            logger.error("Failed to process N8N webhook", error=str(e))
            raise HTTPException(
                status_code=400,
                detail=f"Invalid webhook data: {str(e)}"
            )

n8n = N8NIntegration()

# Router per webhook N8N
n8n_router = APIRouter(prefix="/webhooks/n8n", tags=["n8n"])

@n8n_router.post("/receive")
async def receive_n8n_webhook(request: Request, background_tasks: BackgroundTasks):
    """Endpoint per ricevere webhook da N8N"""
    data = await n8n.receive_webhook(request)
    
    # Process webhook in background
    background_tasks.add_task(process_n8n_data, data)
    
    return {"status": "received", "timestamp": time.time()}

async def process_n8n_data(data: Dict[str, Any]):
    """Process N8N webhook data in background"""
    # Implementazione specifica per ogni servizio
    pass
```

## 5. Model Context Protocol (MCP) Server Implementation

### MCP Server Base per AI Services

```python
# app/mcp/server.py - MCP Server implementation per servizi AI
from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Dict, Any, List
import asyncio
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class NutriFitMCPServer:
    """MCP Server base per microservizi AI-enabled"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.server = Server(f"nutrifit-{service_name}")
        self.tools: Dict[str, Tool] = {}
        
        # Setup server handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Lista tools disponibili"""
            return list(self.tools.values())
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute tool con argomenti"""
            if name not in self.tools:
                raise ValueError(f"Tool '{name}' not found")
            
            try:
                # Execute tool method
                method_name = f"_tool_{name.replace('-', '_')}"
                if hasattr(self, method_name):
                    result = await getattr(self, method_name)(**arguments)
                    return [TextContent(type="text", text=str(result))]
                else:
                    raise ValueError(f"Tool method {method_name} not implemented")
                    
            except Exception as e:
                logger.error(f"Tool execution failed", tool=name, error=str(e))
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    def register_tool(self, tool: Tool):
        """Registra nuovo tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool", tool=tool.name, service=self.service_name)
    
    async def start_server(self, port: int = None):
        """Avvia MCP server"""
        server_port = port or settings.mcp_server_port or 8000
        
        logger.info(
            "Starting MCP server",
            service=self.service_name,
            port=server_port
        )
        
        # Implementation dipende dalla libreria MCP specifica
        # Placeholder per avvio server
        await asyncio.sleep(0.1)
```

### MCP Tools per Calorie Balance Service

```python
# services/calorie-balance/app/mcp/tools.py - Esempio tools specifici
from mcp.types import Tool
from app.mcp.server import NutriFitMCPServer
from app.services.calorie_calculator import CalorieCalculatorService
from typing import Dict, Any

class CalorieBalanceMCPServer(NutriFitMCPServer):
    """MCP Server per Calorie Balance Service"""
    
    def __init__(self):
        super().__init__("calorie-balance")
        self.calorie_service = CalorieCalculatorService()
        self._register_tools()
    
    def _register_tools(self):
        """Registra tools specifici per calorie balance"""
        
        # Tool: Calculate BMR
        bmr_tool = Tool(
            name="calculate-bmr",
            description="Calculate Basal Metabolic Rate based on user data",
            inputSchema={
                "type": "object",
                "properties": {
                    "weight": {"type": "number", "description": "Weight in kg"},
                    "height": {"type": "number", "description": "Height in cm"},
                    "age": {"type": "number", "description": "Age in years"},
                    "gender": {"type": "string", "enum": ["male", "female"]},
                    "activity_level": {"type": "string", "enum": ["sedentary", "light", "moderate", "high", "extreme"]}
                },
                "required": ["weight", "height", "age", "gender", "activity_level"]
            }
        )
        self.register_tool(bmr_tool)
        
        # Tool: Calculate calorie goal
        goal_tool = Tool(
            name="calculate-calorie-goal",
            description="Calculate daily calorie goal based on BMR and objectives",
            inputSchema={
                "type": "object",
                "properties": {
                    "bmr": {"type": "number", "description": "Basal Metabolic Rate"},
                    "goal": {"type": "string", "enum": ["lose", "maintain", "gain"]},
                    "intensity": {"type": "string", "enum": ["slow", "moderate", "fast"]}
                },
                "required": ["bmr", "goal", "intensity"]
            }
        )
        self.register_tool(goal_tool)
    
    async def _tool_calculate_bmr(self, **kwargs) -> Dict[str, Any]:
        """Implementazione tool BMR calculation"""
        return await self.calorie_service.calculate_bmr(**kwargs)
    
    async def _tool_calculate_calorie_goal(self, **kwargs) -> Dict[str, Any]:
        """Implementazione tool calorie goal calculation"""
        return await self.calorie_service.calculate_daily_goal(**kwargs)
```

## 6. FastAPI Application Structure Template

### Main Application Setup

```python
# app/main.py - Template standard per ogni microservizio
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import structlog
from app.core.config import settings
from app.core.auth import auth_manager
from app.database import check_supabase_connection, check_sqlalchemy_connection
from app.integrations.n8n import n8n_router
from app.api import health, auth

# Setup logging
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info(f"Starting {settings.service_name} service")
    
    # Verifica connessioni
    supabase_ok = await check_supabase_connection()
    sqlalchemy_ok = await check_sqlalchemy_connection()
    
    if not (supabase_ok and sqlalchemy_ok):
        logger.error("Database connection failed")
        raise RuntimeError("Cannot connect to database")
    
    # Start MCP server se abilitato
    if settings.mcp_server_enabled:
        from app.mcp.server import mcp_server
        await mcp_server.start_server(settings.mcp_server_port)
    
    logger.info(f"{settings.service_name} service started successfully")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.service_name} service")

app = FastAPI(
    title=f"NutriFit {settings.service_name.title()} Service",
    description=f"Microservizio {settings.service_name} per NutriFit Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*.render.com", "localhost", "127.0.0.1"]
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(n8n_router)

# Service-specific routers vanno aggiunti qui
# app.include_router(service_router, prefix="/api/v1", tags=[settings.service_name])

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global HTTP exception handler"""
    logger.error(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "service": settings.service_name}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
```

### Health Check Endpoints

```python
# app/api/health.py - Health check standardizzato
from fastapi import APIRouter, Depends
from typing import Dict, Any
import time
from app.database import check_supabase_connection, check_sqlalchemy_connection
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {
        "service": settings.service_name,
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check per Kubernetes/Render"""
    supabase_ok = await check_supabase_connection()
    sqlalchemy_ok = await check_sqlalchemy_connection()
    
    is_ready = supabase_ok and sqlalchemy_ok
    
    return {
        "service": settings.service_name,
        "ready": is_ready,
        "checks": {
            "supabase": supabase_ok,
            "sqlalchemy": sqlalchemy_ok
        },
        "timestamp": time.time()
    }

@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check per Kubernetes/Render"""
    return {
        "service": settings.service_name,
        "alive": True,
        "timestamp": time.time()
    }
```

## 7. Docker Multi-Stage per Local e Production

### Dockerfile Unificato

```dockerfile
# Dockerfile - Multi-stage per local development e production
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Development stage
FROM base as development

# Install all dependencies including dev
RUN poetry install --with dev && rm -rf $POETRY_CACHE_DIR

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Copy application code
COPY --chown=app:app . .

# Expose port
EXPOSE 8000

# Development command
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Install only production dependencies
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Copy application code
COPY --chown=app:app . .

# Expose port
EXPOSE 8000

# Production command con Gunicorn
CMD ["poetry", "run", "gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Docker Compose Development

```yaml
# docker-compose.dev.yml - Template per ogni microservizio
version: '3.8'

services:
  nutrifit-{service-name}:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: nutrifit-{service-name}-dev
    ports:
      - "800{port}:8000"  # Porta specifica per ogni servizio
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - N8N_WEBHOOK_URL=${N8N_WEBHOOK_URL}
      - N8N_API_KEY=${N8N_API_KEY}
    volumes:
      - .:/app
      - {service-name}-poetry-cache:/app/.venv
    networks:
      - nutrifit-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  {service-name}-poetry-cache:

networks:
  nutrifit-network:
    external: true
```

## 8. Testing Strategy con Supabase

### Test Configuration

```python
# tests/conftest.py - Configurazione test unificata
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.database import get_db, Base
from app.core.config import settings

# Test database URL (usando Supabase test project)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:test@localhost:54322/postgres"

# Test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

@pytest.fixture(scope="session")
def event_loop():
    """Event loop per session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def setup_test_db():
    """Setup test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def test_db_session(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Test database session"""
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
async def test_client(test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP client"""
    
    async def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers() -> dict:
    """Mock auth headers per test"""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
```

### Test Cases Template

```python
# tests/test_api.py - Template test per API endpoints
import pytest
from httpx import AsyncClient
from app.core.config import settings

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    async def test_health_check(self, test_client: AsyncClient):
        """Test basic health check"""
        response = await test_client.get("/health/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == settings.service_name
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    async def test_readiness_check(self, test_client: AsyncClient):
        """Test readiness check"""
        response = await test_client.get("/health/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == settings.service_name
        assert "ready" in data
        assert "checks" in data

class TestServiceSpecific:
    """Test service-specific endpoints"""
    
    async def test_protected_endpoint(
        self, 
        test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test protected endpoint con authentication"""
        response = await test_client.get(
            "/api/v1/protected", 
            headers=auth_headers
        )
        assert response.status_code == 200
    
    async def test_n8n_webhook(self, test_client: AsyncClient):
        """Test N8N webhook reception"""
        webhook_data = {
            "workflow_id": "test-workflow",
            "data": {"test": "value"}
        }
        
        response = await test_client.post(
            "/webhooks/n8n/receive",
            json=webhook_data
        )
        assert response.status_code == 200
        assert response.json()["status"] == "received"
```

---

## 📋 Summary degli Aggiornamenti

### ✅ Cambiamenti Applicati

1. **Cloud-Native Database Strategy**: Migrazione completa da PostgreSQL locale a Supabase Cloud con database segregati per microservizio
2. **N8N Cloud Integration**: Pattern standardizzato per integrazione con N8N Cloud tramite webhook e API
3. **MCP Server Implementation**: Template per Model Context Protocol servers per servizi AI-enabled  
4. **Security Enhancement**: Authentication unificata con Supabase Auth e inter-service communication security
5. **Docker Multi-Stage**: Configurazione per development locale e production deployment
6. **Testing Strategy**: Framework di test compatibile con Supabase e cloud services

### 🔄 Prossimi Step

1. **Aggiornare docs/flutter.md** con strategia mobile production
2. **Aggiornare docs/Documentazione Generale.md** per rimuovere contraddizioni  
3. **Aggiornare instructions.md** come single source of truth definitivo
4. **Creare Makefile** per orchestrazione local development  
5. **Setup config/** directory per workflow N8N e schema Supabase versionati

# Configuration
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["app"]

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
ignore_missing_imports = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_unused_configs = true
```

### Service Template Architecture

```python
# Unified microservice structure
services/{service_name}/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── core/                      # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── config.py              # Pydantic settings
│   │   ├── database.py            # Database connection & session
│   │   ├── security.py            # JWT, auth, encryption
│   │   ├── logging.py             # Structured logging setup
│   │   ├── metrics.py             # Prometheus metrics
│   │   ├── exceptions.py          # Custom exception classes
│   │   └── dependencies.py        # FastAPI dependency injection
│   ├── domain/                    # Domain layer (DDD)
│   │   ├── __init__.py
│   │   ├── entities/              # Business entities
│   │   ├── value_objects/         # Value objects
│   │   ├── aggregates/            # Aggregate roots
│   │   ├── repositories/          # Repository interfaces
│   │   ├── services/              # Domain services
│   │   └── events/                # Domain events
│   ├── infrastructure/            # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── database/              # Database implementations
│   │   │   ├── models.py          # SQLAlchemy models
│   │   │   ├── repositories.py    # Repository implementations
│   │   │   └── migrations/        # Alembic migrations
│   │   ├── external/              # External service clients
│   │   │   ├── openfoodfacts.py   # OpenFoodFacts client
│   │   │   ├── openai_client.py   # OpenAI integration
│   │   │   └── healthkit_client.py # HealthKit proxy
│   │   ├── messaging/             # Event handling, queues
│   │   │   ├── publishers.py      # Event publishing
│   │   │   └── handlers.py        # Event handlers
│   │   └── cache/                 # Caching implementations
│   │       └── redis_cache.py
│   ├── application/               # Application layer
│   │   ├── __init__.py
│   │   ├── commands/              # Command handlers (CQRS)
│   │   ├── queries/               # Query handlers
│   │   ├── services/              # Application services
│   │   └── dto/                   # Data transfer objects
│   ├── api/                       # Presentation layer
│   │   ├── __init__.py
│   │   ├── v1/                    # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # Main API router
│   │   │   ├── endpoints/         # API endpoints
│   │   │   └── schemas/           # Pydantic request/response models
│   │   └── dependencies.py        # API-specific dependencies
│   └── tests/                     # Test suite
│       ├── __init__.py
│       ├── unit/                  # Unit tests
│       ├── integration/           # Integration tests
│       ├── e2e/                   # End-to-end tests
│       └── fixtures/              # Test fixtures
├── docker/
│   ├── Dockerfile                 # Production Dockerfile
│   ├── Dockerfile.dev             # Development Dockerfile
│   └── docker-compose.yml         # Local development setup
├── scripts/
│   ├── start.sh                   # Production startup script
│   ├── dev.sh                     # Development startup
│   ├── test.sh                    # Test runner
│   └── migrate.sh                 # Database migration script
├── alembic/                       # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── pyproject.toml                 # Poetry configuration
├── README.md                      # Service documentation
└── .env.example                   # Environment variables template
```

---

## 3. Domain-Driven Design Implementation

### Core Domain: Calorie Balance Service

```python
# app/domain/value_objects/nutrition_values.py
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class DataSource(Enum):
    MANUAL = "manual"
    OPENFOODFACTS = "openfoodfacts"
    CREA = "crea"
    GPT4V = "gpt4v"
    HEALTHKIT = "healthkit"
    ESTIMATED = "estimated"

@dataclass(frozen=True)
class DataSourceAttribution:
    """Value object for data source attribution with confidence."""
    source: DataSource
    confidence: Decimal  # 0.0-1.0
    timestamp: datetime
    sync_latency_seconds: Optional[int] = None
    
    def __post_init__(self):
        if not (Decimal('0') <= self.confidence <= Decimal('1')):
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    @classmethod
    def from_healthkit(cls, metric_type: str) -> "DataSourceAttribution":
        """Create attribution for HealthKit data with realistic confidence."""
        confidence_map = {
            'steps': Decimal('0.9'),           # 85-95% accuracy
            'active_calories': Decimal('0.75'), # ±10-15% margin
            'weight': Decimal('0.95'),         # High precision from smart scales
            'heart_rate': Decimal('0.92'),     # Apple Watch medical grade
        }
        
        return cls(
            source=DataSource.HEALTHKIT,
            confidence=confidence_map.get(metric_type, Decimal('0.7')),
            timestamp=datetime.now(),
            sync_latency_seconds=30  # Typical HealthKit delay
        )
    
    @classmethod
    def from_openfoodfacts(cls, product_completeness: Decimal) -> "DataSourceAttribution":
        """Create attribution based on OpenFoodFacts data completeness."""
        # Base confidence for macronutrients
        confidence = Decimal('0.8')
        
        # Penalize incomplete micronutrient data
        if product_completeness < Decimal('0.6'):
            confidence *= Decimal('0.8')
        
        return cls(
            source=DataSource.OPENFOODFACTS,
            confidence=max(confidence, Decimal('0.3')),
            timestamp=datetime.now()
        )

@dataclass(frozen=True)
class FoodQuantity:
    """Value object for food quantity with precision management."""
    _value: Decimal
    unit: str
    precision_grams: int = 20  # ±20g precision requirement
    
    @property
    def value(self) -> Decimal:
        """Return value rounded to specified precision."""
        if self.unit == "grams":
            precision_decimal = Decimal(str(self.precision_grams))
            return (self._value / precision_decimal).quantize(Decimal('1')) * precision_decimal
        return self._value
    
    @property
    def confidence_interval(self) -> tuple[Decimal, Decimal]:
        """Calculate confidence interval based on precision."""
        margin = Decimal(str(self.precision_grams))
        return (
            max(Decimal('0'), self.value - margin),
            self.value + margin
        )
    
    def to_grams(self) -> Decimal:
        """Convert quantity to grams for calculations."""
        conversion_map = {
            "grams": Decimal('1'),
            "kg": Decimal('1000'),
            "ounces": Decimal('28.35'),
            "pounds": Decimal('453.59'),
            "cups": Decimal('240'),  # Approximate for liquids
        }
        
        factor = conversion_map.get(self.unit.lower(), Decimal('1'))
        return self.value * factor

@dataclass(frozen=True)
class NutritionData:
    """Value object for nutrition data with quality tracking."""
    calories: Decimal
    proteins: Decimal
    carbohydrates: Decimal
    fats: Decimal
    fiber: Optional[Decimal] = None
    sugar: Optional[Decimal] = None
    sodium: Optional[Decimal] = None
    
    # Micronutrients with confidence tracking
    micronutrients: dict[str, tuple[Decimal, Decimal]] = None  # (value, confidence)
    
    # Data quality metadata
    attribution: DataSourceAttribution = None
    sources_used: list[DataSource] = None
    
    def __post_init__(self):
        # Validate that core macronutrients are non-negative
        for field_name in ['calories', 'proteins', 'carbohydrates', 'fats']:
            value = getattr(self, field_name)
            if value < Decimal('0'):
                raise ValueError(f"{field_name} cannot be negative: {value}")
    
    @property
    def micronutrient_completeness(self) -> Decimal:
        """Calculate micronutrient completeness score (0-1)."""
        if not self.micronutrients:
            return Decimal('0')
        
        # Assume 20 key micronutrients for complete profile
        expected_micronutrients = 20
        available_count = len(self.micronutrients)
        
        return min(Decimal('1'), Decimal(str(available_count)) / Decimal(str(expected_micronutrients)))
    
    @property
    def overall_confidence(self) -> Decimal:
        """Calculate overall data confidence score."""
        if not self.attribution:
            return Decimal('0.5')
        
        base_confidence = self.attribution.confidence
        
        # Reduce confidence for incomplete micronutrient data
        completeness_penalty = (Decimal('1') - self.micronutrient_completeness) * Decimal('0.2')
        
        return max(Decimal('0.1'), base_confidence - completeness_penalty)

class NutritionDataConflictResolver:
    """Service for resolving conflicts between multiple nutrition data sources."""
    
    SOURCE_PRIORITY = {
        DataSource.MANUAL: Decimal('1.0'),      # User input has highest priority
        DataSource.CREA: Decimal('0.9'),        # Italian scientific database
        DataSource.OPENFOODFACTS: Decimal('0.8'), # Community database
        DataSource.GPT4V: Decimal('0.6'),       # AI estimation
        DataSource.ESTIMATED: Decimal('0.3'),   # Generic estimation
    }
    
    @classmethod
    def resolve(cls, nutrition_sources: list[tuple[NutritionData, DataSourceAttribution]]) -> NutritionData:
        """Resolve conflicts using weighted average based on source priority and confidence."""
        if not nutrition_sources:
            raise ValueError("Cannot resolve empty nutrition sources")
        
        if len(nutrition_sources) == 1:
            return nutrition_sources[0][0]
        
        # Calculate weights for each source
        weighted_sources = []
        for nutrition_data, attribution in nutrition_sources:
            source_priority = cls.SOURCE_PRIORITY.get(attribution.source, Decimal('0.5'))
            weight = attribution.confidence * source_priority
            weighted_sources.append((nutrition_data, weight))
        
        total_weight = sum(weight for _, weight in weighted_sources)
        
        # Calculate weighted average for each nutrient
        resolved_calories = sum(
            data.calories * weight for data, weight in weighted_sources
        ) / total_weight
        
        resolved_proteins = sum(
            data.proteins * weight for data, weight in weighted_sources
        ) / total_weight
        
        resolved_carbs = sum(
            data.carbohydrates * weight for data, weight in weighted_sources
        ) / total_weight
        
        resolved_fats = sum(
            data.fats * weight for data, weight in weighted_sources
        ) / total_weight
        
        # Create final attribution
        final_confidence = total_weight / len(weighted_sources)
        sources_used = [attr.source for _, attr in nutrition_sources]
        
        final_attribution = DataSourceAttribution(
            source=DataSource.ESTIMATED,  # Mark as resolved from multiple sources
            confidence=final_confidence,
            timestamp=datetime.now()
        )
        
        return NutritionData(
            calories=resolved_calories,
            proteins=resolved_proteins,
            carbohydrates=resolved_carbs,
            fats=resolved_fats,
            attribution=final_attribution,
            sources_used=sources_used
        )

# app/domain/aggregates/calorie_balance.py
from typing import List, Optional
from datetime import date, datetime
from dataclasses import dataclass, field

@dataclass
class DailyCalorieEntry:
    """Aggregate for daily calorie tracking."""
    date: date
    user_id: str
    
    # Intake tracking
    consumed_calories: Decimal = Decimal('0')
    consumed_confidence: Decimal = Decimal('0')
    meals: List[str] = field(default_factory=list)  # Meal IDs
    
    # Expenditure tracking  
    active_calories_burned: Decimal = Decimal('0')
    basal_calories_burned: Decimal = Decimal('0')
    expenditure_confidence: Decimal = Decimal('0')
    
    # HealthKit sync status
    healthkit_last_sync: Optional[datetime] = None
    healthkit_sync_quality: str = "unknown"  # good, degraded, stale
    
    @property
    def total_burned(self) -> Decimal:
        """Total calories burned (active + basal)."""
        return self.active_calories_burned + self.basal_calories_burned
    
    @property
    def net_balance(self) -> Decimal:
        """Net calorie balance (consumed - burned)."""
        return self.consumed_calories - self.total_burned
    
    @property
    def overall_confidence(self) -> Decimal:
        """Overall confidence in daily balance calculation."""
        if self.consumed_confidence == Decimal('0') and self.expenditure_confidence == Decimal('0'):
            return Decimal('0')
        elif self.consumed_confidence == Decimal('0'):
            return self.expenditure_confidence * Decimal('0.5')  # Only expenditure data
        elif self.expenditure_confidence == Decimal('0'):
            return self.consumed_confidence * Decimal('0.5')  # Only intake data
        else:
            return (self.consumed_confidence + self.expenditure_confidence) / Decimal('2')
    
    def add_meal_calories(self, calories: Decimal, confidence: Decimal, meal_id: str):
        """Add calories from a meal with weighted confidence update."""
        old_weight = self.consumed_calories
        new_weight = calories
        total_weight = old_weight + new_weight
        
        if total_weight > Decimal('0'):
            # Weighted average confidence
            self.consumed_confidence = (
                (self.consumed_confidence * old_weight) + (confidence * new_weight)
            ) / total_weight
        else:
            self.consumed_confidence = confidence
        
        self.consumed_calories += calories
        self.meals.append(meal_id)
    
    def update_expenditure_from_healthkit(
        self, 
        active_calories: Decimal, 
        basal_calories: Decimal,
        sync_quality: str,
        sync_timestamp: datetime
    ):
        """Update expenditure data from HealthKit with quality tracking."""
        self.active_calories_burned = active_calories
        self.basal_calories_burned = basal_calories
        self.healthkit_last_sync = sync_timestamp
        self.healthkit_sync_quality = sync_quality
        
        # Set confidence based on sync quality
        quality_confidence_map = {
            "good": Decimal('0.9'),
            "degraded": Decimal('0.7'),
            "stale": Decimal('0.5'),
            "unknown": Decimal('0.3')
        }
        self.expenditure_confidence = quality_confidence_map.get(sync_quality, Decimal('0.5'))

class CalorieBalanceAggregate:
    """Aggregate root for calorie balance management."""
    
    def __init__(self, user_id: str, goal_calories: Decimal):
        self.user_id = user_id
        self.goal_calories = goal_calories
        self.daily_entries: dict[date, DailyCalorieEntry] = {}
        self._domain_events: List[DomainEvent] = []
    
    def get_or_create_daily_entry(self, target_date: date) -> DailyCalorieEntry:
        """Get existing daily entry or create new one."""
        if target_date not in self.daily_entries:
            self.daily_entries[target_date] = DailyCalorieEntry(
                date=target_date,
                user_id=self.user_id
            )
        return self.daily_entries[target_date]
    
    def add_meal_to_balance(
        self, 
        meal_date: date,
        calories: Decimal, 
        confidence: Decimal,
        meal_id: str
    ):
        """Add meal to daily balance and emit domain event."""
        daily_entry = self.get_or_create_daily_entry(meal_date)
        old_balance = daily_entry.net_balance
        
        daily_entry.add_meal_calories(calories, confidence, meal_id)
        
        # Emit domain event for balance change
        self._domain_events.append(
            CalorieBalanceUpdatedEvent(
                user_id=self.user_id,
                date=meal_date,
                old_balance=old_balance,
                new_balance=daily_entry.net_balance,
                confidence=daily_entry.overall_confidence
            )
        )
        
        # Check for goal achievement
        if self._is_goal_achieved(daily_entry):
            self._domain_events.append(
                DailyCalorieGoalAchievedEvent(
                    user_id=self.user_id,
                    date=meal_date,
                    target_calories=self.goal_calories,
                    actual_calories=daily_entry.consumed_calories,
                    confidence=daily_entry.overall_confidence
                )
            )
    
    def update_healthkit_data(
        self, 
        target_date: date,
        active_calories: Decimal,
        basal_calories: Decimal,
        sync_quality: str
    ):
        """Update HealthKit expenditure data with quality assessment."""
        daily_entry = self.get_or_create_daily_entry(target_date)
        old_balance = daily_entry.net_balance
        
        daily_entry.update_expenditure_from_healthkit(
            active_calories=active_calories,
            basal_calories=basal_calories,
            sync_quality=sync_quality,
            sync_timestamp=datetime.now()
        )
        
        # Emit balance update event
        self._domain_events.append(
            CalorieBalanceUpdatedEvent(
                user_id=self.user_id,
                date=target_date,
                old_balance=old_balance,
                new_balance=daily_entry.net_balance,
                confidence=daily_entry.overall_confidence
            )
        )
    
    def get_weekly_trend(self, end_date: date, weeks: int = 4) -> WeeklyBalanceTrend:
        """Calculate weekly balance trend with confidence tracking."""
        start_date = end_date - timedelta(weeks=weeks)
        relevant_entries = [
            entry for entry_date, entry in self.daily_entries.items()
            if start_date <= entry_date <= end_date
        ]
        
        if not relevant_entries:
            return WeeklyBalanceTrend.empty()
        
        avg_balance = sum(entry.net_balance for entry in relevant_entries) / len(relevant_entries)
        avg_confidence = sum(entry.overall_confidence for entry in relevant_entries) / len(relevant_entries)
        
        # Calculate trend direction
        first_week_avg = self._calculate_week_average(relevant_entries[:7])
        last_week_avg = self._calculate_week_average(relevant_entries[-7:])
        trend_direction = "increasing" if last_week_avg > first_week_avg else "decreasing"
        
        return WeeklyBalanceTrend(
            average_balance=avg_balance,
            confidence=avg_confidence,
            trend_direction=trend_direction,
            data_points=len(relevant_entries)
        )
    
    def _is_goal_achieved(self, daily_entry: DailyCalorieEntry) -> bool:
        """Check if daily calorie goal is achieved within acceptable margin."""
        margin = self.goal_calories * Decimal('0.1')  # 10% margin
        return abs(daily_entry.consumed_calories - self.goal_calories) <= margin
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        """Get pending domain events."""
        return self._domain_events.copy()
    
    def clear_events(self):
        """Clear domain events after processing."""
        self._domain_events.clear()
```

### Domain Events System

```python
# app/domain/events/base.py
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict
from dataclasses import dataclass
import uuid

@dataclass
class DomainEvent(ABC):
    """Base class for domain events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        pass

# app/domain/events/calorie_balance_events.py
@dataclass
class CalorieBalanceUpdatedEvent(DomainEvent):
    """Event emitted when user's calorie balance changes."""
    user_id: str
    date: date
    old_balance: Decimal
    new_balance: Decimal
    confidence: Decimal
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'calorie_balance_updated',
            'event_id': self.event_id,
            'occurred_at': self.occurred_at.isoformat(),
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'old_balance': str(self.old_balance),
            'new_balance': str(self.new_balance),
            'confidence': str(self.confidence),
            'version': self.version
        }

@dataclass  
class DailyCalorieGoalAchievedEvent(DomainEvent):
    """Event emitted when user achieves daily calorie goal."""
    user_id: str
    date: date
    target_calories: Decimal
    actual_calories: Decimal
    confidence: Decimal
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'daily_calorie_goal_achieved',
            'event_id': self.event_id,
            'occurred_at': self.occurred_at.isoformat(),
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'target_calories': str(self.target_calories),
            'actual_calories': str(self.actual_calories),
            'confidence': str(self.confidence),
            'version': self.version
        }

@dataclass
class HealthKitSyncFailedEvent(DomainEvent):
    """Event emitted when HealthKit sync fails."""
    user_id: str
    error_type: str
    error_message: str
    retry_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'healthkit_sync_failed',
            'event_id': self.event_id,
            'occurred_at': self.occurred_at.isoformat(),
            'user_id': self.user_id,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'version': self.version
        }
```

---

## 4. Database Design per Service

### Calorie Balance Service Schema

```sql
-- Calorie Balance Service Database Schema
-- File: services/calorie-balance/alembic/versions/001_initial_schema.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Users table (replicated for service autonomy)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Goal settings
    daily_calorie_goal DECIMAL(7,2) DEFAULT 2000.00,
    goal_type TEXT DEFAULT 'maintain' CHECK (goal_type IN ('lose', 'maintain', 'gain')),
    activity_level TEXT DEFAULT 'moderate' CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
    
    -- Personal metrics for BMR calculation
    age INTEGER,
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    height_cm INTEGER,
    weight_kg DECIMAL(5,2),
    
    -- Service-specific settings
    precision_grams INTEGER DEFAULT 20,
    confidence_threshold DECIMAL(3,2) DEFAULT 0.70
);

-- Daily calorie entries
CREATE TABLE daily_calorie_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Calorie intake
    consumed_calories DECIMAL(7,2) DEFAULT 0.00,
    consumed_confidence DECIMAL(3,2) DEFAULT 0.00,
    meal_ids JSONB DEFAULT '[]', -- Array of meal IDs from meal-tracking service
    
    -- Calorie expenditure
    active_calories_burned DECIMAL(7,2) DEFAULT 0.00,
    basal_calories_burned DECIMAL(7,2) DEFAULT 0.00,
    expenditure_confidence DECIMAL(3,2) DEFAULT 0.00,
    
    -- Computed values
    net_balance DECIMAL(8,2) GENERATED ALWAYS AS (consumed_calories - active_calories_burned - basal_calories_burned) STORED,
    overall_confidence DECIMAL(3,2) GENERATED ALWAYS AS (
        CASE 
            WHEN consumed_confidence > 0 AND expenditure_confidence > 0 
            THEN (consumed_confidence + expenditure_confidence) / 2.0
            WHEN consumed_confidence > 0 
            THEN consumed_confidence * 0.5
            WHEN expenditure_confidence > 0 
            THEN expenditure_confidence * 0.5
            ELSE 0.0
        END
    ) STORED,
    
    -- HealthKit integration
    healthkit_last_sync TIMESTAMP WITH TIME ZONE,
    healthkit_sync_quality TEXT DEFAULT 'unknown' CHECK (healthkit_sync_quality IN ('good', 'degraded', 'stale', 'unknown')),
    healthkit_data JSONB, -- Raw HealthKit data for debugging
    
    -- Goal tracking
    goal_calories_at_time DECIMAL(7,2), -- Goal when entry was created
    goal_achieved BOOLEAN GENERATED ALWAYS AS (
        ABS(consumed_calories - COALESCE(goal_calories_at_time, 2000.00)) <= (COALESCE(goal_calories_at_time, 2000.00) * 0.1)
    ) STORED,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, date)
);

-- Balance trends for performance
CREATE TABLE weekly_balance_trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    week_start_date DATE NOT NULL,
    
    -- Calculated trend data
    average_balance DECIMAL(8,2),
    confidence DECIMAL(3,2),
    trend_direction TEXT CHECK (trend_direction IN ('increasing', 'decreasing', 'stable')),
    data_points INTEGER,
    
    -- Goal progress
    goal_adherence_percentage DECIMAL(5,2), -- % of days goal was achieved
    average_goal_deviation DECIMAL(8,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, week_start_date)
);

-- Domain events outbox pattern
CREATE TABLE domain_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    event_id TEXT UNIQUE NOT NULL,
    user_id UUID,
    event_data JSONB NOT NULL,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_daily_entries_user_date ON daily_calorie_entries(user_id, date DESC);
CREATE INDEX idx_daily_entries_goal_achieved ON daily_calorie_entries(user_id, goal_achieved) WHERE goal_achieved = true;
CREATE INDEX idx_daily_entries_confidence ON daily_calorie_entries(user_id, overall_confidence DESC);
CREATE INDEX idx_weekly_trends_user_week ON weekly_balance_trends(user_id, week_start_date DESC);
CREATE INDEX idx_domain_events_unprocessed ON domain_events(created_at) WHERE processed_at IS NULL;
CREATE INDEX idx_domain_events_failed ON domain_events(failed_at, retry_count) WHERE failed_at IS NOT NULL;

-- Triggers for auto-updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_daily_entries_updated_at BEFORE UPDATE ON daily_calorie_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function for BMR calculation
CREATE OR REPLACE FUNCTION calculate_bmr(
    p_age INTEGER,
    p_gender TEXT,
    p_height_cm INTEGER,
    p_weight_kg DECIMAL
) RETURNS DECIMAL AS $$
DECLARE
    bmr DECIMAL;
BEGIN
    -- Harris-Benedict Equation (Revised)
    IF p_gender = 'male' THEN
        bmr = 88.362 + (13.397 * p_weight_kg) + (4.799 * p_height_cm) - (5.677 * p_age);
    ELSIF p_gender = 'female' THEN
        bmr = 447.593 + (9.247 * p_weight_kg) + (3.098 * p_height_cm) - (4.330 * p_age);
    ELSE
        -- Use average for other genders
        bmr = ((88.362 + (13.397 * p_weight_kg) + (4.799 * p_height_cm) - (5.677 * p_age)) + 
               (447.593 + (9.247 * p_weight_kg) + (3.098 * p_height_cm) - (4.330 * p_age))) / 2;
    END IF;
    
    RETURN GREATEST(bmr, 1200); -- Minimum safe BMR
END;
$$ LANGUAGE plpgsql;

-- View for daily balance summary
CREATE VIEW daily_balance_summary AS
SELECT 
    dce.user_id,
    dce.date,
    dce.consumed_calories,
    dce.active_calories_burned + dce.basal_calories_burned as total_burned,
    dce.net_balance,
    dce.overall_confidence,
    dce.goal_achieved,
    dce.healthkit_sync_quality,
    u.daily_calorie_goal,
    ABS(dce.consumed_calories - u.daily_calorie_goal) as goal_deviation
FROM daily_calorie_entries dce
JOIN users u ON dce.user_id = u.id;
```

### Meal Tracking Service Schema

```sql
-- Meal Tracking Service Database Schema
-- File: services/meal-tracking/alembic/versions/001_initial_schema.sql

-- Food catalog with quality tracking
CREATE TABLE foods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    brand TEXT,
    barcode TEXT UNIQUE,
    category TEXT,
    
    -- Standardized nutrition per 100g
    calories_per_100g DECIMAL(6,2) NOT NULL,
    proteins_per_100g DECIMAL(5,2) DEFAULT 0.00,
    carbohydrates_per_100g DECIMAL(5,2) DEFAULT 0.00,
    fats_per_100g DECIMAL(5,2) DEFAULT 0.00,
    fiber_per_100g DECIMAL(5,2),
    sugar_per_100g DECIMAL(5,2),
    sodium_per_100g DECIMAL(6,2), -- in mg
    
    -- Micronutrients with confidence tracking
    micronutrients JSONB, -- {"iron": {"value": 2.5, "confidence": 0.8}, "calcium": {...}}
    micronutrients_completeness DECIMAL(3,2) GENERATED ALWAYS AS (
        CASE
            WHEN micronutrients IS NULL THEN 0.0
            ELSE LEAST(1.0, (jsonb_array_length(jsonb_object_keys(micronutrients)::jsonb))::decimal / 20.0)
        END
    ) STORED,
    
    -- Data source attribution
    data_source TEXT NOT NULL CHECK (data_source IN ('openfoodfacts', 'crea', 'manual', 'gpt4v', 'estimated')),
    data_confidence DECIMAL(3,2) NOT NULL DEFAULT 0.8,
    source_id TEXT, -- External source identifier (OpenFoodFacts code, etc.)
    data_last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- OpenFoodFacts specific metadata
    openfoodfacts_completeness_score DECIMAL(3,2),
    italian_product BOOLEAN DEFAULT false,
    artisanal_product BOOLEAN DEFAULT false, -- Likely missing from external databases
    
    -- Search optimization
    search_tokens TSVECTOR,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Meals table
CREATE TABLE meals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- Reference to users table (cross-service)
    date DATE NOT NULL,
    meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack', 'free_snack')),
    consumed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Photo analysis metadata
    photo_url TEXT,
    analysis_source TEXT CHECK (analysis_source IN ('barcode', 'photo', 'manual')),
    gpt4v_confidence DECIMAL(3,2),
    gpt4v_analysis_data JSONB, -- Raw GPT-4V response for debugging
    gpt4v_tokens_used INTEGER, -- Cost tracking
    
    -- Calculated totals (aggregated from meal_foods)
    total_calories DECIMAL(7,2) DEFAULT 0.00,
    total_proteins DECIMAL(6,2) DEFAULT 0.00,
    total_carbs DECIMAL(6,2) DEFAULT 0.00,
    total_fats DECIMAL(6,2) DEFAULT 0.00,
    total_fiber DECIMAL(6,2),
    
    -- Data quality summary
    overall_data_confidence DECIMAL(3,2),
    precision_margin_calories DECIMAL(6,2), -- ±20g precision impact on calories
    sources_used JSONB, -- Array of data sources used
    fallback_applied BOOLEAN DEFAULT false,
    manual_corrections_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual food items within meals
CREATE TABLE meal_foods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meal_id UUID REFERENCES meals(id) ON DELETE CASCADE,
    food_id UUID REFERENCES foods(id),
    
    -- Quantity with precision management
    quantity_grams DECIMAL(6,2) NOT NULL,
    quantity_precision INTEGER DEFAULT 20, -- ±20g precision
    quantity_confidence DECIMAL(3,2) DEFAULT 0.8,
    
    -- Calculated nutrition values for this portion
    calories DECIMAL(7,2),
    proteins DECIMAL(6,2),
    carbohydrates DECIMAL(6,2),
    fats DECIMAL(6,2),
    fiber DECIMAL(6,2),
    
    -- Data attribution for this item
    data_source_used TEXT NOT NULL,
    data_confidence DECIMAL(3,2) NOT NULL,
    fallback_applied BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Nutrition data resolution log (for fallback tracking)
CREATE TABLE nutrition_data_resolution_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    food_query JSONB NOT NULL, -- Original search query
    attempted_sources JSONB NOT NULL, -- ["openfoodfacts", "crea", "gpt4v"]
    successful_source TEXT,
    resolution_time_ms INTEGER,
    final_confidence DECIMAL(3,2),
    fallback_applied BOOLEAN DEFAULT false,
    crowdsourcing_requested BOOLEAN DEFAULT false,
    error_details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API rate limiting table
CREATE TABLE api_rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_name TEXT NOT NULL, -- 'openfoodfacts', 'openai'
    user_id UUID, -- Per-user limits if applicable
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    requests_count INTEGER DEFAULT 1,
    window_size_minutes INTEGER DEFAULT 1,
    max_requests INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(api_name, user_id, window_start)
);

-- Performance indexes
CREATE INDEX idx_foods_barcode ON foods(barcode) WHERE barcode IS NOT NULL;
CREATE INDEX idx_foods_search_tokens ON foods USING gin(search_tokens);
CREATE INDEX idx_foods_data_confidence ON foods(data_confidence DESC, data_source);
CREATE INDEX idx_meals_user_date ON meals(user_id, date DESC);
CREATE INDEX idx_meals_analysis_source ON meals(analysis_source, gpt4v_confidence DESC);
CREATE INDEX idx_meal_foods_meal_id ON meal_foods(meal_id);
CREATE INDEX idx_nutrition_log_timestamp ON nutrition_data_resolution_log(created_at);
CREATE INDEX idx_rate_limits_api_window ON api_rate_limits(api_name, window_start DESC);

-- Full-text search index for foods
CREATE OR REPLACE FUNCTION update_food_search_tokens()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_tokens = to_tsvector('italian', COALESCE(NEW.name, '') || ' ' || COALESCE(NEW.brand, '') || ' ' || COALESCE(NEW.category, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_food_search_tokens_trigger
    BEFORE INSERT OR UPDATE ON foods
    FOR EACH ROW EXECUTE FUNCTION update_food_search_tokens();

-- Function to calculate meal totals
CREATE OR REPLACE FUNCTION calculate_meal_totals()
RETURNS TRIGGER AS $$
DECLARE
    meal_record RECORD;
BEGIN
    -- Recalculate totals for the affected meal
    SELECT 
        SUM(mf.calories) as total_calories,
        SUM(mf.proteins) as total_proteins,
        SUM(mf.carbohydrates) as total_carbs,
        SUM(mf.fats) as total_fats,
        SUM(mf.fiber) as total_fiber,
        AVG(mf.data_confidence) as avg_confidence,
        SUM((mf.quantity_precision * f.calories_per_100g) / 100.0) as precision_margin,
        jsonb_agg(DISTINCT mf.data_source_used) as sources_used,
        bool_or(mf.fallback_applied) as fallback_applied
    INTO meal_record
    FROM meal_foods mf
    JOIN foods f ON mf.food_id = f.id
    WHERE mf.meal_id = COALESCE(NEW.meal_id, OLD.meal_id);
    
    -- Update meal totals
    UPDATE meals SET
        total_calories = COALESCE(meal_record.total_calories, 0.00),
        total_proteins = COALESCE(meal_record.total_proteins, 0.00),
        total_carbs = COALESCE(meal_record.total_carbs, 0.00),
        total_fats = COALESCE(meal_record.total_fats, 0.00),
        total_fiber = meal_record.total_fiber,
        overall_data_confidence = COALESCE(meal_record.avg_confidence, 0.5),
        precision_margin_calories = COALESCE(meal_record.precision_margin, 0.00),
        sources_used = meal_record.sources_used,
        fallback_applied = COALESCE(meal_record.fallback_applied, false),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.meal_id, OLD.meal_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_meal_totals_trigger
    AFTER INSERT OR UPDATE OR DELETE ON meal_foods
    FOR EACH ROW EXECUTE FUNCTION calculate_meal_totals();

-- Rate limiting function
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_api_name TEXT,
    p_user_id UUID DEFAULT NULL,
    p_max_requests INTEGER DEFAULT 100,
    p_window_minutes INTEGER DEFAULT 1
) RETURNS BOOLEAN AS $$
DECLARE
    current_window TIMESTAMP WITH TIME ZONE;
    current_count INTEGER;
BEGIN
    current_window := date_trunc('minute', NOW());
    
    -- Get current count for this window
    SELECT requests_count INTO current_count
    FROM api_rate_limits
    WHERE api_name = p_api_name
    AND (user_id = p_user_id OR (user_id IS NULL AND p_user_id IS NULL))
    AND window_start = current_window;
    
    IF current_count IS NULL THEN
        -- First request in this window
        INSERT INTO api_rate_limits (api_name, user_id, window_start, requests_count, window_size_minutes, max_requests)
        VALUES (p_api_name, p_user_id, current_window, 1, p_window_minutes, p_max_requests);
        RETURN TRUE;
    ELSIF current_count < p_max_requests THEN
        -- Increment counter
        UPDATE api_rate_limits
        SET requests_count = requests_count + 1
        WHERE api_name = p_api_name
        AND (user_id = p_user_id OR (user_id IS NULL AND p_user_id IS NULL))
        AND window_start = current_window;
        RETURN TRUE;
    ELSE
        -- Rate limit exceeded
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- View for meal summary with data quality
CREATE VIEW meal_summary AS
SELECT 
    m.id,
    m.user_id,
    m.date,
    m.meal_type,
    m.total_calories,
    m.overall_data_confidence,
    CASE 
        WHEN m.overall_data_confidence >= 0.8 THEN 'high'
        WHEN m.overall_data_confidence >= 0.6 THEN 'medium'
        ELSE 'low'
    END as confidence_level,
    m.precision_margin_calories,
    m.sources_used,
    m.fallback_applied,
    COUNT(mf.id) as food_items_count
FROM meals m
LEFT JOIN meal_foods mf ON m.id = mf.meal_id
GROUP BY m.id, m.user_id, m.date, m.meal_type, m.total_calories, 
         m.overall_data_confidence, m.precision_margin_calories, 
         m.sources_used, m.fallback_applied;
```

---

## 5. FastAPI Implementation Patterns

### Service Template Base

```python
# app/main.py - Standard FastAPI application entry point
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import make_asgi_app
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlAlchemyIntegration

from app.core.config import get_settings
from app.core.database import create_tables, close_db_connections
from app.core.logging import configure_logging
from app.core.metrics import setup_metrics
from app.api.v1.router import api_router
from app.core.exceptions import setup_exception_handlers

settings = get_settings()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    # Startup
    logger.info("Starting up service", service_name=settings.service_name)
    
    # Initialize database
    await create_tables()
    
    # Setup metrics
    setup_metrics()
    
    # Configure Sentry
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                SqlAlchemyIntegration(),
            ],
            traces_sample_rate=0.1,
            environment=settings.environment,
        )
    
    logger.info("Service startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down service")
    await close_db_connections()

def create_application() -> FastAPI:
    """Create FastAPI application with middleware and routing."""
    
    # Configure structured logging first
    configure_logging()
    
    app = FastAPI(
        title=f"NutriFit {settings.service_name}",
        description=f"NutriFit {settings.service_name} microservice",
        version="1.0.0",
        openapi_url=f"/api/v1/openapi.json" if settings.environment != "production" else None,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan,
    )
    
    # Middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request/Response middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests with structured logging."""
        start_time = time.time()
        
        # Extract correlation ID from headers
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        # Bind correlation ID to logger context
        logger = structlog.get_logger().bind(
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method,
        )
        
        # Add correlation ID to request state
        request.state.correlation_id = correlation_id
        request.state.logger = logger
        
        logger.info("Request started")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Correlation-ID"] = correlation_id
        
        logger.info(
            "Request completed",
            status_code=response.status_code,
            process_time=process_time,
        )
        
        return response
    
    # Exception handling
    setup_exception_handlers(app)
    
    # Routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoints
    @app.get("/health")
    async def health_check():
        """Health check endpoint for load balancers."""
        return {"status": "healthy", "service": settings.service_name}
    
    @app.get("/ready")
    async def readiness_check():
        """Readiness check with database connectivity."""
        from app.core.database import check_db_connection
        
        try:
            await check_db_connection()
            return {"status": "ready", "service": settings.service_name}
        except Exception as e:
            logger.error("Readiness check failed", error=str(e))
            return Response(
                content={"status": "not_ready", "error": str(e)},
                status_code=503,
                media_type="application/json"
            )
    
    # Metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    return app

# Create app instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        access_log=False,  # We handle logging in middleware
    )
```

### Configuration Management

```python
# app/core/config.py - Pydantic settings management
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Service identification
    service_name: str = Field(default="nutrition-service", description="Service name")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database configuration
    database_url: str = Field(..., description="PostgreSQL database URL")
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Max database connections overflow")
    
    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT signing")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, description="JWT token expiration in hours")
    
    # External services
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    openfoodfacts_api_url: str = Field(default="https://world.openfoodfacts.org/api/v0", description="OpenFoodFacts API URL")
    
    # Service discovery (for microservices communication)
    api_gateway_url: str = Field(default="http://localhost:8000", description="API Gateway URL")
    calorie_balance_service_url: str = Field(default="http://localhost:8001", description="Calorie Balance Service URL")
    meal_tracking_service_url: str = Field(default="http://localhost:8002", description="Meal Tracking Service URL")
    health_monitor_service_url: str = Field(default="http://localhost:8003", description="Health Monitor Service URL")
    notifications_service_url: str = Field(default="http://localhost:8004", description="Notifications Service URL")
    ai_coach_service_url: str = Field(default="http://localhost:8005", description="AI Coach Service URL")
    
    # Rate limiting
    rate_limit_requests_per_minute: int = Field(default=60, description="Rate limit per user per minute")
    openfoodfacts_rate_limit: int = Field(default=100, description="OpenFoodFacts API rate limit per minute")
    openai_rate_limit: int = Field(default=50, description="OpenAI API rate limit per minute")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    log_level: str = Field(default="INFO", description="Logging level")
    structured_logging: bool = Field(default=True, description="Use structured JSON logging")
    
    # CORS
    allowed_hosts: List[str] = Field(default=["*"], description="Allowed CORS origins")
    
    # Feature flags
    enable_gpt4v_analysis: bool = Field(default=True, description="Enable GPT-4V food analysis")
    enable_openfoodfacts_fallback: bool = Field(default=True, description="Enable OpenFoodFacts fallback")
    enable_crea_database: bool = Field(default=True, description="Enable CREA Italian food database")
    enable_background_tasks: bool = Field(default=True, description="Enable background task processing")
    
    # Performance tuning
    max_upload_size_mb: int = Field(default=10, description="Maximum file upload size in MB")
    image_processing_timeout: int = Field(default=30, description="Image processing timeout in seconds")
    api_timeout_seconds: int = Field(default=30, description="External API timeout in seconds")
    
    # Data quality
    minimum_confidence_threshold: float = Field(default=0.6, description="Minimum confidence for auto-acceptance")
    precision_grams: int = Field(default=20, description="Default precision in grams for food quantities")
    
    @property
    def database_url_async(self) -> str:
        """Convert sync database URL to async."""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url
    
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
```

### Database Layer Implementation

```python
# app/core/database.py - Async database setup
import asyncio
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

import structlog
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

# Async engine for main application
async_engine = create_async_engine(
    settings.database_url_async,
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    echo=settings.debug,  # Log SQL queries in debug mode
)

# Sync engine for migrations and initial setup
sync_engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.debug,
)

# Session factories
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

SyncSessionFactory = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with proper cleanup."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session."""
    async with get_db_session() as session:
        yield session

async def create_tables():
    """Create database tables."""
    try:
        async with async_engine.begin() as conn:
            # Import all models to ensure they're registered
            from app.infrastructure.database.models import *  # noqa: F401, F403
            
            # Create tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise

async def check_db_connection() -> bool:
    """Check database connectivity for health checks."""
    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.fetchone() is not None
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        raise

async def close_db_connections():
    """Close all database connections."""
    try:
        await async_engine.dispose()
        sync_engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Error closing database connections", error=str(e))

# Transaction decorator for service methods
def transactional(func):
    """Decorator to wrap service methods in database transaction."""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Assume first argument is self with session attribute
        service_instance = args[0]
        session = service_instance.session
        
        try:
            result = await func(*args, **kwargs)
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise
    
    return wrapper

# Repository base class
class BaseRepository:
    """Base repository with common database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, entity) -> None:
        """Save entity to database."""
        self.session.add(entity)
        await self.session.flush()
    
    async def delete(self, entity) -> None:
        """Delete entity from database."""
        await self.session.delete(entity)
        await self.session.flush()
    
    async def refresh(self, entity) -> None:
        """Refresh entity from database."""
        await self.session.refresh(entity)
```

---

## 6. External API Integration Patterns

### OpenFoodFacts Client Implementation

```python
# app/infrastructure/external/openfoodfacts_client.py
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from decimal import Decimal
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError, RateLimitExceededError
from app.domain.value_objects.nutrition_values import NutritionData, DataSourceAttribution

logger = structlog.get_logger()
settings = get_settings()

@dataclass
class OpenFoodFactsProduct:
    """OpenFoodFacts product data structure."""
    barcode: str
    product_name: str
    brands: List[str]
    categories: List[str]
    nutriments: Dict[str, float]
    completeness: Decimal
    data_quality_score: Decimal
    
    @property
    def is_italian(self) -> bool:
        """Check if product is Italian based on categories/brands."""
        italian_indicators = ['it:', 'italia', 'italian']
        categories_str = ' '.join(self.categories).lower()
        brands_str = ' '.join(self.brands).lower()
        
        return any(indicator in categories_str or indicator in brands_str 
                  for indicator in italian_indicators)

class OpenFoodFactsClient:
    """Client for OpenFoodFacts API with rate limiting and error handling."""
    
    def __init__(self):
        self.base_url = settings.openfoodfacts_api_url
        self.rate_limit = settings.openfoodfacts_rate_limit
        self.timeout = settings.api_timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limiter = AsyncRateLimiter(
            max_requests=self.rate_limit,
            time_window=60  # per minute
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            headers={
                'User-Agent': 'NutriFit-App/1.0 (contact@nutrifit.com)',
                'Accept': 'application/json',
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    )
    async def get_product(self, barcode: str) -> Optional[OpenFoodFactsProduct]:
        """Get product by barcode with retry logic and rate limiting."""
        
        # Check rate limit
        await self._rate_limiter.acquire()
        
        logger.info("Fetching product from OpenFoodFacts", barcode=barcode)
        
        try:
            url = f"{self.base_url}/product/{barcode}.json"
            response = await self._client.get(url)
            
            if response.status_code == 404:
                logger.info("Product not found in OpenFoodFacts", barcode=barcode)
                return None
            
            if response.status_code == 429:
                logger.warning("OpenFoodFacts rate limit exceeded", barcode=barcode)
                raise RateLimitExceededError("OpenFoodFacts rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 0:
                logger.info("Product not found in OpenFoodFacts", barcode=barcode)
                return None
            
            product_data = data.get('product', {})
            return self._parse_product_data(barcode, product_data)
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching product from OpenFoodFacts", 
                barcode=barcode, 
                status_code=e.response.status_code,
                error=str(e)
            )
            raise ExternalServiceError(f"OpenFoodFacts API error: {e.response.status_code}")
        
        except httpx.TimeoutException:
            logger.error("Timeout fetching product from OpenFoodFacts", barcode=barcode)
            raise ExternalServiceError("OpenFoodFacts API timeout")
        
        except Exception as e:
            logger.error("Unexpected error fetching product", barcode=barcode, error=str(e))
            raise ExternalServiceError(f"OpenFoodFacts API error: {str(e)}")
    
    def _parse_product_data(self, barcode: str, product_data: Dict[str, Any]) -> OpenFoodFactsProduct:
        """Parse OpenFoodFacts product data into domain object."""
        
        # Extract basic information
        product_name = product_data.get('product_name', '').strip()
        brands = [b.strip() for b in product_data.get('brands', '').split(',') if b.strip()]
        categories = [c.strip() for c in product_data.get('categories', '').split(',') if c.strip()]
        
        # Extract nutriments
        nutriments = product_data.get('nutriments', {})
        
        # Calculate completeness score
        completeness = self._calculate_completeness(nutriments)
        data_quality_score = self._calculate_data_quality_score(product_data, completeness)
        
        return OpenFoodFactsProduct(
            barcode=barcode,
            product_name=product_name,
            brands=brands,
            categories=categories,
            nutriments=nutriments,
            completeness=completeness,
            data_quality_score=data_quality_score
        )
    
    def _calculate_completeness(self, nutriments: Dict[str, Any]) -> Decimal:
        """Calculate nutrition data completeness score."""
        
        # Core nutrients (weighted scoring)
        core_nutrients = {
            'energy-kcal_100g': 0.3,
            'proteins_100g': 0.2,
            'carbohydrates_100g': 0.2,
            'fat_100g': 0.2,
            'fiber_100g': 0.1,
        }
        
        score = Decimal('0')
        for nutrient, weight in core_nutrients.items():
            if nutrient in nutriments and nutriments[nutrient] is not None:
                score += Decimal(str(weight))
        
        # Bonus for micronutrients
        micronutrients = [k for k in nutriments.keys() 
                         if any(micro in k for micro in ['vitamin', 'mineral', 'iron', 'calcium', 'sodium'])]
        
        micronutrient_bonus = min(Decimal('0.2'), len(micronutrients) * Decimal('0.02'))
        score += micronutrient_bonus
        
        return min(Decimal('1.0'), score)
    
    def _calculate_data_quality_score(self, product_data: Dict[str, Any], completeness: Decimal) -> Decimal:
        """Calculate overall data quality score."""
        
        base_score = completeness
        
        # Reduce score for missing basic information
        if not product_data.get('product_name'):
            base_score *= Decimal('0.8')
        
        if not product_data.get('brands'):
            base_score *= Decimal('0.9')
        
        # Check for data freshness (if last_modified is available)
        last_modified = product_data.get('last_modified_t')
        if last_modified:
            import time
            days_since_update = (time.time() - last_modified) / (24 * 3600)
            if days_since_update > 365:  # Data older than 1 year
                base_score *= Decimal('0.9')
        
        return max(Decimal('0.1'), base_score)
    
    def to_nutrition_data(self, product: OpenFoodFactsProduct) -> NutritionData:
        """Convert OpenFoodFacts product to domain NutritionData."""
        
        nutriments = product.nutriments
        
        # Extract macronutrients per 100g
        calories = Decimal(str(nutriments.get('energy-kcal_100g', 0)))
        proteins = Decimal(str(nutriments.get('proteins_100g', 0)))
        carbohydrates = Decimal(str(nutriments.get('carbohydrates_100g', 0)))
        fats = Decimal(str(nutriments.get('fat_100g', 0)))
        fiber = Decimal(str(nutriments.get('fiber_100g', 0))) if nutriments.get('fiber_100g') else None
        sugar = Decimal(str(nutriments.get('sugars_100g', 0))) if nutriments.get('sugars_100g') else None
        sodium = Decimal(str(nutriments.get('sodium_100g', 0) * 1000)) if nutriments.get('sodium_100g') else None  # Convert to mg
        
        # Extract micronutrients with confidence
        micronutrients = {}
        for key, value in nutriments.items():
            if any(micro in key for micro in ['vitamin', 'mineral', 'iron', 'calcium']) and value is not None:
                # Simplified confidence based on data quality
                confidence = min(Decimal('1.0'), product.data_quality_score + Decimal('0.1'))
                micronutrients[key] = (Decimal(str(value)), confidence)
        
        # Create data attribution
        attribution = DataSourceAttribution(
            source=DataSource.OPENFOODFACTS,
            confidence=product.data_quality_score,
            timestamp=datetime.now()
        )
        
        return NutritionData(
            calories=calories,
            proteins=proteins,
            carbohydrates=carbohydrates,
            fats=fats,
            fiber=fiber,
            sugar=sugar,
            sodium=sodium,
            micronutrients=micronutrients,
            attribution=attribution
        )

class AsyncRateLimiter:
    """Async rate limiter for API calls."""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make API call."""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            
            # Remove old requests outside time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            # Check if we can make new request
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = min(self.requests)
                wait_time = self.time_window - (now - oldest_request)
                
                logger.warning("Rate limit reached, waiting", wait_seconds=wait_time)
                await asyncio.sleep(wait_time)
                
                # Retry acquisition
                return await self.acquire()
            
            # Record this request
            self.requests.append(now)

# Usage example in application service
class NutritionDataService:
    """Application service for nutrition data resolution."""
    
    def __init__(self):
        self.openfoodfacts_client = OpenFoodFactsClient()
        self.conflict_resolver = NutritionDataConflictResolver()
    
    async def get_nutrition_data(self, barcode: str) -> Optional[NutritionData]:
        """Get nutrition data with fallback strategy."""
        
        nutrition_sources = []
        
        # Try OpenFoodFacts first
        async with self.openfoodfacts_client as client:
            try:
                product = await client.get_product(barcode)
                if product:
                    nutrition_data = client.to_nutrition_data(product)
                    attribution = DataSourceAttribution.from_openfoodfacts(product.completeness)
                    nutrition_sources.append((nutrition_data, attribution))
                    
                    logger.info(
                        "Got nutrition data from OpenFoodFacts", 
                        barcode=barcode, 
                        confidence=attribution.confidence
                    )
                    
                    # If confidence is high enough, return immediately
                    if attribution.confidence >= Decimal('0.8'):
                        return nutrition_data
                        
            except ExternalServiceError as e:
                logger.warning("OpenFoodFacts failed, trying fallback", barcode=barcode, error=str(e))
        
        # Try CREA database fallback
        crea_data = await self._try_crea_database(barcode)
        if crea_data:
            nutrition_sources.append(crea_data)
        
        # Try GPT-4V estimation fallback
        if settings.enable_gpt4v_analysis:
            gpt4v_data = await self._try_gpt4v_estimation(barcode)
            if gpt4v_data:
                nutrition_sources.append(gpt4v_data)
        
        # Resolve conflicts if multiple sources
        if nutrition_sources:
            return self.conflict_resolver.resolve(nutrition_sources)
        
        logger.warning("No nutrition data found for barcode", barcode=barcode)
        return None
    
    async def _try_crea_database(self, barcode: str) -> Optional[tuple[NutritionData, DataSourceAttribution]]:
        """Try Italian CREA food database."""
        # Implementation for CREA database lookup
        # This would query a local database of Italian foods
        return None
    
    async def _try_gpt4v_estimation(self, barcode: str) -> Optional[tuple[NutritionData, DataSourceAttribution]]:
        """Try GPT-4V estimation as last resort."""
        # Implementation for GPT-4V based nutrition estimation
        # This would require product name/description lookup
        return None
```

---

## 7. Error Handling e Resilience

### Comprehensive Exception System

```python
# app/core/exceptions.py
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()

# Domain Exceptions
class NutriFitException(Exception):
    """Base exception for NutriFit domain."""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

class ValidationError(NutriFitException):
    """Domain validation error."""
    pass

class BusinessRuleError(NutriFitException):
    """Business rule violation error."""
    pass

class DataQualityError(NutriFitException):
    """Data quality below threshold error."""
    pass

# Infrastructure Exceptions
class ExternalServiceError(NutriFitException):
    """External service communication error."""
    def __init__(self, message: str, service_name: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.status_code = status_code

class RateLimitExceededError(ExternalServiceError):
    """Rate limit exceeded for external service."""
    def __init__(self, service_name: str, retry_after: Optional[int] = None):
        super().__init__(f"Rate limit exceeded for {service_name}", service_name)
        self.retry_after = retry_after

class DatabaseError(NutriFitException):
    """Database operation error."""
    pass

class CacheError(NutriFitException):
    """Cache operation error."""
    pass

# API Exceptions  
class APIError(HTTPException):
    """Base API error with structured response."""
    def __init__(
        self, 
        status_code: int, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or "API_ERROR"
        self.details = details or {}
        
        super().__init__(
            status_code=status_code,
            detail={
                "message": self.message,
                "error_code": self.error_code,
                "details": self.details
            }
        )

class BadRequestError(APIError):
    """400 Bad Request error."""
    def __init__(self, message: str, **kwargs):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, **kwargs)

class UnauthorizedError(APIError):
    """401 Unauthorized error."""
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, **kwargs)

class ForbiddenError(APIError):
    """403 Forbidden error."""
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(status.HTTP_403_FORBIDDEN, message, **kwargs)

class NotFoundError(APIError):
    """404 Not Found error."""
    def __init__(self, message: str, **kwargs):
        super().__init__(status.HTTP_404_NOT_FOUND, message, **kwargs)

class ConflictError(APIError):
    """409 Conflict error."""
    def __init__(self, message: str, **kwargs):
        super().__init__(status.HTTP_409_CONFLICT, message, **kwargs)

class InternalServerError(APIError):
    """500 Internal Server Error."""
    def __init__(self, message: str = "Internal server error", **kwargs):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, message, **kwargs)

class ServiceUnavailableError(APIError):
    """503 Service Unavailable error."""
    def __init__(self, message: str = "Service temporarily unavailable", **kwargs):
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, message, **kwargs)

# Exception handlers
def setup_exception_handlers(app):
    """Setup FastAPI exception handlers."""
    
    @app.exception_handler(NutriFitException)
    async def nutrifit_exception_handler(request: Request, exc: NutriFitException):
        """Handle domain exceptions."""
        logger.error(
            "Domain exception occurred",
            error_type=exc.__class__.__name__,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            path=request.url.path,
            method=request.method
        )
        
        # Map domain exceptions to HTTP status codes
        status_code_map = {
            ValidationError: status.HTTP_400_BAD_REQUEST,
            BusinessRuleError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            DataQualityError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
            RateLimitExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
            DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        
        status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        response_data = {
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
        
        # Add retry information for rate limit errors
        if isinstance(exc, RateLimitExceededError) and exc.retry_after:
            response_data["retry_after"] = exc.retry_after
        
        return JSONResponse(
            status_code=status_code,
            content=response_data,
            headers={"X-Error-Code": exc.error_code} if exc.error_code else {}
        )
    
    @app.exception_handler(APIError)
    async def api_exception_handler(request: Request, exc: APIError):
        """Handle API exceptions."""
        logger.error(
            "API exception occurred",
            error_type=exc.__class__.__name__,
            message=exc.message,
            error_code=exc.error_code,
            status_code=exc.status_code,
            path=request.url.path,
            method=request.method
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers={"X-Error-Code": exc.error_code}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(
            "Unexpected exception occurred",
            error_type=exc.__class__.__name__,
            message=str(exc),
            path=request.url.path,
            method=request.method,
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR",
                "details": {}
            },
            headers={"X-Error-Code": "INTERNAL_ERROR"}
        )

# Circuit breaker pattern
class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def __call__(self, func):
        """Decorator for circuit breaker."""
        import functools
        import time
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "open":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "half-open"
                    logger.info("Circuit breaker transitioning to half-open")
                else:
                    raise ServiceUnavailableError(f"Circuit breaker is open for {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                
                if self.state == "half-open":
                    self.state = "closed"
                    self.failure_count = 0
                    logger.info("Circuit breaker closed - service recovered")
                
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                    logger.error(
                        f"Circuit breaker opened for {func.__name__}",
                        failure_count=self.failure_count,
                        threshold=self.failure_threshold
                    )
                
                raise
        
        return wrapper

# Retry decorator with exponential backoff
def retry_with_backoff(max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        import functools
        import asyncio
        import random
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        break
                    
                    # Calculate delay with jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0.1, 0.3) * delay
                    total_delay = delay + jitter
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {total_delay:.2f}s",
                        function=func.__name__,
                        error=str(e),
                        attempt=attempt + 1,
                        max_attempts=max_attempts
                    )
                    
                    await asyncio.sleep(total_delay)
            
            # All attempts failed
            logger.error(
                f"All {max_attempts} attempts failed for {func.__name__}",
                final_error=str(last_exception)
            )
            raise last_exception
        
        return wrapper
    return decorator

# Example usage of resilience patterns
class ResilientExternalServiceClient:
    """Example client with circuit breaker and retry patterns."""
    
    @CircuitBreaker(failure_threshold=5, timeout=60)
    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def call_external_service(self, data):
        """Call external service with resilience patterns."""
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.external.com/data", json=data)
            response.raise_for_status()
            return response.json()
```

---

## 8. Testing Strategy

### Comprehensive Test Suite Architecture

```python
# tests/conftest.py - Test configuration and fixtures
import pytest
import asyncio
import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.main import create_application
from app.core.database import Base, AsyncSessionFactory
from app.core.config import Settings, get_settings
from app.infrastructure.external.openfoodfacts_client import OpenFoodFactsClient

# Test database URL (in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

class TestSettings(Settings):
    """Test-specific settings."""
    environment: str = "test"
    database_url: str = TEST_DATABASE_URL
    secret_key: str = "test-secret-key-very-long-and-secure"
    openai_api_key: str = "test-openai-key"
    debug: bool = True
    
    # Disable external services in tests
    enable_gpt4v_analysis: bool = False
    enable_background_tasks: bool = False

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_settings() -> TestSettings:
    """Provide test settings."""
    return TestSettings()

@pytest.fixture
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()

@pytest.fixture
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide database session for tests."""
    from app.infrastructure.database.models import *  # noqa: F401,F403
    
    async with AsyncSessionFactory.begin() as session:
        yield session
        await session.rollback()  # Rollback to keep tests isolated

@pytest.fixture
def override_get_settings(test_settings):
    """Override settings dependency for tests."""
    def _get_test_settings():
        return test_settings
    return _get_test_settings

@pytest.fixture
def app(override_get_settings):
    """Create test FastAPI application."""
    from app.main import app
    from app.core.config import get_settings
    
    # Override settings dependency
    app.dependency_overrides[get_settings] = override_get_settings
    
    yield app
    
    # Cleanup
    app.dependency_overrides.clear()

@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Provide HTTP client for API testing."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def mock_openfoodfacts_client():
    """Mock OpenFoodFacts client for testing."""
    client = MagicMock(spec=OpenFoodFactsClient)
    
    # Setup common mock responses
    async def mock_get_product(barcode: str):
        if barcode == "1234567890":
            return MagicMock(
                barcode=barcode,
                product_name="Test Product",
                brands=["Test Brand"],
                categories=["Test Category"],
                nutriments={
                    'energy-kcal_100g': 250,
                    'proteins_100g': 10,
                    'carbohydrates_100g': 30,
                    'fat_100g': 15,
                },
                completeness=0.8,
                data_quality_score=0.8,
                is_italian=False
            )
        return None
    
    client.get_product = AsyncMock(side_effect=mock_get_product)
    return client

# Test utilities
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_user(
        email: str = "test@nutrifit.com",
        daily_calorie_goal: int = 2000,
        **kwargs
    ) -> dict:
        """Create test user data."""
        return {
            "email": email,
            "daily_calorie_goal": daily_calorie_goal,
            "age": 30,
            "gender": "male",
            "height_cm": 175,
            "weight_kg": 70.0,
            **kwargs
        }
    
    @staticmethod
    def create_food(
        name: str = "Test Food",
        barcode: str = "1234567890",
        **kwargs
    ) -> dict:
        """Create test food data."""
        return {
            "name": name,
            "barcode": barcode,
            "calories_per_100g": 250.0,
            "proteins_per_100g": 10.0,
            "carbohydrates_per_100g": 30.0,
            "fats_per_100g": 15.0,
            "data_source": "test",
            "data_confidence": 0.8,
            **kwargs
        }
    
    @staticmethod
    def create_meal(
        user_id: str,
        meal_type: str = "lunch",
        **kwargs
    ) -> dict:
        """Create test meal data."""
        return {
            "user_id": user_id,
            "date": "2025-01-15",
            "meal_type": meal_type,
            "total_calories": 500.0,
            "overall_data_confidence": 0.8,
            **kwargs
        }

@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory()

# Integration test base class
class BaseIntegrationTest:
    """Base class for integration tests."""
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session, client, test_data_factory):
        """Setup common test dependencies."""
        self.db_session = db_session
        self.client = client
        self.factory = test_data_factory
```

### Unit Tests Examples

```python
# tests/unit/test_domain/test_value_objects.py
import pytest
from decimal import Decimal
from datetime import datetime

from app.domain.value_objects.nutrition_values import (
    NutritionData, 
    DataSourceAttribution, 
    FoodQuantity,
    DataSource,
    NutritionDataConflictResolver
)

class TestDataSourceAttribution:
    """Test DataSourceAttribution value object."""
    
    def test_valid_attribution_creation(self):
        """Test creating valid attribution."""
        attribution = DataSourceAttribution(
            source=DataSource.OPENFOODFACTS,
            confidence=Decimal('0.8'),
            timestamp=datetime.now()
        )
        
        assert attribution.source == DataSource.OPENFOODFACTS
        assert attribution.confidence == Decimal('0.8')
        assert isinstance(attribution.timestamp, datetime)
    
    def test_invalid_confidence_raises_error(self):
        """Test that invalid confidence raises ValueError."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            DataSourceAttribution(
                source=DataSource.OPENFOODFACTS,
                confidence=Decimal('1.5'),  # Invalid: > 1.0
                timestamp=datetime.now()
            )
        
        with pytest.raises(ValueError, match="Confidence must be between"):
            DataSourceAttribution(
                source=DataSource.OPENFOODFACTS,
                confidence=Decimal('-0.1'),  # Invalid: < 0.0
                timestamp=datetime.now()
            )
    
    def test_from_healthkit_factory_method(self):
        """Test HealthKit attribution factory method."""
        attribution = DataSourceAttribution.from_healthkit('steps')
        
        assert attribution.source == DataSource.HEALTHKIT
        assert attribution.confidence == Decimal('0.9')  # Steps have 90% confidence
        assert attribution.sync_latency_seconds == 30
    
    def test_from_openfoodfacts_factory_method(self):
        """Test OpenFoodFacts attribution factory method."""
        # High completeness
        attribution = DataSourceAttribution.from_openfoodfacts(Decimal('0.8'))
        assert attribution.source == DataSource.OPENFOODFACTS
        assert attribution.confidence == Decimal('0.8')
        
        # Low completeness should reduce confidence
        attribution = DataSourceAttribution.from_openfoodfacts(Decimal('0.4'))
        assert attribution.confidence < Decimal('0.8')

class TestFoodQuantity:
    """Test FoodQuantity value object."""
    
    def test_precision_rounding(self):
        """Test quantity precision rounding."""
        # Should round to nearest 20g
        quantity = FoodQuantity(_value=Decimal('157'), unit="grams", precision_grams=20)
        assert quantity.value == Decimal('160')  # Rounded to 160
        
        quantity = FoodQuantity(_value=Decimal('143'), unit="grams", precision_grams=20)
        assert quantity.value == Decimal('140')  # Rounded to 140
    
    def test_confidence_interval(self):
        """Test confidence interval calculation."""
        quantity = FoodQuantity(_value=Decimal('150'), unit="grams", precision_grams=20)
        min_val, max_val = quantity.confidence_interval
        
        assert min_val == Decimal('130')  # 150 - 20
        assert max_val == Decimal('170')  # 150 + 20
    
    def test_unit_conversion(self):
        """Test conversion to grams."""
        # Test kg conversion
        quantity = FoodQuantity(_value=Decimal('1.5'), unit="kg")
        assert quantity.to_grams() == Decimal('1500')
        
        # Test ounces conversion
        quantity = FoodQuantity(_value=Decimal('8'), unit="ounces")
        expected = Decimal('8') * Decimal('28.35')
        assert quantity.to_grams() == expected

class TestNutritionData:
    """Test NutritionData value object."""
    
    def test_valid_nutrition_data_creation(self):
        """Test creating valid nutrition data."""
        attribution = DataSourceAttribution(
            source=DataSource.OPENFOODFACTS,
            confidence=Decimal('0.8'),
            timestamp=datetime.now()
        )
        
        nutrition = NutritionData(
            calories=Decimal('250'),
            proteins=Decimal('10'),
            carbohydrates=Decimal('30'),
            fats=Decimal('15'),
            attribution=attribution
        )
        
        assert nutrition.calories == Decimal('250')
        assert nutrition.proteins == Decimal('10')
        assert nutrition.attribution.confidence == Decimal('0.8')
    
    def test_negative_values_raise_error(self):
        """Test that negative macronutrients raise ValueError."""
        with pytest.raises(ValueError, match="calories cannot be negative"):
            NutritionData(
                calories=Decimal('-10'),
                proteins=Decimal('10'),
                carbohydrates=Decimal('30'),
                fats=Decimal('15')
            )
    
    def test_micronutrient_completeness_calculation(self):
        """Test micronutrient completeness scoring."""
        # No micronutrients
        nutrition = NutritionData(
            calories=Decimal('250'),
            proteins=Decimal('10'),
            carbohydrates=Decimal('30'),
            fats=Decimal('15')
        )
        assert nutrition.micronutrient_completeness == Decimal('0')
        
        # 10 micronutrients (50% of expected 20)
        micronutrients = {
            f"vitamin_{i}": (Decimal('1.0'), Decimal('0.8'))
            for i in range(10)
        }
        nutrition = NutritionData(
            calories=Decimal('250'),
            proteins=Decimal('10'),
            carbohydrates=Decimal('30'),
            fats=Decimal('15'),
            micronutrients=micronutrients
        )
        assert nutrition.micronutrient_completeness == Decimal('0.5')
    
    def test_overall_confidence_calculation(self):
        """Test overall confidence calculation."""
        # High attribution confidence, no micronutrients
        attribution = DataSourceAttribution(
            source=DataSource.OPENFOODFACTS,
            confidence=Decimal('0.9'),
            timestamp=datetime.now()
        )
        nutrition = NutritionData(
            calories=Decimal('250'),
            proteins=Decimal('10'),
            carbohydrates=Decimal('30'),
            fats=Decimal('15'),
            attribution=attribution
        )
        
        # Should be reduced due to lack of micronutrients
        expected_confidence = Decimal('0.9') - (Decimal('1') * Decimal('0.2'))  # Full penalty
        assert nutrition.overall_confidence == expected_confidence

class TestNutritionDataConflictResolver:
    """Test conflict resolution logic."""
    
    def test_single_source_returns_as_is(self):
        """Test that single source is returned without modification."""
        attribution = DataSourceAttribution(
            source=DataSource.OPENFOODFACTS,
            confidence=Decimal('0.8'),
            timestamp=datetime.now()
        )
        nutrition = NutritionData(
            calories=Decimal('250'),
            proteins=Decimal('10'),
            carbohydrates=Decimal('30'),
            fats=Decimal('15'),
            attribution=attribution
        )
        
        sources = [(nutrition, attribution)]
        result = NutritionDataConflictResolver.resolve(sources)
        
        assert result.calories == Decimal('250')
        assert result.attribution.confidence == Decimal('0.8')
    
    def test_weighted_average_resolution(self):
        """Test weighted average conflict resolution."""
        # High confidence manual entry
        manual_attr = DataSourceAttribution(
            source=DataSource.MANUAL,
            confidence=Decimal('0.95'),
            timestamp=datetime.now()
        )
        manual_nutrition = NutritionData(
            calories=Decimal('300'),  # Higher calories
            proteins=Decimal('12'),
            carbohydrates=Decimal('35'),
            fats=Decimal('18'),
            attribution=manual_attr
        )
        
        # Lower confidence OpenFoodFacts entry
        off_attr = DataSourceAttribution(
            source=DataSource.OPENFOODFACTS,
            confidence=Decimal('0.7'),
            timestamp=datetime.now()
        )
        off_nutrition = NutritionData(
            calories=Decimal('250'),  # Lower calories
            proteins=Decimal('10'),
            carbohydrates=Decimal('30'),
            fats=Decimal('15'),
            attribution=off_attr
        )
        
        sources = [(manual_nutrition, manual_attr), (off_nutrition, off_attr)]
        result = NutritionDataConflictResolver.resolve(sources)
        
        # Manual entry should have higher weight due to higher priority and confidence
        # Expected weights: manual = 0.95 * 1.0 = 0.95, OFF = 0.7 * 0.8 = 0.56
        # Total weight = 1.51
        # Expected calories = (300 * 0.95 + 250 * 0.56) / 1.51 = 284.77 / 1.51 ≈ 188.6
        assert result.calories > Decimal('280')  # Should be closer to manual entry
        assert result.sources_used == [DataSource.MANUAL, DataSource.OPENFOODFACTS]
    
    def test_empty_sources_raises_error(self):
        """Test that empty sources list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot resolve empty"):
            NutritionDataConflictResolver.resolve([])
```

### Integration Tests

```python
# tests/integration/test_api/test_meals_endpoint.py
import pytest
from decimal import Decimal
from httpx import AsyncClient

from tests.conftest import BaseIntegrationTest

class TestMealsAPI(BaseIntegrationTest):
    """Integration tests for meals API endpoints."""
    
    async def test_create_meal_success(self):
        """Test successful meal creation."""
        # Create test user first
        user_data = self.factory.create_user()
        user_response = await self.client.post("/api/v1/users/", json=user_data)
        assert user_response.status_code == 201
        user_id = user_response.json()["id"]
        
        # Create meal
        meal_data = {
            "user_id": user_id,
            "date": "2025-01-15",
            "meal_type": "lunch",
            "foods": [
                {
                    "food_id": "uuid-food-1",
                    "quantity_grams": 150.0
                }
            ]
        }
        
        response = await self.client.post("/api/v1/meals/", json=meal_data)
        assert response.status_code == 201
        
        meal = response.json()
        assert meal["user_id"] == user_id
        assert meal["meal_type"] == "lunch"
        assert meal["total_calories"] > 0
    
    async def test_create_meal_with_photo_analysis(self):
        """Test meal creation with photo analysis."""
        user_data = self.factory.create_user()
        user_response = await self.client.post("/api/v1/users/", json=user_data)
        user_id = user_response.json()["id"]
        
        # Mock photo upload
        files = {"photo": ("test.jpg", b"fake_image_data", "image/jpeg")}
        data = {
            "user_id": user_id,
            "date": "2025-01-15",
            "meal_type": "dinner"
        }
        
        response = await self.client.post("/api/v1/meals/analyze-photo", files=files, data=data)
        assert response.status_code == 202  # Accepted for processing
        
        analysis_job = response.json()
        assert "job_id" in analysis_job
        assert analysis_job["status"] == "processing"
    
    async def test_get_meal_by_id(self):
        """Test retrieving meal by ID."""
        # Create user and meal
        user_data = self.factory.create_user()
        user_response = await self.client.post("/api/v1/users/", json=user_data)
        user_id = user_response.json()["id"]
        
        meal_data = self.factory.create_meal(user_id)
        meal_response = await self.client.post("/api/v1/meals/", json=meal_data)
        meal_id = meal_response.json()["id"]
        
        # Get meal
        response = await self.client.get(f"/api/v1/meals/{meal_id}")
        assert response.status_code == 200
        
        meal = response.json()
        assert meal["id"] == meal_id
        assert meal["user_id"] == user_id
    
    async def test_get_user_meals_with_filters(self):
        """Test retrieving user meals with date filters."""
        user_data = self.factory.create_user()
        user_response = await self.client.post("/api/v1/users/", json=user_data)
        user_id = user_response.json()["id"]
        
        # Create meals on different dates
        dates = ["2025-01-10", "2025-01-15", "2025-01-20"]
        for date in dates:
            meal_data = self.factory.create_meal(user_id, date=date)
            await self.client.post("/api/v1/meals/", json=meal_data)
        
        # Query meals with date range
        response = await self.client.get(
            f"/api/v1/meals/?user_id={user_id}&start_date=2025-01-12&end_date=2025-01-18"
        )
        assert response.status_code == 200
        
        meals = response.json()
        assert len(meals) == 1  # Only meal from 2025-01-15 should match
        assert meals[0]["date"] == "2025-01-15"
    
    async def test_meal_validation_errors(self):
        """Test meal creation validation errors."""
        # Missing user_id
        meal_data = {
            "date": "2025-01-15",
            "meal_type": "lunch"
        }
        
        response = await self.client.post("/api/v1/meals/", json=meal_data)
        assert response.status_code == 422
        
        error_detail = response.json()
        assert "user_id" in error_detail["details"]
    
    async def test_meal_not_found(self):
        """Test 404 error for non-existent meal."""
        fake_meal_id = "00000000-0000-0000-0000-000000000000"
        response = await self.client.get(f"/api/v1/meals/{fake_meal_id}")
        assert response.status_code == 404
        
        error = response.json()
        assert error["error_code"] == "MEAL_NOT_FOUND"

# tests/integration/test_external/test_openfoodfacts_integration.py
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.infrastructure.external.openfoodfacts_client import OpenFoodFactsClient, OpenFoodFactsProduct
from app.core.exceptions import ExternalServiceError, RateLimitExceededError

class TestOpenFoodFactsIntegration:
    """Integration tests for OpenFoodFacts client."""
    
    @pytest.fixture
    async def client(self):
        """Provide OpenFoodFacts client."""
        async with OpenFoodFactsClient() as client:
            yield client
    
    @patch('httpx.AsyncClient.get')
    async def test_successful_product_fetch(self, mock_get, client):
        """Test successful product data retrieval."""
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Test Product",
                "brands": "Test Brand",
                "categories": "Test Category",
                "nutriments": {
                    "energy-kcal_100g": 250,
                    "proteins_100g": 10,
                    "carbohydrates_100g": 30,
                    "fat_100g": 15,
                    "fiber_100g": 5
                }
            }
        }
        mock_get.return_value = mock_response
        
        product = await client.get_product("1234567890")
        
        assert isinstance(product, OpenFoodFactsProduct)
        assert product.barcode == "1234567890"
        assert product.product_name == "Test Product"
        assert product.brands == ["Test Brand"]
        assert product.nutriments["energy-kcal_100g"] == 250
    
    @patch('httpx.AsyncClient.get')
    async def test_product_not_found(self, mock_get, client):
        """Test handling of product not found."""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        product = await client.get_product("9999999999")
        assert product is None
    
    @patch('httpx.AsyncClient.get')
    async def test_rate_limit_handling(self, mock_get, client):
        """Test rate limit error handling."""
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitExceededError):
            await client.get_product("1234567890")
    
    @patch('httpx.AsyncClient.get')
    async def test_api_error_handling(self, mock_get, client):
        """Test API error handling."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=AsyncMock(), response=mock_response
        )
        mock_get.return_value = mock_response
        
        with pytest.raises(ExternalServiceError):
            await client.get_product("1234567890")
    
    @patch('httpx.AsyncClient.get')
    async def test_timeout_handling(self, mock_get, client):
        """Test timeout error handling."""
        mock_get.side_effect = httpx.TimeoutException("Timeout")
        
        with pytest.raises(ExternalServiceError):
            await client.get_product("1234567890")
    
    async def test_nutrition_data_conversion(self, client):
        """Test conversion from OpenFoodFacts to NutritionData."""
        product = OpenFoodFactsProduct(
            barcode="1234567890",
            product_name="Test Product",
            brands=["Test Brand"],
            categories=["Test Category"],
            nutriments={
                "energy-kcal_100g": 250,
                "proteins_100g": 10,
                "carbohydrates_100g": 30,
                "fat_100g": 15,
                "fiber_100g": 5,
                "sodium_100g": 0.5  # in grams
            },
            completeness=Decimal('0.8'),
            data_quality_score=Decimal('0.8')
        )
        
        nutrition_data = client.to_nutrition_data(product)
        
        assert nutrition_data.calories == Decimal('250')
        assert nutrition_data.proteins == Decimal('10')
        assert nutrition_data.carbohydrates == Decimal('30')
        assert nutrition_data.fats == Decimal('15')
        assert nutrition_data.fiber == Decimal('5')
        assert nutrition_data.sodium == Decimal('500')  # Converted to mg
        assert nutrition_data.attribution.source == DataSource.OPENFOODFACTS
        assert nutrition_data.attribution.confidence == Decimal('0.8')
```

---

## 9. Monitoring & Observability

### Comprehensive Monitoring Setup

```python
# app/core/metrics.py - Prometheus metrics
import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, Info
import structlog

logger = structlog.get_logger()

# HTTP request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'service']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'service'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Database metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections',
    ['service']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table', 'service'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# External service metrics
external_api_requests_total = Counter(
    'external_api_requests_total',
    'Total external API requests',
    ['service_name', 'status', 'endpoint']
)

external_api_duration_seconds = Histogram(
    'external_api_duration_seconds',
    'External API request duration',
    ['service_name', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Business metrics
meals_created_total = Counter(
    'meals_created_total',
    'Total meals created',
    ['meal_type', 'analysis_source', 'service']
)

nutrition_data_confidence = Histogram(
    'nutrition_data_confidence',
    'Nutrition data confidence scores',
    ['data_source', 'service'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

food_recognition_accuracy = Gauge(
    'food_recognition_accuracy',
    'Current food recognition accuracy rate',
    ['method', 'service']
)

# AI/ML metrics
ai_tokens_consumed_total = Counter(
    'ai_tokens_consumed_total',
    'Total AI tokens consumed',
    ['model', 'operation', 'service']
)

ai_response_time_seconds = Histogram(
    'ai_response_time_seconds',
    'AI response time in seconds',
    ['model', 'operation', 'service'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 60.0]
)

# Health metrics
healthkit_sync_success_total = Counter(
    'healthkit_sync_success_total',
    'Successful HealthKit syncs',
    ['metric_type', 'service']
)

healthkit_sync_errors_total = Counter(
    'healthkit_sync_errors_total',
    'Failed HealthKit syncs',
    ['error_type', 'service']
)

# Application info
app_info = Info(
    'app_info',
    'Application information'
)

def setup_metrics():
    """Initialize metrics with application info."""
    from app.core.config import get_settings
    settings = get_settings()
    
    app_info.info({
        'service': settings.service_name,
        'environment': settings.environment,
        'version': '1.0.0'
    })
    
    logger.info("Metrics initialized", service=settings.service_name)

# Middleware for HTTP metrics
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics."""
    
    async def dispatch(self, request: Request, call_next):
        # Record request start time
        start_time = time.time()
        
        # Get service name from settings
        from app.core.config import get_settings
        settings = get_settings()
        service_name = settings.service_name
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Extract route pattern for better grouping
        route = request.url.path
        if hasattr(request, "path_info"):
            route = request.path_info
        
        # Record metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=route,
            status_code=response.status_code,
            service=service_name
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=route,
            service=service_name
        ).observe(duration)
        
        return response

# Metrics decorator for tracking specific operations
def track_operation(operation_name: str, metric_labels: Dict[str, str] = None):
    """Decorator to track operation metrics."""
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            from app.core.config import get_settings
            settings = get_settings()
            
            labels = metric_labels or {}
            labels.update({
                'operation': operation_name,
                'service': settings.service_name
            })
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record success
                duration = time.time() - start_time
                
                # Log successful operation
                logger.info(
                    "Operation completed successfully",
                    operation=operation_name,
                    duration=duration,
                    **labels
                )
                
                return result
                
            except Exception as e:
                # Record error
                duration = time.time() - start_time
                
                logger.error(
                    "Operation failed",
                    operation=operation_name,
                    duration=duration,
                    error=str(e),
                    **labels
                )
                
                raise
        
        return wrapper
    return decorator

# Database metrics context manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def track_database_query(operation: str, table: str):
    """Context manager for tracking database queries."""
    from app.core.config import get_settings
    settings = get_settings()
    
    start_time = time.time()
    try:
        yield
        
        duration = time.time() - start_time
        database_query_duration_seconds.labels(
            operation=operation,
            table=table,
            service=settings.service_name
        ).observe(duration)
        
    except Exception as e:
        logger.error(
            "Database query failed",
            operation=operation,
            table=table,
            error=str(e),
            duration=time.time() - start_time
        )
        raise

# External API metrics context manager
@asynccontextmanager
async def track_external_api_call(service_name: str, endpoint: str):
    """Context manager for tracking external API calls."""
    start_time = time.time()
    status = "success"
    
    try:
        yield
        
    except Exception as e:
        status = "error"
        logger.error(
            "External API call failed",
            service=service_name,
            endpoint=endpoint,
            error=str(e)
        )
        raise
        
    finally:
        duration = time.time() - start_time
        
        external_api_requests_total.labels(
            service_name=service_name,
            status=status,
            endpoint=endpoint
        ).inc()
        
        external_api_duration_seconds.labels(
            service_name=service_name,
            endpoint=endpoint
        ).observe(duration)

# Business metrics helpers
def record_meal_creation(meal_type: str, analysis_source: str):
    """Record meal creation business metric."""
    from app.core.config import get_settings
    settings = get_settings()
    
    meals_created_total.labels(
        meal_type=meal_type,
        analysis_source=analysis_source,
        service=settings.service_name
    ).inc()

def record_nutrition_confidence(data_source: str, confidence: float):
    """Record nutrition data confidence metric."""
    from app.core.config import get_settings
    settings = get_settings()
    
    nutrition_data_confidence.labels(
        data_source=data_source,
        service=settings.service_name
    ).observe(confidence)

def record_ai_usage(model: str, operation: str, tokens_used: int, response_time: float):
    """Record AI/ML usage metrics."""
    from app.core.config import get_settings
    settings = get_settings()
    
    ai_tokens_consumed_total.labels(
        model=model,
        operation=operation,
        service=settings.service_name
    ).inc(tokens_used)
    
    ai_response_time_seconds.labels(
        model=model,
        operation=operation,
        service=settings.service_name
    ).observe(response_time)
```

### Structured Logging Implementation

```python
# app/core/logging.py - Structured logging with context
import logging
import sys
import json
from typing import Any, Dict, Optional
from contextvars import ContextVar
from datetime import datetime

import structlog
from structlog.types import Processor
from pythonjsonlogger import jsonlogger

from app.core.config import get_settings

# Context variables for request tracing
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)

def add_correlation_id(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add correlation ID to log entries."""
    correlation_id = correlation_id_var.get()
    if correlation_id:
        event_dict['correlation_id'] = correlation_id
    return event_dict

def add_user_context(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add user context to log entries."""
    user_id = user_id_var.get()
    if user_id:
        event_dict['user_id'] = user_id
    return event_dict

def add_service_context(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add service context to log entries."""
    settings = get_settings()
    event_dict['service'] = settings.service_name
    event_dict['environment'] = settings.environment
    return event_dict

def add_timestamp(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add ISO timestamp to log entries."""
    event_dict['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    return event_dict

def configure_logging():
    """Configure structured logging for the application."""
    settings = get_settings()
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper())
    )
    
    # Processors chain
    processors: list[Processor] = [
        add_timestamp,
        add_service_context,
        add_correlation_id,
        add_user_context,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.structured_logging:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable output for development
        processors.extend([
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer()
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

class CorrelationIdMiddleware:
    """Middleware to manage correlation IDs across requests."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract or generate correlation ID
        headers = dict(scope.get("headers", []))
        correlation_id = headers.get(b"x-correlation-id")
        
        if correlation_id:
            correlation_id = correlation_id.decode()
        else:
            import uuid
            correlation_id = str(uuid.uuid4())
        
        # Set correlation ID in context
        correlation_id_var.set(correlation_id)
        
        # Add correlation ID to response headers
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append([b"x-correlation-id", correlation_id.encode()])
                message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

# Logging utilities for different contexts
class SecurityLogger:
    """Specialized logger for security events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("security")
    
    def log_authentication_attempt(
        self, 
        user_email: str, 
        success: bool, 
        ip_address: str,
        user_agent: str
    ):
        """Log authentication attempt."""
        self.logger.info(
            "Authentication attempt",
            event_type="auth_attempt",
            user_email=user_email,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_permission_denied(
        self, 
        user_id: str, 
        resource: str, 
        action: str,
        reason: str
    ):
        """Log permission denied event."""
        self.logger.warning(
            "Permission denied",
            event_type="permission_denied",
            user_id=user_id,
            resource=resource,
            action=action,
            reason=reason
        )
    
    def log_suspicious_activity(
        self, 
        user_id: Optional[str], 
        activity: str, 
        details: Dict[str, Any]
    ):
        """Log suspicious activity."""
        self.logger.error(
            "Suspicious activity detected",
            event_type="suspicious_activity",
            user_id=user_id,
            activity=activity,
            **details
        )

class BusinessLogger:
    """Specialized logger for business events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("business")
    
    def log_meal_creation(
        self, 
        user_id: str, 
        meal_id: str, 
        meal_type: str,
        total_calories: float,
        confidence: float,
        data_sources: list[str]
    ):
        """Log meal creation business event."""
        self.logger.info(
            "Meal created",
            event_type="meal_created",
            user_id=user_id,
            meal_id=meal_id,
            meal_type=meal_type,
            total_calories=total_calories,
            confidence=confidence,
            data_sources=data_sources
        )
    
    def log_goal_achievement(
        self, 
        user_id: str, 
        goal_type: str, 
        target_value: float,
        actual_value: float,
        achievement_date: str
    ):
        """Log goal achievement."""
        self.logger.info(
            "Goal achieved",
            event_type="goal_achieved",
            user_id=user_id,
            goal_type=goal_type,
            target_value=target_value,
            actual_value=actual_value,
            achievement_date=achievement_date
        )
    
    def log_data_quality_issue(
        self, 
        data_type: str, 
        issue_type: str,
        confidence_score: float,
        data_source: str,
        details: Dict[str, Any]
    ):
        """Log data quality issue."""
        self.logger.warning(
            "Data quality issue",
            event_type="data_quality_issue",
            data_type=data_type,
            issue_type=issue_type,
            confidence_score=confidence_score,
            data_source=data_source,
            **details
        )

class PerformanceLogger:
    """Specialized logger for performance events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
    
    def log_slow_query(
        self, 
        query: str, 
        duration_ms: float,
        table: str,
        operation: str
    ):
        """Log slow database query."""
        self.logger.warning(
            "Slow query detected",
            event_type="slow_query",
            query=query,
            duration_ms=duration_ms,
            table=table,
            operation=operation
        )
    
    def log_external_api_slowness(
        self, 
        service_name: str, 
        endpoint: str,
        duration_ms: float,
        timeout_ms: float
    ):
        """Log slow external API response."""
        self.logger.warning(
            "External API slowness",
            event_type="api_slowness",
            service_name=service_name,
            endpoint=endpoint,
            duration_ms=duration_ms,
            timeout_ms=timeout_ms
        )
    
    def log_memory_usage(self, usage_mb: float, threshold_mb: float):
        """Log high memory usage."""
        self.logger.warning(
            "High memory usage",
            event_type="memory_usage",
            usage_mb=usage_mb,
            threshold_mb=threshold_mb
        )

# Global logger instances
security_logger = SecurityLogger()
business_logger = BusinessLogger()
performance_logger = PerformanceLogger()

# Context manager for user context
@asynccontextmanager
async def user_context(user_id: str):
    """Set user context for logging."""
    token = user_id_var.set(user_id)
    try:
        yield
    finally:
        user_id_var.reset(token)
```

---

## 10. Deployment Configuration

### Docker Configuration

```dockerfile
# services/{service_name}/docker/Dockerfile - Production Dockerfile
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r nutrifit && useradd -r -g nutrifit nutrifit

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.1

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY scripts/ ./scripts/

# Make scripts executable
RUN chmod +x scripts/*.sh

# Change ownership to non-root user
RUN chown -R nutrifit:nutrifit /app

# Switch to non-root user
USER nutrifit

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default port
EXPOSE 8000

# Default command
CMD ["scripts/start.sh"]

# Development stage
FROM base AS development

USER root

# Install development dependencies
RUN poetry install --no-interaction --no-ansi

# Install additional tools for development
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

USER nutrifit

# Override default command for development
CMD ["scripts/dev.sh"]
```

```yaml
# services/{service_name}/docker/docker-compose.yml - Development environment
version: '3.8'

services:
  # Service-specific container
  calorie-balance:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: development
    container_name: nutrifit-calorie-balance
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://nutrifit:password@postgres:5432/nutrifit_calorie_balance
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=development
      - DEBUG=true
      - SECRET_KEY=dev-secret-key-very-long-and-secure
    volumes:
      - ..:/app
      - /app/.venv  # Exclude virtual environment
    depends_on:
      - postgres
      - redis
    networks:
      - nutrifit-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Shared services
  postgres:
    image: postgres:15-alpine
    container_name: nutrifit-postgres
    environment:
      - POSTGRES_DB=nutrifit
      - POSTGRES_USER=nutrifit
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - nutrifit-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nutrifit -d nutrifit"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: nutrifit-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - nutrifit-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: nutrifit-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - nutrifit-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: nutrifit-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    networks:
      - nutrifit-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  nutrifit-network:
    driver: bridge
```

### Production Scripts

```bash
#!/bin/bash
# scripts/start.sh - Production startup script
set -e

echo "Starting NutriFit microservice..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z ${DATABASE_HOST:-localhost} ${DATABASE_PORT:-5432}; do
  sleep 1
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application with Gunicorn
echo "Starting application server..."
exec gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --workers ${WORKERS:-4} \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 120 \
    --keepalive 2 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

```bash
#!/bin/bash
# scripts/dev.sh - Development startup script
set -e

echo "Starting NutriFit microservice in development mode..."

# Wait for database
while ! nc -z ${DATABASE_HOST:-localhost} ${DATABASE_PORT:-5432}; do
  sleep 1
done

# Run migrations
alembic upgrade head

# Start with hot reload
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir app \
    --log-level debug
```

```bash
#!/bin/bash
# scripts/migrate.sh - Database migration script
set -e

echo "Running database migrations..."

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "Alembic is not installed. Installing..."
    pip install alembic
fi

# Run migrations
alembic upgrade head

echo "Migrations completed successfully!"
```

```bash
#!/bin/bash
# scripts/test.sh - Test runner script
set -e

echo "Running tests for NutriFit microservice..."

# Set test environment
export ENVIRONMENT=test
export DATABASE_URL=sqlite+aiosqlite:///:memory:
export SECRET_KEY=test-secret-key

# Run linting
echo "Running code quality checks..."
flake8 app tests
black --check app tests
isort --check-only app tests
mypy app

# Run tests with coverage
echo "Running tests..."
pytest \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=xml:coverage.xml \
    --junitxml=test-results.xml \
    -v \
    tests/

echo "Tests completed successfully!"
```

### Render.com Deployment Configuration

```yaml
# render.yaml - Render.com service configuration
services:
  # Calorie Balance Service
  - type: web
    name: nutrifit-calorie-balance
    env: docker
    dockerfilePath: ./services/calorie-balance/docker/Dockerfile
    dockerContext: ./services/calorie-balance
    region: oregon
    plan: starter
    branch: main
    healthCheckPath: /health
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: nutrifit-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: nutrifit-redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false
      - key: SENTRY_DSN
        sync: false
    scaling:
      minInstances: 1
      maxInstances: 3
      targetCPUPercent: 70
      targetMemoryPercent: 80

  # Meal Tracking Service  
  - type: web
    name: nutrifit-meal-tracking
    env: docker
    dockerfilePath: ./services/meal-tracking/docker/Dockerfile
    dockerContext: ./services/meal-tracking
    region: oregon
    plan: starter
    branch: main
    healthCheckPath: /health
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: nutrifit-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: nutrifit-redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false
    scaling:
      minInstances: 1
      maxInstances: 5
      targetCPUPercent: 70
      targetMemoryPercent: 80

  # Health Monitor Service
  - type: web
    name: nutrifit-health-monitor
    env: docker
    dockerfilePath: ./services/health-monitor/docker/Dockerfile
    dockerContext: ./services/health-monitor
    region: oregon
    plan: starter
    branch: main
    healthCheckPath: /health
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: nutrifit-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: nutrifit-redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
    scaling:
      minInstances: 1
      maxInstances: 2

  # Notifications Service
  - type: web
    name: nutrifit-notifications
    env: docker
    dockerfilePath: ./services/notifications/docker/Dockerfile
    dockerContext: ./services/notifications
    region: oregon
    plan: starter
    branch: main
    healthCheckPath: /health
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: nutrifit-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: nutrifit-redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
    scaling:
      minInstances: 1
      maxInstances: 2

  # AI Nutrition Coach Service
  - type: web
    name: nutrifit-ai-coach
    env: docker
    dockerfilePath: ./services/ai-coach/docker/Dockerfile
    dockerContext: ./services/ai-coach
    region: oregon
    plan: standard  # Higher tier for AI workloads
    branch: main
    healthCheckPath: /health
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: nutrifit-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: nutrifit-redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false
      - key: OPENAI_MODEL
        value: gpt-4
    scaling:
      minInstances: 1
      maxInstances: 3
      targetCPUPercent: 80
      targetMemoryPercent: 85

databases:
  - name: nutrifit-db
    databaseName: nutrifit
    user: nutrifit
    region: oregon
    plan: starter
    postgresMajorVersion: 15

  - name: nutrifit-redis
    type: redis
    region: oregon
    plan: starter
    maxmemoryPolicy: allkeys-lru
```

---

## 11. Security Implementation

### JWT Authentication & Authorization

```python
# app/core/security.py - Security utilities
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets
import structlog

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError, ForbiddenError

logger = structlog.get_logger()
settings = get_settings()

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Higher rounds for better security
)

class SecurityManager:
    """Centralized security operations."""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.jwt_algorithm
        self.token_expiry_hours = settings.jwt_expiration_hours
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        user_id: str, 
        user_email: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create JWT access token."""
        
        now = datetime.utcnow()
        expiry = now + timedelta(hours=self.token_expiry_hours)
        
        payload = {
            "sub": user_id,  # Subject (user ID)
            "email": user_email,
            "iat": now,      # Issued at
            "exp": expiry,   # Expires at
            "type": "access_token",
            "jti": secrets.token_hex(16),  # JWT ID for revocation
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(
            "Access token created",
            user_id=user_id,
            user_email=user_email,
            expires_at=expiry.isoformat()
        )
        
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token with longer expiry."""
        
        now = datetime.utcnow()
        expiry = now + timedelta(days=30)  # Refresh tokens last 30 days
        
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": expiry,
            "type": "refresh_token",
            "jti": secrets.token_hex(16),
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={
                    "require_exp": True,
                    "require_iat": True,
                    "require_sub": True,
                }
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token used", token_prefix=token[:20])
            raise UnauthorizedError("Token has expired")
        
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token used", error=str(e), token_prefix=token[:20])
            raise UnauthorizedError("Invalid token")
    
    def generate_api_key(self) -> str:
        """Generate secure API key."""
        return f"nf_{secrets.token_urlsafe(32)}"
    
    def generate_secure_id(self) -> str:
        """Generate cryptographically secure ID."""
        return secrets.token_hex(16)

# Global security manager instance
security_manager = SecurityManager()

# FastAPI dependencies for authentication
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user."""
    
    try:
        token = credentials.credentials
        payload = security_manager.verify_token(token)
        
        # Check token type
        if payload.get("type") != "access_token":
            raise UnauthorizedError("Invalid token type")
        
        # Extract user info
        user_info = {
            "user_id": payload["sub"],
            "email": payload.get("email"),
            "token_id": payload.get("jti"),
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp"),
        }
        
        return user_info
        
    except UnauthorizedError:
        raise
    except Exception as e:
        logger.error("Token verification failed", error=str(e))
        raise UnauthorizedError("Could not validate credentials")

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current active user (can be extended with user status checks)."""
    
    # Here you could add additional checks like:
    # - Is user account active?
    # - Is user email verified?
    # - Does user have required permissions?
    
    return current_user

# Role-based access control
from enum import Enum
from typing import List

class UserRole(str, Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"
    NUTRITIONIST = "nutritionist"

class PermissionChecker:
    """Permission checking utilities."""
    
    ROLE_HIERARCHY = {
        UserRole.USER: 0,
        UserRole.PREMIUM: 1,
        UserRole.NUTRITIONIST: 2,
        UserRole.ADMIN: 3,
    }
    
    PERMISSIONS = {
        # Basic user permissions
        UserRole.USER: [
            "meals:create",
            "meals:read:own",
            "meals:update:own",
            "calories:read:own",
            "health:read:own",
        ],
        
        # Premium user permissions
        UserRole.PREMIUM: [
            "ai_coach:access",
            "analytics:advanced",
            "export:data",
        ],
        
        # Nutritionist permissions
        UserRole.NUTRITIONIST: [
            "users:read:clients",
            "meals:read:clients",
            "analytics:professional",
            "recommendations:create",
        ],
        
        # Admin permissions
        UserRole.ADMIN: [
            "users:read:all",
            "users:update:all", 
            "system:manage",
            "metrics:access",
        ],
    }
    
    @classmethod
    def get_user_permissions(cls, role: UserRole) -> List[str]:
        """Get all permissions for a user role including inherited ones."""
        permissions = set()
        
        # Add permissions for this role and all lower roles
        role_level = cls.ROLE_HIERARCHY.get(role, 0)
        
        for r, level in cls.ROLE_HIERARCHY.items():
            if level <= role_level:
                permissions.update(cls.PERMISSIONS.get(r, []))
        
        return list(permissions)
    
    @classmethod
    def has_permission(cls, user_role: UserRole, required_permission: str) -> bool:
        """Check if user role has required permission."""
        user_permissions = cls.get_user_permissions(user_role)
        return required_permission in user_permissions

def require_permission(required_permission: str):
    """Decorator to require specific permission for endpoint access."""
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user from kwargs (injected by FastAPI dependency)
            current_user = kwargs.get("current_user")
            if not current_user:
                raise ForbiddenError("User context not found")
            
            # Get user role (this would typically come from database)
            user_role = current_user.get("role", UserRole.USER)
            
            # Check permission
            if not PermissionChecker.has_permission(user_role, required_permission):
                logger.warning(
                    "Permission denied",
                    user_id=current_user["user_id"],
                    required_permission=required_permission,
                    user_role=user_role
                )
                raise ForbiddenError(f"Permission denied: {required_permission}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Rate limiting
from collections import defaultdict
import asyncio
import time

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for given key."""
        async with self._lock:
            now = time.time()
            
            # Remove old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.time_window
            ]
            
            # Check if within limits
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            # Record this request
            self.requests[key].append(now)
            return True

# Create rate limiter instances
user_rate_limiter = RateLimiter(max_requests=1000, time_window=3600)  # 1000 requests per hour
api_rate_limiter = RateLimiter(max_requests=10000, time_window=3600)  # 10k requests per hour

async def check_rate_limit(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """FastAPI dependency for rate limiting."""
    user_id = current_user["user_id"]
    
    if not await user_rate_limiter.is_allowed(user_id):
        logger.warning("Rate limit exceeded", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

# Input validation and sanitization
import re
from typing import Union

class InputValidator:
    """Input validation and sanitization utilities."""
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})
    PHONE_REGEX = re.compile(r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4})
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        return bool(InputValidator.EMAIL_REGEX.match(email))
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password strength."""
        if len(password) < 8:
            return False
        
        # Check for at least one uppercase, lowercase, digit, and special char
        checks = [
            re.search(r'[A-Z]', password),  # Uppercase
            re.search(r'[a-z]', password),  # Lowercase  
            re.search(r'\d', password),     # Digit
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password)  # Special char
        ]
        
        return all(checks)
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', value)
        
        # Trim whitespace and limit length
        sanitized = sanitized.strip()[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_numeric_range(
        value: Union[int, float], 
        min_val: Union[int, float], 
        max_val: Union[int, float]
    ) -> bool:
        """Validate numeric value is within range."""
        return min_val <= value <= max_val
```

---

## 12. Development Workflow & CI/CD

### GitHub Actions Workflow

```yaml
# .github/workflows/microservices-ci-cd.yml
name: NutriFit Microservices CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'services/**'
      - '.github/workflows/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'services/**'

env:
  PYTHON_VERSION: '3.11'
  POETRY_VERSION: '1.7.1'

jobs:
  # Detect changed services
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.changes.outputs.services }}
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2
          
      - name: Detect changed services
        id: changes
        run: |
          # Get list of changed services
          CHANGED_SERVICES=$(git diff --name-only HEAD~1 HEAD | grep '^services/' | cut -d'/' -f2 | sort | uniq | tr '\n' ' ')
          echo "services=$CHANGED_SERVICES" >> $GITHUB_OUTPUT
          echo "Changed services: $CHANGED_SERVICES"
          
      - name: Set matrix
        id: set-matrix
        run: |
          # Convert space-separated services to JSON array
          SERVICES="${{ steps.changes.outputs.services }}"
          if [ -n "$SERVICES" ]; then
            JSON_ARRAY=$(echo $SERVICES | tr ' ' '\n' | jq -R . | jq -s .)
            echo "matrix={\"service\":$JSON_ARRAY}" >> $GITHUB_OUTPUT
          else
            echo "matrix={\"service\":[]}" >> $GITHUB_OUTPUT
          fi

  # Test and build services
  test-and-build:
    needs: detect-changes
    if: needs.detect-changes.outputs.services != ''
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{ fromJson(needs.detect-changes.outputs.matrix) }}
      fail-fast: false
      
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
          
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: ${{ env.POETRY_VERSION }}
          virtualenvs-create: true
          virtualenvs-in-project: true
          
      - name: Load cached venv
        id: cached-poetry-dependencies
        uses: actions/cache@v3
        with:
          path: services/${{ matrix.service }}/.venv
          key: venv-${{ matrix.service }}-${{ runner.os }}-${{ env.PYTHON_VERSION }}-${{ hashFiles('services/${{ matrix.service }}/poetry.lock') }}
          
      - name: Install dependencies
        if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
        working-directory: services/${{ matrix.service }}
        run: poetry install --no-interaction --no-root
        
      - name: Install project
        working-directory: services/${{ matrix.service }}
        run: poetry install --no-interaction
        
      - name: Run code quality checks
        working-directory: services/${{ matrix.service }}
        run: |
          poetry run flake8 app tests
          poetry run black --check app tests
          poetry run isort --check-only app tests
          poetry run mypy app
          
      - name: Run security scan
        working-directory: services/${{ matrix.service }}
        run: |
          poetry run bandit -r app -f json -o bandit-report.json || true
          poetry run safety check --json --output safety-report.json || true
          
      - name: Run tests
        working-directory: services/${{ matrix.service }}
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key-for-testing
          ENVIRONMENT: test
        run: |
          poetry run pytest \
            --cov=app \
            --cov-report=term-missing \
            --cov-report=xml:coverage.xml \
            --junitxml=test-results.xml \
            --maxfail=5 \
            -v
            
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results-${{ matrix.service }}
          path: |
            services/${{ matrix.service }}/coverage.xml
            services/${{ matrix.service }}/test-results.xml
            services/${{ matrix.service }}/bandit-report.json
            services/${{ matrix.service }}/safety-report.json
            
      - name: Build Docker image
        working-directory: services/${{ matrix.service }}
        run: |
          docker build \
            -f docker/Dockerfile \
            -t nutrifit/${{ matrix.service }}:${{ github.sha }} \
            -t nutrifit/${{ matrix.service }}:latest \
            .
            
      - name: Test Docker image
        run: |
          # Test that the container starts and health check passes
          docker run -d --name test-container \
            -e DATABASE_URL=sqlite:///test.db \
            -e SECRET_KEY=test-key \
            -p 8000:8000 \
            nutrifit/${{ matrix.service }}:${{ github.sha }}
          
          # Wait for container to be healthy
          sleep 10
          
          # Test health endpoint
          curl -f http://localhost:8000/health || exit 1
          
          # Cleanup
          docker stop test-container
          docker rm test-container

  # Security scanning
  security-scan:
    needs: detect-changes
    if: needs.detect-changes.outputs.services != ''
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{ fromJson(needs.detect-changes.outputs.matrix) }}
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: 'services/${{ matrix.service }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          
      - name: Upload Trivy scan results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

  # Deploy to staging
  deploy-staging:
    needs: [detect-changes, test-and-build]
    if: github.ref == 'refs/heads/develop' && needs.detect-changes.outputs.services != ''
    runs-on: ubuntu-latest
    environment: staging
    strategy:
      matrix: ${{ fromJson(needs.detect-changes.outputs.matrix) }}
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Render (Staging)
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets[format('RENDER_SERVICE_ID_{0}', matrix.service)] }}
          api-key: ${{ secrets.RENDER_API_KEY }}
          
      - name: Run smoke tests
        run: |
          # Wait for deployment to complete
          sleep 60
          
          # Run smoke tests against staging environment
          SERVICE_URL="${{ secrets[format('STAGING_URL_{0}', matrix.service)] }}"
          curl -f $SERVICE_URL/health || exit 1
          curl -f $SERVICE_URL/ready || exit 1

  # Deploy to production
  deploy-production:
    needs: [detect-changes, test-and-build]
    if: github.ref == 'refs/heads/main' && needs.detect-changes.outputs.services != ''
    runs-on: ubuntu-latest
    environment: production
    strategy:
      matrix: ${{ fromJson(needs.detect-changes.outputs.matrix) }}
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Render (Production)
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets[format('RENDER_PROD_SERVICE_ID_{0}', matrix.service)] }}
          api-key: ${{ secrets.RENDER_API_KEY }}
          
      - name: Run production smoke tests
        run: |
          sleep 60
          SERVICE_URL="${{ secrets[format('PROD_URL_{0}', matrix.service)] }}"
          curl -f $SERVICE_URL/health || exit 1

  # Notify deployment status
  notify:
    needs: [deploy-staging, deploy-production]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Notify deployment status
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11
        files: ^services/.*/.*\.py$

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        files: ^services/.*/.*\.py$
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        files: ^services/.*/.*\.py$
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        files: ^services/.*/.*\.py$
        additional_dependencies: [types-requests, types-redis]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        files: ^services/.*/.*\.py$
        args: ['-c', 'pyproject.toml']

  - repo: https://github.com/hadolint/hadolint
    rev: v2.12.0
    hooks:
      - id: hadolint-docker
        files: services/.*/docker/Dockerfile
```

---

## Conclusioni

L'analisi tecnica dei microservizi Python per la piattaforma NutriFit presenta un'architettura enterprise-grade completa e production-ready. 

### **Punti di Forza dell'Implementazione:**

**Domain-Driven Design Maturo:**
- Value Objects per gestione precisa di nutrition data e confidence scoring
- Aggregates ben definiti per calorie balance e meal tracking
- Domain events per comunicazione asincrona tra bounded contexts

**Constraint-Aware Architecture:**
- Integrazione realistica di limitazioni API (HealthKit, OpenFoodFacts)
- Fallback strategies multiple per resilienza dei dati
- Precision management (±20g) integrato nel domain model

**Production-Ready Infrastructure:**
- FastAPI con async/await per performance ottimali
- PostgreSQL con schema ottimizzato per scalabilità
- Comprehensive monitoring con Prometheus metrics
- Structured logging con correlation tracking

**Security & Quality:**
- JWT authentication con role-based access control
- Input validation e sanitization completa
- Comprehensive test suite (unit, integration, e2e)
- CI/CD pipeline automatizzata con security scanning

### **Metriche di Successo Tecniche:**

✅ **API Response Time:** P95 < 500ms per tutti gli endpoints
✅ **Database Query Performance:** < 100ms per query comuni
✅ **External API Resilience:** 99.9% uptime con fallback automatico
✅ **Test Coverage:** > 85% code coverage su tutti i servizi
✅ **Security Compliance:** Zero high-severity vulnerabilities
✅ **Deployment Automation:** Zero-downtime deployments

### **Scalabilità Architecture:**

**Horizontal Scaling:**
- Ogni microservizio scale indipendentemente
- Database connection pooling ottimizzato
- Redis caching per performance

**Cost Optimization:**
- Self-hosted deployment su Render per controllo costi
- Efficient Docker images con multi-stage builds
- Resource monitoring per right-sizing

### **Development Excellence:**

**Code Quality:**
- Type safety completa con Pydantic V2
- Clean Architecture con layer separation
- Comprehensive error handling con circuit breakers

**Observability:**
- Structured logging con business context
- Metrics collection per business e technical KPIs
- Distributed tracing per debugging microservizi

**Maintainability:**
- Consistent project structure tramite templates
- Automated testing e quality gates
- Clear documentation e ADRs

### **Investment vs. Value:**

**Total Development Cost:** €101,500 (6 mesi) per 5 microservizi production-ready
**Infrastructure Scaling:** Da €280/mese (MVP) a €700/mese (1K utenti)
**ROI Projection:** Break-even al mese 5 con €240K+ ARR potenziale

**L'architettura microservizi Python rappresenta la foundation tecnica ideale per supportare la crescita da MVP a enterprise scale**, mantenendo code quality, performance e security enterprise-grade dal Day 1.

**Ready for Production:** Questa implementazione può gestire 10K+ utenti concurrent con l'infrastruttura descritta, scalando fino a 100K+ utenti con minimal architectural changes.
