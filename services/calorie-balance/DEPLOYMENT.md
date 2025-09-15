# Calorie Balance Service - Deployment Guide

## 🚀 Quick Start

### Local Development

1. **Setup Environment**
   ```bash
   cd services/calorie-balance
   cp .env.template .env
   # Edit .env with your Supabase credentials
   ```

2. **Install Dependencies**
   ```bash
   poetry install
   ```

3. **Deploy Database Schema**
   ```bash
   # Execute SQL scripts in order on Supabase:
   # 1. sql/000_reset_schema.sql
   # 2. sql/001_initial_schema.sql  
   # 3. sql/002_temporal_views.sql
   # 4. sql/003_grants.sql
   
   # Verify deployment:
   # Execute sql/check_current_permissions.sql
   ```

4. **Start Development Server**
   ```bash
   ./start-dev.sh
   # Or manually:
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
   ```

5. **Verify Service**
   ```bash
   curl http://localhost:8002/health
   curl http://localhost:8002/docs  # API documentation
   ```

### Production Deployment

#### Render.com (Recommended)

1. **Prerequisites**
   - GitHub repository with the code
   - Render.com account  
   - Supabase project setup with calorie_balance schema deployed

2. **Setup Steps**
   ```bash
   # 1. Deploy database schema first (manually via Supabase SQL Editor)
   # 2. Push code to GitHub
   git add .
   git commit -m "feat: add calorie-balance service"
   git push origin main
   ```

3. **Environment Variables**
   Set these in Render dashboard:
   ```
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=INFO
   PORT=8001
   DATABASE_SCHEMA=calorie_balance
   
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-key
   
   SECRET_KEY=your-secure-production-key
   JWT_SECRET_KEY=your-jwt-production-key
   JWT_ALGORITHM=HS256
   
   ALLOWED_ORIGINS=https://your-frontend-domain.com
   ```

4. **Build Configuration**
   ```
   Build Command: poetry install --only=main
   Start Command: poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

## 🗄️ Database Schema

### Event-Driven Architecture

The Calorie Balance service uses a 5-level temporal analytics system:

1. **High-Frequency Events** (`calorie_events`) - Real-time data collection
2. **Daily Aggregations** (`daily_balances`) - Performance optimization  
3. **Analytics Views** - 5 temporal levels (hourly, daily, weekly, monthly, balance)
4. **Goal Management** (`calorie_goals`) - Dynamic targets with AI optimization
5. **Metabolic Profiles** (`metabolic_profiles`) - BMR/TDEE calculations

### Schema Deployment

**Sequential execution required:**
1. `000_reset_schema.sql` - Schema cleanup and setup
2. `001_initial_schema.sql` - Core tables and business functions
3. `002_temporal_views.sql` - 5-level analytics views  
4. `003_grants.sql` - Row Level Security and permissions

### Verification

Use `sql/check_current_permissions.sql` to audit:
- Schema existence and accessibility
- Table security status (RLS enabled)
- Row Level Security policies  
- Role privileges on tables and views
- Function execution privileges
- Security validation checklist

## 🔒 Security

### Row Level Security (RLS)

All tables have RLS enabled with policies:
- **Users**: Can only access their own data (`auth.uid()::text = user_id`)
- **Anonymous**: No access to personal calorie data
- **Service Role**: Full access for backend operations
- **Analytics Role**: Read-only access to aggregated data

### API Security

- JWT token authentication via Supabase
- CORS configuration for allowed origins
- Request rate limiting (configurable)
- Input validation on all endpoints

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/e2e/
```

## 📊 Monitoring

### Health Checks

- **Basic**: `/health` - Service status
- **Database**: `/health/db` - Database connectivity  
- **Dependencies**: `/health/deps` - External service status

### Logging

Structured logging with levels:
- `DEBUG` - Development details
- `INFO` - Operational information
- `WARNING` - Potential issues
- `ERROR` - Service errors
- `CRITICAL` - Service failures

### Metrics

Key metrics to monitor:
- Request rate and latency
- Database connection pool status
- Event processing throughput
- Goal achievement rates
- Data quality scores

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check connection string
   echo $SUPABASE_URL
   
   # Verify schema exists
   # Execute: sql/debug_schema.sql
   ```

2. **Permission Errors**
   ```bash
   # Check RLS policies
   # Execute: sql/check_current_permissions.sql
   ```

3. **Event Processing Issues**
   ```bash
   # Check logs for event validation errors
   poetry run python -m app.debug_events
   ```

### Performance Optimization

- Monitor view query performance
- Consider materialized views for heavy aggregations
- Index optimization for high-frequency queries
- Connection pool tuning

## 📈 Scaling Considerations

- **Horizontal Scaling**: Stateless service design allows multiple instances
- **Database**: Event partitioning by date for large datasets
- **Caching**: Consider Redis for frequent aggregation queries
- **Event Processing**: Queue system for high-throughput scenarios

## 🔄 CI/CD Pipeline

1. **Code Quality**: Linting, type checking, security scanning
2. **Testing**: Unit, integration, and E2E tests
3. **Database Migration**: Schema validation and deployment
4. **Deployment**: Blue-green deployment with health checks
5. **Monitoring**: Performance and error tracking