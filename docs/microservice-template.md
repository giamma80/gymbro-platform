# 🏗️ Standard Template per Microservizi GymBro - DUAL API ARCHITECTURE

Questo è il template standardizzato per tutti i microservizi della piattaforma GymBro che implementa **DUAL API ARCHITECTURE** (REST + GraphQL) usando Domain-Driven Design con Poetry.

> ✅ **BEST PRACTICE CONSOLIDATE**: Ogni nuovo microservizio DEVE implementare sia REST che GraphQL endpoints fin dall'inizio

## 🎯 DOMAIN-DRIVEN DESIGN APPROACH

**DUAL API ARCHITECTURE OBBLIGATORIA:**
- ✅ REST API endpoints per operazioni CRUD e business logic
- ✅ GraphQL schema per query federate e integrazione Apollo
- ✅ Apollo Federation ready fin dall'inizio  
- ✅ Unified data models condivisi tra REST e GraphQL

## 📁 Struttura Directory Standard

```
services/{service-name}/
├── app/                    # 📦 Codice applicazione
│   ├── __init__.py
│   ├── main.py            # 🚀 Entry point FastAPI con DUAL API integration
│   ├── config.py          # ⚙️ Configurazione
│   ├── models.py          # 📋 Pydantic schemas (condivisi REST/GraphQL)
│   ├── database.py        # 🗄️ SQLAlchemy models
│   ├── auth.py            # 🔐 Autenticazione
│   ├── services.py        # 💼 Business logic
│   ├── graphql_schema.py  # 🔗 Strawberry GraphQL schema - APOLLO FEDERATION
│   └── api/               # 🌐 REST API endpoints
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── endpoints.py
├── tests/                 # 🧪 Test suite
│   ├── __init__.py
│   ├── conftest.py        # Test configuration
│   ├── test_models.py     # Model tests
│   ├── test_auth.py       # Auth tests
│   ├── test_config.py     # Config tests
│   ├── test_graphql.py    # GraphQL schema tests - APOLLO FEDERATION
│   ├── test_endpoints.py  # REST endpoints tests
│   └── test_services.py   # Service tests
├── alembic/               # 📊 Database migrations
├── scripts/               # 🔧 Utility scripts
├── pyproject.toml         # 📦 Poetry configuration - DEPENDENCIES CONSOLIDATE
├── poetry.lock            # 🔒 Lock file - DEVE essere committato
├── README.md              # 📚 Documentation
├── .env.example           # 🔐 Environment template
├── .env.test              # 🧪 Test environment
├── .dockerignore          # 🐳 Docker ignore file - BUILD OPTIMIZATION
└── Dockerfile             # 🐳 Container definition - SINGLE-STAGE BUILD
```

## 📦 pyproject.toml Template - CONSOLIDATO

```toml
[tool.poetry]
name = "gymbro-{service-name}"
version = "1.0.0"
description = "GymBro Platform - {Service Name} Service - Dual API (REST + GraphQL)"
authors = ["GymBro Team <team@gymbro-platform.com>"]
readme = "README.md"
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.11"
# FastAPI + ASGI server
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
# Validation + Settings
pydantic = {extras = ["email"], version = "^2.5.0"}
pydantic-settings = "^2.0.3"
# Database + async
sqlalchemy = {extras = ["asyncio"], version = "^2.0.23"}
asyncpg = "^0.29.0"
# GraphQL - APOLLO FEDERATION READY
strawberry-graphql = {extras = ["fastapi"], version = "^0.215.3"}
# Auth + Security
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
# Monitoring + Logging
sentry-sdk = {extras = ["fastapi"], version = "^1.38.0"}
structlog = "^23.2.0"
# Utilities
httpx = "^0.25.2"
email-validator = "^2.1.0"
redis = "^5.0.1"

[tool.poetry.group.dev.dependencies]
pytest = "^8.4.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
black = "^25.1.0"
isort = "^6.0.0"
flake8 = "^7.3.0"
mypy = "^1.17.0"
pre-commit = "^4.0.1"
factory-boy = "^3.3.0"

[tool.poetry.group.test.dependencies]
pytest-mock = "^3.14.0"
pytest-xdist = "^3.6.0"
coverage = "^7.6.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

# Tool configurations
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

## 🔧 **POETRY DEPENDENCY MANAGEMENT WORKFLOW**

**⚠️ PROCESSO OBBLIGATORIO per gestione dipendenze Python:**

### 📦 Installazione Dipendenze
```bash
# Installazione iniziale progetto
poetry install

