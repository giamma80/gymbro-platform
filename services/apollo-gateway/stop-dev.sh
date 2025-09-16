#!/bin/bash

# 🌐 Apollo Gateway - Stop Development Server

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🛑 Stopping Apollo Gateway${NC}"
echo -e "${BLUE}============================================================${NC}"

# Kill gateway processes
echo -e "${BLUE}🛑 Stopping gateway processes...${NC}"
pkill -f "node src/index.js" || true
pkill -f "nodemon --exec node src/index.js" || true

# Wait a moment
sleep 2

# Check if any processes are still running
REMAINING=$(pgrep -f "apollo-gateway" || true)
if [ ! -z "$REMAINING" ]; then
    echo -e "${BLUE}🔪 Force killing remaining processes...${NC}"
    pkill -9 -f "apollo-gateway" || true
fi

echo -e "${GREEN}✅ Apollo Gateway stopped successfully${NC}"
echo ""