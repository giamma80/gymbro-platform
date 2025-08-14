#!/bin/bash
# 🧪 GymBro Platform - Test Setup Script
# ====================================
# Automatizza il setup dell'ambiente di test per CI/CD e sviluppo locale

set -e  # Exit on any error

echo "🚀 Starting GymBro Platform Test Setup..."

# ==========================================
# 📍 Variables
# ==========================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
USER_MANAGEMENT_DIR="$PROJECT_ROOT/services/user-management"

# Default values (can be overridden by environment)
DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres123@localhost:5432/gymbro_test_db}"
REDIS_URL="${REDIS_URL:-redis://localhost:6379}"
JWT_SECRET="${JWT_SECRET:-test-secret-key-for-ci}"

echo "📁 Project root: $PROJECT_ROOT"
echo "📁 User Management: $USER_MANAGEMENT_DIR"

# ==========================================
# 🗄️ Database Setup
# ==========================================

# Check if we're in CI environment - be more robust for database checks
if [ "${CI}" = "true" ] || [ "${GITHUB_ACTIONS}" = "true" ]; then
    echo "🔍 CI environment detected - checking database connectivity..."
    
    # Extract database components from URL
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_USER=$(echo "$DATABASE_URL" | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
    DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')

    echo "🔧 Database config:"
    echo "  Host: $DB_HOST"
    echo "  Port: $DB_PORT"
    echo "  User: $DB_USER"
    echo "  Database: $DB_NAME"

    # Wait for PostgreSQL to be ready
    echo "⏳ Waiting for PostgreSQL to be ready..."
    max_attempts=30
    attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
            echo "✅ PostgreSQL is ready!"
            break
        fi
        
        attempt=$((attempt + 1))
        echo "  Attempt $attempt/$max_attempts: Waiting for PostgreSQL..."
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        echo "❌ ERROR: PostgreSQL is not ready after $max_attempts attempts"
        exit 1
    fi
else
    echo "🏠 Local environment detected - skipping database connectivity check"
    echo "💡 Assuming database services are managed externally (Docker, etc.)"
fi

# ==========================================
# 🔧 Environment Setup
# ==========================================
echo "🔧 Setting up environment..."

cd "$USER_MANAGEMENT_DIR"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
fi

# Update .env with test values
echo "📝 Updating environment variables..."
{
    echo "# Test Environment Configuration"
    echo "DATABASE_URL=$DATABASE_URL"
    echo "REDIS_URL=$REDIS_URL"
    echo "JWT_SECRET=$JWT_SECRET"
    echo "ENVIRONMENT=test"
    echo "DEBUG=true"
} > .env.test

echo "✅ Environment configuration ready!"

# ==========================================
# 📦 Dependencies Check
# ==========================================
echo "📦 Checking Poetry dependencies..."

if ! command -v poetry &> /dev/null; then
    echo "❌ ERROR: Poetry is not installed!"
    echo "   Install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dependencies if needed
if [ ! -d .venv ]; then
    echo "📦 Installing Poetry dependencies..."
    poetry install --no-interaction
else
    echo "✅ Poetry dependencies already installed"
fi

# ==========================================
# 🧪 Test Verification
# ==========================================
echo "🧪 Running verification tests..."

# Use the test environment (filter out comments and empty lines)
export $(cat .env.test | grep -v '^#' | grep -v '^$' | xargs)

# Run a simple test to verify setup
echo "🔍 Testing application import..."
if poetry run python -c "from main import app; print('✅ App imported successfully')" 2>/dev/null; then
    echo "✅ Application import test passed!"
else
    echo "❌ ERROR: Application import test failed!"
    exit 1
fi

# Test database connectivity only in CI
if [ "${CI}" = "true" ] || [ "${GITHUB_ACTIONS}" = "true" ]; then
    echo "🔍 Testing database connectivity..."
    if poetry run python -c "
import asyncio
from database import engine
async def test_db():
    try:
        async with engine.begin() as conn:
            result = await conn.execute('SELECT 1')
            print('✅ Database connection test passed!')
    except Exception as e:
        print(f'❌ Database test failed: {e}')
        exit(1)
asyncio.run(test_db())
" 2>/dev/null; then
        echo "✅ Database connectivity test passed!"
    else
        echo "❌ ERROR: Database connectivity test failed!"
        exit 1
    fi
else
    echo "🏠 Skipping database connectivity test in local environment"
fi

echo ""
echo "🎉 Test Setup Complete!"
echo ""
echo "🚀 You can now run tests with:"
echo "   cd $USER_MANAGEMENT_DIR"
echo "   poetry run pytest tests/ -v"
echo ""
echo "📊 Or with coverage:"
echo "   poetry run pytest tests/ -v --cov=. --cov-report=term-missing"
echo ""
