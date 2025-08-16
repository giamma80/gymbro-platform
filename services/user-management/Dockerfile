# ==========================================
# 🏋️ User Management Service - Production Dockerfile
# Single-stage approach for Poetry compatibility and reliability
# ==========================================

FROM python:3.11-slim

# 📦 Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 🔧 Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 👤 Create app user
RUN useradd --create-home --shell /bin/bash app

# Install Poetry
RUN pip install poetry==1.8.3

# 📁 Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies with Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-dev

# 📄 Copy application code
COPY . .

# 👤 Change ownership to app user
RUN chown -R app:app /app

# 🏃‍♂️ Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# 🌐 Expose port
EXPOSE ${PORT:-8000}

# Switch to app user
USER app

# 🚀 Run the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
