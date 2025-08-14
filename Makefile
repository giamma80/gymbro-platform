# ==========================================
# 🏋️ GymBro Platform - Development Makefile
# ==========================================

.PHONY: help setup start stop restart logs clean test build deploy

# Default target
help: ## Mostra questo help
	@echo "🏋️ GymBro Platform - Comandi disponibili:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ==========================================
# 🚀 Setup e Sviluppo
# ==========================================

setup: ## Setup ambiente di sviluppo completo
	@echo "🔧 Setting up GymBro development environment..."
	@cp .env.example .env
	@echo "✅ Environment file created (.env)"
	@echo "📝 Please edit .env with your API keys before running 'make start'"
	@echo ""
	@echo "📋 Required services to register (all FREE):"
	@echo "   - Supabase: https://supabase.com"
	@echo "   - OpenAI: https://platform.openai.com"
	@echo "   - SendGrid: https://sendgrid.com"
	@echo "   - Firebase: https://console.firebase.google.com"
	@echo "   - USDA API: https://fdc.nal.usda.gov/api-key-signup"

install: install-all ## Installa dipendenze Python per sviluppo locale (alias per install-all)

start: ## Avvia tutti i servizi con Docker Compose
	@echo "🚀 Starting GymBro Platform..."
	@docker-compose up -d
	@echo "✅ Platform started!"
	@echo ""
	@echo "🌐 Available services:"
	@echo "   - GraphQL Gateway: http://localhost:8000/docs"
	@echo "   - User Management: http://localhost:8001/docs"
	@echo "   - Data Ingestion: http://localhost:8002/docs"
	@echo "   - Calorie Service: http://localhost:8003/docs"
	@echo "   - Meal Service: http://localhost:8004/docs"
	@echo "   - Analytics: http://localhost:8005/docs"
	@echo "   - Notifications: http://localhost:8006/docs"
	@echo "   - LLM Service: http://localhost:8007/docs"
	@echo "   - n8n Workflows: http://localhost:5678"
	@echo "   - Traefik Dashboard: http://localhost:8080"

start-dev: ## Avvia solo servizi core per sviluppo
	@echo "🔧 Starting core services for development..."
	@docker-compose up -d postgres redis
	@echo "✅ Core services started!"

stop: ## Ferma tutti i servizi
	@echo "🛑 Stopping GymBro Platform..."
	@docker-compose down
	@echo "✅ Platform stopped"

restart: ## Riavvia tutti i servizi
	@echo "🔄 Restarting GymBro Platform..."
	@docker-compose down
	@docker-compose up -d
	@echo "✅ Platform restarted"

# ==========================================
# 📊 Monitoring e Logs
# ==========================================

logs: ## Mostra logs di tutti i servizi
	@docker-compose logs -f

logs-user: ## Mostra logs del servizio user-management
	@docker-compose logs -f user-service

logs-graphql: ## Mostra logs del GraphQL gateway
	@docker-compose logs -f graphql-gateway

status: ## Mostra status di tutti i servizi
	@echo "📊 GymBro Platform Status:"
	@docker-compose ps

health: ## Verifica health di tutti i servizi
	@echo "🏥 Health Check Results:"
	@echo ""
	@curl -s http://localhost:8001/health | jq '.' || echo "❌ User Management: DOWN"
	@curl -s http://localhost:8000/health | jq '.' || echo "❌ GraphQL Gateway: DOWN"

# ==========================================
# 📦 Poetry Management
# ==========================================

install-all: ## Installa dipendenze per tutti i servizi migrati
	@echo "📦 Installing dependencies for all services..."
	@cd services/user-management && poetry install && echo "✅ User Management installed"
	@echo "🚧 Altri servizi in migrazione verso Poetry..."

test-all: ## Esegui test per tutti i servizi
	@echo "🧪 Running tests for all services..."
	@cd services/user-management && poetry run pytest tests/ -v
	@echo "✅ All tests completed"

lint-all: ## Linting per tutti i servizi
	@echo "🔍 Running linting for all services..."
	@cd services/user-management && poetry run flake8 . && poetry run mypy .
	@echo "✅ All linting completed"

format-all: ## Formattazione per tutti i servizi
	@echo "✨ Formatting all services..."
	@cd services/user-management && poetry run black . && poetry run isort .
	@echo "✅ All formatting completed"

# Comandi per servizi specifici
dev-user: ## Avvia user-management in modalità sviluppo
	@echo "🔧 Starting user-management in development mode..."
	@set -a && source .env && set +a && cd services/user-management && poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001

test-user: ## Test solo per user-management service
	@echo "🧪 Testing User Management Service..."
	@cd services/user-management && poetry run pytest tests/ -v --cov=app