# Aggiungere nuova dipendenza runtime
poetry add {package-name}

# Aggiungere dipendenza dev/testing
poetry add --group dev {package-name}
poetry add --group test {package-name}

# Esempio GraphQL support
poetry add "strawberry-graphql[fastapi]"
poetry add python-multipart
```

### 🔄 Rigenerazione Lock File (CRITICO!)
```bash
# SEMPRE dopo modifiche dipendenze:
# 1. Cancella lock file esistente
rm poetry.lock

# 2. Rigenera lock file pulito
poetry install

# 3. Verifica installazione
poetry show | grep {package-name}
```

### 🐳 Docker Build Process
```bash
# SEMPRE rebuild no-cache dopo poetry changes
docker-compose build --no-cache {service-name}

# Restart service per testing
docker-compose restart {service-name}

# Verifica logs
docker-compose logs {service-name}
```

### 🔌 Integration Steps (es. GraphQL)
```python
# 1. Crea schema/router file
# services/{service}/graphql_schema.py

# 2. Import in main.py
from graphql_schema import graphql_router

# 3. Include router in FastAPI app
app.include_router(graphql_router)
```

**📋 Poetry Workflow Checklist:**
- [ ] `poetry add {package}` per nuove dipendenze
- [ ] `rm poetry.lock && poetry install` per lock rebuild
- [ ] Update main.py imports/setup
- [ ] `docker-compose build --no-cache {service}`
- [ ] `docker-compose restart {service}` per testing
- [ ] Verifica endpoint funzionanti

## � Dockerfile Template - SINGLE-STAGE BUILD (CONSOLIDATO)

> ✅ **PROVATO**: Single-Stage Build > Multi-Stage per compatibility con Poetry

```dockerfile
# STANDARD DOCKERFILE per microservizi GymBro
FROM python:3.11-slim

# Environment variables STANDARD
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.3

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/opt/poetry_cache \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV_PATH=/opt/poetry_venv

# Copy dependency files
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root \
    && rm -rf /opt/poetry_cache

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 .dockerignore Template - BUILD OPTIMIZATION

```dockerignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.pytest_cache/
htmlcov/

# Poetry
poetry.lock.orig

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Documentation
README.md
docs/
*.md

# Tests
tests/
test_*
*_test.py

# Environment files
.env
.env.*

# Logs
*.log
logs/
```

## 🔗 GraphQL Schema Template - APOLLO FEDERATION READY

### ⚠️ CRITICAL APOLLO FEDERATION REQUIREMENTS

**🔧 LESSONS LEARNED FROM PRODUCTION IMPLEMENTATION:**

1. **✅ _service Field Implementation (MANDATORY)**
   ```python
   # REQUIRED: Manual _service field for Apollo Federation discovery
   @strawberry.type
   class ServiceDefinition:
       """Apollo Federation service definition"""
       sdl: str

   @strawberry.field(name="_service")
   def service_field(self) -> ServiceDefinition:
       """Apollo Federation service definition - Required by Gateway"""
       # CRITICAL: Use camelCase field names to match Strawberry conversion
       sdl = """
           extend type Query {
               healthCheck: String
               serviceInfo: ServiceInfo
               healthStatus: HealthStatus
           }
       """
       return ServiceDefinition(sdl=sdl)
   ```

2. **✅ Strawberry Field Name Convention**
   - Strawberry auto-converts snake_case to camelCase
   - SDL schema MUST match actual exposed field names
   - Example: `health_check` → `healthCheck` in SDL

3. **✅ Federation Import Pattern**
   ```python
   # REQUIRED: Graceful fallback for federation import
   try:
       from strawberry.federation import build_schema
       FEDERATION_AVAILABLE = True
   except ImportError:
       from strawberry import Schema as build_schema
       FEDERATION_AVAILABLE = False
       print("⚠️ Strawberry Federation not available, using regular schema")
   ```

