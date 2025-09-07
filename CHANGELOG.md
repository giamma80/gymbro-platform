# 📝 NutriFit Platform - Changelog

Questo file documenta tutti i cambiamenti significativi al progetto NutriFit Platform.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### � Documentation Cleanup - v1.2.1 (2025-09-07)
- **Removed redundant instructions.md** - Eliminato file duplicato nella root del progetto
- **Centralized documentation references** - Tutti i riferimenti ora puntano a `.github/instructions/instructions.md`
- **User Management Service integration** - Aggiornata tutta la documentazione per includere il 6° microservizio
- **Fixed circular references** - Risolti link circolari e riferimenti obsoleti nei documenti
- **Architecture consistency** - Allineamento completo tra README, instructions, e documentazione microservizi
- **Database documentation complete** - Creata documentazione completa per User Management Service database

### �🚀 Added - v1.2.0 Event-Driven Architecture (2025-09-05)
- **Event-Driven Database Schema** - Migrazione completa ad architettura event-driven per Calorie Balance Service
- **5-Level Temporal Analytics** - Sistema completo di aggregazioni temporali (hourly → daily → weekly → monthly → balance)
- **High-Frequency Event Collection** - Supporto campionamento smartphone ogni 2 minuti via `calorie_events` table
- **Performance Views** - 5 viste database pre-calcolate per analytics sub-secondo:
  - `hourly_calorie_summary` - Real-time intraday trends
  - `daily_calorie_summary` - Day-over-day comparisons  
  - `weekly_calorie_summary` - Weekly patterns con active_days tracking
  - `monthly_calorie_summary` - Long-term trends con multi-level averages
  - `daily_balance_summary` - Net calorie calculations con weight correlation
- **Mobile-First Architecture** - Ottimizzazioni per raccolta dati smartphone ad alta frequenza
- **Enhanced API Roadmap** - Espansione da 45 a 54 endpoints con timeline analytics APIs
- **Database Validation System** - Check strutturale completo con verifica tabelle, viste, indici e constraints
- **Event Sourcing Capability** - Completa ricostruzione timeline da eventi granulari
- **Comprehensive Documentation** - Aggiornamento README.md e API-roadmap.md per nuova architettura

### 🔄 Changed - Event-Driven Migration
- **Database Schema**: Migrazione da daily-only a bi-level (events + aggregations)
- **daily_balances** enhanced con `events_count` e `last_event_timestamp` per aggregation tracking
- **API Completion**: 27% → 31% (17/54 endpoints) con nuove categorie temporal analytics
- **Performance Strategy**: Da query real-time a pre-computed views per mobile optimization
- **Documentation**: API-roadmap.md e README.md completamente rivisti per event-driven architecture

### 🔥 New Database Features
- **calorie_events table** - Eventi ad alta frequenza con precision al secondo
- **Event types**: consumed, burned_exercise, burned_bmr, weight con JSONB metadata
- **Compound indexes** - Ottimizzati per query pattern mobile (user_id + event_timestamp)
- **Event sourcing** - Capacità ricostruzione completa timeline utente
- **Multi-source support** - Tracking source eventi (app, smartwatch, manual, api, sync)

### 📊 Analytics Capabilities
- **Real-time intraday** - Trends orari per meal timing analysis
- **Pattern detection** - Weekly habits e seasonal patterns
- **Engagement metrics** - Active days, event frequency, consistency tracking
- **Cross-period analysis** - Week numbers, month numbers per seasonal comparisons
- **Balance calculations** - Net calories, deficit/surplus analysis, peso correlation

### 🏗️ Breaking Changes
- **Database Migration Required** - Schema migration da legacy daily_balances
- **setup_database.py REMOVED** - Consolidato in create_tables_direct.py
- **UNIQUE constraint changed** - daily_balances.UNIQUE(user_id, date) ora compatible con eventi
- **API Versioning** - Preparazione per /api/v1/events/ e /api/v1/timeline/ endpoints

## [v1.1.0] - 2025-09-04 - API Roadmap Foundation

### Added
- **Calorie Balance Microservice** - Completa implementazione del microservizio per calcolo calorie e metabolismo
- **Clean Architecture** - Domain-driven design con separazione layers (Domain, Application, Infrastructure, API)
- **FastAPI + SQLAlchemy 2.0** - API moderna con async/await e type hints completi
- **Supabase Integration** - Connessione ottimizzata con Supabase PostgreSQL + connection pooling
- **Comprehensive Testing** - Script di test automation con 100% success rate (6 test completi)
- **Enum Validation** - Validatori Pydantic case-insensitive per Gender e ActivityLevel
- **Email Validation** - Validazione formato email con regex patterns
- **API Documentation** - Swagger/ReDoc completamente configurato e accessibile
- **Health Monitoring** - Endpoint di health check con status database e servizi
- **Development Tools** - Script per setup ambiente, test automation, database creation
- Struttura documentazione hub-and-spoke con `.github/instructions/instructions.md` centrale
- Link organizzati tra README principale e documentazione specializzata
- **[Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)** - Git flow, coding standards, DDD patterns, testing strategy
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Render.com deployment, CI/CD, monitoring, security

### Fixed
- **SQLAlchemy Prepared Statements** - Risolto DuplicatePreparedStatementError con Supabase transaction pooling
- **Database Connection** - Configurazione `statement_cache_size=0` per compatibilità PgBouncer/Supabase
- **Enum Handling** - Gestione dinamica enum/string nel repository layer con `hasattr()` checks
- **Test Automation** - Corretti pattern JSON matching negli script di test (spazi rimossi)

