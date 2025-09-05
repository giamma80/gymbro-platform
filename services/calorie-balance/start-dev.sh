#!/bin/bash

# Start Calorie Balance Service in development mode
echo "🚀 Starting Calorie Balance Service..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your actual configuration values"
    echo "   Especially DATABASE_URL, SUPABASE_URL, and SUPABASE keys"
fi

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "📦 Installing dependencies with Poetry..."
    poetry install
fi

# Run database migrations (when implemented)
# echo "🗃️  Running database migrations..."
# poetry run alembic upgrade head

# Start the service
echo "🏃‍♂️ Starting FastAPI server on http://localhost:8001"
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