### graphql_schema.py
```python
"""
GraphQL Schema per {Service Name} Service
Apollo Federation Ready - Dual API Architecture
"""

from typing import List, Optional
from enum import Enum
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

# ✅ ENUM PATTERN CONSOLIDATO - @strawberry.enum class Pattern
@strawberry.enum
class StatusType(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

@strawberry.enum
class PriorityType(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# ✅ STRAWBERRY TYPE per modelli GraphQL
@strawberry.type
class HealthStatus:
    service: str
    status: str
    timestamp: str

@strawberry.type
class ServiceInfo:
    name: str
    version: str
    environment: str
    
# ✅ QUERY CLASS con test endpoints
@strawberry.type
class Query:
    @strawberry.field
    def health_check(self) -> str:
        """GraphQL health check endpoint"""
        return "GraphQL endpoint operational for {Service Name}"
    
    @strawberry.field
    def service_info(self) -> ServiceInfo:
        """Service information for Apollo Federation"""
        return ServiceInfo(
            name="{service-name}",
            version="1.0.0",
            environment="development"
        )
    
    @strawberry.field
    def health_status(self) -> HealthStatus:
        """Detailed health status"""
        from datetime import datetime
        return HealthStatus(
            service="{service-name}",
            status="healthy",
            timestamp=datetime.now().isoformat()
        )

# ✅ MUTATION CLASS (esempio)
@strawberry.type
class Mutation:
    @strawberry.field
    def ping(self) -> str:
        """Test mutation endpoint"""
        return "pong from {Service Name} GraphQL"

# ✅ SCHEMA SETUP per Apollo Federation
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # Apollo Federation extensions saranno aggiunte qui
)

# ✅ ROUTER SETUP per FastAPI integration
graphql_router = GraphQLRouter(
    schema,
    graphiql=True,  # GraphiQL interface abilitata
    path="/graphql"
)
```

## ⚡ main.py Template - DUAL API INTEGRATION

```python
"""
{Service Name} Service - Dual API Architecture
FastAPI + GraphQL (Strawberry) con Apollo Federation Ready
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

# GraphQL integration
from graphql_schema import graphql_router

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(
    title="{Service Name} Service",
    description="GymBro Platform - {Service Name} Service - Dual API (REST + GraphQL)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure per production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REST API ENDPOINTS - Core functionality
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "{service-name}",
        "version": "1.0.0",
        "status": "operational",
        "apis": ["REST", "GraphQL"],
        "endpoints": {
            "rest": "/docs",
            "graphql": "/graphql"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint per monitoring"""
    return {
        "status": "healthy",
        "service": "{service-name}",
        "timestamp": datetime.now().isoformat(),
        "apis": {
            "rest": "operational",
            "graphql": "operational"
        }
    }

@app.get("/ping")
async def ping():
    """Ping endpoint per connectivity testing"""
    return {"message": "pong", "service": "{service-name}"}

# ✅ GRAPHQL INTEGRATION - Apollo Federation ready
app.include_router(graphql_router, prefix="", tags=["GraphQL"])

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🌐 GraphQL Gateway Template (Node.js/TypeScript)

### ⚠️ CRITICAL GATEWAY REQUIREMENTS

**🔧 LESSONS LEARNED FOR APOLLO GATEWAY:**

1. **✅ Express JSON Middleware (MANDATORY)**
   ```typescript
   // CRITICAL: JSON parsing middleware for Apollo Server
   app.use(express.json());
   app.use(express.urlencoded({ extended: true }));
   
   // MUST be added BEFORE Apollo Server middleware
   app.use('/graphql', expressMiddleware(server, {
       context: async ({ req, res }): Promise<Context> => ({
           req, res
       })
   }));
   ```

2. **✅ Centralized PORT Configuration**
   ```typescript
   // config.ts - Prevent PORT NaN errors
   export const config = {
       PORT: (() => {
           const port = process.env.PORT || process.env.RENDER_EXTERNAL_PORT || '4000';
           const parsed = parseInt(port, 10);
           if (isNaN(parsed)) {
               console.error(`❌ Invalid PORT value: ${port}`);
               return 4000;
           }
           return parsed;
       })(),
       NODE_ENV: process.env.NODE_ENV || 'development'
   };
   ```

3. **✅ Schema Refresh Pattern**
   ```typescript
   // Force schema refresh when subgraph schemas change
   const gateway = new ApolloGateway({
       supergraphSdl: new IntrospectAndCompose({
           subgraphs: [
               { name: 'service-name', url: SERVICE_URL }
           ]
       }),
       debug: config.NODE_ENV !== 'production'
   });
   ```

from models import {ModelName} as {ModelName}Model
from services import {ServiceName}Service
from database import get_db

@strawberry.type
class {EntityName}:
    """GraphQL Type per {EntityName}"""
    id: strawberry.ID
    name: str
    email: Optional[str] = None
    created_at: str
    updated_at: str
    
    @classmethod
    def from_model(cls, model: {ModelName}Model) -> "{EntityName}":
        return cls(
            id=strawberry.ID(str(model.id)),
            name=model.name,
            email=model.email,
            created_at=model.created_at.isoformat(),
            updated_at=model.updated_at.isoformat()
        )

@strawberry.input
class {EntityName}Input:
    """Input type per create/update {EntityName}"""
    name: str
    email: Optional[str] = None

@strawberry.type
class Query:
    """Query root per {Service Name}"""
    
    @strawberry.field
    async def {entity_name}s(self, info: Info) -> List[{EntityName}]:
        """Fetch all {entity_name}s"""
        async with get_db() as db:
            service = {ServiceName}Service(db)
            models = await service.get_all()
            return [{EntityName}.from_model(model) for model in models]
    
    @strawberry.field
    async def {entity_name}(self, info: Info, id: strawberry.ID) -> Optional[{EntityName}]:
        """Fetch {entity_name} by ID"""
        async with get_db() as db:
            service = {ServiceName}Service(db)
            model = await service.get_by_id(int(id))
            return {EntityName}.from_model(model) if model else None

@strawberry.type
class Mutation:
    """Mutation root per {Service Name}"""
    
    @strawberry.field
    async def create_{entity_name}(self, info: Info, input: {EntityName}Input) -> {EntityName}:
        """Create new {entity_name}"""
        async with get_db() as db:
            service = {ServiceName}Service(db)
            model = await service.create(input.__dict__)
            return {EntityName}.from_model(model)
    
    @strawberry.field
    async def update_{entity_name}(self, info: Info, id: strawberry.ID, input: {EntityName}Input) -> Optional[{EntityName}]:
## 🚀 DEPLOYMENT WORKFLOW - CONSOLIDATO

### Step 1: Poetry Setup
```bash
# 1. Inizializza progetto
poetry init --no-interaction --name "gymbro-{service-name}"

