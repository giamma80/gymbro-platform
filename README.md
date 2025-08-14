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
- [ ] Configurazione CI/CD GitHub Actions
- [ ] Setup Supabase (DB + Auth)
- [ ] Servizio User Management
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
- **GitHub**: Repository + CI/CD (2000 min/mese)
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

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
Made with ❤️ for the fitness community
