#!/bin/bash

# 🚀 GymBro Platform - Microservice Generator with GraphQL Federation
# Genera automaticamente microservizi da template con GraphQL Federation
# Usage: ./scripts/generate-microservice.sh <service-name> <template-type>
# Example: ./scripts/generate-microservice.sh meal-tracking supabase

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SERVICE_NAME=$1
TEMPLATE_TYPE=$2

# Functions
print_usage() {
    echo -e "${YELLOW}📋 Usage:${NC}"
    echo "  ./scripts/generate-microservice.sh <service-name> <template-type>"
    echo ""
    echo -e "${YELLOW}📝 Available templates:${NC}"
    echo "  • supabase     - For real-time services (auth, notifications, real-time data)"
    echo "  • postgresql   - For analytics services (complex queries, ML, high performance)"
    echo ""
    echo -e "${YELLOW}📝 Examples:${NC}"
    echo "  ./scripts/generate-microservice.sh meal-tracking supabase"
    echo "  ./scripts/generate-microservice.sh analytics-engine postgresql"
    echo "  ./scripts/generate-microservice.sh notifications supabase"
}

validate_inputs() {
    if [ -z "$SERVICE_NAME" ] || [ -z "$TEMPLATE_TYPE" ]; then
        echo -e "${RED}❌ Error: Missing required arguments${NC}"
        print_usage
        exit 1
    fi

    # Validate service name format
    if [[ ! "$SERVICE_NAME" =~ ^[a-z0-9-]+$ ]]; then
        echo -e "${RED}❌ Error: Service name must contain only lowercase letters, numbers, and hyphens${NC}"
        exit 1
    fi

    # Validate template type
    if [[ "$TEMPLATE_TYPE" != "supabase" && "$TEMPLATE_TYPE" != "postgresql" ]]; then
        echo -e "${RED}❌ Error: Template type must be 'supabase' or 'postgresql'${NC}"
        print_usage
        exit 1
    fi
}

check_prerequisites() {
    # Check if templates exist
    local template_dir="$WORKSPACE_ROOT/templates/microservice-template"
    local supabase_template="$template_dir/supabase-client-template"
    local postgresql_template="$template_dir/postgresql-direct-template"

    if [[ "$TEMPLATE_TYPE" == "supabase" && ! -d "$supabase_template" ]]; then
        echo -e "${RED}❌ Error: Supabase template not found at $supabase_template${NC}"
        exit 1
    fi

    if [[ "$TEMPLATE_TYPE" == "postgresql" && ! -d "$postgresql_template" ]]; then
        echo -e "${RED}❌ Error: PostgreSQL template not found at $postgresql_template${NC}"
        exit 1
    fi

    # Check if service already exists
    local service_dir="$WORKSPACE_ROOT/services/$SERVICE_NAME"
    if [ -d "$service_dir" ]; then
        echo -e "${RED}❌ Error: Service '$SERVICE_NAME' already exists at $service_dir${NC}"
        exit 1
    fi

    # Check for poetry
    if ! command -v poetry &> /dev/null; then
        echo -e "${RED}❌ Error: Poetry is required but not installed${NC}"
        echo "Install it from: https://python-poetry.org/docs/#installation"
        exit 1
    fi
}

get_template_source() {
    local template_dir="$WORKSPACE_ROOT/templates/microservice-template"
    if [[ "$TEMPLATE_TYPE" == "supabase" ]]; then
        echo "$template_dir/supabase-client-template"
    else
        echo "$template_dir/postgresql-direct-template"
    fi
}

generate_service_name_variants() {
    # Convert service-name to different formats
    # service-name -> ServiceName (PascalCase)
    SERVICE_NAME_PASCAL=$(echo "$SERVICE_NAME" | sed -E 's/(^|-)([a-z])/\U\2/g')
    
    # service-name -> service_name (snake_case)
    SERVICE_NAME_SNAKE=$(echo "$SERVICE_NAME" | tr '-' '_')
    
    # service-name -> Service Name (Title Case)
    SERVICE_NAME_TITLE=$(echo "$SERVICE_NAME" | sed -E 's/(^|-)([a-z])/\U\2/g' | sed 's/\([A-Z]\)/ \1/g' | sed 's/^ //')
}

