# 📝 NutriFit Platform - Changelog

Questo file documenta tutti i cambiamenti significativi al progetto NutriFit Platform.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v1.7.0] - 2025-01-15 - UUID Validation System Fixed

### 🔧 UUID Cross-Service Consistency
- **Task 2.4 Progress**: Fixed UUID validation inconsistencies across microservices  
- **Schema Alignment**: Updated `calorie-balance` schemas from UUID4 → UUID for consistency with user-management
- **Database Mapping**: Fixed repository functions to preserve UUID objects vs string conversion
- **Pydantic Validation**: Resolved "UUID version 4 expected" errors in API responses

### 🛠️ Technical Improvements
- **Schemas Updated**: `MetabolicProfileResponse` and related models now use generic UUID type
- **Repository Fixes**: `profile_model_to_entity` mapping functions preserve UUID object types  
- **Cross-Service Standards**: Aligned UUID handling patterns with user-management service architecture
- **Test Compatibility**: Improved test UUID validation while maintaining backward compatibility

### 📊 Performance Impact
- **Test Success Rate**: Improved from 68.8% to **75%** (12/16 tests passing)
- **API Validation**: Metabolic profile endpoints showing improved validation success
- **Error Reduction**: Eliminated UUID version validation conflicts in responses

### 🎯 Mobile Client Preparation
- **Documentation**: Enhanced technical specifications for Flutter development  
- **UUID Standards**: Established cross-service UUID handling guidelines
- **API Consistency**: Standardized validation patterns for mobile integration

## [v1.6.0] - 2025-09-14 - Calorie Balance Service: Events API Fixed

### 🔥 Events API Validation Complete
- **Task 2.3 Resolved**: Fixed triple inconsistency in `event_source` enum values
- **Database Schema Alignment**: Added missing enum values (`fitness_tracker`, `smart_scale`, `nutrition_scan`)
- **API Endpoints Operational**: All Events API endpoints now return 200/201 instead of 500 errors
- **Test Success Rate**: Improved from 56% to **68.8%** (11/16 tests passing)

### 🛠️ Database Schema Updates
- **SQL Migration**: `007_fix_event_source_enum.sql` script created and executed
- **Enum Values Added**: `fitness_tracker`, `smart_scale`, `nutrition_scan` added to `calorie_balance.event_source`
- **Legacy Mapping**: `app_tracking` → `manual`, `ai_estimation` → `nutrition_scan`  
- **PostgreSQL Constraints**: Proper handling of enum value commits for safe migration

### ✅ API Fixes Verified
- **POST `/api/v1/calorie-event/burned`** with `source: "fitness_tracker"` → ✅ 200 OK
- **POST `/api/v1/calorie-event/weight`** with `source: "smart_scale"` → ✅ 200 OK
- **POST `/api/v1/calorie-event/consumed`** with `source: "nutrition_scan"` → ✅ 200 OK
- **Enum Validation**: All 6 Python enum values now supported in database

### 🎯 Architecture Improvements  
- **Triple Consistency**: Resolved conflicts between documentation, database SQL, and Python code
- **Source of Truth**: Python code chosen as authoritative enum definition (most complete)
- **Pattern Alignment**: Enum values now follow architectural DataSource pattern from `docs/microservizi_python.md`

### 📊 Progress Tracking
- **FASE 1**: ✅ Complete (4/4 tasks) - Critical schema fixes
- **FASE 2**: 🟡 75% Complete (3/4 tasks) - API implementation fixes  
- **Remaining**: Task 2.4 (Events Timeline), Tasks 3.x (Metabolic), Tasks 4.x (Final polish)

## [v1.5.0] - 2025-09-11 - Production Deployment & CI/CD Pipeline Complete

### 🚀 Production Deployment Success
- **Live Service**: https://nutrifit-user-management.onrender.com deployed and operational
- **100% Production Test Success**: All 22 comprehensive tests pass in production environment
- **Render Auto-Deploy**: Repository-based deployment with buildFilter configuration
- **Environment Variables**: Production secrets configured via Render dashboard (manual entry)
- **Database Connection**: Supabase production database fully operational

