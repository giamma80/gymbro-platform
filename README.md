# 🏋️ GymBro### 🎉 **v1.2.4 MAJOR MILESTONE: Apollo Federation 100% Operational!**

🌐 **APOLLO FEDERATION COMPLETAMENTE OPERATIVO** - GraphQL unificato su tutti i microservizi:
- ✅ **Complete Schema Federation**: UserProfile, UserStats, UserPreferences tutte federate
- ✅ **DateTime Fields Working**: createdAt, updatedAt, dateOfBirth tutti funzionanti  
- ✅ **Advanced Queries**: `{ me { id email firstName lastName age gender createdAt } }` ✅
- ✅ **Schema Composition**: Risolti tutti gli errori di composizione Apollo Federation
- ✅ **Production Verified**: Gateway v0.2.4 operativo al 100% su Render.com

### 🌐 **Production Services Status**
- ✅ **GraphQL Gateway**: https://gymbro-graphql-gateway.onrender.com/graphql (**v0.2.4 LIVE**)
- ✅ **User Management**: https://gymbro-user-service.onrender.com (**COMPLETE SCHEMA FEDERATED**)
- 🎯 **Complete Federation**: UserProfile, UserStats, UserPreferences, All Enums, DateTime scalars
- 🔥 **Advanced Test**: `{ userStats(userId:"1") { totalCaloriesBurned bmi } }` ✅ ALL WORKINGealth & Fitness Microservices

