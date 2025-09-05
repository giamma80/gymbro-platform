# NutriFit Calorie Balance Service

## Overview

Il **Calorie Balance Service** è il microservizio centrale della piattaforma NutriFit con **architettura event-driven** di nuova generazione, responsabile per:

- 🔥 **Energy Metabolism**: Calcolo BMR, TDEE, e fabbisogno calorico personalizzato
- ⚖️ **Balance Tracking**: Monitoraggio bilancio calorico in tempo reale con campionamento 2-minuti
- 🎯 **Goal Management**: Gestione obiettivi calorici dinamici con AI optimization
- 📊 **Timeline Analytics**: Pattern analysis e trend calculation con 5-level temporal aggregations
- 📱 **Mobile-First**: Architettura ottimizzata per raccolta dati smartphone ad alta frequenza

> **📋 [API Development Roadmap](API-roadmap.md)** - Stato completo delle API implementate e da sviluppare  
> **Status**: ✅ **Event-Driven Ready** | **v1.2.0** | **Database Migration Complete**

## 🚀 Event-Driven Architecture

### Architettura Bi-Level
1. **High-Frequency Events** (`calorie_events`) - Precisione al secondo, campionamento 2-minuti
2. **Daily Aggregations** (`daily_balances`) - Cache giornaliera per performance

### 🗓️ 5-Level Temporal Analytics
| Livello | Vista Database | Aggregazione | Use Case |
|---------|---------------|--------------|----------|
| 🕐 **Hourly** | `hourly_calorie_summary` | Per ora | Real-time intraday trends |
| 📅 **Daily** | `daily_calorie_summary` | Per giorno | Day-over-day comparisons |
| 📆 **Weekly** | `weekly_calorie_summary` | Per settimana | Weekly patterns, habits |
| 🗓️ **Monthly** | `monthly_calorie_summary` | Per mese | Long-term trends |
| ⚖️ **Balance** | `daily_balance_summary` | Bilanci netti | Net calories, weight correlation |

## Architecture

Questo servizio implementa **Event-Driven Design** con Clean Architecture:

```
app/
├── core/              # Cross-cutting concerns
├── domain/            # Business logic (DDD) + Event entities
├── application/       # Use cases & event handlers  
├── infrastructure/    # External integrations + Event storage
└── api/              # REST endpoints + Event APIs
```

## Domain Model

### Core Entities
- **User**: Profilo utente con parametri metabolici
- **CalorieGoal**: Obiettivi calorici dinamici
- **CalorieEvent**: 🔥 **NEW** - Eventi ad alta frequenza per timeline analytics
- **DailyBalance**: Bilancio giornaliero con aggregazioni da eventi
- **MetabolicProfile**: Profilo metabolico personalizzato

### Event Types
- **CalorieConsumed**: Eventi consumo calorico da pasti
- **CalorieBurnedExercise**: Eventi consumo da esercizio fisico  
- **CalorieBurnedBMR**: Eventi consumo metabolismo basale
- **WeightMeasurement**: Eventi misurazione peso

### Value Objects
- **CalorieAmount**: Quantità calorica con precision management
- **EventTimestamp**: Timestamp preciso al secondo per eventi
- **AggregationWindow**: Finestre temporali per analisi (hour/day/week/month)
- **ConfidenceScore**: Scoring qualità dati (0.0-1.0)

## API Endpoints

### Health & Status
- `GET /health` - Basic health check
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### User Management
- `POST /api/v1/users/` - Create user profile ✅
- `GET /api/v1/users/{user_id}` - Get user profile ✅
- `PUT /api/v1/users/{user_id}` - Update user profile ✅
- `DELETE /api/v1/users/{user_id}` - Delete user profile (TODO)
- `GET /api/v1/users/` - List users (admin) (TODO)

### Calorie Goals
- `POST /api/v1/goals/users/{user_id}` - Create calorie goal ✅
- `GET /api/v1/goals/users/{user_id}/active` - Get active goal ✅
- `PUT /api/v1/goals/users/{user_id}/goals/{goal_id}` - Update goal (TODO)
- `DELETE /api/v1/goals/users/{user_id}/goals/{goal_id}` - Delete goal (TODO)
- `GET /api/v1/goals/users/{user_id}/history` - Goals history (TODO)

