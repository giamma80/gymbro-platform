# 🔍 Quality Assurance Scripts

Questa cartella contiene gli script per il controllo qualità, il monitoraggio della salute della GymBro Platform e i processi di **Data Preparation & Validation** per database testing.

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

## 🧪 Data Preparation & Database Testing

### 🔥 BREAKTHROUGH (17 Settembre) - Processo di Test Data Preparation

**INNOVAZIONE**: Implementato sistema completo di preparazione dati di test con scenari realistici multi-sorgente per validazione database e RPC functions.

#### 📊 009_test_data_preparation.sql - Schema Realistica Test Data

**OBIETTIVO**: Creare dataset completo e realistico per testare:
- Calcoli `progress_percentage` on-the-fly
- Funzioni RPC `getBehavioralPatterns()`
- Allineamento schema database vs SQLAlchemy
- Pattern comportamentali utente multi-giorno

```sql
-- SCENARIO UTENTE: Mario Rossi - Atleta Intermedio
-- TIMEFRAME: 9 giorni completi di tracking
-- SORGENTI: Manual, HealthKit, Smart Scale, Nutrition Scan
-- PATTERN: Colazione, pranzo, cena, spuntini + allenamenti + pesate

-- 🎯 DISTRIBUZIONE SORGENTI DATI:
-- manual: 40% - Inserimenti manuali utente  
-- healthkit: 25% - Sync automatico fitness tracker
-- nutrition_scan: 20% - AI scanning cibo
-- smart_scale: 10% - Bilancia intelligente  
-- fitness_tracker: 5% - Altri dispositivi wearable
```

#### 🔍 Validation Process Implementato

**1. Schema Structure Validation**
```sql
-- Query automatica per verifica allineamento:
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'calorie_balance'
ORDER BY table_name, ordinal_position;

-- ✅ RISULTATO: 100% allineamento SQL ↔ SQLAlchemy ↔ Database
```

**2. Behavioral Pattern Validation** 
```sql
-- Test realistico pattern comportamentali:
-- Giorni feriali: 3 pasti + 2 spuntini + allenamento
-- Weekend: Pattern più irregolare ma realistico
-- Correlazione peso-net_calories: Variazione fisiologica
```

**3. Multi-Source Data Quality**
```sql
-- Verifica distribuzione sorgenti:
SELECT 
    source,
    COUNT(*) as event_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
FROM calorie_events 
GROUP BY source 
ORDER BY event_count DESC;

-- Target: Distribuzione realistica come utente reale
```

#### 📋 Test Data Standards

**PATTERN TEMPORALI**:
- **07:30**: Colazione (nutrition_scan) - ~400 cal
- **10:00**: Spuntino (manual) - ~150 cal
- **13:00**: Pranzo (nutrition_scan) - ~600 cal  
- **16:00**: Allenamento (healthkit) - ~400 cal burned
- **19:30**: Cena (manual) - ~700 cal
- **21:00**: Snack (manual) - ~200 cal
- **08:00**: Peso giornaliero (smart_scale)

**RANGE VALIDATION**:
- Colazione: 300-500 cal
- Pranzo: 500-800 cal  
- Cena: 600-1000 cal
- Spuntini: 100-300 cal
- Allenamenti: 200-600 cal
- Variazione peso: ±0.5 kg/giorno (realistico)

#### 🎯 Use Cases di Test Coperti

**1. Progress Percentage Accuracy**
```sql
-- Test calcolo on-the-fly con goal dinamici:
-- Goal 2000 cal, consumed 1500 → progress 75%
-- Goal 2500 cal, consumed 2000 → progress 80%  
-- Goal cambio mid-period → ricalcolo automatico
```

**2. Net Calories Correlation**
```sql  
-- Pattern realistici deficit/surplus:
-- Giorni allenamento: Surplus moderato
-- Giorni riposo: Leggero deficit
-- Weekend: Variabilità maggiore
```

**3. Multi-Day Behavioral Analysis**
```sql
-- RPC getBehavioralPatterns() test scenarios:
-- Consistenza orari pasti
-- Frequenza allenamenti  
-- Pattern weekend vs feriali
-- Correlazione peso-net_calories
```

### 🚀 Execution Workflow

**STEP 1**: Schema Setup
```bash
# Setup database structure
psql -f services/calorie-balance/sql/001_setup_schema.sql

# Apply test data
psql -f services/calorie-balance/sql/009_test_data_preparation.sql
```

**STEP 2**: Validation Execution
```bash
# Run schema validation
./scripts/QA/quality-check.sh --database-schema

# Test RPC functions with prepared data
./scripts/QA/health-check.sh --rpc-validation
```

**STEP 3**: Behavioral Analysis
```bash
# Execute getBehavioralPatterns with test user
curl -X POST "http://localhost:54321/rest/v1/rpc/getBehavioralPatterns" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user-uuid", "start_date": "2024-09-10", "end_date": "2024-09-18"}'
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
