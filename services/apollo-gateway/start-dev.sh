#!/bin/bash

# 🌐 Apollo Gateway - Development Server
# Start the Apollo Federation Gateway for local development

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🌐 Apollo Gateway - Development Server${NC}"
echo -e "${BLUE}============================================================${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install npm${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️ .env file not found. Copying from .env.example...${NC}"
    cp .env.example .env
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    npm install
fi

# Check if required services are running
echo -e "${BLUE}🔍 Checking required services...${NC}"

# Check user-management service
if ! curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${YELLOW}⚠️ user-management service not running on port 8001${NC}"
    echo -e "${YELLOW}   Please start it first: cd ../user-management && ./start-dev.sh${NC}"
fi

# Check calorie-balance service  
if ! curl -s http://localhost:8002/health > /dev/null; then
    echo -e "${YELLOW}⚠️ calorie-balance service not running on port 8002${NC}"
    echo -e "${YELLOW}   Please start it first: cd ../calorie-balance && ./start-dev.sh${NC}"
fi

# Stop any existing gateway process
echo -e "${BLUE}🛑 Stopping any existing gateway...${NC}"
pkill -f "node src/index.js" || true
sleep 2

# Start the gateway
echo -e "${GREEN}🚀 Starting Apollo Gateway on port 4000...${NC}"
echo -e "${BLUE}📊 GraphQL Playground: http://localhost:4000/graphql${NC}"
echo -e "${BLUE}🏥 Health Check: http://localhost:4000/health${NC}"
echo -e "${BLUE}💡 Press Ctrl+C to stop${NC}"
echo ""

# Start with nodemon for development
npm run dev