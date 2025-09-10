#!/bin/bash

# =============================================================================
# User Management Service - Stop Script
# =============================================================================
# Project: gymbro-platform
# Service: user-management  
# Environment: Development
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="user-management"
SERVICE_PORT=8001
PID_FILE="/tmp/${SERVICE_NAME}-${SERVICE_PORT}.pid"

echo -e "${BLUE}🛑 Stopping User Management Service${NC}"
echo "============================================================"

# Simply call the main script with stop argument
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
exec "$SCRIPT_DIR/start-dev.sh" stop
