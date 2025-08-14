# 🚀 Release Process - GymBro Platform

## 📋 Processo di Release Dettagliato

Guida step-by-step per creare una release con aggiornamento automatico dei changelog.

## 🔄 Fasi del Release Process

### Phase 1: Pre-Release Preparation

#### 1.1 **Feature Freeze & Testing**
```bash
# Assicurati che tutti i servizi siano attivi
make start-dev
make health

# Esegui tutti i test
make test-all

# Verifica linting e formattazione
make lint
make format
```

#### 1.2 **Documentation Review**
- [ ] Verificare che tutti i README.md siano aggiornati
- [ ] Controllare che la documentazione API sia corretta
- [ ] Validare esempi di codice e comandi

#### 1.3 **Environment Validation**
```bash
# Test con environment pulito
make clean
make setup
make start

# Verificare che tutto funzioni senza cache
```

### Phase 2: Version Planning

#### 2.1 **Determinare Versione**
Basato su Semantic Versioning:

```bash
# PATCH (v1.0.1) - Bug fixes minori
git log --oneline $(git describe --tags --abbrev=0)..HEAD | grep -E "(fix|hotfix)"

# MINOR (v1.1.0) - Nuove feature, servizi aggiunti  
git log --oneline $(git describe --tags --abbrev=0)..HEAD | grep -E "(feat|add)"

# MAJOR (v2.0.0) - Breaking changes
git log --oneline $(git describe --tags --abbrev=0)..HEAD | grep -E "(break|major)"
```

#### 2.2 **Identificare Servizi Modificati**
```bash
# Lista file modificati dall'ultimo tag
git diff --name-only $(git describe --tags --abbrev=0)

# Identificare servizi interessati
git diff --name-only $(git describe --tags --abbrev=0) | grep "services/" | cut -d'/' -f2 | sort -u
```

### Phase 3: Release Creation

#### 3.1 **Commit Finale**
```bash
# Staging di tutti i cambiamenti
git add .

# Commit con formato standardizzato
git commit -m "🚀 Release v0.2.0 - Data Ingestion Service

📦 Services Updated:
- data-ingestion: New service implementation
- user-management: Integration endpoints added

✨ Features:
- Google Fit API integration
- Apple HealthKit support
- Real-time data validation
- WebSocket notifications

🔧 Technical:
- Async data processing pipeline
- Redis caching for performance
- Error handling improvements

📊 Performance:
- 40% faster data ingestion
- Reduced memory usage by 25%"
```

#### 3.2 **Creazione Tag Annotato**
```bash
# Tag con messaggio dettagliato
git tag -a v0.2.0 -m "v0.2.0 - Data Ingestion Service

Major addition of data ingestion capabilities with multi-device support.

Components:
- Data Ingestion Service (port 8002)
- Google Fit API integration  
- Apple HealthKit support
- Real-time validation pipeline

Breaking Changes: None
Migration Required: None

Compatibility:
- User Management v0.1.0+
- PostgreSQL 15+
- Redis 7+"

# Push commit e tag
git push origin main
git push origin v0.2.0
```

### Phase 4: Changelog Automation

#### 4.1 **GitHub Copilot Automation Trigger**
Una volta creato il tag, GitHub Copilot eseguirà automaticamente:

1. **Analisi delle modifiche**
2. **Generazione changelog**
3. **Aggiornamento README files**
4. **Update CHECKPOINT.md**

#### 4.2 **Files Aggiornati Automaticamente**

##### README.md Principale
```markdown
## 📋 Changelog

### v0.2.0 (15 Agosto 2025)
#### 🆕 New Services
- **Data Ingestion Service**: Multi-device data collection and validation

#### ✨ Features  
- Google Fit API integration
- Apple HealthKit support
- Real-time data validation pipeline
- WebSocket notifications for live updates

#### 🔧 Technical Improvements
- Async data processing with improved performance
- Redis caching layer for faster responses
- Enhanced error handling and logging

#### 📊 Performance
- 40% faster data ingestion
- 25% reduction in memory usage
- Improved real-time response times

#### 🔗 Compatibility
- Compatible with User Management v0.1.0+
- Requires PostgreSQL 15+ and Redis 7+

---

### v0.1.0 (14 Agosto 2025)
#### ✨ Features
- User Management Service completo
- Autenticazione JWT completa
- Database PostgreSQL setup

#### 🔧 Technical  
- Environment variables management
- Docker Compose infrastructure
- Makefile development commands

#### 🐛 Fixes
- Pydantic settings configuration
- Sentry disabled per sviluppo locale
```