### 🔥 Calorie Events (Event-Driven APIs)
- `POST /api/v1/calorie-event/consumed` - Log consumption event ✅
- `POST /api/v1/calorie-event/burned` - Log exercise burn ✅
- `POST /api/v1/calorie-event/weight` - Log weight measurement ✅
- `POST /api/v1/calorie-event/batch` - Batch events from mobile ✅
- `GET /api/v1/events/users/{user_id}/timeline` - Get events timeline (TODO)
- `GET /api/v1/events/users/{user_id}/latest` - Get latest events (TODO)

### ⚖️ Daily Balance (Legacy Support)
- `PUT /api/v1/balance/users/{user_id}` - Update daily balance ✅
- `GET /api/v1/balance/users/{user_id}/date/{date}` - Get balance for date ✅
- `GET /api/v1/balance/users/{user_id}/today` - Get today's balance ✅
- `POST /api/v1/balance/users/{user_id}/progress` - Get progress data ✅
- `GET /api/v1/balance/users/{user_id}/summary/weekly` - Weekly summary (TODO)
- `GET /api/v1/balance/users/{user_id}/summary/monthly` - Monthly summary (TODO)

### 📈 Timeline Analytics (Multi-Level Temporal)
- `GET /api/v1/timeline/users/{user_id}/hourly` - Hourly aggregations (TODO)
- `GET /api/v1/timeline/users/{user_id}/daily` - Daily aggregations (TODO)
- `GET /api/v1/timeline/users/{user_id}/weekly` - Weekly patterns & trends (TODO)
- `GET /api/v1/timeline/users/{user_id}/monthly` - Monthly progress analytics (TODO)
- `GET /api/v1/timeline/users/{user_id}/balance` - Net balance calculations (TODO)
- `GET /api/v1/timeline/users/{user_id}/intraday` - Detailed intra-day view (TODO)
- `GET /api/v1/timeline/users/{user_id}/patterns` - Behavioral patterns (TODO)
- `GET /api/v1/timeline/users/{user_id}/real-time` - Real-time current status (TODO)
- `GET /api/v1/timeline/users/{user_id}/export` - Export timeline data (TODO)
- `GET /api/v1/timeline/users/{user_id}/compare` - Compare time periods (TODO)

### 📊 Analytics & Trends
- `GET /api/v1/users/{user_id}/trends` - Weekly/monthly trends (TODO)
- `GET /api/v1/users/{user_id}/insights` - AI-powered insights (TODO)
- `GET /api/v1/users/{user_id}/analytics/weight` - Weight trend analysis (TODO)
- `GET /api/v1/users/{user_id}/analytics/performance` - Performance metrics (TODO)

### 🧬 Metabolic Profiles
- `GET /api/v1/users/{user_id}/profile/metabolic` - Get metabolic profile (TODO)
- `PUT /api/v1/users/{user_id}/profile/metabolic` - Update metabolic profile (TODO)
- `POST /api/v1/users/{user_id}/profile/metabolic/calculate` - Recalculate BMR/TDEE (TODO)

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

# Create database schema (Event-Driven)
poetry run python create_tables_direct.py

# Start development server
poetry run uvicorn app.main:app --reload --port 8001
```

### Database Setup (Event-Driven)
```bash
# Create complete event-driven schema with temporal views
poetry run python create_tables_direct.py

# The script creates:
# - calorie_events table (high-frequency events)
# - Enhanced daily_balances (with event aggregations)
# - 5-level temporal views (hourly → monthly)
# - Performance indexes for mobile queries
# - Complete structure validation
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

## Database Schema (Event-Driven)

### Core Tables
- **`users`** - User profiles con parametri metabolici
- **`calorie_goals`** - Obiettivi calorici con AI optimization  
- **`calorie_events`** - 🔥 **NEW** - Eventi ad alta frequenza (2-min sampling)
- **`daily_balances`** - Enhanced con aggregazioni da eventi
- **`metabolic_profiles`** - Profili metabolici personalizzati

