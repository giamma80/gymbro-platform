# ==========================================
# 🏋️ User Management Service - Dockerfile
# ==========================================

FROM python:3.11-slim

# 📦 Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 🔧 Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 👤 Create app user
RUN useradd --create-home --shell /bin/bash app

# 📁 Set work directory
WORKDIR /app

# Install Poetry with specific version for stability
RUN pip install poetry==1.8.3

# Copy Poetry files FIRST for better caching
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create virtual environments (we're already in a container)
RUN poetry config virtualenvs.create false

# Install dependencies with verbose output for debugging
RUN poetry install --only=main --no-dev -v

# 📄 Copy application code
COPY . .

# 👤 Change ownership to app user
RUN chown -R app:app /app

# 🏃‍♂️ Health check - use PORT env var or default to 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# 🌐 Expose port (dynamic based on PORT env var)
EXPOSE ${PORT:-8000}

# Switch to app user ONLY for running the app
USER app

# 🚀 Run the application with dynamic port
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
