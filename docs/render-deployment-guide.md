# 🚀 GymBro Platform - Render.com Deployment Guide
# ================================================================

## 🎯 Deploy Configuration per Render.com (100% Free Tier)

### ✅ **VANTAGGI REDIS-FREE DEPLOYMENT:**
- 💰 **Zero costi**: Solo PostgreSQL managed gratuito
- 🚀 **Setup semplificato**: Nessuna configurazione Redis
- 📊 **Performance MVP**: Cache in-memory sufficiente
- 🔄 **Scaling path**: Migrazione a Redis quando necessario

---

## 📋 **RENDER.COM DEPLOYMENT STEPS**

### 🎉 **QUICK DEPLOY** - `render.yaml` già configurato!
```yaml
# File: render.yaml (già creato nella root del progetto)
# Deploy automatico: basta connettere GitHub a Render.com
```

### 1️⃣ **Setup Account Render.com**
```bash
1. Vai su https://render.com
2. Sign up con GitHub account
3. Autorizza accesso al repository gymbro-platform
```

### **2. Creare Web Service**
```bash
1. Dashboard Render → "New +" → "Web Service"
2. Connect GitHub repository: gymbro-platform
3. Nome service: gymbro-user-management
4. Branch: main
5. Root Directory: services/user-management
6. Runtime: Docker
7. Dockerfile path: Dockerfile
```

### **3. Environment Variables (Render Dashboard)**
```bash
# 🗄️ Database (Render PostgreSQL Free)
DATABASE_URL=<render-postgresql-url>  # Auto-generated

# 🔐 Security & Auth
JWT_SECRET=your-super-secret-jwt-key-change-in-production-render
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# 🏃 Application
ENVIRONMENT=production
DEBUG=false
APP_NAME=GymBro Platform
APP_VERSION=1.0.0

# 📧 Email (SendGrid Free Tier)
SENDGRID_API_KEY=<your-sendgrid-api-key>
FROM_EMAIL=noreply@gymbro.app

# 🔍 Monitoring (Optional - Sentry Free Tier)
SENTRY_DSN=<your-sentry-dsn>

# 🌐 CORS (Render auto-generated URLs)
CORS_ORIGINS=["https://gymbro-user-management.onrender.com"]
```

### **4. Creare PostgreSQL Database**
```bash
1. Dashboard Render → "New +" → "PostgreSQL"
2. Nome: gymbro-postgres
3. Plan: Free ($0/month)
4. Region: Same as web service
5. Copy "External Database URL"
6. Aggiungi come DATABASE_URL nel web service
```

### **5. Deploy Configuration**
```bash
# Build & Deploy Settings:
Build Command: (empty - usa Dockerfile)
Start Command: (empty - usa Dockerfile CMD)

# Auto-Deploy:
✅ Auto-Deploy: Yes
✅ Branch: main

# Health Check:
Health Check Path: /health
```

---

## 🔧 **DOCKERFILE OPTIMIZATION (già pronto)**

Il Dockerfile in `services/user-management/` è già ottimizzato per Render:

```dockerfile
# Multi-stage build per dimensioni ridotte
FROM python:3.11-slim as builder
# Poetry installation e dependency building
FROM python:3.11-slim as runtime  
# Production runtime con solo dependencies necessarie
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 **MONITORING & VALIDATION**

### **Health Check Endpoints:**
```bash
# Health check
GET https://gymbro-user-management.onrender.com/health

# API Documentation  
GET https://gymbro-user-management.onrender.com/docs

# Example API call
POST https://gymbro-user-management.onrender.com/auth/register
```

### **Expected Response Times (Free Tier):**
```bash
🔄 Cold Start: 30-60 seconds (prima richiesta)
⚡ Warm Requests: <500ms
🗄️ Database: 5-20ms (PostgreSQL free tier)
🧠 Cache: <1ms (in-memory)
```

---

## 🔄 **CI/CD INTEGRATION**

### **GitHub Actions Auto-Deploy:**
```yaml
# Il webhook Render è già configurato in CI/CD:
- name: Deploy to Render
  if: github.ref == 'refs/heads/main'
  run: |
    curl -X POST "${{ secrets.RENDER_STAGING_DEPLOY_HOOK }}"
```

### **Setup Deploy Hook:**
```bash
1. Render Dashboard → Service Settings → Build & Deploy
2. Copy "Deploy Hook URL" 
3. GitHub Repository → Settings → Secrets
4. Add secret: RENDER_STAGING_DEPLOY_HOOK=<hook-url>
```

---

## 💡 **PRODUCTION OPTIMIZATIONS**

### **Performance Tuning:**
```bash
# Environment Variables per Production:
WORKER_PROCESSES=1  # Free tier limit
MAX_CONNECTIONS=20  # Database connection pool
CACHE_TTL=3600     # 1 hour cache TTL
LOG_LEVEL=WARNING  # Reduce logging overhead
```

### **Security Hardening:**
```bash
# Production Security:
JWT_SECRET=<generate-strong-32-char-secret>
CORS_ORIGINS=["https://your-frontend-domain.com"]
DEBUG=false
SENTRY_DSN=<your-sentry-dsn>
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues:**
```bash
# Build Failures:
- Check Dockerfile syntax
- Verify Poetry dependencies
- Check Python version compatibility

# Runtime Errors:
- Check environment variables
- Verify database connection
- Check logs in Render dashboard

# Performance Issues:
- Monitor cold start times
- Check database query performance
- Optimize cache usage
```

### **Logs & Debugging:**
```bash
# Render Dashboard:
1. Service → Logs tab
2. Real-time log streaming
3. Historical logs available

# Health Check:
curl https://gymbro-user-management.onrender.com/health
```

---

## 📈 **SCALING STRATEGY**

### **When to Upgrade from Free Tier:**
```bash
# Metrics to Monitor:
- Daily active users > 1000
- Response times > 2 seconds consistently  
- Database connections limit reached
- Need for custom domains

# Upgrade Path:
1. Render Pro Plan: $7/month
2. Add Redis: $10/month
3. Custom domain: Included in Pro
4. Enhanced performance: 2x faster
```

### **Redis Re-integration (Future):**
```bash
# When needed, add back Redis:
1. Create Render Redis service
2. Add REDIS_URL environment variable
3. Uncomment Redis code in user-management
4. Deploy with zero downtime
```

---

## 🎯 **SUCCESS METRICS**

### **MVP Success Indicators:**
```bash
✅ Deploy Success: Service healthy
✅ Database Connected: PostgreSQL queries working
✅ API Functional: /health returns 200
✅ Authentication: JWT tokens working
✅ Performance: <2s response times
✅ Cost: $0/month achieved
```

### **Ready for User Testing:**
```bash
🧪 Registration/Login flow working
📊 User profiles CRUD operations
🔐 JWT authentication & authorization
📱 API documentation accessible
🏥 Health monitoring active
```

---

*Deploy Guide - 15 Agosto 2025*
*Target: Zero-cost MVP deployment su Render.com*
