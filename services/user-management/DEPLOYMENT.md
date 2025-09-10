# User Management Service - Deployment Guide

## 🚀 Quick Start

### Local Development

1. **Setup Environment**
   ```bash
   cd services/user-management
   cp .env.template .env
   # Edit .env with your Supabase credentials
   ```

2. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Using Poetry (Native)**
   ```bash
   poetry install
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

### Production Deployment

#### Render.com (Recommended)

1. **Prerequisites**
   - GitHub repository with the code
   - Render.com account
   - Supabase project setup

2. **Setup Steps**
   ```bash
   # 1. Push code to GitHub
   git add .
   git commit -m "feat: add deployment infrastructure"
   git push origin main
   
   # 2. Create Render service
   # - Go to Render.com dashboard
   # - Connect your GitHub repository
   # - Use render.yaml for configuration
   ```

3. **Environment Variables**
   Set these in Render dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `SECRET_KEY` (auto-generated)
   - `JWT_SECRET_KEY` (auto-generated)

#### Manual Docker Deployment

```bash
# Build production image
docker build -t nutrifit-user-management --target production .

# Run with environment variables
docker run -p 8001:8001 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_ANON_KEY=your_key \
  nutrifit-user-management
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | ✅ | - | Supabase project URL |
| `SUPABASE_ANON_KEY` | ✅ | - | Supabase anonymous key |
| `SUPABASE_SERVICE_KEY` | ✅ | - | Supabase service key |
| `SECRET_KEY` | ✅ | - | Application secret key |
| `JWT_SECRET_KEY` | ✅ | - | JWT signing secret |
| `ENVIRONMENT` | ❌ | `production` | Environment name |
| `PORT` | ❌ | `8001` | Server port |
| `WORKERS` | ❌ | `2` | Gunicorn workers |

### Health Checks

The service provides health check endpoints:

- **Basic Health**: `GET /health`
- **Detailed Health**: `GET /health/detailed`
- **Database Health**: `GET /health/database`

## 🧪 Testing

### Run Tests Locally

```bash
# Using Docker
docker-compose exec user-management poetry run pytest

# Using Poetry
cd services/user-management
poetry run pytest --cov=app --cov-report=html
```

### CI/CD Pipeline

GitHub Actions automatically:
- ✅ Runs tests on Python 3.11
- ✅ Checks code quality (Black, isort, flake8, mypy)
- ✅ Scans for security vulnerabilities
- ✅ Builds and pushes Docker images
- ✅ Deploys to staging/production

## 📊 Monitoring

### Logs

```bash
# View application logs
docker-compose logs -f user-management

# In production (Render)
# Use Render dashboard logs viewer
```

### Metrics

Production monitoring includes:
- Response time tracking
- Error rate monitoring
- Database connection health
- Memory and CPU usage

### Alerts

Configure alerts for:
- High error rates (>5%)
- Slow response times (>2s)
- Database connection failures
- Memory usage (>80%)

## 🔒 Security

### Security Headers

The application includes:
- CORS protection
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

### Secrets Management

- Use environment variables for secrets
- Never commit `.env` files
- Rotate secrets regularly
- Use strong, unique passwords

### Database Security

- Row Level Security (RLS) enabled
- Service key for admin operations only
- Anon key for public operations
- Regular security audits

## 🚨 Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check Supabase connectivity
curl -H "apikey: YOUR_ANON_KEY" "YOUR_SUPABASE_URL/rest/v1/"
```

#### Permission Errors
```bash
# Verify RLS policies in Supabase
# Check user authentication tokens
```

#### Performance Issues
```bash
# Monitor database connections
# Check for slow queries
# Verify caching configuration
```

### Debug Mode

Enable debug mode for development:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Performance Optimization

1. **Database Optimization**
   - Use connection pooling
   - Implement proper indexing
   - Cache frequent queries

2. **Application Optimization**
   - Use async/await properly
   - Implement response caching
   - Optimize serialization

3. **Infrastructure Optimization**
   - Use CDN for static assets
   - Implement horizontal scaling
   - Monitor resource usage

## 📈 Scaling

### Horizontal Scaling

```yaml
# render.yaml
numInstances: 3  # Scale to 3 instances
```

### Database Scaling

- Use read replicas for heavy read workloads
- Implement database sharding if needed
- Monitor connection pool usage

### Caching Strategy

- Redis for session storage
- Application-level caching
- Database query caching

## 🔄 Updates and Maintenance

### Rolling Updates

```bash
# Zero-downtime deployment
git push origin main  # Triggers automatic deployment
```

### Database Migrations

```bash
# Run migrations
poetry run alembic upgrade head
```

### Backup Strategy

- Automated Supabase backups
- Application state backups
- Configuration backups

## 📞 Support

### Getting Help

1. Check the logs first
2. Review this documentation
3. Check GitHub Issues
4. Contact the development team

### Emergency Contacts

- **Development Team**: dev@nutrifit.app
- **Operations Team**: ops@nutrifit.app
- **Security Issues**: security@nutrifit.app

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database schema updated
- [ ] Tests passing
- [ ] Security scan clean
- [ ] Performance benchmarks met

### Post-Deployment
- [ ] Health checks passing
- [ ] Logs show no errors
- [ ] Monitoring alerts configured
- [ ] Performance metrics normal
- [ ] User acceptance testing complete

### Rollback Plan
- [ ] Previous version tagged
- [ ] Rollback procedure documented
- [ ] Database rollback plan ready
- [ ] Communication plan for users
