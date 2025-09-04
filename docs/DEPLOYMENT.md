# 🚀 Deployment Guide - NutriFit Platform

## 🎯 Overview

Questo documento definisce la strategia di deployment per la piattaforma NutriFit, focalizzata su **Render.com** come piattaforma cloud-native con CI/CD automatizzato e monitoraggio integrato.

## 🏗️ Architettura Deployment

### Environment Strategy

```
Production (main branch)
├── 5 Microservizi Render Services
├── Supabase Cloud (Production)
├── N8N Cloud (Production)
└── Flutter App (App Store + Google Play)

Staging (develop branch)  
├── 5 Microservizi Render Services
├── Supabase Cloud (Staging)
├── N8N Cloud (Staging)
└── Flutter Web (Preview)

Development (local)
├── Docker Compose Services
├── Supabase Local Development
├── N8N Self-hosted
└── Flutter Local Debug
```

## ☁️ Render.com Deployment

### Service Configuration

#### 1. Microservice Deployment Template
```yaml
# render.yaml (per ogni microservice)
services:
  - type: web
    name: nutrifit-calorie-balance
    env: python
    buildCommand: |
      cd services/calorie-balance
      pip install poetry
      poetry install --only=main
    startCommand: |
      cd services/calorie-balance
      poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: nutrifit-calorie-balance-db
          property: connectionString
      - key: SUPABASE_URL
        value: https://your-project.supabase.co
      - key: SUPABASE_ANON_KEY
        sync: false  # Secret value
      - key: N8N_WEBHOOK_URL
        value: https://your-n8n.app.n8n.cloud/webhook
      - key: OPENAI_API_KEY
        sync: false  # Secret value
      - key: REDIS_URL
        fromService:
          type: redis
          name: nutrifit-redis

databases:
  - name: nutrifit-calorie-balance-db
    databaseName: calorie_balance
    user: nutrifit_user
    region: frankfurt  # EU per GDPR compliance

  - name: nutrifit-redis
    type: redis
    region: frankfurt
    maxmemoryPolicy: allkeys-lru
```

#### 2. Environment Variables Management
```bash
# Production Environment
DATABASE_URL=postgresql://user:pass@host:5432/calorie_balance
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...  # Secret
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # Secret
N8N_WEBHOOK_URL=https://your-n8n.app.n8n.cloud/webhook
N8N_API_KEY=n8n_...  # Secret
OPENAI_API_KEY=sk-...  # Secret
REDIS_URL=redis://user:pass@host:6379
ENVIRONMENT=production
LOG_LEVEL=INFO
SENTRY_DSN=https://...  # Error tracking

# Staging Environment  
DATABASE_URL=postgresql://user:pass@staging-host:5432/calorie_balance_staging
SUPABASE_URL=https://your-staging-project.supabase.co
# ... staging values
ENVIRONMENT=staging
LOG_LEVEL=DEBUG
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [calorie-balance, meal-tracking, health-monitor, notifications, ai-coach]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: 1.6.1
          virtualenvs-create: true
          virtualenvs-in-project: true
      
      - name: Install dependencies
        run: |
          cd services/${{ matrix.service }}
          poetry install
      
      - name: Run tests
        run: |
          cd services/${{ matrix.service }}
          poetry run pytest --cov=app --cov-report=xml
      
      - name: Code quality checks
        run: |
          cd services/${{ matrix.service }}
          poetry run black --check app tests
          poetry run isort --check-only app tests
          poetry run flake8 app tests
          poetry run mypy app

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run security scan
        uses: securecodewarrior/github-action-add-sarif@v1
        with:
          sarif-file: 'security-scan.sarif'

  deploy-staging:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
      - name: Deploy to Render (Staging)
        uses: renderinc/render-deploy-action@v1.2.0
        with:
          service-id: ${{ secrets.RENDER_STAGING_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
          wait-for-success: true

  deploy-production:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to Render (Production)
        uses: renderinc/render-deploy-action@v1.2.0
        with:
          service-id: ${{ secrets.RENDER_PRODUCTION_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
          wait-for-success: true
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Database Migrations

#### Alembic Migration Strategy
```python
# services/calorie-balance/alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
from app.core.config import settings
from app.infrastructure.database.models import Base

# Alembic Config object
config = context.config

# Override database URL from environment
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

#### Migration Commands
```bash
# Generate migration
cd services/calorie-balance
poetry run alembic revision --autogenerate -m "Add user nutrition preferences"

# Apply migrations (staging)
ENVIRONMENT=staging poetry run alembic upgrade head

# Apply migrations (production)
ENVIRONMENT=production poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

## 📊 Monitoring & Observability

### Logging Strategy

#### Structured Logging
```python
# app/core/logging.py
import structlog
import logging.config
from typing import Any, Dict

def configure_logging(environment: str) -> None:
    """Configure structured logging"""
    
    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if environment == "development":
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

