# 🌐 Apollo Gateway - GraphQL Federation Gateway

**GymBro Platform Unified API** | **Apollo Federation v2.5**

---

## 🎯 Overview

Apollo Gateway per la piattaforma GymBro che unifica tutti i microservizi GraphQL in un singolo endpoint. Implementa Apollo Federation v2.5 per creare una supergraph che combina schemi da:

- **user-management** (porta 8001)
- **calorie-balance** (porta 8002)  
- **meal-tracking** (porta 8003)
- **health-monitor** (porta 8004)
- **ai-coach** (porta 8005)
- **notifications** (porta 8006)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Microservizi con GraphQL endpoints attivi

### Installation
```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start in development
npm run dev

# Start in production
npm run start:prod
```

### Health Check
```bash
# Check gateway health
npm run health-check

# Manual health check
curl http://localhost:4000/health
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────────────────────────┐
│   Client Apps   │────▶│        Apollo Gateway              │
│                 │    │         :4000/graphql              │
└─────────────────┘    └─────────────────┬───────────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │                       │                       │
                 ▼                       ▼                       ▼
        ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
        │ user-management │    │ calorie-balance │    │  meal-tracking  │
        │     :8001       │    │     :8002       │    │     :8003       │
        └─────────────────┘    └─────────────────┘    └─────────────────┘
                 │                       │                       │
                 ▼                       ▼                       ▼
        ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
        │ health-monitor  │    │    ai-coach     │    │  notifications  │
        │     :8004       │    │     :8005       │    │     :8006       │
        └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment (development/production) | `development` |
| `GATEWAY_PORT` | Gateway server port | `4000` |
| `GATEWAY_HOST` | Gateway server host | `0.0.0.0` |
| `GRAPHQL_PATH` | GraphQL endpoint path | `/graphql` |
| `POLL_INTERVAL` | Schema polling interval (ms) | `30000` |
| `CORS_ORIGINS` | Allowed CORS origins | `localhost:3000,localhost:8080` |
| `LOG_LEVEL` | Logging level | `info` |

### Subgraph URLs
- `USER_MANAGEMENT_URL`: User management GraphQL endpoint
- `CALORIE_BALANCE_URL`: Calorie balance GraphQL endpoint  
- `MEAL_TRACKING_URL`: Meal tracking GraphQL endpoint
- `HEALTH_MONITOR_URL`: Health monitor GraphQL endpoint
- `AI_COACH_URL`: AI coach GraphQL endpoint
- `NOTIFICATIONS_URL`: Notifications GraphQL endpoint

## 🔧 Development

### Scripts
```bash
npm run dev          # Development with nodemon
npm run start        # Production start
npm run test         # Run tests
npm run lint         # ESLint check
npm run health-check # Health verification
```

### GraphQL Playground
In development mode:
- **Gateway**: http://localhost:4000/graphql
- **Health**: http://localhost:4000/health

### Logs
- Development: Console with colors
- Production: JSON format + file logging

## 📊 Federation Features

- ✅ **Automatic Schema Composition**: Composes schemas from all subgraphs
- ✅ **Query Planning**: Efficient cross-service query execution
- ✅ **Error Handling**: Centralized error formatting and logging
- ✅ **Health Monitoring**: Service availability checking
- ✅ **CORS Support**: Configurable cross-origin requests
- ✅ **Security**: Helmet.js protection
- ✅ **Graceful Shutdown**: Clean server termination

## 🧪 Testing

```bash
# Unit tests
npm test

# Integration tests with running services
npm run test:integration

# Health check
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { __schema { types { name } } }"}'
```

## 🚀 Deployment

### Docker
```bash
# Build image
docker build -t apollo-gateway .

# Run container
docker run -p 4000:4000 --env-file .env apollo-gateway
```

### Production Checklist
- [ ] Set `NODE_ENV=production`
- [ ] Configure all subgraph URLs
- [ ] Set up proper CORS origins
- [ ] Configure logging level
- [ ] Set up health monitoring
- [ ] Configure Apollo Studio (optional)

## 📚 Next Steps

1. **Implement Subgraphs**: Add GraphQL to existing microservices
2. **Authentication**: Add JWT token validation
3. **Rate Limiting**: Implement query complexity analysis
4. **Caching**: Add response caching with Redis
5. **Monitoring**: Integrate with Apollo Studio
6. **Testing**: Add comprehensive integration tests

## 🔗 Resources

- [Apollo Federation Docs](https://www.apollographql.com/docs/federation/)
- [GymBro API Federation Guide](../../docs/API_FEDERATION_GUIDE.md)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)

---

**Created**: 16 settembre 2025 | **Status**: 🚧 In Development