### 🔄 CI/CD Pipeline Implementation
- **GitHub Actions Workflow**: Simplified test-only pipeline (removed Container Registry complexity)
- **Repository-Based Deployment**: Direct repository sync instead of Container Registry approach
- **Build Filter Configuration**: Selective deployment triggers for `services/user-management/**` and `render.yaml`
- **Automated Releases**: GitHub releases with proper versioning and changelog generation
- **Environment Profiles**: Support for `local` and `prod` testing profiles

### 🛠️ Infrastructure Improvements
- **render.yaml**: Switched from Container Registry to repository-based configuration
- **Docker Multi-stage Build**: Production-ready containers with Poetry and Python 3.11
- **Secret Management**: Environment variables configured directly in Render dashboard
- **Auto-Deploy**: Enabled with proper buildFilter for selective deployments

### 🧪 Enhanced Testing Suite
- **test_comprehensive.py**: Added environment profile support (`local`/`prod`)
- **Production Testing**: Comprehensive validation against live production endpoints
- **Performance Metrics**: Production tests complete in ~17 seconds vs ~8 seconds local
- **API Documentation**: Swagger UI available in development (disabled in production for security)

### 🔧 Technical Configuration
- **Environment Variable Corrections**: Fixed `SUPABASE_SERVICE_KEY` and `SECRET_KEY` naming
- **Poetry Integration**: All testing and development commands use Poetry virtual environment
- **GitHub Actions Simplification**: Removed unnecessary Container Registry push steps
- **Deployment Strategy**: Direct repository monitoring with automatic builds on Render

### 📊 Production Metrics
- **Service Health**: All health checks passing (`/health`, `/health/ready`, `/health/live`)
- **API Response Times**: Average response times within acceptable limits
- **Database Performance**: Supabase queries executing efficiently in production
- **Test Coverage**: 22/22 tests passing (100% success rate) in both local and production

### 🎯 Quality Assurance
- **Zero Failed Tests**: Complete test suite passes in production environment
- **Database Integrity**: All CRUD operations working correctly with real production data
- **Security Compliance**: Swagger documentation properly disabled in production
- **Error Handling**: Proper HTTP status codes and error responses validated

## [v1.4.0] - 2025-09-10 - User Management Service Production Ready

### 🎯 Major Achievements - Complete Service Lifecycle
- **100% Test Success Rate** - All 22 comprehensive tests now pass (upgraded from 86% to 100%)
- **Service Lifecycle Management** - Complete start/stop/status/restart functionality with PID management
- **Production-Ready API** - All CRUD operations working with proper database permissions
- **SQL Grants System** - Reusable template system for all future microservices database permissions
- **Data Reset Automation** - Robust test suite with automatic data cleanup between test runs

### 🔧 Critical Fixes
- **start-dev.sh Complete Rewrite** - Fixed corrupted script with proper shell syntax and health check patterns
- **Supabase Permission Issues Resolved** - Fixed 403/42501 permission denied errors for write operations
- **Health Check Pattern Matching** - Corrected 'healthy' vs 'ok' pattern matching for Uvicorn responses
- **Service-Role Key Separation** - Implemented secure dual-key strategy (service-role for startup, anon for runtime)
- **Database Write Permissions** - Added INSERT, UPDATE, DELETE grants for anon/authenticated roles

### 📁 New Infrastructure Files
- **config/supabase/grants_template.sql** - Universal SQL grants template for all microservices
- **scripts/generate-grants-script.sh** - Automated grants generation with schema name substitution
- **services/user-management/start-dev.sh** - Production-quality service lifecycle management script
- **services/user-management/stop-dev.sh** - Clean service shutdown with PID cleanup
- **services/user-management/sql/004_grants.sql** - Working database grants (replaces previous versions)
- **services/user-management/sql/check_current_permissions.sql** - Database permissions verification queries

### 🧪 Enhanced Testing Infrastructure
- **test_comprehensive.py Enhanced** - Added automatic test data reset functionality
- **ORIGINAL_DATA Constants** - Defined baseline test data values for consistent reset
- **Reset Function** - `reset_test_data()` method ensures clean state between test runs
- **Complete API Coverage** - All 22 endpoints tested including repositories, health checks, and validation