##### services/data-ingestion/README.md
```markdown
# 📊 Data Ingestion Service

## 📋 Changelog

### v0.2.0 (15 Agosto 2025)
#### 🎉 Initial Release
- **Service Launch**: First stable version
- **Multi-Device Support**: Google Fit, Apple HealthKit integration
- **Real-time Processing**: Async data validation pipeline

#### ✨ Features
- `/ingest/google-fit` - Google Fit data ingestion
- `/ingest/apple-health` - Apple HealthKit integration  
- `/ingest/validate` - Real-time data validation
- `/devices/register` - Device registration endpoint

#### 🔧 Technical Details
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with async SQLAlchemy
- **Cache**: Redis for performance optimization
- **Validation**: Pydantic models with custom validators

#### 📊 Performance Metrics
- Processes 1000+ data points/second
- <50ms response time for validation
- 99.9% uptime target

#### 🔗 Dependencies
- User Management Service v0.1.0+
- PostgreSQL 15+
- Redis 7+
```

##### CHECKPOINT.md Update
```markdown
## 📅 Data: 15 Agosto 2025
## 📍 Stato: User Management + Data Ingestion Services Attivi

### ✅ Servizi Funzionanti
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- User Management: `localhost:8001` 
- Data Ingestion: `localhost:8002` ✨ NUOVO

### 🏷️ Versione Corrente: v0.2.0

### 🚀 Come Continuare da Qui
```bash
# Avvia ambiente completo
make start-dev
make dev-user
make dev-ingestion

# Test servizi  
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### 🎯 Roadmap Progress
✅ **v0.1.0**: User Management Service  
✅ **v0.2.0**: Data Ingestion Service
🔄 **v0.3.0**: Calorie Service (prossimo)
🔄 **v0.4.0**: GraphQL Gateway
```

### Phase 5: Post-Release Validation

#### 5.1 **Smoke Tests**
```bash
# Verifica che tutti i servizi siano healthy dopo la release
make health

# Test endpoint critici
curl http://localhost:8001/health
curl http://localhost:8002/health

# Test integrazione tra servizi
make test-integration
```

#### 5.2 **Documentation Verification**
- [ ] README principale aggiornato correttamente
- [ ] Changelog servizi specifici aggiornati
- [ ] CHECKPOINT.md riflette stato corrente
- [ ] Versioni compatibili documentate

#### 5.3 **Git Verification**
```bash
# Verifica tag creato correttamente
git tag -l | tail -5

# Verifica metadati tag
git show v0.2.0

# Verifica push completato
git ls-remote --tags origin
```

## 🔄 Rollback Process

### In caso di problemi critici:

```bash
# 1. Identificare ultimo tag stabile
git tag -l | tail -2

# 2. Rollback a versione precedente
git checkout v0.1.0

# 3. Creare hotfix tag se necessario  
git tag -a v0.1.1 -m "Hotfix: critical issue resolved"

# 4. Aggiornare changelog con hotfix
```

## 📊 Release Metrics

### Metriche da Tracciare:
- **Tempo di release**: Target <30 minuti
- **Test coverage**: Mantenere >80%
- **Documentation completeness**: 100% README aggiornati
- **Zero-downtime**: Nessun servizio down durante release
- **Rollback time**: <5 minuti se necessario

## 🎯 Success Criteria

Una release è considerata successuful quando:

- [ ] **Tag creato** e pushato correttamente
- [ ] **Changelog aggiornati** automaticamente da GitHub Copilot  
- [ ] **Services healthy** dopo deployment
- [ ] **Integration tests** passano
- [ ] **Documentation** completa e accurata
- [ ] **CHECKPOINT.md** riflette nuovo stato
- [ ] **No breaking changes** non documentati
- [ ] **Performance** mantenuta o migliorata

---

**Next Steps**: Questo processo verrà seguito per ogni release, garantendo consistency e tracciabilità completa del progetto.