### Infrastructure
- **Poetry Setup** - Gestione dipendenze con Poetry + lock file per riproducibilità
- **Database Schema** - Tabelle PostgreSQL ottimizzate con constraints e indexes
- **Connection Pooling** - Configurazione asyncpg ottimizzata per Supabase
- **Structured Logging** - Implementazione structlog per logging professionale
- **Environment Config** - Configurazione .env con Pydantic Settings

### Documentation
- GitHub Instructions.md aggiornato con collegamenti ipertestuali coerenti
- README principale con sezione "Project Management" e link al changelog
- Eliminata ridondanza di contenuti tra documenti

## [0.2.0] - 2025-09-05 🚀

### Added - Calorie Balance Microservice
- **Complete FastAPI Microservice** - Full implementation with Clean Architecture patterns
- **User Management API** - CRUD operations for user profiles with comprehensive validation
- **Health Check System** - Advanced monitoring endpoint with database/service status
- **Supabase Integration** - Optimized PostgreSQL connection with asyncpg driver
- **Comprehensive Test Suite** - 100% automated testing with 6 complete test scenarios
- **API Documentation** - Full Swagger/ReDoc integration with interactive documentation

### Technical Features
- **Domain-Driven Design** - Separated layers: Domain, Application, Infrastructure, API
- **SQLAlchemy 2.0** - Modern async ORM with type safety and performance optimization
- **Pydantic Validation** - Advanced request/response validation with enum support
- **Structured Logging** - Professional logging system with structlog integration
- **Poetry Dependency Management** - Reproducible builds with lock file

### Database & Infrastructure
- **PostgreSQL Schema** - Optimized tables with constraints, indexes, and foreign keys
- **Connection Pooling** - Configured for Supabase transaction mode compatibility
- **Environment Configuration** - Secure .env setup with Pydantic Settings
- **Database Setup Scripts** - Automated table creation with constraint validation

### Development Experience
- **Test Automation** - Complete end-to-end testing with colored output and statistics
- **Development Scripts** - Quick setup and testing utilities for developers
- **Clean Project Structure** - Organized codebase following Python best practices
- **Type Safety** - Full type hints coverage for enhanced IDE support

### Performance & Reliability
- **Async/Await** - Non-blocking operations for high performance
- **Error Handling** - Comprehensive error management with proper HTTP status codes
- **Email Validation** - Robust input validation with regex patterns
- **Case-Insensitive Enums** - Flexible enum handling for better UX

### API Endpoints
- `GET /health/` - Service health monitoring
- `POST /api/v1/users/` - User creation with validation
- `GET /api/v1/users/{id}` - User profile retrieval
- `PUT /api/v1/users/{id}` - User profile updates
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative documentation interface

### Quality Metrics
- **100% Test Success Rate** - All automated tests passing
- **Type Coverage** - Full type hints implementation
- **Code Quality** - Clean architecture principles applied
- **Performance** - Optimized database queries and async operations

## [0.1.0] - 2025-09-04

### Added
- Documentazione strategica completa (Documentazione Generale.md)
- Architettura cloud-native con Supabase + N8N Cloud (architettura.md)
- Strategia microservizi Python con DDD patterns (microservizi_python.md)
- Strategia mobile Flutter cross-platform (flutter.md)
- ROI analysis e business positioning
- Database schema con segregation e real-time sync
- MCP (Model Context Protocol) integration per AI coaching
- CI/CD pipeline per Render deployment
- Project structure templates per microservizi

### Architecture Decisions
- **Cloud-Native Strategy**: Migrazione da self-hosted a Supabase Cloud + N8N Cloud
- **Database Segregation**: Un database Supabase per microservizio
- **Real-time Sync**: WebSocket + Supabase subscriptions per cross-device sync
- **AI Integration**: N8N workflow orchestration + MCP servers
- **Mobile Strategy**: Flutter production-ready per launch simultaneo iOS + Android

### Business Impact
- Investment analysis: €247,273 totale con ROI 320% a 24 mesi
- Time-to-market: 6 mesi vs 12-18 mesi competitors
- Global scalability: Supabase edge network per performance mondiale
- Development efficiency: 40% riduzione costi vs approccio tradizionale

## [0.0.1] - 2025-09-01

### Added
- Repository iniziale
- Struttura base microservizi
- Setup Docker e containerization
- Scripts di utility per development
- Base testing framework

### Infrastructure
- Docker compose per development locale
- PostgreSQL database setup
- Redis per caching
- Base CI/CD con GitHub Actions

---

## Formato Changelog

### Tipi di Cambiamenti
- **Added** per nuove funzionalità
- **Changed** per cambiamenti a funzionalità esistenti  
- **Deprecated** per funzionalità che saranno rimosse
- **Removed** per funzionalità rimosse
- **Fixed** per bug fix
- **Security** per vulnerabilità e patch di sicurezza

### Categorie Principali
- **Architecture Decisions** - Decisioni architetturali significative
- **Business Impact** - Impatto business e ROI
- **Infrastructure** - Cambiamenti infrastruttura e deployment
- **Documentation** - Aggiornamenti documentazione maggiori
- **API Changes** - Breaking changes alle API
- **Database** - Schema changes e migrazioni
- **Security** - Security updates e vulnerability fixes