# Usage in services
import structlog

logger = structlog.get_logger(__name__)

async def create_user(user_data: UserCreate) -> User:
    logger.info("Creating user", email=user_data.email)
    
    try:
        user = await user_service.create_user(user_data)
        logger.info("User created successfully", user_id=str(user.id))
        return user
    except Exception as e:
        logger.error("Failed to create user", error=str(e), email=user_data.email)
        raise
```

### Health Checks

#### Service Health Endpoints
```python
# app/api/routers/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.config import settings
import httpx
import redis

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "calorie-balance"}

@router.get("/health/detailed")
async def detailed_health_check(session: AsyncSession = Depends(get_session)):
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "service": "calorie-balance",
        "checks": {}
    }
    
    # Database check
    try:
        await session.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
    
    # External API checks
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.SUPABASE_URL}/rest/v1/", timeout=5.0)
            if response.status_code == 200:
                health_status["checks"]["supabase"] = "healthy"
            else:
                health_status["checks"]["supabase"] = f"unhealthy: {response.status_code}"
                health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["supabase"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
```

### Error Tracking & Monitoring

#### Sentry Integration
```python
# app/core/monitoring.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from app.core.config import settings

def init_monitoring():
    """Initialize error tracking and monitoring"""
    
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                FastApiIntegration(auto_enable=True),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,
            environment=settings.ENVIRONMENT,
            release=settings.APP_VERSION,
        )

# app/main.py
from app.core.monitoring import init_monitoring

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_monitoring()
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)
```

#### Custom Metrics
```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
REQUEST_COUNT = Counter(
    'requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

NUTRITION_CALCULATIONS = Counter(
    'nutrition_calculations_total',
    'Total nutrition calculations',
    ['calculation_type', 'confidence_level']
)

# Middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🔧 Deployment Commands

### Production Deployment
```bash
# Manual deployment trigger
curl -X POST "https://api.render.com/deploy/srv-SERVICE_ID" \
     -H "Authorization: Bearer $RENDER_API_KEY"

# Check deployment status
curl "https://api.render.com/v1/services/srv-SERVICE_ID/deploys" \
     -H "Authorization: Bearer $RENDER_API_KEY"

# View service logs
render logs -s srv-SERVICE_ID --tail=100
```

### Database Operations
```bash
# Run migrations on production
render exec -s srv-calorie-balance-SERVICE_ID -- \
  poetry run alembic upgrade head

# Backup database
render pg:backup nutrifit-calorie-balance-db

# Restore database
render pg:restore nutrifit-calorie-balance-db backup-file.sql
```

### Service Management
```bash
# Scale service
curl -X PATCH "https://api.render.com/v1/services/srv-SERVICE_ID" \
     -H "Authorization: Bearer $RENDER_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"numInstances": 3}'

# Update environment variables
curl -X PUT "https://api.render.com/v1/services/srv-SERVICE_ID/env-vars" \
     -H "Authorization: Bearer $RENDER_API_KEY" \
     -H "Content-Type: application/json" \
     -d '[{"key": "LOG_LEVEL", "value": "INFO"}]'
```

## 🛡️ Security & Compliance

### HTTPS & Certificates
- **Automatic HTTPS**: Render provides automatic SSL certificates
- **HSTS Headers**: Implemented in FastAPI middleware
- **Security Headers**: CSP, X-Frame-Options, etc.

### Environment Security
```python
# app/core/security.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt
from app.core.config import settings

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/api/v1/nutrition/analyze")
@limiter.limit("10/minute")
async def analyze_nutrition(request: Request):
    # API endpoint with rate limiting
    pass
```

### Data Privacy (GDPR)
- **EU Region Deployment**: Frankfurt region for EU users
- **Data Encryption**: At rest and in transit
- **Audit Logging**: All data access logged
- **Right to Deletion**: Automated user data deletion

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (≥80% coverage)
- [ ] Security scan completed
- [ ] Database migrations reviewed
- [ ] Environment variables configured
- [ ] Health checks implemented
- [ ] Monitoring dashboards setup

### Production Deployment
- [ ] Blue-green deployment strategy
- [ ] Database migration executed
- [ ] Health checks verified
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] Rollback plan prepared

### Post-Deployment
- [ ] Service health verified
- [ ] API endpoints tested
- [ ] Performance metrics reviewed
- [ ] Error rates monitored
- [ ] User feedback collected
- [ ] Documentation updated

---

## 🚀 Next Steps

Consulta anche:
- **[Development Workflow](DEVELOPMENT_WORKFLOW.md)** - Git flow e coding standards
- **[Testing Guide](TESTING_GUIDE.md)** - Testing strategy dettagliata *(da creare)*
- **[API Documentation](API_DOCUMENTATION.md)** - REST/GraphQL specifications *(da creare)*