lint-user: ## Linting per user-management
	@echo "🔍 Linting User Management Service..."
	@cd services/user-management && poetry run flake8 . && poetry run mypy .

format-user: ## Formattazione per user-management
	@echo "✨ Formatting User Management Service..."
	@cd services/user-management && poetry run black . && poetry run isort .

# ==========================================
# 🧪 Testing
# ==========================================

test: test-all ## Esegui tutti i test (alias per test-all)

test-ci: ## Test completi per CI/CD con coverage
	@echo "🧪 Running CI tests with coverage..."
	@cd services/user-management && poetry run pytest tests/ -v --cov=. --cov-report=xml --cov-report=html --cov-report=term
	@echo "✅ CI tests completed with coverage report"

test-unit: ## Esegui solo test unitari
	@echo "🧪 Running unit tests..."
	@cd services/user-management && poetry run pytest tests/ -v -m "not integration and not slow"
	@echo "✅ Unit tests completed"

test-integration: ## Test di integrazione con servizi reali
	@echo "🔗 Running integration tests..."
	@docker-compose -f docker-compose.test.yml up -d test-postgres test-redis
	@sleep 10
	@cd services/user-management && poetry run pytest tests/ -v -m integration
	@docker-compose -f docker-compose.test.yml down
	@echo "✅ Integration tests completed"

test-e2e: ## Test end-to-end completi
	@echo "🔗 Running end-to-end tests..."
	@docker-compose -f docker-compose.test.yml up --build -d
	@sleep 30
	@curl -f http://localhost:8011/health || (echo "❌ Service not ready" && exit 1)
	@cd services/user-management && poetry run pytest tests/test_api_endpoints.py::TestIntegrationScenarios -v
	@docker-compose -f docker-compose.test.yml down -v
	@echo "✅ End-to-end tests completed"

test-performance: ## Test di performance
	@echo "🚀 Running performance tests..."
	@cd services/user-management && poetry run pytest tests/ -v -m slow
	@echo "✅ Performance tests completed"

test-watch: ## Test in modalità watch (riavvio automatico)
	@echo "👀 Running tests in watch mode..."
	@cd services/user-management && poetry run ptw tests/ -- -v

# ==========================================
# 🔍 Quality Assurance
# ==========================================

qa: ## Quality Assurance completo (formattazione, linting, test, coverage)
	@echo "🔍 Running complete Quality Assurance..."
	@./scripts/quality-check.sh
	@echo "✅ Quality Assurance completed"

qa-integration: ## QA completo con test di integrazione
	@echo "🔍 Running complete QA with integration tests..."
	@./scripts/quality-check.sh --integration
	@echo "✅ Complete QA with integration tests completed"

qa-docker: ## QA completo con test Docker build
	@echo "🔍 Running complete QA with Docker build test..."
	@./scripts/quality-check.sh --docker
	@echo "✅ Complete QA with Docker build completed"

pre-commit: qa ## Controlli pre-commit (alias per qa)
	@echo "🚀 Pre-commit checks completed - ready to commit!"

ci-checks: ## Controlli per CI/CD pipeline
	@echo "🔄 Running CI/CD checks..."
	@./scripts/quality-check.sh --integration --docker
	@echo "✅ CI/CD checks completed"

# ==========================================
# 🗄️ Database
# ==========================================

db-migrate: ## Esegui migrazioni database
	@echo "🗄️ Running database migrations..."
	@cd services/user-management && alembic upgrade head
	@echo "✅ Migrations completed"

db-reset: ## Reset completo database (⚠️ PERDE TUTTI I DATI!)
	@echo "⚠️  WARNING: This will DELETE ALL DATA!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		echo "🗄️ Resetting database..."; \
		docker-compose down; \
		docker volume rm gymbro-platform_postgres_data; \
		docker-compose up -d postgres; \
		sleep 5; \
		make db-migrate; \
		echo "✅ Database reset completed"; \
	else \
		echo ""; \
		echo "❌ Database reset cancelled"; \
	fi

db-backup: ## Backup database
	@echo "💾 Creating database backup..."
	@docker-compose exec postgres pg_dump -U postgres gymbro_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created"

# ==========================================
# 🔧 Utilities
# ==========================================

clean: ## Pulisci container, volumi e immagini
	@echo "🧹 Cleaning up..."
	@docker-compose down -v
	@docker system prune -f
	@echo "✅ Cleanup completed"

build: ## Build di tutte le immagini Docker
	@echo "🔨 Building Docker images..."
	@docker-compose build
	@echo "✅ Build completed"

shell-user: ## Apri shell nel container user-management
	@docker-compose exec user-service bash