### 🗓️ Temporal Views (Performance Optimized)
- **`hourly_calorie_summary`** - Aggregazioni orarie per real-time analytics
- **`daily_calorie_summary`** - Aggregazioni giornaliere per comparisons
- **`weekly_calorie_summary`** - Pattern settimanali (Mon-Sun) con active_days
- **`monthly_calorie_summary`** - Trend mensili con multi-level averages
- **`daily_balance_summary`** - Bilanci calorici netti con weight correlation

### Key Relationships
- User 1:N CalorieGoals (time-based goals)
- User 1:N CalorieEvents (high-frequency timeline)
- User 1:N DailyBalances (daily aggregations from events)
- User 1:1 MetabolicProfile (current profile)

### Performance Features
- **Compound indexes** su user_id + event_timestamp per mobile queries
- **Pre-computed aggregations** via views per sub-second response
- **Event sourcing** per complete timeline reconstruction
- **Optimized for Supabase** con soluzione UUID per prepared statements
- **PgBouncer compatibility** completa per production deployment

### 🔧 Database Persistence Solution
Il servizio implementa una **soluzione ottimizzata per PgBouncer** che risolve completamente i conflitti di prepared statements:

**Configurazione UUID per Prepared Statements:**
```python
engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,  # Compatibilità PgBouncer transaction mode
    connect_args={
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4().hex}__",
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        # Timeout ottimizzati per cloud deployment
    }
)
```

**Benefici della soluzione:**
- ✅ **Zero conflitti** di prepared statements con PgBouncer
- ✅ **Compatibilità totale** con modalità transaction
- ✅ **Performance ottimali** per high-frequency events
- ✅ **Produzione-ready** con validazione completa
- ✅ **Supabase native** senza compromessi funzionali

## Integration Points

### 📱 Mobile App Integration (High-Frequency)
- **2-minute sampling** supportata via calorie_events
- **Batch API** per ridurre network calls
- **Offline support** con event queuing
- **Real-time aggregations** per dashboard updates

### Supabase Integration
- **Real-time subscriptions** per balance updates
- **Row Level Security** per data isolation
- **Event-driven functions** per calcoli automatici
- **Performance views** per analytics veloci

### External Services
- **Meal Tracking Service**: Invia eventi CalorieConsumed
- **Health Monitor Service**: Invia eventi CalorieBurned da HealthKit/GoogleFit
- **AI Coach Service**: Consuma timeline analytics per insights AI
- **N8N Workflows**: Trigger su pattern anomali e milestone achievements

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
- **Request latency** P95/P99 per endpoint
- **Event processing rate** (events/second)
- **Timeline query performance** (view response times)
- **Error rates** per endpoint type
- **Mobile sync success rate**
- **Temporal aggregation accuracy**
- **User engagement** via event frequency

### Logging
- **Structured JSON logging** con event correlation
- **Request/response tracking** per API calls
- **Event processing monitoring** con batch metrics
- **Error tracking** con Sentry integration
- **Performance monitoring** per temporal views

---

## 🚀 Event-Driven Features

### 📱 Mobile-First Design
- **High-frequency sampling** (2-minute intervals)
- **Batch processing** per network efficiency
- **Offline-first** con event synchronization
- **Real-time dashboard** updates

### 📊 5-Level Analytics
- **Hourly trends** per meal timing analysis
- **Daily comparisons** per goal tracking
- **Weekly patterns** per habit formation
- **Monthly insights** per long-term progress
- **Balance calculations** per deficit/surplus analysis

### ⚡ Performance Optimizations
- **Pre-computed views** per sub-second responses
- **Compound indexes** per mobile query patterns
- **Event sourcing** per complete data lineage
- **Supabase-optimized** queries

---

**Tech Stack**: FastAPI + SQLAlchemy + Supabase + Redis + Python 3.11  
**Architecture**: Event-Driven Design + Clean Architecture + Temporal Analytics  
**Database**: PostgreSQL con 5-Level Temporal Views + Event Sourcing