### 🚀 Production Readiness Features
- **Health Check Endpoints** - `/health`, `/health/ready`, `/health/live` fully operational
- **Service Discovery** - Proper service status detection and health monitoring
- **Error Handling** - Comprehensive error logging and correlation ID tracking
- **Database Connection Management** - Dual Supabase client strategy for security and functionality
- **API Endpoint Coverage** - Complete CRUD operations for users, profiles, privacy, contexts, and actions

### 🗂️ File Organization Cleanup
- **Removed Duplicate Files** - Eliminated `003_public_schema_fix.sql` (empty refuso file)
- **SQL File Sequencing** - Clean numbered sequence: 000→001→002→003→004 grants progression
- **Template Integration** - All SQL grants now generated from central template system

### 🔄 Template System for Future Microservices
- **Versionable SQL Grants** - Template with {{SCHEMA_NAME}} placeholder for any microservice
- **Automation Script** - One-command generation: `./scripts/generate-grants-script.sh service-name`
- **Manual Execution Workflow** - Clear instructions for Supabase Dashboard SQL Editor execution
- **Reusable Pattern** - Established pattern for future microservice database permission management

### 📊 Test Results Improvement
**Before**: 19/22 tests passing (86% success rate)  
**After**: 22/22 tests passing (100% success rate)

**Fixed Tests**:
- ✅ User Profile Repository - Get by User ID
- ✅ Get User Profile API
- ✅ Update User Profile
- ✅ Update Privacy Settings  
- ✅ Record User Login

### 💡 Technical Innovations
- **Health Check Pattern Detection** - Smart pattern matching for Uvicorn JSON health responses
- **Service Role Separation** - Security-first approach with minimal privilege principle
- **Test Data Lifecycle** - Automated reset ensures test reliability and repeatability
- **SQL Template Engine** - Simple but effective placeholder substitution for schema-agnostic SQL
- **Error Correlation** - Complete request tracking with correlation IDs for debugging

### 🔧 Breaking Changes
- **start-dev.sh Completely Rewritten** - Previous version was corrupted, new version has different API
- **SQL Grants Numbering** - New 004_grants.sql supersedes previous grant files
- **Test Execution** - Now requires Poetry environment: `poetry run python test_comprehensive.py`

### 🎯 Service Status
**User Management Service**: ✅ Production Ready
- All API endpoints operational
- Database permissions correctly configured  
- Service lifecycle management working
- 100% test coverage with automated data reset
- Health monitoring and error tracking implemented

### 🚀 GraphQL Implementation Complete - v1.3.0 (2025-09-09)
- **Full GraphQL API Layer** - Implementazione completa layer GraphQL per User Management Service
- **Apollo Federation 2.0 Ready** - Schema federato con @key directives per architettura microservizi
- **Dual API Architecture** - Supporto simultaneo REST (13 endpoints) + GraphQL (4+ queries)
- **Interactive GraphiQL Playground** - Interfaccia interattiva disponibile su `/graphql` endpoint
- **Comprehensive Testing** - Suite test completa per entrambe le API con 100% pass rate
- **Repository Pattern Integration** - GraphQL resolvers integrati con pattern repository esistente
- **Federation Features** - Entity resolution, service SDL, cross-service query capabilities
- **Template Updates Complete** - Template microservice aggiornato con struttura GraphQL completa
- **Production Ready** - Type safety, error handling, performance validation completati

### 📚 Documentation Cleanup - v1.2.1 (2025-09-07)
- **Removed redundant instructions.md** - Eliminato file duplicato nella root del progetto
- **Centralized documentation references** - Tutti i riferimenti ora puntano a `.github/instructions/instructions.md`
- **User Management Service integration** - Aggiornata tutta la documentazione per includere il 6° microservizio
- **Fixed circular references** - Risolti link circolari e riferimenti obsoleti nei documenti
- **Architecture consistency** - Allineamento completo tra README, instructions, e documentazione microservizi
- **Database documentation complete** - Creata documentazione completa per User Management Service database

### 🚀 Added - v1.2.0 Event-Driven Architecture (2025-09-05)
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