shell-db: ## Apri shell PostgreSQL
	@docker-compose exec postgres psql -U postgres -d gymbro_db

format: format-all ## Formatta codice Python (alias per format-all)

lint: lint-all ## Lint codice Python (alias per lint-all)

# ==========================================
# 📈 Monitoring
# ==========================================

monitor: ## Avvia stack di monitoring (Prometheus + Grafana)
	@echo "📈 Starting monitoring stack..."
	@docker-compose -f docker-compose.monitoring.yml up -d
	@echo "✅ Monitoring started!"
	@echo "   - Prometheus: http://localhost:9090"
	@echo "   - Grafana: http://localhost:3000 (admin/admin)"

monitor-stop: ## Ferma monitoring
	@docker-compose -f docker-compose.monitoring.yml down

# ==========================================
# 🚀 Deployment
# ==========================================

deploy-staging: ## Deploy to staging (Render.com)
	@echo "🚀 Deploying to staging..."
	@git push origin main
	@echo "✅ Deployment triggered (check Render dashboard)"

deploy-prod: ## Deploy to production
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Make sure all tests pass first!"
	@make test
	@git tag -a v$(shell date +%Y%m%d_%H%M%S) -m "Production release"
	@git push origin --tags
	@echo "✅ Production deployment triggered"

# ==========================================
# 📚 Documentation
# ==========================================

docs: ## Genera documentazione API
	@echo "📚 Generating API documentation..."
	@cd services/user-management && python -c "\
import asyncio; \
from main import app; \
from fastapi.openapi.utils import get_openapi; \
import json; \
\
def generate_openapi(): \
    openapi_schema = get_openapi( \
        title=app.title, \
        version=app.version, \
        description=app.description, \
        routes=app.routes, \
    ); \
    return openapi_schema; \
\
schema = generate_openapi(); \
with open('api_docs.json', 'w') as f: \
    json.dump(schema, f, indent=2); \
"
	@echo "✅ Documentation generated (api_docs.json)"

# ==========================================
# 🎯 Development Helpers
# ==========================================

seed-db: ## Popola database con dati di test
	@echo "🌱 Seeding database with test data..."
	@cd services/user-management && poetry run python scripts/seed_db.py
	@echo "✅ Database seeded"

update: ## Aggiorna tutte le dipendenze con Poetry
	@echo "📦 Updating dependencies..."
	@cd services/user-management && poetry update
	@docker-compose pull
	@echo "✅ Dependencies updated"

# ==========================================
# 🔍 Debug
# ==========================================

debug-user: ## Debug user-management service
	@echo "🐛 Debugging user-management..."
	@docker-compose run --rm --service-ports user-service python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn main:app --reload

debug-logs: ## Mostra logs dettagliati di debug
	@docker-compose logs -f --tail=100

# ==========================================
# 📊 Analytics
# ==========================================

stats: ## Mostra statistiche di utilizzo
	@echo "📊 Platform Statistics:"
	@echo "----------------------"
	@echo "🐳 Docker containers: $(shell docker ps -q | wc -l)"
	@echo "💾 Database size: $(shell docker-compose exec postgres psql -U postgres -d gymbro_db -t -c "SELECT pg_size_pretty(pg_database_size('gymbro_db'));" | xargs)"
	@echo "📦 Docker images: $(shell docker images | grep gymbro | wc -l)"
	@echo "📁 Project files: $(shell find . -name "*.py" | wc -l) Python files"

# ==========================================
# 🎯 Quick Actions
# ==========================================

quick-start: setup start ## Setup rapido + start
	@echo "🎯 Quick start completed!"

reset-all: clean setup start ## Reset completo dell'ambiente
	@echo "🔄 Complete environment reset completed!"

# ==========================================
# 🆘 Troubleshooting
# ==========================================

troubleshoot: ## Guida al troubleshooting
	@echo "🆘 GymBro Platform Troubleshooting:"
	@echo ""
	@echo "Common issues and solutions:"
	@echo ""
	@echo "1. Port already in use:"
	@echo "   - Run: lsof -ti:8000 | xargs kill -9"
	@echo "   - Or change ports in docker-compose.yml"
	@echo ""
	@echo "2. Database connection failed:"
	@echo "   - Check if PostgreSQL is running: make status"
	@echo "   - Verify .env DATABASE_URL"
	@echo "   - Try: make db-reset"
	@echo ""
	@echo "3. Service not responding:"
	@echo "   - Check logs: make logs-[service]"
	@echo "   - Restart: make restart"
	@echo "   - Health check: make health"
	@echo ""
	@echo "4. Permission denied:"
	@echo "   - Check Docker daemon is running"
	@echo "   - Try: sudo make [command]"
