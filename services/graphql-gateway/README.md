# 🚪 GraphQL Gateway

[![🚀 Production](https://img.shields.io/badge/Status-DEPLOYING-yellow)](https://gymbro-graphql-gateway.onrender.com)
[![💰 Cost](https://img.shields.io/badge/Cost-FREE-success)](https://render.com)
[![🏥 Health](https://img.shields.io/badge/Health-Building-orange)](https://gymbro-graphql-gateway.onrender.com/health)
[![📋 Version](https://img.shields.io/badge/Version-v0.2.0-informational)](https://github.com/giamma80/gymbro-platform/releases/tag/v0.2.0)

## 🚀 **v0.2.0 - DEPLOYING TO PRODUCTION**

**Production URL**: https://gymbro-graphql-gateway.onrender.com (**BUILDING**)  
**Health Check**: https://gymbro-graphql-gateway.onrender.com/health  
**Status**: 🔄 Initial deployment in progress

### 🎯 **Architecture Decision - Hybrid GraphQL Stack**

**Stack Ottimale Adottato**:
- **🌐 API Gateway**: TypeScript + Apollo Server (routing/performance)  
- **🐍 Business Logic**: Python + FastAPI + Strawberry GraphQL (domain services)

**Motivazioni Performance**:
- ⚡ **Gateway Optimization**: Node.js Event Loop ottimale per I/O intensive proxy
- � **Memory Efficiency**: ~30-50MB Node.js vs ~100-200MB Python per gateway  
- 🚀 **Latency**: <10ms overhead vs ~20-50ms Python per request forwarding
- 🔗 **Apollo Federation**: Standard industry maturo per federazione microservizi
- 🎯 **Separation of Concerns**: Thin gateway layer, business logic nei servizi Python

**Pattern Architetturale**:
```
Frontend/Mobile Apps
    ↓
🌐 GraphQL Gateway (TypeScript + Apollo Server) ← Questo servizio
    ↓ ↓ ↓ ↓ 
🐍 user-management (Python + Strawberry)    ← https://gymbro-user-service.onrender.com
🐍 calorie-service (Python + Strawberry)    ← https://gymbro-calorie-service.onrender.com (futuro)
🐍 meal-service (Python + Strawberry)       ← https://gymbro-meal-service.onrender.com (futuro)  
🐍 analytics-service (Python + Strawberry)  ← https://gymbro-analytics-service.onrender.com (futuro)
```

### 🔧 **v0.2.0 - Progressive Enhancement Strategy**

#### **✅ Phase 1: Minimal Server (DEPLOYED)**
- ✅ Basic Express server with health checks
- ✅ Endpoint `/ping`, `/health`, `/` 
- ✅ Production deployment su Render.com
- ✅ CI/CD pipeline integration

#### **🔄 Phase 2: Apollo Server Integration (IN PROGRESS)**
- 🔄 Apollo Server 4.x setup with Federation
- 🔄 Service discovery per User Management
- 🔄 Schema composition con Strawberry services
- 🔄 Error handling e monitoring

#### **🚀 Phase 3: Full Federation (PLANNED)**
- 📋 Multi-service federation attiva
- 📋 Advanced caching strategies  
- 📋 Request/response transforms
- 📋 Security middleware integration

## 🏗️ Setup e Sviluppo

### Prerequisiti
- Node.js 20+ 
- npm o yarn
- PostgreSQL (per servizi backend)

### Installazione
```bash
cd services/graphql-gateway
npm install
```

### Configurazione
Crea file `.env`:
```env
NODE_ENV=development
PORT=4000
USER_MANAGEMENT_URL=http://localhost:8001
CORS_ORIGINS=*
LOG_LEVEL=debug
```

### Avvio Sviluppo
```bash
# Compilazione TypeScript + avvio
npm run dev

# Solo compilazione
npm run build

# Avvio produzione
npm start

# Test
npm test

# Linting
npm run lint
```

## 📊 API Endpoints

### Health Checks
- `GET /ping` - Test connettività base
- `GET /health` - Health check semplice  
- `GET /health/detailed` - Health check completo con stato subgraph

### GraphQL
- `POST /graphql` - Endpoint GraphQL principale
- `GET /graphql` - GraphQL Playground (solo development)

## 🔧 Configurazione

### Environment Variables
| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `PORT` | `4000` | Porta server (dynamic per Render.com) |
| `NODE_ENV` | `development` | Environment |
| `USER_MANAGEMENT_URL` | `http://localhost:8001` | URL User Management Service |
| `CORS_ORIGINS` | `*` | Domini CORS permessi |
| `LOG_LEVEL` | `debug` | Livello logging |

### Subgraph Configuration
Il gateway aggrega automaticamente gli schemi GraphQL da:
- **User Management**: Autenticazione, profili utente
- **Calorie Service**: Calcoli calorici (future)
- **Meal Service**: Gestione pasti (future)  
- **Analytics Service**: Reportistica (future)

## 🐳 Docker

### Build
```bash
docker build -t gymbro-graphql-gateway .
```

### Run
```bash
docker run -p 4000:4000 \
  -e USER_MANAGEMENT_URL=http://user-service:8000 \
  gymbro-graphql-gateway
```

## 🚀 Deployment

### Render.com (Raccomandato)
Il servizio è ottimizzato per Render.com seguendo le [lezioni apprese](../../CHECKPOINT.md) dal deployment di User Management:

**render.yaml**:
```yaml
services:
  - type: web
    name: gymbro-graphql-gateway
    env: node
    buildCommand: npm ci && npm run build
    startCommand: npm start
    healthCheckPath: /health
    envVars:
      - key: PORT
        generateValue: true
      - key: USER_MANAGEMENT_URL
        value: https://gymbro-user-service.onrender.com
```

### Best Practices Applicate
✅ **Port Binding Dinamico**: `PORT=${PORT:-4000}`  
✅ **Health Checks**: Endpoint `/health` + `/ping`  
✅ **CORS Permissivo**: Per debug MVP  
✅ **Multi-stage Docker**: Build ottimizzato  
✅ **Error Handling**: Graceful degradation  

## 🧪 Testing

### Test Strategy
- **Unit Tests**: Logic del gateway e configurazione
- **Integration Tests**: Connettività con subgraph
- **E2E Tests**: GraphQL queries complete

### Comandi Test
```bash
# Test unitari
npm test

# Test con coverage
npm run test:coverage

# Test integration (richiede servizi attivi)
npm run test:integration
```

## 📈 Monitoring

### Health Monitoring
```bash
# Test connettività
curl http://localhost:4000/ping

# Health check basic
curl http://localhost:4000/health

# Health check dettagliato
curl http://localhost:4000/health/detailed
```

### GraphQL Introspection
```bash
# Schema introspection
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query IntrospectionQuery { __schema { types { name } } }"}'
```

## 🔄 Development Workflow

### Federation Development
1. **Implementa nuovo servizio** (es. Calorie Service con Strawberry)
2. **Aggiungi subgraph** nel gateway configuration
3. **Update schema** via Apollo introspection
4. **Test integration** con Postman/GraphQL Playground

### Code Quality
- **TypeScript Strict**: Configurazione rigorosa
- **ESLint + Prettier**: Code formatting automatico  
- **Husky**: Pre-commit hooks
- **Jest**: Test framework

## 🔗 Collegamenti
- **Production URL**: TBD (dopo deployment)
- **User Management API**: https://gymbro-user-service.onrender.com
- **Main Repository**: https://github.com/giamma80/gymbro-platform
- **Architecture Docs**: [../../docs/](../../docs/)

---

**Versione**: v0.2.0  
**Deployment**: Render.com ready  
**Stack**: TypeScript + Apollo Server + Express  
**Status**: 🔄 In Development
