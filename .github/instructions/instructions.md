# 🏋️ NutriFit Platform - GitHub Instructions

## 📋 Project Overview

**NutriFit** è una piattaforma fitness-nutrizionale enterprise basata su microservizi Python, con focus sul bilanciamento calorico intelligente e tracking nutrizionale per il mercato italiano.

### 🎯 Core Mission
- Bilanciamento calorico precision-aware (±20g accuracy)
- Integrazione HealthKit/Health Connect per dati fitness
- AI-powered food recognition con GPT-4V
- Coaching nutrizionale personalizzato via RAG system
- Cross-platform mobile app (Flutter POC)

## 🏗️ Architecture Overview

### Microservices Structure (5 Services)
1. **🔥 Calorie Balance Service** - Energy metabolism & balance calculation
2. **🍎 Meal Tracking Service** - Food recognition, OpenFoodFacts integration
3. **📊 Health Monitor Service** - HealthKit sync, data quality scoring
4. **🔔 Notifications Service** - Smart notifications & coaching prompts
5. **🤖 AI Nutrition Coach Service** - RAG system, conversational AI

### Tech Stack
- **Backend**: Python 3.11 + FastAPI + PostgreSQL
- **Mobile**: Flutter (cross-platform POC)
- **AI**: OpenAI GPT-4V + RAG system
- **Infrastructure**: Docker + Render deployment
- **Database**: PostgreSQL + Supabase integration

## 💻 Development Guidelines

### Code Standards
- **Language**: Python 3.11+ con type hints obbligatori
- **Framework**: FastAPI per tutti i microservizi
- **Architecture**: Domain-Driven Design (DDD) con Clean Architecture
- **Dependencies**: Poetry per dependency management
- **Testing**: pytest con coverage minimo 80%
- **Code Quality**: black + isort + flake8 + mypy

### Project Structure Template
```bash
services/{service_name}/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── core/                   # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── config.py          # Settings & environment vars
│   │   ├── database.py        # Database connection & session
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── logging.py         # Structured logging setup
│   │   └── security.py        # JWT & auth utilities
│   ├── domain/                 # Domain layer (DDD)
│   │   ├── __init__.py
│   │   ├── entities/          # Business entities
│   │   ├── value_objects/     # Immutable value objects
│   │   ├── aggregates/        # Aggregate roots
│   │   ├── repositories/      # Repository interfaces
│   │   └── services/          # Domain services
│   ├── application/            # Application services
│   │   ├── __init__.py
│   │   ├── commands/          # Command handlers (CQRS)
│   │   ├── queries/           # Query handlers
│   │   ├── services/          # Application services
│   │   └── dto/               # Data Transfer Objects
│   ├── infrastructure/         # External integrations
│   │   ├── __init__.py
│   │   ├── database/          # SQLAlchemy models & repositories
│   │   ├── external/          # External API clients
│   │   ├── messaging/         # Event publishing/subscribing
│   │   └── caching/           # Redis caching
│   └── api/                    # REST endpoints
│       ├── __init__.py
│       ├── dependencies.py    # FastAPI dependencies
│       ├── middleware.py      # Custom middleware
│       ├── routers/           # API route handlers
│       └── schemas/           # Pydantic request/response models
├── tests/                      # Test suites
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── fixtures/              # Test fixtures & factories
│   └── conftest.py            # Pytest configuration
├── alembic/                    # DB migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Alembic configuration
├── docker/                     # Containerization
│   ├── Dockerfile             # Production image
│   ├── Dockerfile.dev         # Development image
│   └── docker-compose.yml     # Service-specific compose
├── scripts/                    # Utility scripts
│   ├── setup.sh              # Service setup script
│   ├── test.sh               # Test runner
│   └── migrate.sh            # Migration runner
├── docs/                       # Service documentation
│   ├── README.md             # Service overview
│   ├── api.md                # API documentation
│   └── deployment.md         # Deployment notes
├── pyproject.toml             # Poetry configuration
├── alembic.ini               # Alembic settings
├── .env.example              # Environment template
├── .dockerignore             # Docker ignore rules
└── .gitignore                # Git ignore rules
```

