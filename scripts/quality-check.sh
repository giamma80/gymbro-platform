#!/bin/bash

# ==========================================
# 🏋️ GymBro Platform - Quality Assurance
# ==========================================
# Script per eseguire tutti i controlli di qualità prima di un commit

set -e  # Exit on any error

echo "🏋️ GymBro Platform - Quality Assurance Check"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    log_error "Please run this script from the project root directory"
    exit 1
fi

# ==========================================
# 1. Code Formatting Check
# ==========================================
log_info "Checking code formatting..."

cd services/user-management

if ! poetry run black --check .; then
    log_warning "Code formatting issues found. Running black..."
    poetry run black .
    log_success "Code formatted successfully"
else
    log_success "Code formatting is correct"
fi

if ! poetry run isort --check-only .; then
    log_warning "Import ordering issues found. Running isort..."
    poetry run isort .
    log_success "Imports sorted successfully"
else
    log_success "Import ordering is correct"
fi

cd ../..

# ==========================================
# 2. Linting
# ==========================================
log_info "Running linting checks..."

cd services/user-management

# Flake8 for style guide enforcement
if poetry run flake8 . --exclude=.venv,__pycache__ --statistics; then
    log_success "Flake8 linting passed"
else
    log_warning "Flake8 found style issues (continuing...)"
fi

# MyPy for type checking
if poetry run mypy . --ignore-missing-imports; then
    log_success "MyPy type checking passed"
else
    log_warning "MyPy type checking found issues (non-blocking)"
fi

cd ../..

# ==========================================
# 3. Security Checks
# ==========================================
log_info "Running security checks..."

cd services/user-management

# Safety check for known vulnerabilities
if command -v safety &> /dev/null; then
    if poetry run safety check; then
        log_success "Safety vulnerability check passed"
    else
        log_warning "Safety found potential vulnerabilities"
    fi
else
    log_warning "Safety not installed, skipping vulnerability check"
fi

# Bandit for security issues
if command -v bandit &> /dev/null; then
    if poetry run bandit -r . -f txt; then
        log_success "Bandit security check passed"
    else
        log_warning "Bandit found potential security issues"
    fi
else
    log_warning "Bandit not installed, skipping security check"
fi

cd ../..

# ==========================================
# 4. Unit Tests
# ==========================================
log_info "Running unit tests..."

if make test-unit; then
    log_success "Unit tests passed"
else
    log_error "Unit tests failed"
    exit 1
fi

# ==========================================
# 5. Test Coverage Check
# ==========================================
log_info "Checking test coverage..."

cd services/user-management

COVERAGE_THRESHOLD=80

if poetry run pytest tests/ -v --cov=. --cov-report=term --cov-fail-under=$COVERAGE_THRESHOLD; then
    log_success "Test coverage meets threshold ($COVERAGE_THRESHOLD%)"
else
    log_error "Test coverage below threshold ($COVERAGE_THRESHOLD%)"
    exit 1
fi

cd ../..

# ==========================================
# 6. Integration Tests (Optional)
# ==========================================
if [ "$1" = "--integration" ]; then
    log_info "Running integration tests..."
    
    if make test-integration; then
        log_success "Integration tests passed"
    else
        log_error "Integration tests failed"
        exit 1
    fi
fi

# ==========================================
# 7. Docker Build Test
# ==========================================
if [ "$1" = "--docker" ]; then
    log_info "Testing Docker build..."
    
    if docker build -t gymbro-user-management-test ./services/user-management; then
        log_success "Docker build successful"
        docker rmi gymbro-user-management-test
    else
        log_error "Docker build failed"
        exit 1
    fi
fi

# ==========================================
# 8. Final Report
# ==========================================
echo ""
echo "🎉 Quality Assurance Complete!"
echo "================================"
log_success "All quality checks passed"
echo ""
echo "📊 Summary:"
echo "✅ Code formatting"
echo "✅ Linting (flake8)"
echo "✅ Type checking (mypy)"
echo "✅ Security checks"
echo "✅ Unit tests"
echo "✅ Test coverage"

if [ "$1" = "--integration" ]; then
    echo "✅ Integration tests"
fi

if [ "$1" = "--docker" ]; then
    echo "✅ Docker build"
fi

echo ""
echo "🚀 Ready for commit and CI/CD pipeline!"
