#!/bin/bash

# ==========================================
# 🏋️ GymBro Platform - Health Check Script
# ==========================================

echo "🏥 GymBro Platform Health Check"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service endpoints
declare -A SERVICES=(
    ["User Management"]="http://localhost:8001/health"
    ["Data Ingestion"]="http://localhost:8002/health"
    ["Calorie Service"]="http://localhost:8003/health"
    ["Meal Service"]="http://localhost:8004/health"
    ["Analytics Service"]="http://localhost:8005/health"
    ["Notification Service"]="http://localhost:8006/health"
    ["LLM Service"]="http://localhost:8007/health"
    ["GraphQL Gateway"]="http://localhost:8000/health"
)

# Check if docker-compose is running
echo -e "${BLUE}🐳 Checking Docker Compose Status...${NC}"
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Docker Compose services are not running!${NC}"
    echo -e "${YELLOW}💡 Run: make start${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is running${NC}"
echo ""

# Check individual services
echo -e "${BLUE}🔍 Checking Individual Services...${NC}"
FAILED_SERVICES=()

for service in "${!SERVICES[@]}"; do
    url="${SERVICES[$service]}"
    
    # Try to curl the health endpoint
    if curl -s -f "$url" > /dev/null 2>&1; then
        response=$(curl -s "$url" | jq -r '.status' 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✅ $service: $response${NC}"
    else
        echo -e "${RED}❌ $service: DOWN${NC}"
        FAILED_SERVICES+=("$service")
    fi
done

echo ""

# Database connectivity
echo -e "${BLUE}🗄️ Checking Database...${NC}"
if docker-compose exec -T postgres pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL: Connected${NC}"
else
    echo -e "${RED}❌ PostgreSQL: Connection failed${NC}"
    FAILED_SERVICES+=("PostgreSQL")
fi

# Redis connectivity
echo -e "${BLUE}🔄 Checking Redis...${NC}"
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis: Connected${NC}"
else
    echo -e "${RED}❌ Redis: Connection failed${NC}"
    FAILED_SERVICES+=("Redis")
fi

echo ""

# Summary
if [ ${#FAILED_SERVICES[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 All services are healthy!${NC}"
    echo ""
    echo -e "${BLUE}📋 Available Services:${NC}"
    echo -e "   • GraphQL Gateway: ${YELLOW}http://localhost:8000/docs${NC}"
    echo -e "   • User Management: ${YELLOW}http://localhost:8001/docs${NC}"
    echo -e "   • n8n Workflows: ${YELLOW}http://localhost:5678${NC}"
    echo -e "   • Traefik Dashboard: ${YELLOW}http://localhost:8080${NC}"
    echo ""
    echo -e "${GREEN}🚀 Platform is ready for development!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some services are not healthy:${NC}"
    for service in "${FAILED_SERVICES[@]}"; do
        echo -e "   • ${RED}$service${NC}"
    done
    echo ""
    echo -e "${YELLOW}💡 Troubleshooting steps:${NC}"
    echo -e "   1. Check logs: ${BLUE}make logs${NC}"
    echo -e "   2. Restart services: ${BLUE}make restart${NC}"
    echo -e "   3. Check .env configuration"
    echo -e "   4. Reset environment: ${BLUE}make reset-all${NC}"
    exit 1
fi
