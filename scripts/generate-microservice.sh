#!/bin/bash

# 🚀 GymBro Platform - Microservice Generator
# Genera automaticamente la struttura base per un nuovo microservizio
# Usage: ./scripts/generate-microservice.sh <service-name> <runtime>
# Example: ./scripts/generate-microservice.sh data-ingestion python

set -e

SERVICE_NAME=$1
RUNTIME=$2

if [ -z "$SERVICE_NAME" ] || [ -z "$RUNTIME" ]; then
    echo "❌ Usage: ./scripts/generate-microservice.sh <service-name> <runtime>"
    echo "📝 Available runtimes: python, node, go"
    echo "📝 Example: ./scripts/generate-microservice.sh data-ingestion python"
    exit 1
fi

SERVICE_DIR="services/${SERVICE_NAME}"
GYMBRO_SERVICE_NAME="gymbro-${SERVICE_NAME}"

echo "🚀 Generating microservice: ${SERVICE_NAME} (${RUNTIME})"

# Verifica che il servizio non esista già
if [ -d "$SERVICE_DIR" ]; then
    echo "❌ Service directory already exists: $SERVICE_DIR"
    exit 1
fi

# Crea struttura directory
mkdir -p "$SERVICE_DIR"
mkdir -p "$SERVICE_DIR/tests"

echo "📁 Created directory structure"

# Genera files basati sul runtime
case $RUNTIME in
    "python")
        # requirements.txt
        cat > "$SERVICE_DIR/requirements.txt" << EOF
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
EOF

        # main.py
        cat > "$SERVICE_DIR/main.py" << EOF
from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(
    title="${SERVICE_NAME} Service",
    description="GymBro Platform - ${SERVICE_NAME} microservice",
    version="1.0.0"
)

@app.get("/ping")
async def ping():
    """Basic health check endpoint"""
    return {"ping": "pong"}

@app.get("/health")
async def health():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "${SERVICE_NAME}",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "port": os.getenv("PORT", "8000")
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "${SERVICE_NAME}",
        "status": "running",
        "message": "GymBro Platform - ${SERVICE_NAME} Service"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

        # Dockerfile.minimal
        cat > "$SERVICE_DIR/Dockerfile.minimal" << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\
    CMD curl -f http://localhost:\${PORT:-8000}/health || exit 1

# ⚠️ CRITICAL: Dynamic port binding for Render.com
CMD uvicorn main:app --host 0.0.0.0 --port \${PORT:-8000}
EOF

        # pyproject.toml (if using Poetry)
        cat > "$SERVICE_DIR/pyproject.toml" << EOF
[tool.poetry]
name = "${SERVICE_NAME}"
version = "1.0.0"
description = "GymBro Platform - ${SERVICE_NAME} microservice"
authors = ["GymBro Team"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = "^0.24.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
python-multipart = "^0.0.6"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
httpx = "^0.25.2"
black = "^23.11.0"
flake8 = "^6.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

        # Test file
        cat > "$SERVICE_DIR/tests/test_main.py" << EOF
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "${SERVICE_NAME}"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "${SERVICE_NAME}"
    assert data["status"] == "running"
EOF
        ;;

    "node")
        # package.json
        cat > "$SERVICE_DIR/package.json" << EOF
{
  "name": "${SERVICE_NAME}",
  "version": "1.0.0",
  "description": "GymBro Platform - ${SERVICE_NAME} microservice",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "jest": "^29.7.0",
    "supertest": "^6.3.3"
  }
}
EOF

        # server.js
        cat > "$SERVICE_DIR/server.js" << EOF
const express = require('express');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Health endpoints
app.get('/ping', (req, res) => {
    res.json({ ping: 'pong' });
});

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: '${SERVICE_NAME}',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        port: port
    });
});

app.get('/', (req, res) => {
    res.json({
        service: '${SERVICE_NAME}',
        status: 'running',
        message: 'GymBro Platform - ${SERVICE_NAME} Service'
    });
});

