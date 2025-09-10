# 🔍 Quality Assurance Scripts

Questa cartella contiene gli script per il controllo qualità e il monitoraggio della salute della GymBro Platform.

## 📋 Script Disponibili

### 🏥 health-check.sh
**Scopo**: Monitora la salute di tutti i servizi della piattaforma

**Funzionalità**:
- Verifica lo stato di Docker Compose
- Controlla tutti i microservizi (porte 8001-8007)
- Testa la connettività al database PostgreSQL
- Fornisce un report completo dello stato della piattaforma

**Utilizzo**:
```bash
# Diretto
./scripts/QA/health-check.sh

# Tramite Makefile
make health
make services-start  # Include automaticamente health check
```

**Output**:
- ✅ Servizi operativi con status
- ❌ Servizi non funzionanti con suggerimenti per il debug
- 📋 Lista degli endpoint disponibili per lo sviluppo

### 📊 quality-check.sh
**Scopo**: Esegue controlli completi sulla qualità del codice

**Funzionalità**:
- **Formatting**: Black, isort per Python
- **Linting**: Flake8 per style guide enforcement
- **Type Checking**: MyPy per controlli di tipo
- **Security**: Safety check per vulnerabilità note
- **Testing**: Esecuzione test unitari
- **Coverage**: Report di copertura dei test

**Utilizzo**:
```bash
# Diretto
./scripts/QA/quality-check.sh

# Con opzioni
./scripts/QA/quality-check.sh --integration  # Include test integrazione
./scripts/QA/quality-check.sh --docker      # Include test build Docker

# Tramite Makefile
make quality-check
```

**Parametri Opzionali**:
- `--integration`: Include test di integrazione
- `--docker`: Testa la build Docker dell'applicazione

## 🚀 Integrazione CI/CD

Questi script sono integrati nel workflow di sviluppo:

```bash
# Quick start completo con health check
make quick-start

# Pre-commit quality checks
make quality-check

# Verifica servizi in esecuzione
make health
```

## 📊 Monitoraggio Continuo

Per un monitoraggio continuo durante lo sviluppo:

```bash
# Controlla salute ogni 30 secondi
watch -n 30 './scripts/QA/health-check.sh'

# Quality check prima di ogni commit
git config core.hooksPath .githooks
# (configurare pre-commit hook con quality-check.sh)
```

## 🛠️ Troubleshooting

**Health Check Failures**:
1. Verifica Docker: `docker-compose ps`
2. Controlla logs: `make logs`
3. Restart servizi: `make restart`
4. Reset completo: `make reset-all`

**Quality Check Issues**:
1. Auto-fix formatting: Gli script correggono automaticamente black/isort
2. Type errors: Controlla MyPy output per errori di tipo
3. Security issues: Aggiorna dipendenze con poetry
4. Test failures: Verifica configurazione ambiente di test

## 📈 Metriche Qualità

Gli script QA forniscono metriche per:
- ✅ **Code Coverage**: Percentuale di codice coperto da test
- 🔒 **Security Score**: Assenza di vulnerabilità note
- 📏 **Code Quality**: Conformità agli standard di codifica
- ⚡ **Performance**: Tempo di risposta dei servizi
- 🏥 **Health Status**: Disponibilità servizi essenziali
