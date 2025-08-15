# ==========================================
# 🏋️ User Management Service - Optimized Dockerfile
# ==========================================

# Build stage
FROM python:3.11-slim as builder

# 📦 Set build environment variables
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 🔧 Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.3

# Set work directory
WORKDIR /app

# Copy Poetry files and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-dev

# Runtime stage
FROM python:3.11-slim

# 📦 Runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 🔧 Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 👤 Create app user
RUN useradd --create-home --shell /bin/bash app

# 📁 Set work directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

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