app.listen(port, '0.0.0.0', () => {
    console.log(\`✅ \${SERVICE_NAME} service running on port \${port}\`);
});

module.exports = app;
EOF

        # Dockerfile.minimal
        cat > "$SERVICE_DIR/Dockerfile.minimal" << EOF
FROM node:20-alpine

WORKDIR /app

# Install system dependencies for health checks
RUN apk add --no-cache curl

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY server.js .

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\
    CMD curl -f http://localhost:\${PORT:-8000}/health || exit 1

# ⚠️ CRITICAL: Dynamic port binding for Render.com
CMD ["node", "server.js"]
EOF

        # Test file
        cat > "$SERVICE_DIR/tests/server.test.js" << EOF
const request = require('supertest');
const app = require('../server');

describe('${SERVICE_NAME} Service', () => {
    test('GET /ping', async () => {
        const response = await request(app).get('/ping');
        expect(response.statusCode).toBe(200);
        expect(response.body).toEqual({ ping: 'pong' });
    });

    test('GET /health', async () => {
        const response = await request(app).get('/health');
        expect(response.statusCode).toBe(200);
        expect(response.body.status).toBe('healthy');
        expect(response.body.service).toBe('${SERVICE_NAME}');
    });

    test('GET /', async () => {
        const response = await request(app).get('/');
        expect(response.statusCode).toBe(200);
        expect(response.body.service).toBe('${SERVICE_NAME}');
        expect(response.body.status).toBe('running');
    });
});
EOF
        ;;

    "go")
        # go.mod
        cat > "$SERVICE_DIR/go.mod" << EOF
module github.com/gymbro-platform/${SERVICE_NAME}

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
)
EOF

        # main.go
        cat > "$SERVICE_DIR/main.go" << EOF
package main

import (
    "net/http"
    "os"
    "time"
    "github.com/gin-gonic/gin"
)

func main() {
    router := gin.Default()

    // Health endpoints
    router.GET("/ping", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"ping": "pong"})
    })

    router.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "status":    "healthy",
            "service":   "${SERVICE_NAME}",
            "version":   "1.0.0",
            "timestamp": time.Now().UTC().Format(time.RFC3339),
            "port":      getPort(),
        })
    })

    router.GET("/", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "service": "${SERVICE_NAME}",
            "status":  "running",
            "message": "GymBro Platform - ${SERVICE_NAME} Service",
        })
    })

    port := getPort()
    router.Run(":" + port)
}

func getPort() string {
    port := os.Getenv("PORT")
    if port == "" {
        port = "8000"
    }
    return port
}
EOF

        # Dockerfile.minimal
        cat > "$SERVICE_DIR/Dockerfile.minimal" << EOF
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY main.go .

# Build the application
RUN go build -o main .

# Final stage
FROM alpine:latest

# Install curl for health checks
RUN apk --no-cache add curl

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/main .

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\
    CMD curl -f http://localhost:\${PORT:-8000}/health || exit 1

# ⚠️ CRITICAL: Application handles PORT env var internally
CMD ["./main"]
EOF
        ;;

    *)
        echo "❌ Unsupported runtime: $RUNTIME"
        echo "📝 Available runtimes: python, node, go"
        exit 1
        ;;
esac

# README.md
cat > "$SERVICE_DIR/README.md" << EOF
# 🏋️ ${SERVICE_NAME} Service

GymBro Platform - ${SERVICE_NAME} microservice

## 🚀 Quick Start

### Local Development
\`\`\`bash
cd services/${SERVICE_NAME}

# Python
pip install -r requirements.txt
python main.py

# Node.js
npm install
npm start

# Go
go mod tidy
go run main.go
\`\`\`

### Docker
\`\`\`bash
# Build
docker build -f Dockerfile.minimal -t ${SERVICE_NAME} .

# Run
docker run -p 8000:8000 ${SERVICE_NAME}
\`\`\`

## 🏥 Health Checks

- **Ping**: \`GET /ping\` - Basic connectivity
- **Health**: \`GET /health\` - Detailed status  
- **Root**: \`GET /\` - Service info

## 🧪 Testing

\`\`\`bash
# Python
pytest tests/ -v

# Node.js  
npm test

# Go
go test -v
\`\`\`

## 🚀 Deployment

Service is configured for deployment on Render.com with:
- ✅ Dynamic port binding (\`PORT\` env var)
- ✅ Health check endpoints
- ✅ Multi-stage Docker build
- ✅ Non-root user security

Deploy URL: \`https://${GYMBRO_SERVICE_NAME}.onrender.com\`
EOF

echo "📝 Generated microservice files for: $SERVICE_NAME ($RUNTIME)"

# Aggiorna render.yaml
echo "🔧 Updating render.yaml configuration..."

# Backup render.yaml
cp render.yaml render.yaml.backup

# Determina build e start commands
case $RUNTIME in
    "python")
        BUILD_CMD="pip install -r requirements.txt"
        START_CMD="python main.py"
        ;;
    "node")
        BUILD_CMD="npm ci"
        START_CMD="npm start"
        ;;
    "go")
        BUILD_CMD="go build -o main ."
        START_CMD="./main"
        ;;
esac

# Aggiunge il nuovo servizio a render.yaml
cat >> render.yaml << EOF

  # 🚀 ${SERVICE_NAME} Service (Generated $(date +%Y-%m-%d))
  - type: web
    name: ${GYMBRO_SERVICE_NAME}
    env: ${RUNTIME}
    plan: free
    buildCommand: ${BUILD_CMD}
    startCommand: ${START_CMD}
    healthCheckPath: /health
    dockerfilePath: services/${SERVICE_NAME}/Dockerfile.minimal
    envVars:
      - key: PORT
        generateValue: true
      - key: NODE_ENV
        value: production
EOF

echo "✅ Added service to render.yaml"

# Istruzioni per completare setup
echo ""
echo "🎉 Microservice '${SERVICE_NAME}' generated successfully!"
echo ""
echo "📋 Next steps:"
echo "1. 🔧 Implement business logic in services/${SERVICE_NAME}/"
echo "2. 🧪 Run tests: cd services/${SERVICE_NAME} && make test"
echo "3. 🐳 Test Docker: docker build -f services/${SERVICE_NAME}/Dockerfile.minimal -t ${SERVICE_NAME} ."
echo "4. 🚀 Activate in CI/CD: Edit .github/workflows/ci-cd.yml matrix"
echo "5. 📝 Update CHECKPOINT.md roadmap"
echo ""
echo "🔗 Test endpoints:"
echo "   Local: http://localhost:8000/health"
echo "   Deploy: https://${GYMBRO_SERVICE_NAME}.onrender.com/health"
echo ""
echo "⚠️  Don't forget to activate in GitHub Actions matrix strategy!"