# 2. Aggiungi dipendenze core
poetry add fastapi uvicorn strawberry-graphql[fastapi] sqlalchemy[asyncio] asyncpg pydantic-settings

# 3. Aggiungi dev dependencies  
poetry add --group dev pytest pytest-asyncio black isort mypy

# 4. Genera lock file
poetry install
```

### Step 2: File Setup da Template
```bash
# Copy template files con pattern consolidati
cp /path/to/template/Dockerfile ./
cp /path/to/template/.dockerignore ./
cp /path/to/template/main.py ./
cp /path/to/template/graphql_schema.py ./

# Personalizza placeholders
sed -i 's/{service-name}/your-service-name/g' *.py
sed -i 's/{Service Name}/Your Service Name/g' *.py
```

### Step 3: Docker Build & Test
```bash
# Build con single-stage approach
docker-compose build --no-cache your-service-name

# Start service
docker-compose up your-service-name

# Test endpoints
curl http://localhost:8000/health      # REST endpoint
curl http://localhost:8000/graphql     # GraphQL endpoint (GET)
```

### Step 4: Apollo Federation Integration
```bash
# Test GraphQL schema
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ healthCheck }"}'

# Validate enum patterns
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ serviceInfo { name version } }"}'

# 🚨 SEMPRE eseguire test completi dopo deployment
./scripts/test-all-services.sh
```

### Step 5: Post-Deployment Validation
```bash
# Test pipeline OBBLIGATORIA dopo ogni push GitHub
./scripts/test-all-services.sh      # Test tutti i servizi
./scripts/health-check.sh           # Check infrastruttura