copy_and_process_template() {
    local template_source="$1"
    local service_dir="$WORKSPACE_ROOT/services/$SERVICE_NAME"
    
    echo -e "${BLUE}📁 Creating service directory: $service_dir${NC}"
    mkdir -p "$service_dir"
    
    echo -e "${BLUE}📋 Copying template files...${NC}"
    cp -r "$template_source"/* "$service_dir/"
    
    # Process placeholder substitutions
    echo -e "${BLUE}� Processing template placeholders...${NC}"
    
    # Find all files and process placeholders
    find "$service_dir" -type f \( -name "*.py" -o -name "*.toml" -o -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) -exec sed -i '' \
        -e "s/{service-name}/$SERVICE_NAME/g" \
        -e "s/{ServiceName}/$SERVICE_NAME_PASCAL/g" \
        -e "s/{service_name}/$SERVICE_NAME_SNAKE/g" \
        -e "s/{Service Name}/$SERVICE_NAME_TITLE/g" \
        -e "s/nutrifit-template/gymbro-$SERVICE_NAME/g" \
        -e "s/NutriFit Template/GymBro $SERVICE_NAME_TITLE/g" \
        {} \;
    
    echo -e "${GREEN}✅ Template files processed successfully${NC}"
}

setup_poetry_environment() {
    local service_dir="$WORKSPACE_ROOT/services/$SERVICE_NAME"
    
    echo -e "${BLUE}📦 Setting up Poetry environment...${NC}"
    cd "$service_dir"
    
    # Check poetry.toml validity
    if ! poetry check; then
        echo -e "${RED}❌ Error: Invalid pyproject.toml generated${NC}"
        exit 1
    fi
    
    # Install dependencies
    echo -e "${BLUE}📥 Installing dependencies with Poetry...${NC}"
    if ! poetry install; then
        echo -e "${RED}❌ Error: Failed to install dependencies${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Poetry environment setup complete${NC}"
}

run_validation_tests() {
    local service_dir="$WORKSPACE_ROOT/services/$SERVICE_NAME"
    
    echo -e "${BLUE}🧪 Running validation tests...${NC}"
    cd "$service_dir"
    
    # Test Python imports
    echo -e "${BLUE}  • Testing Python imports...${NC}"
    if ! poetry run python -c "
import app.main
import app.graphql.schema
print('✅ All imports successful')
"; then
        echo -e "${RED}❌ Error: Python import validation failed${NC}"
        exit 1
    fi
    
    # Test FastAPI app creation
    echo -e "${BLUE}  • Testing FastAPI app creation...${NC}"
    if ! poetry run python -c "
from app.main import app
print(f'✅ FastAPI app created: {app.title}')
"; then
        echo -e "${RED}❌ Error: FastAPI app creation failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All validation tests passed${NC}"
}

print_success_summary() {
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Microservice '$SERVICE_NAME' generated successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📍 Service Location:${NC}"
    echo "  $WORKSPACE_ROOT/services/$SERVICE_NAME"
    echo ""
    echo -e "${YELLOW}🚀 Next Steps:${NC}"
    echo "  1. cd services/$SERVICE_NAME"
    echo "  2. cp .env.example .env"
    echo "  3. Edit .env with your configuration"
    echo "  4. poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    echo -e "${YELLOW}🌐 Endpoints:${NC}"
    echo "  • Health:    http://localhost:8000/health"
    echo "  • API Docs:  http://localhost:8000/docs"
    echo "  • GraphQL:   http://localhost:8000/graphql"
    echo ""
    echo -e "${YELLOW}🔗 GraphQL Federation:${NC}"
    echo "  • Schema SDL: curl -X POST http://localhost:8000/graphql -H 'Content-Type: application/json' -d '{\"query\": \"{ _service { sdl } }\"}'"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}🚀 GymBro Platform - Microservice Generator${NC}"
    echo -e "${BLUE}============================================${NC}"
    
    validate_inputs
    check_prerequisites
    generate_service_name_variants
    
    local template_source=$(get_template_source)
    
    echo -e "${BLUE}📋 Generation Summary:${NC}"
    echo "  • Service Name: $SERVICE_NAME"
    echo "  • Template Type: $TEMPLATE_TYPE"
    echo "  • Template Source: $template_source"
    echo "  • Target Directory: $WORKSPACE_ROOT/services/$SERVICE_NAME"
    echo ""
    
    copy_and_process_template "$template_source"
    setup_poetry_environment
    run_validation_tests
    print_success_summary
}

# Run main function
main "$@"
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