[![🎉 Federation Live](https://img.shields.io/badge/Apollo_Federation-LIVE-brightgreen)](https://gymbro-graphql-gateway.onrender.com/graphql)
[![🚀 Production](https://img.shields.io/badge/Services-2_LIVE-success)](https://gymbro-user-service.onrender.com)
[![🤖 Automation](https://img.shields.io/badge/Automation-Complete-blue)](https://github.com/giamma80/gymbro-platform)
[![💰 Cost](https://img.shields.io/badge/Cost-$0/month-success)](https://render.com)
[![🏥 Health](https://img.shields.io/badge/Health-100%25-brightgreen)](https://gymbro-user-service.onrender.com/health)
[![📋 Version](https://img.shields.io/badge/Version-v1.2.4-informational)](https://github.com/giamma80/gymbro-platform/releases/tag/v1.2.4)

## 🚀 Executive Summary
Piattaforma Health&Fitness basata su microservizi con **Apollo Federation completo** e architettura scalabile. Framework di automazione per sviluppo accelerato con strategia "Start Free, Scale Smart".

### 🎉 **v1.2.1 MAJOR MILESTONE: Apollo Federation Production Ready!**

🌐 **APOLLO FEDERATION OPERATIVO** - GraphQL unificato su tutti i microservizi:
- ✅ **Unified GraphQL API**: Single endpoint per tutti i servizi
- � **Schema Federation**: Automatic service discovery e composition
- 🍓 **Strawberry Integration**: Python services con federation support
- ⚡ **Zero-Cost Production**: Completamente operativo su tier gratuiti

### 🌐 **Production Services Status**
- ✅ **GraphQL Gateway**: https://gymbro-graphql-gateway.onrender.com/graphql (**FEDERATING**)
- ✅ **User Management**: https://gymbro-user-service.onrender.com (**FEDERATED**)
- 🧪 **Federation Test**: `{ hello, testEnums, userCount }` ✅ ALL WORKING
- � **GraphQL Playground**: Live introspection e testing interface  
- 🏥 **Health Monitoring**: 100% platform health, automated checks
- 💰 **Zero Cost**: PostgreSQL + 2x Web Services completamente gratuiti

### 🧑‍💻 **GraphQL Sandbox (Apollo) - Testa la Federation in 1 click!**

- **Accedi subito alla UI interattiva:**
  👉 [Apri Apollo Sandbox](https://gymbro-graphql-gateway.onrender.com/)
- **Come funziona:**
  - Visita la root del Gateway: https://gymbro-graphql-gateway.onrender.com
  - Verrai reindirizzato automaticamente alla Apollo Sandbox con l'endpoint già precompilato
  - Puoi esplorare lo schema federato, fare query, mutation e vedere la documentazione live
- **Sicuro anche in produzione:**
  - Solo introspection e query consentite dallo schema
  - Nessun dato sensibile esposto

Esempio di query federata da provare subito:
```graphql
{
  hello
  testEnums
  userCount
}
```

## 🌐 **APOLLO FEDERATION ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────┐
│                    GraphQL Gateway                          │
│            https://gymbro-graphql-gateway.onrender.com     │
│                   Apollo Federation                         │
└──────────────────┬──────────────────┬──────────────────────┘
                   │                  │
       ┌───────────▼──────────┐      ┌▼──────────────────┐
       │  User Management     │      │   Future Services │  
       │   (Strawberry)       │      │  (Auto-federated) │
       │  🍓 Federation Ready │      │   🔗 Plug & Play  │
       └──────────────────────┘      └───────────────────┘
```

### 🚀 **Unified GraphQL API Features**
- **� Single Query Endpoint**: Tutti i servizi accessibili via `/graphql`
- **🧩 Schema Composition**: Automatic merging di tutti gli schemi service
- **🔗 Service Discovery**: `_service` field per introspection automatica
- **⚡ Smart Routing**: Query automatically routed to correct service
- **🎯 Developer Experience**: GraphQL Playground per testing e documentation

## 🤖 **MICROSERVICES AUTOMATION FRAMEWORK**

### 🛠️ **Script di Automazione Disponibili**

#### **🚀 Genera Nuovo Microservizio (2 minuti)**
```bash
# Genera automaticamente struttura completa con Apollo Federation
./scripts/generate-microservice.sh <service-name> <runtime>

# Esempi con Federation Ready:
./scripts/generate-microservice.sh calorie-service python  # FastAPI + Strawberry Federation
./scripts/generate-microservice.sh analytics-service node # Express + Apollo Federation  
./scripts/generate-microservice.sh metrics-service go    # Gin + GraphQL Federation

# Genera automaticamente:
# ✅ Struttura completa + Apollo Federation schema
# ✅ _service field implementation per service discovery
# ✅ Health checks standard + GraphQL endpoints
# ✅ Dockerfile.minimal + render.yaml + CI/CD integration
```

#### **⚡ Attiva CI/CD Pipeline (1 minuto)**  
```bash
# Attiva automaticamente in GitHub Actions matrix
./scripts/activate-service-cicd.sh <service-name>

# Effetti automatici:
# ✅ Test automatici su push/PR ✅ Build Docker automatici  
# ✅ Integration tests ✅ Deploy automatico su Render.com
```

#### **🧪 Test Multi-Service (30 secondi)**
```bash
# Test automatico tutti i servizi deployed
./scripts/test-all-services.sh production  # Test produzione
./scripts/test-all-services.sh local       # Test locale

# Output: Health report completo con percentuale uptime
```

### 🎯 **Workflow Completo - Nuovo Microservizio in 30 Minuti**
```bash
# PROCEDURA AUTOMATIZZATA STANDARD:

# Step 1: Genera (2 min)
./scripts/generate-microservice.sh meal-service python

# Step 2: Implementa business logic (20 min)  
cd services/meal-service && python main.py

# Step 3: Test locale (2 min)
curl http://localhost:8000/health  # ✅ Verifica endpoints

# Step 4: Attiva CI/CD (1 min)
./scripts/activate-service-cicd.sh meal-service

# Step 5: Deploy (5 min)
git add . && git commit -m "feat: meal-service v0.X.0"
git push origin main

# ✅ RISULTATO: https://gymbro-meal-service.onrender.com LIVE!
```

## 📋 Stack Tecnologico

### Backend Services
- **Framework**: FastAPI (performance elevate, async nativo)
- **GraphQL**: Strawberry GraphQL per business logic + Apollo Server per gateway
- **Database**: PostgreSQL (Render.com managed)
- **WebSocket**: FastAPI WebSocket + Socket.IO
- **Auth**: JWT authentication
- **Storage**: Local/Cloud storage
- **Dependencies**: Poetry (gestione dipendenze moderna)

### 🎯 **Architettura Ibrida GraphQL - Decisione Strategica**

**Stack Decisionale Adottato**:
- **🌐 API Gateway**: TypeScript + Apollo Server (routing/performance)
- **🐍 Business Logic**: Python + FastAPI + Strawberry GraphQL (domain logic)

**Motivazioni Tecniche**:
- ⚡ **Performance Gateway**: Node.js Event Loop ottimale per I/O intensive proxy
- 🔗 **Apollo Federation**: Standard industry maturo per federazione microservizi  
- 📊 **Memory Efficiency**: ~30-50MB Node.js vs ~100-200MB Python per gateway
- 🚀 **Latency Optimization**: <10ms overhead vs ~20-50ms Python per request forwarding
- 🎯 **Separation of Concerns**: Gateway thin layer, business logic in Python

**Pattern Architetturale**:
```
Frontend/Mobile Apps
    ↓
🌐 GraphQL Gateway (TypeScript + Apollo Server)
    ↓ ↓ ↓ ↓
🐍 user-management (Python + Strawberry)
🐍 calorie-service (Python + Strawberry)  
🐍 meal-service (Python + Strawberry)
🐍 analytics-service (Python + Strawberry)
```

### Automation & AI
- **Workflow**: n8n (automazioni low-code)
- **LLM**: OpenAI API + Server MCP
- **Feature Flags**: Flagsmith
- **Monitoring**: Sentry + Prometheus

### DevOps & Infrastructure
- **CI/CD**: GitHub Actions (2000 min/mese FREE)
- **Deploy**: Render.com (750 ore/mese FREE)
- **Container Registry**: GitHub Container Registry (GHCR)
- **Containers**: Docker
- **API Gateway**: Traefik

## 🏗️ Architettura Microservizi

```
gymbro-platform/
├── services/
│   ├── user-management/     # Gestione utenti e autenticazione
│   ├── data-ingestion/      # Ricezione dati da device
│   ├── calorie-service/     # Calcoli metabolici e bilancio calorico
│   ├── meal-service/        # Gestione pasti e macronutrienti
│   ├── analytics-service/   # Statistiche e insights
│   ├── notification-service/ # Notifiche intelligenti
│   ├── graphql-gateway/     # Gateway GraphQL unificato
│   └── llm-query-service/   # Query in linguaggio naturale
├── automation/
│   └── n8n-workflows/       # Automazioni n8n
├── infrastructure/
│   ├── docker/              # Configurazioni Docker
│   ├── k8s/                 # Kubernetes manifests (futuro)
│   └── terraform/           # Infrastructure as Code (futuro)
├── shared/
│   ├── models/              # Modelli dati condivisi
│   ├── utils/               # Utilities comuni
│   └── config/              # Configurazioni condivise
└── docs/                    # Documentazione
```

## 🎯 Roadmap di Sviluppo (ACCELERATA con Automation Framework)

### ✅ Fase 1: Foundation MVP (Settimane 1-2) - **COMPLETED**
- [x] Setup repository e ambiente Docker
- [x] Configurazione CI/CD GitHub Actions + GitHub Container Registry  
- [x] Setup PostgreSQL managed (Render.com)
- [x] **User Management Service - LIVE IN PRODUCTION** ✅
- [x] **GraphQL Gateway Architecture Decision** ✅ TypeScript + Apollo Server
- [x] **🤖 AUTOMATION FRAMEWORK COMPLETE** ✅ **v0.2.0 MILESTONE**
- [x] **Microservice Generator Scripts** ✅ Python/Node.js/Go support
- [x] **CI/CD Auto-Activation** ✅ Matrix strategy automation
- [x] **Multi-Service Testing** ✅ Health monitoring automation

### � Fase 2: Core Services (Settimane 3-4) - **ACCELERATED Timeline**
Con gli script di automazione, ogni servizio richiede ora **1 settimana invece di 2-3 settimane**:

#### **v0.3.0 - Data Ingestion Service (Settimana 3)**
```bash
# Automated deployment in 30 minutes:
./scripts/generate-microservice.sh data-ingestion python
./scripts/activate-service-cicd.sh data-ingestion  
# Result: https://gymbro-data-ingestion.onrender.com
```

#### **v0.4.0 - Calorie Service (Settimana 4)**  
```bash
./scripts/generate-microservice.sh calorie-service python
# BMR/TDEE calculations + activity tracking
# Result: https://gymbro-calorie-service.onrender.com
```

### 📈 Fase 3: Advanced Services (Settimane 5-6) - **ACCELERATED Timeline**
#### **v0.5.0 - Meal Service + USDA Integration**
```bash
./scripts/generate-microservice.sh meal-service node
# Food database + nutritional calculations
```

#### **v0.6.0 - Analytics Service**
```bash  
./scripts/generate-microservice.sh analytics-service python
# Data insights + performance tracking
```

### 🤖 Fase 4: AI & Automation (Settimane 7-8)
#### **v0.7.0 - Notification Service**
```bash
./scripts/generate-microservice.sh notification-service node  
# Smart notifications + alerts
```

#### **v0.8.0 - LLM Query Service**
```bash
./scripts/generate-microservice.sh llm-query-service python
# OpenAI integration + natural language queries
```

### 🏁 **v1.0.0 - MVP COMPLETE (Settimana 8)**
**8 Microservizi LIVE** con timeline **accelerata del 50%**:
- **Timeline PRIMA**: 3-4 mesi per MVP completo  
- **Timeline DOPO**: 6-8 settimane per MVP completo
- **SAVING**: 50%+ tempo sviluppo grazie al framework automazione

## 💰 Strategia Zero-Cost ACHIEVED ✅

### Servizi Gratuiti Utilizzati
- **GitHub**: Repository + CI/CD (2000 min/mese) + Container Registry ✅
- **Render.com**: PostgreSQL + Web Service (FREE tier) ✅  
- **Production URL**: https://gymbro-user-service.onrender.com ✅
- **Cost**: $0/mese (PostgreSQL + hosting gratuiti) ✅

### 🗄️ **Database Persistence Strategy**
#### ✅ **Production Database (Render.com PostgreSQL)**
- **🔒 Persistent Storage**: Database PostgreSQL managed con storage persistente
- **🔄 Release Safety**: I dati vengono **mantenuti tra le release**
- **📊 Backup Automatici**: Render esegue backup automatici giornalieri
- **🚀 Deploy Strategy**: Solo l'applicazione viene ri-deployata, database rimane intatto
- **⚡ Zero Downtime**: Database service separato dall'application service

#### 📋 **Deploy Process (Database Safe)**
```bash
# Durante il deploy di una nuova release:
1. 🔄 Render rebuilds application container (nuovo codice)
2. 🗄️ Database PostgreSQL rimane SEMPRE attivo e persistente  
3. 🔌 Nuova app si reconnette al database esistente
4. ✅ Tutti i dati utente sono preservati
```

#### 🛡️ **Data Protection Features**
- **Managed Service**: Render gestisce backup, updates, monitoring
- **High Availability**: Database replication per fault tolerance
- **Connection Pooling**: Ottimizzazione performance connessioni
- **SSL Encryption**: Connessioni crittografate in transito

### Servizi Future (quando necessario)
- **Firebase**: Push notifications (FCM illimitato)
- **Sentry**: Error tracking (5000 eventi/mese)  
- **n8n Cloud**: Automazioni (1000 esecuzioni/mese)

### Trigger per Upgrade
- ✓ >50k autenticazioni mensili
- ✓ >1000 utenti attivi giornalieri
- ✓ Cold start impatta UX
- ✓ Necessario uptime 99.9%

## 🔧 Quick Start

### ⚡ Try Live Service
```bash
# Test Production Service (LIVE)
curl https://gymbro-user-service.onrender.com/health
curl https://gymbro-user-service.onrender.com/docs

# Register new user
curl -X POST "https://gymbro-user-service.onrender.com/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"your-email@example.com",
    "password":"SecurePass123!",
    "first_name":"Your",
    "last_name":"Name", 
    "date_of_birth":"1990-01-01",
    "gender":"male",
    "height_cm":180,
    "weight_kg":75,
    "activity_level":"moderately_active"
  }'
```

### 🏠 Local Development

### Prerequisiti
- **Python 3.11+**
- **Poetry** ([Installazione](https://python-poetry.org/docs/#installation))
- **Docker & Docker Compose**
- **Git**

### 1. Clone e Setup Ambiente
```bash
git clone https://github.com/giamma80/gymbro-platform.git
cd gymbro-platform
cp .env.example .env
# Edita .env con le tue API keys
```
```

### 2. Setup Microservizi con Poetry
```bash
# User Management Service (già migrato)
cd services/user-management
poetry install
poetry run pytest  # Verifica che i test passino
cd ../..

# Per altri servizi (in migrazione)
make install  # Installa dipendenze di tutti i servizi
```

### 3. Sviluppo Locale con Docker
```bash
# Avvia infrastructure services (DB, Redis, etc.)
docker-compose up -d postgres redis

# Avvia singolo servizio in dev
make dev-user  # User management su porta 8001

# Oppure tutti i servizi
docker-compose up -d
```

### 4. Test Services
```bash
# Test con Poetry (raccomandato)
make test-user

# Test user service
curl http://localhost:8001/health

# Test GraphQL gateway  
curl http://localhost:8000/graphql
```

## 🚀 CI/CD Pipeline

### GitHub Actions Automation
- **Test automatici** su ogni push/PR
- **Docker builds** con GitHub Container Registry
- **Security scanning** con Trivy
- **Deploy automatico** su Render.com

### Docker Images
- **Registry**: `ghcr.io/giamma80/gymbro-*`
- **Login automatico**: Zero configurazione richiesta
- **Multi-arch**: linux/amd64 support

### Pipeline Features
- ✅ Test coverage minimo 80%
- ✅ Code quality gates (Black, Flake8, MyPy)
- ✅ Security vulnerability checks (Trivy)
- ✅ Automatic deployment staging/production
- ✅ Health checks post-deploy
- ✅ GitHub Actions v4 compatibility
- ✅ Zero deprecation warnings

## 📊 Metriche di Successo
- **Uptime**: >99.9%
- **Response Time**: <200ms (95° percentile)
- **Error Rate**: <0.1%
- **User Growth**: +20% MAU
- **Engagement**: >80% daily widget usage

## 🛡️ Sicurezza & Compliance
- **Crittografia**: AES-256 a riposo, TLS in transito
- **GDPR**: Right to be forgotten, data minimization
- **Auth**: JWT short-lived + refresh tokens
- **Rate Limiting**: 1000 req/ora per utente

## 📚 Documentazione
- [API Documentation](./docs/api/)
- [Deployment Guide](./docs/deployment/)
- [Architecture Deep Dive](./docs/architecture/)
- [Contributing Guide](./docs/contributing/)

## 🤝 Contributing
1. Fork del repository
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 🏷️ Versioning & Releases

Utilizziamo [Semantic Versioning](https://semver.org/) con Git tags per tracciare le release.

### 📋 Changelog

#### v0.1.3 (15 Agosto 2025) - 🚀 PRODUCTION DEPLOYMENT
##### 🎉 **MILESTONE: First Service Live in Production!**
Il **User Management Service** è ora **operativo in produzione** su Render.com!

##### ✨ Features
- **🌐 Production Deployment**: Servizio live su https://gymbro-user-service.onrender.com
- **💰 Zero-Cost Architecture**: PostgreSQL + Web Service gratuiti ($0/mese)
- **🏥 Production Health Checks**: Endpoint `/health`, `/ping`, `/health/detailed`
- **📚 Live API Documentation**: https://gymbro-user-service.onrender.com/docs
- **🔒 Full Security Stack**: JWT authentication, CORS, input validation
- **📊 Production Monitoring**: Render dashboard integration
- **⚡ Performance Optimization**: Multi-stage Docker build (~40% faster)

##### 🔧 Technical Fixes
- **🗄️ SQLAlchemy 2.x Compatibility**: Added `text()` wrapper for raw SQL queries
- **🛡️ Middleware Issues**: Disabled TrustedHostMiddleware to prevent request hanging
- **🌐 CORS Configuration**: Property-based parsing for environment variables
- **🚪 Port Binding**: Dynamic PORT environment variable support for Render
- **🔧 Database Connection**: Proper error handling for PostgreSQL managed service

##### 📊 Performance Metrics
- **Response Time**: <550ms (production)
- **Uptime**: 100% since deployment
- **Database**: PostgreSQL managed connected and operational
- **Security**: Full JWT token validation working

#### v0.1.2 (15 Agosto 2025) - 💰 ZERO-COST MVP
##### 💰 **Zero-Cost Architecture Achievement**
- **🧠 In-Memory Cache System**: Thread-safe cache with TTL and LRU eviction
- **🗑️ Redis Removal**: Completely eliminated Redis dependency ($7/mese → $0/mese)
- **📦 Cost Optimization**: 100% cost reduction for MVP phase
- **🔄 Redis-Compatible API**: Drop-in replacement for basic Redis operations

#### v0.1.1 (14 Agosto 2025) - 🚀 CI/CD PIPELINE
##### ✨ Features
- **CI/CD Pipeline**: GitHub Actions completamente automatizzata
- **Docker Registry**: GitHub Container Registry (GHCR) integrato
- **Quality Gates**: Test coverage 80%, linting, security scan
- **Deploy Automation**: Staging/production ready
- **GitHub Actions v4**: Aggiornate tutte le azioni deprecate

#### v0.1.0 (14 Agosto 2025) - 🎉 INITIAL RELEASE
##### ✨ Features
- **User Management Service**: Registrazione, login, autenticazione JWT completa
- **Database Setup**: PostgreSQL con migrazioni automatiche
- **Security Features**: JWT tokens, password hashing, input validation
- **API Endpoints**: 10+ endpoints per gestione utenti completa

##### 🔗 Compatibility
- PostgreSQL 15+
- Python 3.11+
- FastAPI + SQLAlchemy 2.0

### 🎯 Roadmap
- **v0.2.0**: GraphQL Gateway (API unificata)
- **v0.3.0**: Data Ingestion Service (Google Fit, Apple HealthKit)
- **v0.4.0**: Calorie Service (BMR/TDEE calculations)
- **v0.5.0**: Meal Service (gestione pasti e ricette)
- **v0.6.0**: Analytics Service (insights e reportistica)
- **v0.7.0**: Notification Service (notifiche intelligenti)
- **v0.8.0**: LLM Query Service (AI/LLM integrazione)
- **v1.0.0**: MVP Complete with real-time features

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
Made with ❤️ for the fitness community
