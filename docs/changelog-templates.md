# 📝 Changelog Templates - GymBro Platform

## 🎯 Template Standardizzati per Changelog

Template per mantenere consistency nei changelog di progetto e microservizi.

## 📋 Template README.md Principale

```markdown
## 📋 Changelog

### v[VERSION] ([DATE])
#### 🆕 New Services  
- **[Service Name]**: [Breve descrizione del servizio]

#### ✨ Features
- [Feature description]
- [Feature description]

#### 🔧 Technical Improvements
- [Technical improvement]
- [Technical improvement]

#### 🐛 Bug Fixes
- [Bug fix description]
- [Bug fix description]

#### 🚨 Breaking Changes
- [Breaking change description]
- [Migration instructions]

#### 📊 Performance
- [Performance metric improvement]
- [Performance metric improvement]

#### 🔗 Compatibility
- Compatible with [Service] v[version]+
- Requires [dependency] [version]+

---
```

## 🔧 Template README.md Microservizio

```markdown
# 🏷️ [Service Name] Service

## 📋 Changelog

### v[VERSION] ([DATE])
#### 🎉 Release Type
- **[Initial Release/Major Update/Minor Update]**: [Description]

#### ✨ Features
- `[endpoint]` - [Endpoint description]
- `[endpoint]` - [Endpoint description]

#### 🔧 Technical Details
- **Framework**: [Framework used]
- **Database**: [Database information]
- **Cache**: [Caching solution]
- **Validation**: [Validation approach]

#### 📊 Performance Metrics
- [Metric]: [Value]
- [Metric]: [Value]
- [Metric]: [Value]

#### 🔗 Dependencies
- [Service] v[version]+
- [Technology] [version]+

#### 🚨 Breaking Changes (if any)
- [Breaking change description]
- **Migration**: [Migration steps]

#### 📚 Documentation
- API Docs: `http://localhost:[port]/docs`
- Health Check: `http://localhost:[port]/health`

---
```

## 🏷️ Template CHECKPOINT.md

```markdown
# 🏋️ GymBro Platform - Checkpoint Sviluppo

## 📅 Data: [DATE]
## 📍 Stato: [Current State Description]

### ✅ Servizi Funzionanti
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
[List all active services with ports]

### 🏷️ Versione Corrente: v[VERSION]

### 🔧 Configurazioni Applicate
1. **[Configuration Type]**: [Description]
2. **[Configuration Type]**: [Description]

### 🚀 Come Continuare da Qui

#### Avviare l'Ambiente
```bash
cd /Users/giamma/workspace/gymbro-platform

# [Commands to start environment]
```

#### Verificare Funzionamento  
```bash
# [Health check commands]
```

#### Test API
```bash
# [API test commands]
```

### 🎯 Roadmap Progress
✅ **v[VERSION]**: [Completed milestone]
✅ **v[VERSION]**: [Completed milestone]  
🔄 **v[VERSION]**: [In progress milestone]
🔄 **v[VERSION]**: [Planned milestone]

### 📁 File Modificati in Questa Release
- `[file path]`: [Description of changes]
- `[file path]`: [Description of changes]

### 🚨 Note Importanti
- [Important note about current state]
- [Migration requirements if any]

### 🔗 Links Utili
- Health Checks: [URLs]
- API Documentation: [URLs]  
- Monitoring: [URLs]

---
*Ultimo aggiornamento: [TIMESTAMP]*
```

## 🏗️ Template Git Tag Message

```
v[VERSION] - [Service/Feature Name]

[Brief description of what this release includes]

📦 Services Updated:
- [service]: [what changed]
- [service]: [what changed]

✨ Features:
- [feature description]
- [feature description]

🔧 Technical:
- [technical improvement]
- [technical improvement]

🐛 Fixes:
- [bug fix]
- [bug fix]

📊 Performance:
- [performance improvement]
- [performance metric]

🚨 Breaking Changes:
- [breaking change description]

🔗 Compatibility:
- [Service] v[version]+
- [Technology] [version]+

📚 Documentation:
- Updated README.md
- Updated service documentation
- Updated CHECKPOINT.md
```

## 📊 Template Commit Message

```
🚀 Release v[VERSION] - [Feature/Service Name]

📦 Services Updated:
- [service]: [brief description]
- [service]: [brief description]

✨ Features:
- [feature]
- [feature]

🔧 Technical:
- [technical change]
- [technical change]

🐛 Fixes:
- [fix]
- [fix]

📊 Performance:
- [performance improvement]

Co-authored-by: GitHub Copilot <noreply@github.com>
```

## 🎨 Emoji Guidelines

### Categorie Standard:
- 🚀 **Release**: Nuove release e deploy
- ✨ **Features**: Nuove funzionalità
- 🔧 **Technical**: Miglioramenti tecnici
- 🐛 **Bug Fixes**: Correzioni di bug
- 📊 **Performance**: Miglioramenti prestazioni
- 🚨 **Breaking**: Breaking changes
- 🔗 **Dependencies**: Dipendenze e compatibilità
- 📚 **Documentation**: Aggiornamenti documentazione
- 🎉 **Major**: Release major o milestone
- 🔄 **In Progress**: Work in progress
- ✅ **Completed**: Completato
- 📦 **Services**: Servizi coinvolti
- 🏷️ **Version**: Informazioni versioning
- 📅 **Date**: Informazioni temporali
- 📍 **Status**: Stato corrente

### Services Icons:
- 👤 **User Management**: Gestione utenti
- 📊 **Data Ingestion**: Ingestione dati
- 🔥 **Calorie Service**: Servizio calorie
- 🍽️ **Meal Service**: Servizio pasti
- 📈 **Analytics**: Analitiche
- 🔔 **Notifications**: Notifiche
- 🚪 **GraphQL Gateway**: Gateway GraphQL
- 🤖 **LLM Service**: Servizi LLM

## 📋 Validation Checklist

### Pre-Release Validation:
- [ ] **Version Number**: Segue Semantic Versioning
- [ ] **Date Format**: DD Mese YYYY (es. 15 Agosto 2025)
- [ ] **Services List**: Tutti i servizi modificati inclusi
- [ ] **Features**: Descrizioni chiare e concise
- [ ] **Technical Details**: Sufficienti per developers
- [ ] **Performance**: Metriche quantificate quando possibile
- [ ] **Compatibility**: Versioni minime specificate
- [ ] **Links**: URL funzionanti e corretti

### Post-Release Validation:
- [ ] **README.md**: Aggiornato correttamente
- [ ] **Service README**: Aggiornati solo servizi modificati
- [ ] **CHECKPOINT.md**: Riflette stato attuale
- [ ] **Git Tag**: Creato e pushato
- [ ] **Documentation**: Accessibile e accurata

## 🔄 Automation Triggers

GitHub Copilot aggiornerà automaticamente i changelog quando rileva:

1. **Nuovo Git Tag**: `git tag -a v[VERSION]`
2. **Keywords nei Commit**: 
   - `🚀 Release v[VERSION]`
   - `feat:`, `fix:`, `docs:`, `perf:`
3. **File Modificati**: 
   - `services/*/` (microservizi)
   - `*.md` (documentazione)
4. **Milestone Raggiunti**:
   - Fine settimana roadmap
   - Feature completate

---

**Usage**: Questi template garantiscono consistency e completezza in tutti i changelog del progetto.
