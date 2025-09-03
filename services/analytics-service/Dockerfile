FROM python:3.11-slim

LABEL maintainer="GymBro Team"
LABEL service="analytics-service" 
LABEL version="0.1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PORT=8003 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry - FOLLOWING TEMPLATE
RUN pip install --no-cache-dir poetry==1.7.1

# Copy Poetry files - DEPENDENCY MANAGEMENT
COPY pyproject.toml poetry.lock* ./

# Configure Poetry and install dependencies - NO DEV DEPENDENCIES
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Copy application code - STANDARD STRUCTURE
COPY . .

# Install the application
RUN poetry install --only=main

# Create non-root user - SECURITY BEST PRACTICE
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check - MANDATORY MONITORING
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE $PORT

# Command - FOLLOWING TEMPLATE PATH
CMD ["python", "app/main.py"]
