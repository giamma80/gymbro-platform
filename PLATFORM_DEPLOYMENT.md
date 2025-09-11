# 🚀 NutriFit Platform - Render Deployment Guide

## 🏗️ **Architettura Platform-Level**

Questo deployment è configurato per gestire **tutta la piattaforma NutriFit** come un ecosistema di microservizi orchestrato.

### ✅ **Vantaggi del Nuovo Approccio**

- **🎯 Centralizzato**: Una sola configurazione per tutti i servizi
- **🔧 Scalabile**: Aggiunta di nuovi microservizi semplificata
- **⚡ Efficiente**: Build solo dei servizi modificati
- **🛡️ Sicuro**: Secrets centralizzati e gestione coerente
- **📊 Monitorabile**: Dashboard unificato per tutta la piattaforma

## 📋 **Configurazione Attuale**

### **Microservizi Configurati**
1. **user-management** - Gestione utenti e autenticazione
2. **calorie-balance** - Calcolo bilancio calorico *(da implementare)*

### **Infrastruttura Condivisa**
- **Redis Cache** - Condiviso tra tutti i servizi
- **Supabase PostgreSQL** - Database con schema multipli
- **GitHub Container Registry** - Repository Docker images

## 🚀 **Step 1: Deploy su Render**

### 1.1 **Blueprint Deployment**

1. **Login su [render.com](https://render.com)**
2. **Create → Blueprint**
3. **Connect Repository**: `https://github.com/giamma80/gymbro-platform`
4. **Blueprint file**: `render.yaml` (root del repository)

### 1.2 **Environment Variables**

⚠️ **Configura nel Render Dashboard per OGNI servizio**:

```bash
# =================================
# User Management Service
# =================================

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
PORT=8000
DATABASE_SCHEMA=user_management

# Supabase (copia dal tuo .env locale)
SUPABASE_URL=https://eipgaagzdoonlrnigtte.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Security (auto-generate in Render)
SECRET_KEY=[AUTO-GENERATE]
JWT_SECRET_KEY=[AUTO-GENERATE]
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS
ALLOWED_ORIGINS=https://nutrifit.app,https://app.nutrifit.app

# Features
ENABLE_REAL_TIME=true
ENABLE_AUTH=true
ENABLE_STORAGE=false

# Performance  
RATE_LIMIT_REQUESTS_PER_MINUTE=100
REQUEST_TIMEOUT_SECONDS=30
MAX_CONNECTIONS=200
WORKERS=2

# =================================
# Calorie Balance Service (future)
# =================================
# Stesse variabili ma con:
# DATABASE_SCHEMA=calorie_balance
# USER_MANAGEMENT_URL=https://nutrifit-user-management.onrender.com
```

## 🔑 **Step 2: GitHub Secrets (Opzionali)**

Per abilitare deploy automatici avanzati:

**Repository → Settings → Secrets → Actions**

```bash
# Per future integrazioni Render API
RENDER_API_KEY=rnd_[your-key]  # Optional per ora
```

## 🎯 **Step 3: Deployment Process**

### **Automatic Deployment**

Il sistema detecta automaticamente i cambiamenti:

```bash
# Deploy user-management se modifichi:
services/user-management/**

# Deploy calorie-balance se modifichi:  
services/calorie-balance/**

# Deploy tutti i servizi se modifichi:
render.yaml
```

### **Manual Deployment**

**GitHub → Actions → NutriFit Platform CI/CD → Run workflow**

- **services**: `all` o `user-management,calorie-balance`

## 📊 **Step 4: Monitoring & URLs**

### **Service URLs**
- **User Management**: https://nutrifit-user-management.onrender.com
- **API Docs**: https://nutrifit-user-management.onrender.com/docs
- **Health Check**: https://nutrifit-user-management.onrender.com/health

### **Platform Status**
- **Render Dashboard**: Monitor tutti i servizi
- **GitHub Actions**: CI/CD pipeline status
- **Container Registry**: Docker images su ghcr.io

## 🔧 **Step 5: Aggiungere Nuovi Microservizi**

### 5.1 **Struttura Directory**
```bash
services/
├── user-management/        # ✅ Existing
├── calorie-balance/        # ✅ Configured
├── workout-tracking/       # 🚀 Future
├── nutrition-planning/     # 🚀 Future
└── progress-analytics/     # 🚀 Future
```

### 5.2 **Aggiornare Configurazione**

1. **Aggiungi in `render.yaml`**:
```yaml
- type: web
  name: nutrifit-workout-tracking
  repo: https://github.com/giamma80/gymbro-platform.git
  rootDir: services/workout-tracking
  dockerfilePath: ./Dockerfile
  # ... rest of config
```

2. **Aggiorna GitHub Action**:
```yaml
# In detect-changes job
if echo "$CHANGED_FILES" | grep -q "services/workout-tracking/"; then
  SERVICES="$SERVICES workout-tracking"
fi
```

3. **Deploy automatico** al prossimo push!

## 🚨 **Troubleshooting**

### **Build Failures**
```bash
# Check GitHub Actions logs
# Verify Dockerfile in each service
# Ensure Poetry dependencies are locked
```

### **Deployment Issues**
```bash
# Check Render service logs
# Verify environment variables
# Test health endpoints
```

### **Service Communication**
```bash
# Use environment variables for service URLs
USER_MANAGEMENT_URL=https://nutrifit-user-management.onrender.com

# Implement service discovery pattern
# Add health checks between services
```

## 🎉 **Success Checklist**

- [x] **Blueprint deployed** su Render
- [x] **Environment variables** configurate
- [x] **Health checks** funzionanti
- [x] **CI/CD pipeline** attiva
- [x] **Docker images** buildando
- [x] **Monitoring** setup

## 🔄 **Next Steps**

1. **🚀 Deploy user-management** seguendo questa guida
2. **🧪 Test endpoints** con Postman/curl
3. **📱 Implementa calorie-balance** service
4. **🔗 Service communication** tra microservizi
5. **📊 Setup monitoring** e alerting
6. **🌐 Custom domain** se necessario

---

## 🌟 **Architettura Target**

```
Internet
    ↓
[Load Balancer/CDN]
    ↓
[API Gateway] (future)
    ↓
┌─────────────────────────────────────┐
│           NutriFit Platform         │
├─────────────┬─────────────┬─────────┤
│user-mgmt    │calorie-bal  │workout  │
│   :8000     │   :8000     │  :8000  │
│             │             │         │
│ [Supabase]  │ [Supabase]  │[Supabase│
│user_mgmt    │calorie_bal  │workout  │
│schema       │schema       │schema   │
└─────────────┴─────────────┴─────────┘
              ↓
        [Redis Cache]
```

**Platform URL**: https://nutrifit-platform.onrender.com *(future)*
