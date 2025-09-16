# 🏋️ NutriFit Platform

> **Piattaforma fitness-nutrizionale con AI per il bilanciamento calorico intelligente**

## 🎯 Overview

**NutriFit** combina microservizi Python 3.11 + FastAPI con mobile app Flutter per un tracking nutrizionale preciso e intelligente.

### ✨ Features Core

- 🌐 **GraphQL Federation** - Apollo Gateway v2.5 con schema unificato per tutti i microservizi
- 🔥 **Bilanciamento Calorico AI** - Calcoli precision-aware con accuratezza ±20g
- 🍎 **Food Recognition** - Riconoscimento alimenti tramite GPT-4V + OpenFoodFacts
- 📊 **Health Integration** - Sync HealthKit/Health Connect automatico
- 📱 **Cross-Platform** - Flutter iOS + Android simultaneo

### 🏗️ Architettura

**GraphQL Federation**: Apollo Gateway v2.5 con schema composition automatica
- **Gateway**: https://apollo-gateway.onrender.com/graphql - Unified API endpoint
- **Apollo Studio**: Explorer integrato per testing e documentazione API

**Backend**: 5 microservizi Python (FastAPI + PostgreSQL/Supabase)
1. **User Management** - Auth, profili, GDPR compliance
2. **Calorie Balance** - Metabolismo e bilanciamento energetico  
3. **Meal Tracking** - Pasti e riconoscimento food
4. **Health Monitor** - Sync dati salute e quality scoring
5. **Notifications** - Notifiche smart e coaching

**Frontend**: Flutter cross-platform con GraphQL client integration

### 📚 Docs Principali
- **[🏗️ Architettura](docs/architettura.md)** - Microservizi, sequence diagrams, pattern
- **[🐍 Microservizi Python](docs/microservizi_python.md)** - FastAPI patterns, DDD, tech stack dettagliato
- **[📋 Docs Generale](docs/Documentazione%20Generale.md)** - Business strategy, use cases
- **[🗄️ Database](docs/databases/)** - Schema, ER diagrams, migrations

