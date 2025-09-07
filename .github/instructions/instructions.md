# 🏋️ NutriFit Platform - Project Hub

## 🎯 Quick Start

**NutriFit** è una piattaforma fitness-nutrizionale cloud-native con architettura microservizi, AI coaching avanzato, e mobile app cross-platform. La piattaforma combina precision tracking, real-time sync, e conversational AI per offrire un'esperienza utente superiore nel mercato nutrition tech.

### ⚡ Architettura Overview
- **6 Microservizi** FastAPI con database segregation + User Management Service centralizzato
- **Flutter Mobile App** cross-platform iOS + Android 
- **Supabase Cloud** per database managed e real-time sync
- **N8N Cloud** per AI workflow orchestration
- **Model Context Protocol (MCP)** per AI integration avanzata

## 📚 Documentazione Completa
### 📚 Documentazione microservizi
Per ogni microservizio, consulta la documentazione specifica nella cartella:

- **🚨 User Management Service**: [docs/databases/user-management-db.md](../../docs/databases/user-management-db.md) - **CORE AUTH** - Autenticazione centralizzata, JWT, OAuth
- **Calorie Balance Service**: [docs/databases/calorie-balance-db.md](../../docs/databases/calorie-balance-db.md) - Metabolismo energetico, BMR, obiettivi
- **Meal Tracking Service**: [docs/databases/meal-tracking-db.md](../../docs/databases/meal-tracking-db.md) - AI food recognition, nutrition data
- **Health Monitor Service**: [docs/databases/health-monitor-db.md](../../docs/databases/health-monitor-db.md) - HealthKit sync, wearables integration
- **Notifications Service**: [docs/databases/notifications-db.md](../../docs/databases/notifications-db.md) - Multi-channel messaging, FCM
- **AI Coach Service**: [docs/databases/ai-coach-db.md](../../docs/databases/ai-coach-db.md) - Conversational AI, RAG, coaching

#### Checklist per la documentazione microservizi
- [ ] Creare la documentazione di dettaglio in `docs/databases/<nome-microservizio>-db.md`
- [ ] Aggiornare il README del microservizio con link alla documentazione database
- [ ] Aggiornare questo file con il riferimento al nuovo microservizio
- [ ] Verificare la coerenza tra datamodel applicativo e schema SQL
- [ ] Aggiornare la documentazione generale se necessario (architettura, microservizi_python)
- [ ] Versionare tutte le modifiche (commit & push)
- [ ] Aggiornare l'issue tracker segnalando la chiusura della procedura

### 🏗️ Architettura & Design
- **[Architettura Cloud-Native](../../docs/architettura.md)** - Schema microservizi, database design, diagrammi Mermaid
- **[Microservizi Python](../../docs/microservizi_python.md)** - FastAPI, DDD patterns, tech stack details
- **[Mobile Flutter Strategy](../../docs/flutter.md)** - Cross-platform development, deployment pipeline

### 📋 Strategic Planning  
- **[Documentazione Generale](../../docs/Documentazione%20Generale.md)** - Business analysis, ROI projections, competitive strategy

### 🚀 Development & Deployment
- **[Development Workflow](../../docs/DEVELOPMENT_WORKFLOW.md)** - Git flow, coding standards, CI/CD pipeline
- **[Deployment Guide](../../docs/DEPLOYMENT.md)** - Render deployment, environment setup, monitoring
- **[Testing Guide](../../docs/TESTING_GUIDE.md)** - Unit tests, integration tests, coverage requirements *(da creare)*
- **[API Documentation](../../docs/API_DOCUMENTATION.md)** - REST endpoints, GraphQL schema, integration guides *(da creare)*

### 📝 Project Management
- **[Changelog](../../CHANGELOG.md)** - Project history, releases, major updates

## 💻 Quick Commands

### Development Setup
```bash
# Clone repository
git clone https://github.com/giamma80/gymbro-platform.git
cd gymbro-platform

# Setup development environment
make setup-dev

# Start all services
make dev-up
```

### Common Tasks
```bash
# Create new microservice
./scripts/create-service.sh my-service bounded-context

# Run tests
make test-all

# Deploy to staging
make deploy-staging
```

## 🧑‍💻 Developer Resources

