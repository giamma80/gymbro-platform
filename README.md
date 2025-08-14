# 🏋️ GymBro Platform - Health & Fitness Microservices

## 🚀 Executive Summary
Piattaforma Health&Fitness basata su microservizi con architettura scalabile, sviluppata seguendo la strategia "Start Free, Scale Smart" utilizzando esclusivamente servizi gratuiti nella fase MVP.

## 📋 Stack Tecnologico

### Backend Services
- **Framework**: FastAPI (performance elevate, async nativo)
- **GraphQL**: Strawberry GraphQL 
- **Database**: PostgreSQL (Supabase)
- **WebSocket**: FastAPI WebSocket + Socket.IO
- **Auth**: Supabase Auth + JWT
- **Storage**: Supabase Storage
- **Dependencies**: Poetry (gestione dipendenze moderna)

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

## 🎯 Roadmap di Sviluppo

### 🚀 Fase 1: Foundation MVP (Settimane 1-2)
- [x] Setup repository e ambiente Docker
- [x] Configurazione CI/CD GitHub Actions + GitHub Container Registry
- [x] Setup Supabase (DB + Auth)
- [x] Servizio User Management
- [ ] GraphQL Gateway base

### 🔧 Fase 2: Core Services (Settimane 3-6)
- [ ] Data Ingestion Service
- [ ] Calorie Service (BMR/TDEE)
- [ ] Meal Service + USDA integration
- [ ] WebSocket real-time
- [ ] Analytics base

### 📈 Fase 3: Advanced Features (Settimane 7+)
- [ ] LLM Integration (OpenAI)
- [ ] n8n Workflows
- [ ] Notification Service
- [ ] Device connectors (Google Fit, HealthKit)

## 💰 Strategia Zero-Cost

### Servizi Gratuiti Utilizzati
- **GitHub**: Repository + CI/CD (2000 min/mese) + Container Registry
- **Supabase**: DB + Auth + Storage (500MB, 50k users)
- **Render.com**: Hosting (750 ore/mese)
- **Firebase**: Push notifications (FCM illimitato)
- **Sentry**: Error tracking (5000 eventi/mese)
- **n8n Cloud**: Automazioni (1000 esecuzioni/mese)

### Trigger per Upgrade
- ✓ >50k autenticazioni mensili
- ✓ >1000 utenti attivi giornalieri
- ✓ Cold start impatta UX
- ✓ Necessario uptime 99.9%

## 🔧 Quick Start

### Prerequisiti
- **Python 3.11+**
- **Poetry** ([Installazione](https://python-poetry.org/docs/#installation))
- **Docker & Docker Compose**
- **Git**

### 1. Clone e Setup Ambiente
```bash
git clone <repo-url>
cd gymbro-platform
cp .env.example .env
# Edita .env con le tue API keys
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
- ✅ Security vulnerability checks
- ✅ Automatic deployment staging/production
- ✅ Health checks post-deploy

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

#### v0.1.1 (15 Gennaio 2025) - CI/CD Pipeline Complete
##### ✨ Features
- **CI/CD Pipeline**: GitHub Actions completamente automatizzata
- **Docker Registry**: GitHub Container Registry (GHCR) integrato
- **Quality Gates**: Test coverage 80%, linting, security scan
- **Deploy Automation**: Staging/production su Render.com

##### 🔧 Technical Improvements  
- **Zero Docker config**: Login automatico con GITHUB_TOKEN
- **Multi-service matrix**: Pipeline pronta per 8 microservizi
- **Security scanning**: Trivy integration per vulnerability detection
- **Test automation**: Setup environment completamente automatizzato

#### v0.1.0 (14 Agosto 2025) - Initial MVP
##### ✨ Features
- **User Management Service**: Registrazione, login, autenticazione JWT completa
- **Database Setup**: PostgreSQL con migrazioni automatiche
- **Environment Management**: Configurazione centralizzata per sviluppo

##### 🔧 Technical Improvements
- FastAPI framework con supporto async
- Pydantic settings per environment variables  
- Docker Compose per ambiente di sviluppo
- Makefile con comandi standardizzati

##### 🐛 Bug Fixes
- Risolto conflitto Pydantic Config vs model_config
- Sentry disabilitato per sviluppo locale
- Environment variables loading ottimizzato

##### 📊 Performance  
- Endpoint response time <200ms
- Database connection pooling attivo
- Health checks implementati

##### 🔗 Compatibility
- PostgreSQL 15+
- Redis 7+
- Python 3.11+

### 🎯 Roadmap
- **v0.2.0**: Data Ingestion Service (Google Fit, Apple HealthKit)
- **v0.3.0**: Calorie Service (BMR/TDEE calculations)
- **v0.4.0**: GraphQL Gateway (unified API)
- **v1.0.0**: MVP Complete with real-time features

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
Made with ❤️ for the fitness community
