# 🏷️ Git Versioning & Changelog Strategy

## 📋 Overview
Strategia di versionamento per GymBro Platform usando Git tags e changelog automatizzati per tracciare l'evoluzione del progetto e dei singoli microservizi.

## 🎯 Obiettivi
- **Tracciabilità**: Ogni release è tracciata con tag Git
- **Changelog Centralizzato**: README.md principale con storia completa
- **Changelog Microservizi**: Ogni servizio ha il suo changelog dedicato
- **Semantic Versioning**: Uso di SemVer (MAJOR.MINOR.PATCH)
- **Automazione**: Processo standardizzato per releases

## 📚 Semantic Versioning (SemVer)

### Formato: `vMAJOR.MINOR.PATCH`

- **MAJOR** (v2.0.0): Breaking changes, architettura major
- **MINOR** (v1.1.0): Nuove feature, microservizi aggiunti
- **PATCH** (v1.0.1): Bug fixes, miglioramenti minori

### Esempi di Versioning:
```
v0.1.0 - Initial MVP User Management
v0.2.0 - Data Ingestion Service aggiunto
v0.3.0 - Calorie Service aggiunto
v0.4.0 - GraphQL Gateway aggiunto
v1.0.0 - MVP Completo (Fase 1 completata)
v1.1.0 - WebSocket real-time aggiunto
v1.1.1 - Fix performance database
v2.0.0 - Architettura Kubernetes (breaking change)
```

## 🔄 Workflow di Release

### 1. **Pre-Release Checklist**
- [ ] Tutti i test passano
- [ ] Documentazione aggiornata
- [ ] Environment variables verificate
- [ ] Services health check OK

### 2. **Creazione Tag e Release**
```bash
# 1. Commit finale
git add .
git commit -m "🚀 Release v0.1.0 - User Management MVP"

# 2. Creare tag annotato
git tag -a v0.1.0 -m "v0.1.0 - User Management Service
- ✅ Autenticazione JWT
- ✅ CRUD utenti completo  
- ✅ Database PostgreSQL
- ✅ Environment management
- ✅ Health checks"

# 3. Push tag
git push origin v0.1.0
```

### 3. **Aggiornamento Changelog (Automatico)**
Ogni volta che viene creato un tag, GitHub Copilot aggiornerà:

1. **README.md principale** - Changelog centralizzato
2. **services/[service]/README.md** - Changelog specifico del servizio
3. **CHECKPOINT.md** - Stato attuale aggiornato

## 📝 Template Changelog

### README.md Principale
```markdown
## 📋 Changelog

### v0.1.0 (14 Agosto 2025)
#### ✨ Features
- User Management Service completo
- Autenticazione JWT
- Database PostgreSQL setup

#### 🔧 Technical
- Environment variables management
- Docker Compose infrastructure
- Makefile commands

#### 🐛 Fixes
- Pydantic settings configuration
- Sentry disabled per sviluppo locale
```

### README.md Microservizio
```markdown
## 📋 Changelog - User Management Service

### v0.1.0 (14 Agosto 2025)
#### ✨ Features
- Registration/Login endpoints
- JWT token management
- User profile CRUD
- Password validation

#### 🔧 Technical  
- FastAPI framework
- SQLAlchemy async ORM
- Pydantic models
- Rate limiting

#### 🐛 Fixes
- Environment variables loading
- Config vs model_config conflict resolved
```

## 🏗️ Struttura Changelog Files

```
gymbro-platform/
├── README.md                    # Changelog principale
├── CHECKPOINT.md               # Stato attuale
├── services/
│   ├── user-management/
│   │   └── README.md          # Changelog User Management
│   ├── data-ingestion/
│   │   └── README.md          # Changelog Data Ingestion  
│   ├── calorie-service/
│   │   └── README.md          # Changelog Calorie Service
│   └── graphql-gateway/
│       └── README.md          # Changelog GraphQL Gateway
└── docs/
    ├── versioning-strategy.md  # Questo file
    ├── release-process.md     # Processo dettagliato
    └── changelog-templates.md # Template standardizzati
```

## 🤖 Automazione con GitHub Copilot

### Responsabilità di GitHub Copilot:
1. **Rilevamento Tag**: Quando viene creato un nuovo tag
2. **Aggiornamento README.md**: Changelog principale con tutte le modifiche
3. **Aggiornamento Service README**: Solo servizi modificati nella release
4. **Aggiornamento CHECKPOINT.md**: Stato corrente con nuovo tag
5. **Validazione**: Verifica che tutti i changelog siano consistenti

### Trigger per Aggiornamenti:
- ✅ Nuovo tag Git creato
- ✅ Milestone raggiunto (fine settimana roadmap)
- ✅ Feature importante implementata
- ✅ Bug fix critico risolto

## 📊 Metadati Release

### Informazioni da Includare:
- **Data release**
- **Versione tag**
- **Servizi modificati**
- **Breaking changes** (se presenti)
- **Migration notes** (se necessarie)
- **Performance improvements**
- **Security fixes**

### Esempio Metadati:
```yaml
version: v0.1.0
date: 2025-08-14
services_updated:
  - user-management
breaking_changes: false
migration_required: false
performance_impact: none
security_fixes: []
```

## 🔍 Best Practices

### Git Tags
- **Sempre annotati**: `git tag -a v1.0.0 -m "message"`
- **Messaggi descrittivi**: Include feature principali
- **Push esplicito**: `git push origin v1.0.0`

### Changelog
- **Categorie standard**: Features, Technical, Fixes, Breaking
- **Linguaggio chiaro**: Comprensibile anche a non-dev
- **Link utili**: Reference a documentazione, API docs

### Microservizi
- **Changelog separati**: Ogni servizio tracked indipendentemente
- **Versioning interno**: Ogni servizio può avere sua versione
- **Dependencies**: Tracciare dipendenze tra servizi

## 🚀 Esempio Workflow Completo

```bash
# 1. Sviluppo feature
git checkout -b feature/data-ingestion-service
# ... sviluppo ...
git commit -m "✨ Add data ingestion service"

# 2. Merge in main
git checkout main
git merge feature/data-ingestion-service

# 3. Preparazione release
git add .
git commit -m "🚀 Release v0.2.0 - Data Ingestion Service"

# 4. Creazione tag
git tag -a v0.2.0 -m "v0.2.0 - Data Ingestion Service
- ✅ Google Fit API integration
- ✅ Apple HealthKit support  
- ✅ Data validation pipeline
- ✅ Real-time ingestion"

# 5. Push e trigger automazione
git push origin main
git push origin v0.2.0

# 6. GitHub Copilot aggiorna automaticamente:
#    - README.md (changelog principale)
#    - services/data-ingestion/README.md  
#    - CHECKPOINT.md
```

## 📋 Checklist Pre-Release

- [ ] **Tests**: Tutti i test passano
- [ ] **Documentation**: README aggiornati
- [ ] **Environment**: Variabili verificate
- [ ] **Health Checks**: Tutti i servizi healthy
- [ ] **Performance**: Nessuna regressione
- [ ] **Security**: Scan vulnerabilità completato
- [ ] **Changelog**: Bozza preparata
- [ ] **Migration Guide**: Se breaking changes

---

**Note**: Questa strategia garantisce tracciabilità completa e facilita onboarding di nuovi sviluppatori attraverso una storia chiara del progetto.
