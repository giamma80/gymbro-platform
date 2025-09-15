# Calorie Balance Service - Render Deployment Guide

## 🚀 Render.com Deployment

### Prerequisites
- ✅ GitHub repository with the code
- ✅ Render.com account
- ✅ Supabase project setup
- ✅ Docker configuration tested locally

### Step-by-Step Deployment

#### 1. **Prepare Code**
```bash
# Ensure all changes are committed and pushed
cd /Users/giamma/workspace/gymbro-platform
git add .
git commit -m "feat: calorie-balance Docker and Render configuration"
git push origin main
```

#### 2. **Render Service Configuration**

**Service Settings:**
- **Name**: `nutrifit-calorie-balance`
- **Runtime**: Docker
- **Repository**: `https://github.com/giamma80/gymbro-platform.git`
- **Root Directory**: `services/calorie-balance`
- **Docker Context**: `services/calorie-balance`
- **Dockerfile Path**: `./Dockerfile`
- **Branch**: `main`
- **Auto Deploy**: Enabled

**Advanced Settings:**
- **Plan**: Starter ($7/month)
- **Region**: Oregon (for performance)
- **Health Check Path**: `/health`

#### 3. **Environment Variables**

**Automatic (from render.yaml):**
- `ENVIRONMENT=production`
- `PORT=8000`
- `PYTHONDONTWRITEBYTECODE=1`
- `PYTHONUNBUFFERED=1`

**Manual Setup Required:**
Add these in Render Dashboard → Service → Environment:

```bash
# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Database Schema
DATABASE_SCHEMA=calorie_balance

# Security (REQUIRED)  
SECRET_KEY=your-production-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256

# CORS (adjust for your frontend)
ALLOWED_ORIGINS=https://your-frontend-domain.com

# Optional Features
ENABLE_REAL_TIME=true
ENABLE_AUTH=true
ENABLE_STORAGE=false
```

#### 4. **Deploy Process**

1. **Push Code**: Ensure latest changes are on GitHub
2. **Render Auto-Deploy**: Service will auto-deploy from render.yaml
3. **Monitor Logs**: Check Render dashboard for deployment status
4. **Health Check**: Service should respond at `/health`

#### 5. **Verification**

Once deployed, verify the service:

```bash
# Health check
curl https://nutrifit-calorie-balance.onrender.com/health

# API documentation
curl https://nutrifit-calorie-balance.onrender.com/docs

# GraphQL endpoint
curl -X POST https://nutrifit-calorie-balance.onrender.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } } }"}'
```

### Expected Output

**Healthy Service Response:**
```json
{
  "status": "healthy",
  "service": "calorie-balance", 
  "timestamp": 1757963013.573322
}
```

### Troubleshooting

#### Common Issues

1. **Port Configuration**
   - Development: Port 8002 (docker-compose)
   - Production: Port 8000 (Render standard)

2. **Environment Variables**
   - Ensure all Supabase credentials are set
   - Verify SECRET_KEY is production-ready
   - Check ALLOWED_ORIGINS for CORS

3. **Health Check Failures**
   - Verify `/health` endpoint is accessible
   - Check Dockerfile exposes correct port
   - Ensure Supabase connection is working

#### Debug Commands

```bash
# Local Docker test (development)
cd services/calorie-balance
docker-compose up --build

# Local Docker test (production simulation)  
docker build --target production -t calorie-balance-prod .
docker run -p 8000:8000 --env-file .env calorie-balance-prod

# View Render logs
# Go to Render Dashboard → Service → Logs
```

### Performance Optimization

#### Render Service Settings
- **Plan**: Starter ($7/month) - suitable for development
- **Auto-Deploy**: Enabled for continuous deployment
- **Build Filter**: Only deploys when `services/calorie-balance/**` changes

#### Docker Optimizations
- Multi-stage build (development/production targets)
- Non-root user for security
- Health checks enabled
- Dependency caching

### Integration with Platform

#### Service Discovery
- **Development**: `http://localhost:8002`
- **Production**: `https://nutrifit-calorie-balance.onrender.com`

#### GraphQL Federation
- Endpoint: `/graphql`
- Federation SDL: `{ _service { sdl } }`
- Compatible with Apollo Gateway

### Next Steps

1. ✅ **Deploy calorie-balance** using this guide
2. ⏳ **Setup monitoring** with Render metrics
3. ⏳ **Configure custom domain** (optional)
4. ⏳ **Setup CI/CD pipeline** with automated testing

---

**🎊 Status: Ready for Production Deployment**
- Docker configuration: ✅ Tested and working
- Render configuration: ✅ Aligned with user-management
- Documentation: ✅ Complete deployment guide
- Environment: ✅ Simplified (no Redis/PostgreSQL dependencies)