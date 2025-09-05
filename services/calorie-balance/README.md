# NutriFit Calorie Balance Service

## Overview

Il **Calorie Balance Service** è il microservizio centrale della piattaforma NutriFit, responsabile per:

- 🔥 **Energy Metabolism**: Calcolo BMR, TDEE, e fabbisogno calorico personalizzato
- ⚖️ **Balance Tracking**: Monitoraggio bilancio calorico giornaliero con precision ±20g
- 🎯 **Goal Management**: Gestione obiettivi calorici dinamici con AI optimization
- 📊 **Analytics**: Pattern analysis e trend calculation per insights nutrizionali

> **📋 [API Development Roadmap](API-roadmap.md)** - Stato completo delle API implementate e da sviluppare

## Architecture

Questo servizio implementa **Domain-Driven Design** con Clean Architecture:

```
app/
├── core/              # Cross-cutting concerns
├── domain/            # Business logic (DDD)
├── application/       # Use cases & commands
├── infrastructure/    # External integrations  
└── api/              # REST endpoints
```

## Domain Model

### Core Entities
- **User**: Profilo utente con parametri metabolici
- **CalorieGoal**: Obiettivi calorici dinamici
- **DailyBalance**: Bilancio giornaliero con confidence scoring
- **MetabolicProfile**: Profilo metabolico personalizzato

### Value Objects
- **CalorieAmount**: Quantità calorica con precision management
- **ConfidenceScore**: Scoring qualità dati (0.0-1.0)
- **TimeWindow**: Finestre temporali per analisi

## API Endpoints

### Health & Status
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health with dependencies

### User Management
- `POST /users` - Create user profile
- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user profile

### Calorie Goals
- `POST /users/{user_id}/goals` - Set calorie goals
- `GET /users/{user_id}/goals` - Get current goals
- `PUT /users/{user_id}/goals/{goal_id}` - Update goals

### Daily Balance
- `GET /users/{user_id}/balance/today` - Current day balance
- `GET /users/{user_id}/balance/{date}` - Specific date balance
- `POST /users/{user_id}/balance/update` - Update balance

### Analytics
- `GET /users/{user_id}/trends` - Weekly/monthly trends
- `GET /users/{user_id}/insights` - AI-powered insights

## Setup & Development

### Prerequisites
- Python 3.11+
- Poetry
- PostgreSQL (via Supabase)
- Redis (for caching)

### Local Development
```bash
# Install dependencies
poetry install

# Setup environment
cp .env.example .env

# Run migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload --port 8001
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run only unit tests
poetry run pytest tests/unit/

# Run only integration tests  
poetry run pytest tests/integration/
```

### Code Quality
```bash
# Format code
poetry run black app tests
poetry run isort app tests

# Lint code
poetry run flake8 app tests
poetry run mypy app

# Pre-commit checks
poetry run pre-commit run --all-files
```

## Database Schema

### Tables
- `users` - User profiles con parametri metabolici
- `calorie_goals` - Obiettivi calorici con AI optimization
- `daily_balances` - Bilanci giornalieri con confidence tracking
- `metabolic_profiles` - Profili metabolici personalizzati

### Key Relationships
- User 1:N CalorieGoals (time-based goals)
- User 1:N DailyBalances (daily tracking)
- User 1:1 MetabolicProfile (current profile)

## Integration Points

### Supabase Integration
- Real-time subscriptions per balance updates
- Row Level Security per data isolation
- Database functions per calcoli metabolici

### External Services
- **Meal Tracking Service**: Riceve calorie consumate
- **Health Monitor Service**: Riceve calorie bruciate da HealthKit
- **AI Coach Service**: Fornisce dati per insights AI
- **N8N Workflows**: Trigger per automation e notifications

## Deployment

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:5432/calorie_balance
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
REDIS_URL=redis://user:pass@host:6379
ENVIRONMENT=development|staging|production
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
```

### Render Deployment
```yaml
# render.yaml
services:
  - type: web
    name: nutrifit-calorie-balance
    env: python
    buildCommand: poetry install --only=main
    startCommand: poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
```

## Monitoring & Observability

### Health Checks
- Database connectivity
- Redis connectivity  
- External service availability
- Business logic validation

### Metrics
- Request latency P95/P99
- Error rates per endpoint
- Calorie calculation accuracy
- User engagement metrics

### Logging
- Structured JSON logging
- Request/response tracking
- Error tracking con Sentry integration
- Performance monitoring

---

**Tech Stack**: FastAPI + SQLAlchemy + Supabase + Redis + Python 3.11
**Architecture**: Domain-Driven Design + Clean Architecture + CQRS patterns