# Se deployment su produzione (Render/AWS)
./scripts/test-all-services.sh prod # Test ambiente produzione
```

## ✅ VALIDATION CHECKLIST

**Poetry & Dependencies:**
- [ ] `poetry install` esegue senza errori
- [ ] `poetry show` mostra strawberry-graphql[fastapi] installato
- [ ] poetry.lock committato nel repository

**Docker & Build:**
- [ ] Dockerfile usa single-stage build pattern
- [ ] `.dockerignore` ottimizza build context
- [ ] Build completa senza ModuleNotFoundError
- [ ] Health check funziona: `curl localhost:8000/health`

**REST API:**
- [ ] GET `/` ritorna service info
- [ ] GET `/health` ritorna status healthy  
- [ ] GET `/ping` ritorna pong message
- [ ] GET `/docs` mostra Swagger documentation

**GraphQL API:**
- [ ] GET `/graphql` mostra GraphiQL interface
- [ ] POST `/graphql` accetta queries
- [ ] Enum types funzionano (@strawberry.enum pattern)
- [ ] Schema validation passa

**Apollo Federation Ready:**
- [ ] GraphQL schema strutturato per federation
- [ ] Service info query disponibile
- [ ] Enum consistency tra servizi
- [ ] Health check GraphQL disponibile

**Best Practices:**
- [ ] Dual API architecture implementata (REST + GraphQL)
- [ ] Domain-Driven Design pattern seguito
- [ ] Error handling configurato
- [ ] CORS middleware configurato
- [ ] Logging strutturato attivo

## 🎯 NEXT STEPS dopo Template

1. **Customize Business Logic**: Implementa domain models specifici
2. **Database Integration**: Configura SQLAlchemy models e migrations
3. **Authentication**: Integra JWT auth pattern del platform
4. **Testing**: Espandi test suite con business logic tests
5. **Apollo Gateway**: Registra service nel gateway per federation

> ✅ **RISULTATO**: Microservizio con Dual API Architecture pronto per Apollo Federation Step 2
app.include_router(graphql_router)
logger.info("✅ GraphQL endpoint added at /graphql")
```
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["app"]
omit = ["*/tests/*", "*/venv/*", "*/__pycache__/*"]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
```

## 🧪 Test Structure Standard

### conftest.py
```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session():
    # Test database session
    yield None

@pytest.fixture
async def client():
    # Test FastAPI client
    yield None
```

### test_models.py Template
```python
import pytest
from pydantic import ValidationError
from models import {ModelName}

class Test{ServiceName}Models:
    def test_model_validation(self):
        # Test model validation
        pass
        
    def test_enum_values(self):
        # Test enum values
        pass
```

## 🔧 Makefile Commands Standard

Ogni servizio avrà questi comandi standard:

```makefile
# Service-specific commands
install-{service}:
	@cd services/{service} && poetry install

test-{service}:
	@cd services/{service} && poetry run pytest tests/ -v --cov=app

lint-{service}:
	@cd services/{service} && poetry run flake8 . && poetry run mypy .

format-{service}:
	@cd services/{service} && poetry run black . && poetry run isort .

dev-{service}:
	@cd services/{service} && poetry run uvicorn main:app --reload --port {port}
```

## 🚀 CI/CD Pipeline Standard

```yaml
- name: Set up Poetry
  uses: snok/install-poetry@v1
  with:
    version: latest
    virtualenvs-create: true
    virtualenvs-in-project: true

- name: Cache Poetry dependencies
  uses: actions/cache@v3
  with:
    path: .venv
    key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}

- name: Install dependencies
  run: poetry install --no-interaction --no-ansi

- name: Run tests
  run: poetry run pytest tests/ -v --cov=app --cov-report=xml

- name: Run linting
  run: |
    poetry run black --check .
    poetry run isort --check-only .
    poetry run flake8 .
    poetry run mypy .
```

## 📝 Documentazione Standard

Ogni servizio avrà:

1. **README.md** con:
   - Descrizione del servizio
   - Setup instructions con Poetry
   - API documentation links
   - Test instructions

2. **Environment files**:
   - `.env.example` - Template per produzione
   - `.env.test` - Variabili per test

## 🔄 Migration Checklist

Per migrare un servizio esistente:

- [ ] Creare `pyproject.toml` dal template
- [ ] Rimuovere `requirements.txt` e `requirements-dev.txt`
- [ ] Creare struttura test standard
- [ ] Aggiornare Makefile commands
- [ ] Aggiornare CI/CD pipeline
- [ ] Aggiornare documentazione
- [ ] Testare che tutto funzioni

## ✨ Best Practices

1. **Dependency Groups**: Separare dev, test e produzione
2. **Lock File**: Sempre committare `poetry.lock`
3. **Version Pinning**: Usare constraint appropriati (^, ~, ==)
4. **Tool Configuration**: Centralizzare in `pyproject.toml`
5. **Testing**: Coverage >= 80% per ogni servizio
6. **Linting**: Zero warnings in produzione

Questo template garantisce consistenza e qualità in tutti i microservizi! 🎯
