# 🏋️ NutriFit Platform - Project Hub

## 🎯 Quick Start

**NutriFit** è una piattaforma fitness-nutrizionale cloud-native con architettura microservizi, AI coaching avanzato, e mobile app cross-platform. La piattaforma combina precision tracking, real-time sync, e conversational AI per offrire un'esperienza utente superiore nel mercato nutrition tech.

### ⚡ Architettura Overview
- **5 Microservizi** FastAPI con database segregation
- **Flutter Mobile App** cross-platform iOS + Android 
- **Supabase Cloud** per database managed e real-time sync
- **N8N Cloud** per AI workflow orchestration
- **Model Context Protocol (MCP)** per AI integration avanzata

## 📚 Documentazione Completa

### 🏗️ Architettura & Design
- **[Architettura Cloud-Native](../../docs/architettura.md)** - Schema microservizi, database design, diagrammi Mermaid
- **[Microservizi Python](../../docs/microservizi_python.md)** - FastAPI, DDD patterns, tech stack details
- **[Mobile Flutter Strategy](../../docs/flutter.md)** - Cross-platform development, deployment pipeline

### 📋 Strategic Planning  
- **[Documentazione Generale](../../docs/Documentazione%20Generale.md)** - Business analysis, ROI projections, competitive strategy

### 🚀 Development & Deployment
- **[Development Workflow](../../docs/DEVELOPMENT_WORKFLOW.md)** - Git flow, coding standards, CI/CD pipeline
- **[Deployment Guide](../../docs/DEPLOYMENT.md)** - Render deployment, environment setup, monitoring
- **[Testing Guide](../../docs/TESTING_GUIDE.md)** - Unit tests, integration tests, coverage requirements *(da creare)*
- **[API Documentation](../../docs/API_DOCUMENTATION.md)** - REST endpoints, GraphQL schema, integration guides *(da creare)*

### 📝 Project Management
- **[Changelog](../../CHANGELOG.md)** - Project history, releases, major updates

## 💻 Quick Commands

### Development Setup
```bash
# Clone repository
git clone https://github.com/giamma80/gymbro-platform.git
cd gymbro-platform

# Setup development environment
make setup-dev

# Start all services
make dev-up
```

### Common Tasks
```bash
# Create new microservice
./scripts/create-service.sh my-service bounded-context

# Run tests
make test-all

# Deploy to staging
make deploy-staging
```

## 🧑‍💻 Developer Resources

### Quick Reference
- **[Project Structure](../../docs/microservizi_python.md#project-structure)** - Microservice templates, folder organization
- **[Database Schema](../../docs/architettura.md#database-design)** - PostgreSQL, Supabase, migrations
- **[Coding Standards](../../docs/DEVELOPMENT_WORKFLOW.md#python-coding-standards)** - Python, FastAPI, DDD patterns

### Development Tools
- **Poetry** per dependency management
- **FastAPI** per REST APIs
- **Alembic** per database migrations  
- **pytest** per testing con coverage minimo 80%
- **Docker** per containerization

## 🚀 Deployment & Operations

### Environment Links
- **Production**: [Deploy on Render](../../docs/DEPLOYMENT.md#render-com-deployment)
- **Staging**: [Environment Setup](../../docs/DEPLOYMENT.md#environment-strategy)
- **Local Dev**: [Docker Setup tramite architettura](../../docs/architettura.md#setup-locale)

### Monitoring & Health
```bash
# Health check all services
./scripts/health-check.sh

# View logs
make logs-follow SERVICE=calorie-balance

# Performance monitoring
make monitoring-dashboard
```

## 🤝 Contributing

### Pull Request Process
1. Leggi [Development Workflow](../../docs/DEVELOPMENT_WORKFLOW.md#git-workflow)
2. Crea feature branch da `main`
3. Implementa con test coverage ≥ 80%
4. Valida con `make quality-check`
5. Crea PR con template standard

### Code Review Guidelines
- Domain-Driven Design compliance
- API contract consistency  
- Performance considerations
- Security best practices
- Documentation updates

## 📞 Support & Community

### Getting Help
- **Documentazione**: Controlla prima la [docs folder](../../docs/)
- **Issues**: Apri GitHub issue con template appropriato
- **Architecture Questions**: Consulta [Documentazione Generale](../../docs/Documentazione%20Generale.md)

### Project Status
- **Current Phase**: MVP Development (Mesi 1-4)
- **Next Milestone**: AI Coach Integration (Mese 5)
- **Production Target**: Q2 2025

---

**🎯 Ready to contribute?** Inizia dalla [Documentazione Generale](../../docs/Documentazione%20Generale.md) per il context completo, poi segui il [Development Workflow](../../docs/DEVELOPMENT_WORKFLOW.md) per setup e best practices.