### 🏗️ Microservice Template Usage

#### 1. Service Creation
```bash
# Crea nuovo microservice dal template
make setup-service SERVICE=meal-tracking

# Oppure manualmente:
mkdir -p services/meal-tracking
cp -r templates/microservice-template/* services/meal-tracking/
```

#### 2. Configuration Setup
**pyproject.toml Template**:
```toml
[tool.poetry]
name = "nutrifit-{{SERVICE_NAME}}"
version = "1.0.0"
description = "NutriFit {{SERVICE_NAME}} Microservice"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
pydantic = {extras = ["email"], version = "^2.4.0"}
pydantic-settings = "^2.0.0"
asyncpg = "^0.29.0"
redis = "^5.0.0"
httpx = "^0.25.0"
structlog = "^23.2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
black = "^23.7.0"
isort = "^5.12.0"
flake8 = "^6.0.0"
mypy = "^1.5.0"
```

#### 3. FastAPI Main Template
**app/main.py**:
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.core.database import create_tables
from app.core.logging import setup_logging
from app.api.routers import health, v1
from app.core.exceptions import DomainException

# Setup structured logging
setup_logging()
logger = structlog.get_logger()

app = FastAPI(
    title=f"NutriFit {settings.service_name.title()} Service",
    description=f"Microservice for {settings.service_name} functionality",
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=400,
        content={"error": exc.message, "code": exc.code}
    )

