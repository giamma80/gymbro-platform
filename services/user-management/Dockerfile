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
    && rm -rf /var/lib/apt/lists/*

# 👤 Create app user
RUN useradd --create-home --shell /bin/bash app

# 📁 Set work directory
WORKDIR /app

# 📋 Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 📄 Copy application code
COPY . .

# 👤 Change ownership to app user
RUN chown -R app:app /app
USER app

# 🏃‍♂️ Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 🌐 Expose port
EXPOSE 8000

# 🚀 Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
