# 🏋️ NutriFit Platform

> **Piattaforma fitness-nutrizionale enterprise con AI per il bilanciamento calorico intelligente e tracking nutrizionale precision-aware**

## 🎯 Overview del Progetto

**NutriFit** è una piattaforma completa per il monitoraggio della salute e nutrizione, progettata per il mercato italiano con focus su precisione e integrazione AI. Combina un'architettura a microservizi Python con una mobile app Flutter cross-platform.

### ✨ Caratteristiche Principali

- 🔥 **Bilanciamento Calorico Intelligente** - Calcoli precision-aware con accuratezza ±20g
- 🍎 **Food Recognition AI** - Riconoscimento alimenti tramite GPT-4V e OpenFoodFacts
- 📊 **Health Data Integration** - Sync automatico con HealthKit/Health Connect
- 🤖 **AI Nutrition Coach** - Coaching personalizzato via RAG system
- 📱 **Mobile Cross-Platform** - App Flutter per iOS e Android simultaneo
- 🏗️ **Architettura Enterprise** - 5 microservizi Python con Domain-Driven Design

### 🏗️ Architettura Tecnica

**Backend Microservizi (Python 3.11 + FastAPI)**:
1. **Calorie Balance Service** - Metabolismo energetico e bilanciamento
2. **Meal Tracking Service** - Tracking pasti e riconoscimento food  
3. **Health Monitor Service** - Sync HealthKit e quality scoring
4. **Notifications Service** - Notifiche smart e coaching prompts
5. **AI Nutrition Coach Service** - Sistema RAG e AI conversazionale

**Frontend**: Flutter cross-platform (POC per validazione simultanea iOS/Android)

**Infrastructure**: Docker containerization + Render deployment + PostgreSQL + Redis

## 📖 Developer Instructions

> 🚨 **IMPORTANTE**: Prima di iniziare lo sviluppo, leggi le **[GitHub Instructions Complete](.github/instructions/instructions.md)**

Le instructions contengono:
- 🏗️ **Architecture Overview** - Struttura microservizi e patterns DDD
- 💻 **Development Guidelines** - Standards, templates, best practices  
- 🐳 **Docker Guidelines** - Containerizzazione e deployment
- 🚀 **Render Deployment** - Procedures production e staging
- 🧪 **Testing Strategy** - Unit, integration, performance tests
- 📊 **Quality Gates** - Coverage 80%+ e code review checklist

### Quick Start per Sviluppatori
```bash
# Setup ambiente completo
make setup && make dev

# Crea nuovo microservice  
make setup-service SERVICE=nome-servizio

# Quality check prima commit
make quick-test
```

## 🚀 Restart Progetto

Questo progetto è stato **completamente riavviato** per un approccio architetturale migliore.

## � Storia del Progetto

### 📚 Versioni e Migration

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