### 🎯 Development
- **[🌐 GraphQL Federation](services/apollo-gateway/)** - Apollo Gateway v2.5, schema composition
- **[User Management](docs/databases/user-management-db.md)** - Auth schema, profili
- **[Calorie Balance](docs/databases/calorie-balance-db.md)** - Eventi, analytics temporali
- **[API Reference](https://apollo-gateway.onrender.com/graphql)** - GraphQL unified endpoint ✨

### 🚀 GraphQL Federation
**Production Endpoint**: https://apollo-gateway.onrender.com/graphql
- ✅ **Schema Unificato** - Federation automatica di tutti i microservizi
- ✅ **Apollo Studio** - Explorer integrato per development e testing
- ✅ **Service Discovery** - Health checks automatici e composition dinamica
- ✅ **Profile Development** - Workflow locale/produzione con --profile flag

### 🏗️ Microservizi Details
Ogni microservizio segue **Domain-Driven Design** con FastAPI + Repository pattern:
- **[📋 Python Microservizi Guide](docs/microservizi_python.md)** - Architettura completa, patterns, esempi
- **[🔧 Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)** - Git flow, testing, deployment

## 🚀 Status Progetto

### Development Progress
- **Apollo Gateway**: 🟢 **PRODUCTION** - [Live Federation](https://apollo-gateway.onrender.com/graphql) (GraphQL unified API) 🚀
- **User Management**: 🟢 **PRODUCTION** - [Live Service](https://nutrifit-user-management.onrender.com) (100% tests)
- **Calorie Balance**: 🟢 **PRODUCTION READY** - [Live Service](https://nutrifit-calorie-balance.onrender.com) (100% test success) 🎉
- **Meal Tracking**: ⏳ **PLANNED** - Food recognition + AI integration
- **Health Monitor**: ⏳ **PLANNED** - HealthKit/Health Connect sync  
- **Mobile App**: ⏳ **PLANNED** - Flutter cross-platform with GraphQL client

### Technical Achievements
- ✅ **GraphQL Federation** - Apollo Gateway v2.5 production deployment
- ✅ **Schema Composition** - Automatic federation of distributed microservices
- ✅ **Apollo Studio Integration** - Production API explorer and documentation
- ✅ **UUID cross-service consistency** established
- ✅ **Parameter Passing pattern** implemented
- ✅ **Profile-based development** workflow (local/prod)
- ✅ **Background process management** with PID and logging

### Next Milestones
- **Q4 2024**: Calorie Balance completion (90%+ tests), Mobile app MVP
- **Q1 2025**: Health integration, AI coaching features
- **Q2 2025**: Production launch iOS + Android

### 💻 Comandi di Sviluppo

```bash
# Clone repository
git clone https://github.com/giamma80/gymbro-platform.git
cd gymbro-platform

# Setup ambiente completo
make setup-dev

# Start GraphQL Federation (Production)
cd services/apollo-gateway
./start-dev.sh start --profile prod  # Federation con servizi remoti

# Start Local Development Environment
cd services/user-management && ./start-dev.sh start &
cd services/calorie-balance && ./start-dev.sh start &
cd services/apollo-gateway && ./start-dev.sh start --profile local

# GraphQL Explorer Access
open https://apollo-gateway.onrender.com/graphql  # Production
open http://localhost:4000/graphql               # Local

# Service Management
./start-dev.sh status        # Check service status
./start-dev.sh logs         # View service logs
./start-dev.sh restart      # Restart service
./start-dev.sh stop         # Stop service

# Run tests
make test-all

# Deploy to production (auto-deploy configured)
git push origin main
```

## 🚀 Project Status

### Current Phase: Foundation Development (Q3 2025)
- ✅ Architettura cloud-native definita e documentata
- ✅ Tech stack e patterns finalizzati (FastAPI + PostgreSQL + Docker)
- ✅ Documentazione strategica completa
- ✅ User Management Service - Production ready (100% test success)
- 🟡 Calorie Balance Service - 68.8% test success (in progress)
- � MVP microservizi core development
- ⏳ Flutter mobile app foundation (planned)

### Development Progress
- **User Management**: 🟢 **PRODUCTION DEPLOYED** - https://nutrifit-user-management.onrender.com
- **Calorie Balance**: 🟡 **ACTIVE DEVELOPMENT** - Events API fixed, Goals API complete
- **Meal Tracking**: ⏳ Planning phase
- **Health Monitor**: ⏳ Planning phase  
- **Notifications**: ⏳ Planning phase
- **AI Nutrition Coach**: ⏳ Planning phase

### Next Milestones
- **Q4 2025**: Core microservizi MVP completion
- **Q1 2026**: AI nutrition coach integration + mobile POC
- **Q2 2026**: Production launch iOS + Android
- **Q3 2026**: Enterprise features e scaling

## 🤝 Contributing

1. Leggi [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md) per best practices
2. Consulta [GitHub Instructions](.github/instructions/instructions.md) per setup completo
3. Crea feature branch da `main`
4. Implementa con test coverage ≥ 80%
5. Crea PR seguendo i template standard

## 📄 License & Support

- **License**: MIT License
- **Architecture**: Cloud-native microservizi con enterprise patterns
- **Deployment**: Render.com con CI/CD automatizzato
- **Documentation**: Completa in [docs/](docs/) folder

---

**🏗️ Enterprise-ready architecture** | **🤖 AI-powered nutrition** | **📱 Cross-platform mobile**

- **v1.0 (Backup)**: Implementazione microservizi completa → `backup-v1-microservices-20250903`  
- **v2.0 (Corrente)**: **NutriFit Platform** - Architettura enterprise con AI e precision nutrition

### 🔄 Come Recuperare la Versione Precedente

```bash
# Vedi tutti i branch di backup
git branch -a

# Cambia alla versione precedente
git checkout backup-v1-microservices-20250903

# Oppure vedi il tag
git checkout v1.0-microservices-backup
```

## 🎯 Roadmap di Sviluppo

### Phase 1: Foundation (In Corso)
- ✅ Architettura definita e documentata
- ✅ GitHub workflows e templates configurati  
- ✅ Makefile automation e Docker setup
- 🔄 Template microservizi e DDD patterns
- 🔄 Database schema e migrations

### Phase 2: Core Services
- 🔄 Calorie Balance Service (metabolismo base)
- 🔄 Meal Tracking Service (OpenFoodFacts integration)
- 🔄 Health Monitor Service (HealthKit sync)

### Phase 3: AI & Mobile  
- 🔄 AI Nutrition Coach (RAG system + GPT-4V)
- 🔄 Flutter mobile app (cross-platform POC)
- 🔄 Notifications Service (smart alerts)

### Phase 4: Production
- 🔄 Performance optimization e load testing
- 🔄 Security audit e penetration testing  
- 🔄 Render deployment e monitoring
- 🔄 User acceptance testing

## 🛠️ Strumenti e Utilities

### 📁 Risorse Disponibili

- **[`scripts/`](./scripts/)** - Utilities di sviluppo e manutenzione
- **[`docs/`](./docs/)** - Documentazione architetturale completa
- **[`.github/`](.github/)** - Templates, workflows e automazioni

### 🔧 Makefile Commands

```bash
# Setup completo ambiente di sviluppo
make setup

# Avvio ambiente locale con database  
make dev

# Creazione nuovo microservice da template
make setup-service SERVICE=nome-servizio  

# Testing completo con coverage
make test

# Quality check (lint + format + security)
make quick-test

# Deploy staging/production
make deploy-staging
make deploy-production

# Monitoring e health checks
make health-check
make logs
```

---

## 📞 Support & Documentation

- 📖 **[GitHub Instructions Complete](.github/instructions/instructions.md)** - Guida sviluppatori
- 📚 **[Architecture Docs](docs/)** - Documentazione tecnica dettagliata  
- 🐛 **[Issue Templates](.github/ISSUE_TEMPLATE/)** - Bug report e feature request
- 🔄 **[PR Template](.github/pull_request_template.md)** - Pull request con quality gates

**Ultimo Backup v1.0:** 3 settembre 2025  
**Stato Corrente:** � NutriFit Platform v2.0 - Enterprise Architecture Ready