### Quick Reference
- **[Project Structure](../../docs/microservizi_python.md#project-structure)** - Microservice templates, folder organization
- **[Database Schema](../../docs/architettura.md#database-design)** - PostgreSQL, Supabase, migrations
- **[Coding Standards](../../docs/DEVELOPMENT_WORKFLOW.md#python-coding-standards)** - Python, FastAPI, DDD patterns

### Development Tools
- **Poetry** per dependency management
- **FastAPI** per REST APIs
- **Alembic** per database migrations  
- **pytest** per testing con coverage minimo 80%
- **Docker** per containerization

## 🚀 Deployment & Operations

### Environment Links
- **Production**: [Deploy on Render](../../docs/DEPLOYMENT.md#render-com-deployment)
- **Staging**: [Environment Setup](../../docs/DEPLOYMENT.md#environment-strategy)
- **Local Dev**: [Docker Setup tramite architettura](../../docs/architettura.md#setup-locale)

### Monitoring & Health
```bash
# Health check all services
./scripts/health-check.sh

# View logs
make logs-follow SERVICE=calorie-balance

# Performance monitoring
make monitoring-dashboard
```

## 📋 Microservice Development Checklist

### 🏗️ **Architecture & Structure**
- [ ] **Service Directory**: Creare cartella `services/{service-name}/`
- [ ] **Domain Definition**: Definire bounded context e responsabilità del servizio
- [ ] **Clean Architecture**: Struttura `app/{core,domain,application,infrastructure,api}/`
- [ ] **Dependency Injection**: Container per IoC pattern
- [ ] **Error Handling**: Exception hierarchy specifica del dominio

### 📊 **Database & Persistence**
- [ ] **Database Schema**: Progettare schema dedicato (`docs/databases/{service-name}-db.md`)
- [ ] **Entity Models**: Domain entities con business logic
- [ ] **Repository Pattern**: Astrazioni per data access
- [ ] **Migrations**: Script di creazione tabelle (`create_tables_direct.py`)
- [ ] **Performance Indexes**: Indici ottimizzati per query patterns
- [ ] **Constraints & Validation**: Business rules a livello database
- [ ] **Event Sourcing**: Se applicabile, progettare event store

### 🔌 **API Design**
- [ ] **REST Endpoints**: Design consistente con HTTP semantics
- [ ] **Request/Response Models**: Pydantic schemas per validation
- [ ] **OpenAPI Documentation**: Auto-generated docs con esempi
- [ ] **Error Responses**: Standard error format con status codes
- [ ] **Authentication**: JWT integration con Supabase Auth
- [ ] **Rate Limiting**: Protection da abuse
- [ ] **API Versioning**: Strategy per backward compatibility

### 📱 **Mobile & Integration**
- [ ] **High-Frequency Support**: Design per raccolta dati mobile
- [ ] **Batch APIs**: Endpoints per sincronizzazione offline
- [ ] **Real-time Updates**: WebSocket o Server-Sent Events
- [ ] **External Service Integration**: Mapping con altri microservizi
- [ ] **Event Publishing**: Integration con message broker (N8N workflows)

### 🧪 **Testing Strategy**
- [ ] **Unit Tests**: ≥ 80% coverage su business logic
- [ ] **Integration Tests**: Database e external services
- [ ] **API Tests**: Contract testing per tutti gli endpoints
- [ ] **Performance Tests**: Load testing per scenari critici
- [ ] **Mock Services**: Test isolation con dependency mocking

### 📚 **Documentation**
- [ ] **README.md**: Overview, setup, API reference
- [ ] **API Roadmap**: Development status tracking (`API-roadmap.md`)
- [ ] **Database Documentation**: Schema, queries, performance (`docs/databases/`)
- [ ] **Architecture Diagrams**: Mermaid diagrams per data flow
- [ ] **Integration Guide**: Como altri servizi usano questo microservizio

### 🚀 **Deployment & Operations**
- [ ] **Docker Support**: Dockerfile e docker-compose configuration
- [ ] **Health Checks**: `/health`, `/health/ready`, `/health/live` endpoints  
- [ ] **Monitoring**: Structured logging con correlation IDs
- [ ] **Environment Config**: 12-factor app principles
- [ ] **CI/CD Pipeline**: GitHub Actions per testing e deployment
- [ ] **Production Readiness**: Render.com deployment configuration

### 🔒 **Security & Compliance**
- [ ] **Input Validation**: Sanitization di tutti gli input
- [ ] **Row Level Security**: Supabase RLS policies
- [ ] **Data Privacy**: GDPR compliance per dati sensibili
- [ ] **Secret Management**: Environment variables per API keys
- [ ] **Audit Logging**: Tracciabilità delle operazioni critiche

### 🎯 **Domain-Specific Patterns**
- [ ] **Event-Driven Architecture**: Se il servizio genera eventi
- [ ] **CQRS Pattern**: Separazione command/query se necessario
- [ ] **Temporal Analytics**: Views aggregate per timeline analysis
- [ ] **Mobile Optimization**: Design per network efficiency
- [ ] **AI Integration Points**: Preparazione per machine learning features

---

### ✅ **User Management Architectural Decision - RESOLVED**

**✅ DECISION IMPLEMENTED**: User Management Service centralizzato implementato con successo.

#### ✅ **Centralized User Service** - IMPLEMENTED
- ✅ Single source of truth per user data (**DONE**)
- ✅ Consistent authentication across services (**ARCHITECTURE READY**)
- ✅ Simplified GDPR compliance (**FRAMEWORK COMPLETE**)
- ✅ Service dependency properly designed (**INTEGRATION PATTERNS DEFINED**)

#### ❌ **Replicated User Tables** - DEPRECATED
- ❌ Service autonomy (sacrificed for consistency)
- ❌ Data inconsistency risk (**ELIMINATED**)
- ❌ Complex user updates (**CENTRALIZED**)
- ❌ GDPR compliance complexity (**SIMPLIFIED**)

**✅ DECISION COMPLETED**: User Management Service architecture e implementation plan complete.
**🚀 RESULT**: All microservices unblocked for development with centralized authentication.

## 🤝 Contributing

### Pull Request Process
1. Leggi [Development Workflow](../../docs/DEVELOPMENT_WORKFLOW.md#git-workflow)
2. Crea feature branch da `main`
3. Implementa con test coverage ≥ 80%
4. Valida con `make quality-check`
5. Crea PR con template standard

### Code Review Guidelines
- Domain-Driven Design compliance
- API contract consistency  
- Performance considerations
- Security best practices
- Documentation updates

## 📞 Support & Community

### Getting Help
- **Documentazione**: Controlla prima la [docs folder](../../docs/)
- **Issues**: Apri GitHub issue con template appropriato
- **Architecture Questions**: Consulta [Documentazione Generale](../../docs/Documentazione%20Generale.md)

### Project Status
- **Current Phase**: MVP Development (Mesi 1-4)
- **Next Milestone**: AI Coach Integration (Mese 5)
- **Production Target**: Q2 2025

---

**🎯 Ready to contribute?** Inizia dalla [Documentazione Generale](../../docs/Documentazione%20Generale.md) per il context completo, poi segui il [Development Workflow](../../docs/DEVELOPMENT_WORKFLOW.md) per setup e best practices.
