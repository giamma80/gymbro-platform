# 🏋️ GymbRo Platform - Cloud-Native Development Makefile

.PHONY: help dev-setup services-start services-stop flutter-dev test-all quality-check deploy-staging clean
 .PHONY: lint format lint-fix type-check

# Default target
help: ## Show this help message
	@echo "🏋️ GymbRo Platform - Cloud-Native Nutrition Tech"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Environment Setup
dev-setup: ## Setup complete development environment
	@echo "🚀 Setting up GymbRo development environment..."
	@echo "📋 Checking prerequisites..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found. Please install Docker Desktop"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found. Please install Python 3.11+"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found. Please install Node.js 18+"; exit 1; }
	@command -v flutter >/dev/null 2>&1 || { echo "❌ Flutter not found. Please install Flutter SDK"; exit 1; }
	@echo "✅ Prerequisites check passed"
	@echo "🏗️ Setting up infrastructure..."
	@docker network create gymbro-network 2>/dev/null || true
	@echo "📦 Setting up Python services..."
	@chmod +x scripts/setup-dev.sh
	@./scripts/setup-dev.sh
	@echo "📱 Setting up Flutter..."
	@cd mobile && flutter pub get
	@echo "✅ Development environment ready!"

# Service Management
services-start: ## Start all microservices with infrastructure
	@echo "🏃‍♂️ Starting GymbRo services..."
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@chmod +x scripts/QA/health-check.sh
	@./scripts/QA/health-check.sh
	@echo "✅ All services running!"

services-stop: ## Stop all services
	@echo "🛑 Stopping GymbRo services..."
	@docker-compose -f docker-compose.dev.yml down
	@echo "✅ Services stopped"

services-logs: ## View logs from all services
	@docker-compose -f docker-compose.dev.yml logs -f

# Flutter Development
flutter-dev: ## Start Flutter development with hot reload
	@echo "📱 Starting Flutter development server..."
	@cd mobile && flutter run -d chrome --web-port 3000

flutter-build: ## Build Flutter app for production
	@echo "🏗️ Building Flutter app for production..."
	@cd mobile && flutter build web
	@cd mobile && flutter build apk
	@cd mobile && flutter build ios
	@echo "✅ Flutter build complete"

# Testing
test-all: ## Run all tests (unit + integration + e2e)
	@echo "🧪 Running comprehensive test suite..."
	@chmod +x scripts/test-all-services.sh
	@./scripts/test-all-services.sh
	@echo "📱 Testing Flutter app..."
	@cd mobile && flutter test
	@echo "✅ All tests passed!"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@find services -name "test.sh" -exec chmod +x {} \;
	@find services -name "test.sh" -exec bash {} \;

test-integration: ## Run integration tests
	@echo "🔗 Running integration tests..."
	@chmod +x scripts/test-services.sh
	@./scripts/test-services.sh

# Code Quality
quality-check: ## Run code quality checks (linting, formatting, security)
	@echo "🔍 Running quality checks..."
	@chmod +x scripts/QA/quality-check.sh
	@./scripts/QA/quality-check.sh
	@echo "📱 Checking Flutter code quality..."
	@cd mobile && flutter analyze
	@cd mobile && flutter format --set-exit-if-changed .
	@echo "✅ Quality checks passed!"

# ---------- Python Lint & Formatting (Microservices) ----------
lint: ## Run flake8 + black --check + isort --check on all Python services
	@echo "🧹 Linting Python services..."
	@find services -maxdepth 2 -name pyproject.toml | while read f; do \
	  d=$$(dirname $$f); \
	  echo "➡️  Checking $$d"; \
	  (cd $$d && poetry run flake8 app || exit 1); \
	  (cd $$d && poetry run black --check app || exit 1); \
	  (cd $$d && poetry run isort --check-only app || exit 1); \
	done
	@echo "✅ Lint OK"

format: ## Apply black + isort formatting to all Python services
	@echo "🛠️ Formatting Python services..."
	@find services -maxdepth 2 -name pyproject.toml | while read f; do \
	  d=$$(dirname $$f); \
	  echo "✏️  Formatting $$d"; \
	  (cd $$d && poetry run isort app); \
	  (cd $$d && poetry run black app); \
	done
	@echo "✅ Formatting applied"

lint-fix: format ## Alias: format then lint to verify
	@$(MAKE) lint

type-check: ## Run mypy on all Python services (strict mode if configured)
	@echo "🔎 Type checking Python services..."
	@find services -maxdepth 2 -name pyproject.toml | while read f; do \
	  d=$$(dirname $$f); \
	  if grep -q "\[tool.mypy\]" $$f; then \
	    echo "🧪 mypy in $$d"; \
	    (cd $$d && poetry run mypy app || exit 1); \
	  else \
	    echo "(skip mypy) $$d"; \
	  fi; \
	done
	@echo "✅ Type check complete"

# Microservice Generation
new-service: ## Generate new microservice (usage: make new-service SERVICE=name TEMPLATE=supabase|postgresql)
	@if [ -z "$(SERVICE)" ] || [ -z "$(TEMPLATE)" ]; then \
		echo "❌ Usage: make new-service SERVICE=my-service TEMPLATE=supabase"; \
		echo "📋 Available templates: supabase, postgresql"; \
		exit 1; \
	fi
	@echo "🚀 Generating new microservice: $(SERVICE) with $(TEMPLATE) template..."
	@chmod +x scripts/generate-microservice.sh
	@./scripts/generate-microservice.sh $(SERVICE) $(TEMPLATE)
	@echo "✅ Microservice $(SERVICE) generated successfully!"
	@echo "📍 Next steps:"
	@echo "  1. cd services/$(SERVICE)"
	@echo "  2. cp .env.example .env"
	@echo "  3. Edit .env with your configuration"
	@echo "  4. Start developing!"