# Health check (required for Render)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.service_name}

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(v1.router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    logger.info("Starting up", service=settings.service_name)
    await create_tables()

@app.on_event("shutdown")  
async def shutdown():
    logger.info("Shutting down", service=settings.service_name)
```

#### 4. Configuration Template
**app/core/config.py**:
```python
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Service config
    service_name: str = "{{SERVICE_NAME}}"
    environment: str = "development"
    debug: bool = False
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl: int = 3600
    
    # External APIs
    openai_api_key: Optional[str] = None
    openfoodfacts_user_agent: str = "NutriFit/1.0"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

#### 5. Domain Layer Template
**app/domain/value_objects/calorie_amount.py**:
```python
from decimal import Decimal
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class CalorieAmount:
    """Value object per quantità caloriche con precision ±20g"""
    value: Decimal
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Calorie amount cannot be negative")
        if self.value > 10000:  # Reasonable upper limit
            raise ValueError("Calorie amount seems unrealistic")
    
    @classmethod
    def from_float(cls, value: float) -> 'CalorieAmount':
        return cls(Decimal(str(value)))
    
    def to_float(self) -> float:
        return float(self.value)
    
    def __add__(self, other: 'CalorieAmount') -> 'CalorieAmount':
        return CalorieAmount(self.value + other.value)
    
    def __sub__(self, other: 'CalorieAmount') -> 'CalorieAmount':
        return CalorieAmount(self.value - other.value)
```

#### 6. Repository Pattern Template
**app/domain/repositories/base.py**:
```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')

class Repository(Generic[T], ABC):
    """Base repository interface"""
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity"""
        pass
    
    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List entities with pagination"""
        pass
```

#### 7. Testing Template
**tests/conftest.py**:
```python
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db

# Test database
TEST_DATABASE_URL = settings.database_url.replace("/nutrifit_", "/test_nutrifit_")

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture
async def db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db):
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
```

Questo template garantisce:
- 🏗️ **Clean Architecture** con separation of concerns
- 📊 **DDD Patterns** con entities, value objects, aggregates
- 🧪 **Testing Ready** con fixtures e mocking
- 🔒 **Security** con JWT e validation
- 📈 **Monitoring** con health checks e metrics
- 🚀 **Production Ready** con Docker e deployment

### Domain-Driven Design Patterns
- **Value Objects**: Immutable per precisione (FoodQuantity, CalorieAmount)
- **Entities**: Business objects con identity
- **Aggregates**: Consistency boundaries
- **Repositories**: Data access abstractions
- **Domain Services**: Business logic complex

### Data Quality & Precision
- **Precision Management**: ±20g accuracy per food quantities
- **Data Source Attribution**: Confidence scoring per data source
- **Fallback Strategies**: Multi-source data resolution
- **Quality Scoring**: Cronometer-style confidence indicators

## 🔧 Development Workflow

### Branch Strategy
- `main` - Production ready code
- `develop` - Integration branch
- `feature/service-name-feature` - Feature branches
- `hotfix/issue-description` - Emergency fixes

### Commit Conventions
```bash
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Scopes: calorie-balance, meal-tracking, health-monitor, notifications, ai-coach
```

### Pull Request Guidelines
1. **Title**: Clear, descriptive con service scope
2. **Description**: Use PR template con checklist
3. **Tests**: Tutti i test devono passare
4. **Coverage**: Mantenere coverage >80%
5. **Documentation**: Aggiornare docs se necessario

## 🧪 Testing Requirements

### Test Pyramid
- **Unit Tests**: Domain logic, value objects, calculations
- **Integration Tests**: Database, external APIs
- **E2E Tests**: Full user journeys
- **Performance Tests**: Latency <200ms per endpoint

### Critical Test Areas
- **Calorie Calculations**: Precision mathematical formulas
- **Data Quality**: Confidence scoring algorithms
- **API Integration**: OpenFoodFacts, HealthKit fallbacks
- **AI Responses**: Prompt engineering validation

## 🔐 Security Guidelines

- **Authentication**: JWT tokens con Supabase Auth
- **API Security**: Rate limiting, input validation
- **Data Privacy**: GDPR compliance per dati italiani
- **Health Data**: HealthKit privacy requirements
- **Environment Variables**: Secrets via .env files

## 📊 Data Management

### Database Design
- **PostgreSQL**: Primary database per tutti i servizi
- **Migrations**: Alembic per schema evolution
- **Indexing**: Ottimizzazione query frequenti
- **Backup**: Automated daily backups

### External APIs
- **OpenFoodFacts**: Fallback strategies per missing data
- **HealthKit**: Real-time sync con confidence scoring
- **OpenAI**: Token usage monitoring
- **Supabase**: Auth e real-time subscriptions

## 🚀 Deployment

### 🐳 Docker Guidelines

#### Dockerfile Structure (Multi-stage)
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false
RUN poetry install --only=main --no-root

# Production stage  
FROM python:3.11-slim as production
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose Setup
- **Development**: `docker/docker-compose.dev.yml` - Hot reload, debug ports
- **Staging**: `docker/docker-compose.staging.yml` - Production-like environment  
- **Production**: `docker/docker-compose.prod.yml` - Optimized for performance

#### Service Communication
- **Internal Network**: `nutrifit-network` per comunicazione interna
- **Health Checks**: Endpoint `/health` obbligatorio per ogni service
- **Logging**: Structured JSON logs per aggregazione
- **Resource Limits**: CPU/Memory limits definiti per ogni container

#### Environment Variables Pattern
```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis Cache  
REDIS_URL=redis://host:6379
REDIS_TTL=3600

# External APIs
OPENAI_API_KEY=sk-...
OPENFOODFACTS_USER_AGENT=NutriFit/1.0
HEALTHKIT_BUNDLE_ID=com.nutrifit.app

# Service Config
SERVICE_NAME=calorie-balance
SERVICE_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### 🚀 Render Deployment

#### Service Configuration
Ogni microservice su Render richiede:

**1. Build Configuration**
```yaml
# render.yaml per ogni service
services:
  - type: web
    name: nutrifit-calorie-balance
    env: python
    plan: starter
    buildCommand: "pip install poetry && poetry install --only=main"
    startCommand: "poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /health
    autoDeploy: false
```

**2. Environment Variables**
- Configurare tramite Render Dashboard
- Utilizzare Secret Files per credentials sensibili
- Database URL auto-generato da Render PostgreSQL

**3. Domain Setup**
- **Production**: `nutrifit.app` con subdomains per services
- **Staging**: `staging.nutrifit.app`
- SSL certificates automatici

#### Database Setup
```sql
-- PostgreSQL setup per ogni service
CREATE DATABASE nutrifit_calorie_balance;
CREATE DATABASE nutrifit_meal_tracking;  
CREATE DATABASE nutrifit_health_monitor;
CREATE DATABASE nutrifit_notifications;
CREATE DATABASE nutrifit_ai_coach;

-- User permissions
CREATE USER nutrifit_user WITH ENCRYPTED PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE nutrifit_* TO nutrifit_user;
```

#### Deployment Pipeline
1. **GitHub Action** triggera build
2. **Docker build** e push a registry
3. **Render webhook** deploy automatico
4. **Health checks** validation
5. **Rollback automatico** se health check fails

#### Monitoring & Alerts
- **Render Metrics**: CPU, Memory, Response time
- **Custom Metrics**: Business KPIs via `/metrics` endpoint
- **Log Aggregation**: Structured logs per troubleshooting
- **Alerts**: Slack notifications per downtime/errori

### CI/CD Pipeline
- **GitHub Actions**: Automated testing e deployment
- **Render**: Production deployment target
- **Environment Promotion**: dev → staging → production

## 📝 Documentation Standards

### Code Documentation
- **Docstrings**: Google style per tutte le funzioni
- **Type Hints**: Completi per tutte le signatures
- **README**: Per ogni microservizio
- **API Docs**: FastAPI auto-generated + examples

### Architecture Documentation
- **ADR**: Architectural Decision Records
- **Domain Models**: Diagrammi updated
- **Integration Patterns**: Sequence diagrams
- **Deployment Diagrams**: Infrastructure overview

## 🎯 Performance Requirements

### Response Time Targets
- **API Endpoints**: <200ms average
- **Database Queries**: <100ms per query
- **AI Responses**: <3s per GPT-4V request
- **HealthKit Sync**: <5s per batch

### Scalability Considerations
- **Horizontal Scaling**: Stateless microservizi
- **Database Sharding**: User-based partitioning
- **Caching**: Redis per frequent data
- **Rate Limiting**: Per-user API quotas

## 🔍 Code Review Checklist

### Technical Review
- [ ] Type hints completi
- [ ] Error handling appropriato
- [ ] Security validations
- [ ] Performance considerations
- [ ] Test coverage adeguato

### Domain Review
- [ ] Business logic correct
- [ ] DDD patterns applicati
- [ ] Data quality managed
- [ ] Precision requirements met
- [ ] Integration constraints handled

### Documentation Review
- [ ] README updated
- [ ] API documentation current
- [ ] Architecture diagrams updated
- [ ] Migration scripts documented

## 🏆 Quality Gates

### Pre-merge Requirements
- [ ] Tutti i test passed (unit + integration)
- [ ] Code coverage ≥80%
- [ ] Linting passed (black, isort, flake8, mypy)
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] PR template completed

### Production Readiness
- [ ] Load testing completed
- [ ] Security audit passed  
- [ ] Monitoring configured
- [ ] Rollback plan documented
- [ ] Health checks implemented

---

## 🚀 Quick Start Guide

### Per Nuovi Sviluppatori
```bash
# 1. Setup iniziale ambiente  
make setup

# 2. Creare primo microservice
make setup-service SERVICE=calorie-balance

# 3. Avviare ambiente sviluppo
make dev

# 4. Test del nuovo service
make test-service SERVICE=calorie-balance
```

### Per Contributi Existing Services
```bash
# 1. Branch feature
make branch-feature NAME=add-precision-calculation

# 2. Sviluppo con hot reload
make dev-service SERVICE=calorie-balance

# 3. Quality check prima del commit
make quick-test

# 4. Deploy staging per testing
make deploy-staging
```

### Docker Workflow Completo
```bash
# 1. Build tutti i services
make docker-build

# 2. Start con database locale
make docker-up

# 3. Health check
make health-check

# 4. Logs monitoring
make docker-logs-service SERVICE=calorie-balance
```

### Render Deployment Commands
```bash
# 1. Deploy staging (automatic su push develop)
git push origin develop

# 2. Deploy production (automatic su push main)  
git push origin main

# 3. Manual deployment
make deploy-production
```

**⚡ Quick Start**: `make setup && make dev` per ambiente locale  
**📖 Full Docs**: Vedi `/docs` per documentazione completa  
**🤝 Support**: Crea issue per domande architetturali
