# Changelog

All notable changes to the Calorie Balance Service will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-09-05

### 🎉 MAJOR: Production-Ready with PgBouncer Solution

#### Added
- **UUID-based prepared statement solution** for complete PgBouncer compatibility
- **Full test validation** for all endpoint implementations
- **Calorie Events API** complete implementation:
  - `POST /api/v1/calorie-event/consumed` - Log food consumption
  - `POST /api/v1/calorie-event/burned` - Log exercise calories
  - `POST /api/v1/calorie-event/weight` - Log weight measurements
  - `POST /api/v1/calorie-event/batch` - Batch events for mobile apps
- **Enhanced development scripts**:
  - `start-dev.sh` with background execution and logging
  - Complete test suite validation
- **Comprehensive documentation** updates

#### Fixed
- **🔧 CRITICAL: DuplicatePreparedStatementError completely resolved**
  - Implemented UUID-based prepared statement naming
  - NullPool configuration for PgBouncer transaction mode
  - Disabled statement caching to prevent conflicts
- **PUT /api/v1/users/{user_id}** endpoint now returns proper HTTP responses
- **JSON formatting issues** in test scripts resolved
- **API routing issues** with trailing slash requirements

#### Changed
- **Database configuration** optimized for Supabase + PgBouncer
- **Test suite** enhanced with timeout handling and better error reporting
- **API Documentation** updated to reflect actual implemented endpoints
- **Performance optimizations** for cloud deployment

#### Technical Details
```python
# New database configuration resolving PgBouncer conflicts
engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,  # Essential for PgBouncer transaction mode
    connect_args={
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4().hex}__",
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        # ... optimized timeout settings
    }
)
```

#### Validation
- ✅ **All API endpoints tested** and working
- ✅ **Zero database conflicts** detected
- ✅ **Production deployment ready**
- ✅ **Complete test coverage** for core functionality

---

## [1.2.0] - 2025-09-05

### Added
- **5-Level Temporal Analytics** database views:
  - `hourly_calorie_summary` - Real-time intraday analysis
  - `daily_calorie_summary` - Day-over-day comparisons
  - `weekly_calorie_summary` - Weekly patterns and habits
  - `monthly_calorie_summary` - Long-term trend analysis
  - `daily_balance_summary` - Net calorie balance calculations
- **Performance-optimized indexes** for mobile query patterns
- **Complete database schema** for event-driven architecture

### Changed
- **Database migration** to support high-frequency events
- **Enhanced user model** with metabolic parameters
- **Improved API documentation** with event-driven examples

---

## [1.1.0] - 2025-09-05

### Added
- **Event-Driven Architecture** foundation
- **Basic API endpoints**:
  - User management (CRUD operations)
  - Calorie goals creation and retrieval
  - Daily balance tracking (legacy support)
- **Health check endpoints** for Kubernetes deployment
- **Initial database schema** with SQLAlchemy async

### Changed
- **Architecture refactor** from simple CRUD to event-driven design
- **Database optimization** for Supabase deployment

---

## [1.0.0] - 2025-09-05

### Added
- **Initial service setup** with FastAPI framework
- **Basic project structure** with Clean Architecture
- **Poetry dependency management**
- **Docker support** for containerized deployment
- **Basic health check** endpoint

### Technical Stack
- **FastAPI** 0.100.1 for REST API
- **SQLAlchemy** 2.0.20 for database ORM
- **asyncpg** 0.27.0 for PostgreSQL async driver
- **Supabase** for managed PostgreSQL with real-time features
- **Python** 3.11+ runtime environment
