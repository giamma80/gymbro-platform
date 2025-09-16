# 🌐 Apollo Gateway - Render Deployment Guide

**GymBro Platform GraphQL Federation** | **Target**: Production Ready

---

## 🎯 Deployment Overview

Apollo Gateway si deploierà su Render.com e fungerà da **endpoint GraphQL unificato** che federa tutti i microservizi della piattaforma GymBro.

### Architecture Flow
```
📱 Client Apps 
     ⬇ HTTPS
🌐 Apollo Gateway (Render)
     ⬇ HTTPS  
┌─────────────────────────────────────────────┐
│ 👥 user-management.onrender.com/graphql    │
│ 🍎 calorie-balance.onrender.com/graphql    │ 
│ 🚧 meal-tracking.onrender.com/graphql      │
│ 💊 health-monitor.onrender.com/graphql     │
│ 🤖 ai-coach.onrender.com/graphql           │
│ 📨 notifications.onrender.com/graphql      │
└─────────────────────────────────────────────┘
```

---

## 🚀 Deployment Steps

### 1. **Pre-requisiti**
- ✅ user-management deployato su Render
- ✅ calorie-balance deployato su Render
- ✅ GitHub repository con apollo-gateway
- ✅ Render account configurato

### 2. **Render Service Setup**

**Creare il servizio su Render:**
```yaml
# render.yaml configuration
services:
  - type: web
    name: apollo-gateway
    runtime: node
    plan: starter
    region: frankfurt
    buildCommand: npm ci
    startCommand: npm start
    rootDir: services/apollo-gateway
```

### 3. **Environment Variables**

**Variabili necessarie su Render:**

| Variable | Value | Description |
|----------|-------|-------------|
| `NODE_ENV` | `production` | Environment mode |
| `GATEWAY_PORT` | `4000` | Server port |
| `GATEWAY_HOST` | `0.0.0.0` | Server host |
| `LOG_LEVEL` | `info` | Logging level |
| `CORS_ORIGINS` | `https://your-app.com` | Allowed origins |

**Subgraph URLs (aggiorna con gli URL reali):**

| Variable | Value |
|----------|-------|
| `USER_MANAGEMENT_URL` | `https://gymbro-user-management.onrender.com/graphql` |
| `CALORIE_BALANCE_URL` | `https://gymbro-calorie-balance.onrender.com/graphql` |

### 4. **Health Check Configuration**

- **Health Check Path**: `/health`
- **Expected Response**: `200 OK`
- **Format**: JSON con `status: "ok"`

---

## 🔗 URL Management Strategy

### Ambiente-Based Configuration

**Development (locale):**
- user-management: `http://localhost:8001/graphql`
- calorie-balance: `http://localhost:8002/graphql`

**Production (Render):**
- user-management: `https://gymbro-user-management.onrender.com/graphql`
- calorie-balance: `https://gymbro-calorie-balance.onrender.com/graphql`

### Dynamic URL Resolution

Il gateway automaticamente seleziona gli URL corretti basandosi su `NODE_ENV`:

```javascript
// src/config/index.js
url: process.env.NODE_ENV === 'production' 
  ? process.env.USER_MANAGEMENT_URL || 'https://gymbro-user-management.onrender.com/graphql'
  : process.env.USER_MANAGEMENT_URL || 'http://localhost:8001/graphql'
```

---

## 🧪 Testing in Production

### 1. **Health Check**
```bash
curl https://apollo-gateway.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "apollo-gateway", 
  "timestamp": "2025-09-16T...",
  "environment": "production"
}
```

### 2. **Schema Introspection**
```bash
curl -X POST https://apollo-gateway.onrender.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```

### 3. **Federation Query**
```bash
curl -X POST https://apollo-gateway.onrender.com/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { 
      listUsers(limit: 2) { 
        success 
        data { id email } 
      } 
      listCalorieBalances(limit: 2) { 
        success 
        data { id name } 
      } 
    }"
  }'
```

---

## 📊 Monitoring & Debugging

### Service Health Monitoring
- **Gateway Health**: `https://apollo-gateway.onrender.com/health`
- **Subgraph Health**: Gateway logs will show subgraph connectivity

### Common Issues & Solutions

**1. Subgraph Connection Failed**
- **Symptom**: `Failed to load service list from remote endpoint`
- **Solution**: Verify subgraph URLs are correct and services are running
- **Check**: Environment variables on Render

**2. CORS Issues**
- **Symptom**: Browser blocks GraphQL requests
- **Solution**: Add frontend domain to `CORS_ORIGINS`
- **Example**: `CORS_ORIGINS=https://app.nutrifit.com,https://admin.nutrifit.com`

**3. Schema Composition Error**
- **Symptom**: Gateway fails to start
- **Solution**: Check subgraph SDL compatibility
- **Debug**: Review Render logs for composition errors

### Render Logs
```bash
# View logs
render logs --service apollo-gateway --tail

# Check health
render ps --service apollo-gateway
```

---

## 🔄 CI/CD Integration

### GitHub Actions Flow
1. **Code Push** → GitHub repository
2. **CI Tests** → Apollo Gateway tests
3. **Auto Deploy** → Render detects changes
4. **Health Check** → Render verifies `/health`
5. **Live** → Gateway available at production URL

### Deployment Verification
```bash
# Automatic via GitHub Actions
✅ Linting
✅ Unit tests  
✅ Docker build test
✅ Auto-deploy to Render
```

---

## 📈 Performance Considerations

### Render Plan Recommendations
- **Development**: Starter Plan ($7/month)
- **Production**: Professional Plan ($25/month)
- **Enterprise**: Team Plan ($85/month)

### Optimization Features
- **Query Caching**: Enable Redis for production
- **Rate Limiting**: Implement query complexity limits
- **CDN**: Use Render's built-in CDN
- **Auto-scaling**: Enable for high traffic

---

## 🔒 Security Checklist

- [ ] **CORS**: Configured with specific origins
- [ ] **HTTPS**: Enforced in production
- [ ] **Headers**: Helmet.js security headers
- [ ] **Input Validation**: GraphQL schema validation
- [ ] **Error Handling**: No sensitive data in errors
- [ ] **Rate Limiting**: Query complexity protection
- [ ] **Authentication**: JWT validation (future)

---

## 🎯 Post-Deployment Checklist

### Verification Steps
- [ ] Health check returns 200
- [ ] Schema introspection works
- [ ] Cross-service queries execute
- [ ] Error handling works properly
- [ ] Logs are readable and informative
- [ ] Performance is within targets (<500ms)

### Integration Testing
- [ ] Frontend can connect to gateway
- [ ] All subgraphs are accessible
- [ ] Federation directives work
- [ ] Authentication (when implemented)

---

**Deployment Status**: 🚧 Ready for Production  
**Expected URL**: `https://apollo-gateway.onrender.com`  
**Last Updated**: 16 settembre 2025

---

**Next Steps**: Deploy to Render → Test federation → Add remaining services