new-service-help: ## Show help for microservice generation
	@echo "🚀 Microservice Generator Help"
	@echo ""
	@echo "📋 Usage:"
	@echo "  make new-service SERVICE=my-service TEMPLATE=supabase"
	@echo ""
	@echo "📝 Available templates:"
	@echo "  • supabase     - For real-time services (auth, notifications, real-time data)"
	@echo "  • postgresql   - For analytics services (complex queries, ML, high performance)"
	@echo ""
	@echo "📝 Examples:"
	@echo "  make new-service SERVICE=meal-tracking TEMPLATE=supabase"
	@echo "  make new-service SERVICE=analytics-engine TEMPLATE=postgresql"
	@echo "  make new-service SERVICE=notifications TEMPLATE=supabase"

# Database Management
db-migrate: ## Run database migrations for all services
	@echo "🗃️ Running database migrations..."
	@for service in services/*/; do \
		if [ -f "$$service/alembic.ini" ]; then \
			echo "📋 Migrating $$service"; \
			cd "$$service" && python -m alembic upgrade head && cd ../..; \
		fi \
	done
	@echo "✅ Database migrations complete"

db-reset: ## Reset all databases (WARNING: Data loss!)
	@echo "⚠️  WARNING: This will reset all databases!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@docker-compose -f docker-compose.dev.yml down -v
	@docker volume prune -f
	@echo "🗃️ Databases reset"

# Deployment
deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	@echo "🧪 Running pre-deployment tests..."
	@make test-all
	@echo "🔍 Running quality checks..."
	@make quality-check
	@echo "🏗️ Building production assets..."
	@make flutter-build
	@echo "📦 Deploying to Render staging..."
	@git push origin staging
	@echo "✅ Staging deployment complete!"

deploy-production: ## Deploy to production (requires manual confirmation)
	@echo "🏭 PRODUCTION DEPLOYMENT"
	@echo "⚠️  This will deploy to production environment!"
	@read -p "Confirm production deployment? (y/N): " confirm && [ "$$confirm" = "y" ]
	@make test-all
	@make quality-check
	@make flutter-build
	@git tag -a "v$$(date +%Y%m%d-%H%M%S)" -m "Production deployment $$(date)"
	@git push origin main --tags
	@echo "✅ Production deployment initiated!"

# Utility Commands
logs: ## View logs from all services
	@docker-compose -f docker-compose.dev.yml logs -f

clean: ## Clean up Docker containers, images, and volumes
	@echo "🧹 Cleaning up Docker resources..."
	@chmod +x scripts/docker-cleanup.sh
	@./scripts/docker-cleanup.sh
	@echo "✅ Cleanup complete"

nuclear-clean: ## Nuclear cleanup (removes everything)
	@echo "☢️  NUCLEAR CLEANUP - This will remove ALL Docker data!"
	@read -p "Are you absolutely sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@chmod +x scripts/docker-nuclear-cleanup.sh
	@./scripts/docker-nuclear-cleanup.sh
	@echo "✅ Nuclear cleanup complete"

# Health Checks
health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@chmod +x scripts/QA/health-check.sh
	@./scripts/QA/health-check.sh

status: ## Show status of all services
	@echo "📊 Service Status:"
	@docker-compose -f docker-compose.dev.yml ps

# Documentation
docs: ## Open documentation in browser
	@echo "📚 Opening documentation..."
	@open docs/README.md 2>/dev/null || xdg-open docs/README.md 2>/dev/null || echo "Please open docs/README.md manually"

# Performance Testing
perf-test: ## Run performance tests
	@echo "⚡ Running performance tests..."
	@chmod +x scripts/test-api.py
	@python scripts/test-api.py
	@echo "✅ Performance tests complete"

# Security Scanning
security-scan: ## Run security vulnerability scan
	@echo "🔒 Running security scan..."
	@find services -name "pyproject.toml" -exec dirname {} \; | while read dir; do \
		echo "🔍 Scanning $$dir"; \
		cd "$$dir" && poetry run safety check && cd ../..; \
	done
	@echo "✅ Security scan complete"

# Environment Management
env-check: ## Check environment configuration
	@echo "🌍 Checking environment configuration..."
	@echo "Docker: $$(docker --version)"
	@echo "Python: $$(python3 --version)"
	@echo "Node.js: $$(node --version)"
	@echo "Flutter: $$(flutter --version | head -1)"
	@echo "✅ Environment check complete"

# Quick Start Workflow
quick-start: ## Complete quick start workflow
	@echo "🚀 GymbRo Platform Quick Start!"
	@make env-check
	@make dev-setup
	@make services-start
	@echo ""
	@echo "🎉 GymbRo Platform is ready!"
	@echo "📱 Flutter app: make flutter-dev"
	@echo "🧪 Run tests: make test-all"
	@echo "📊 Check status: make status"
	@echo "📚 View docs: make docs"
	@echo ""
	@echo "Happy coding! 💪"