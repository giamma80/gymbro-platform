#!/bin/bash

# =============================================================================
# Apollo Gateway Development Server
# Standardized development script with profile support and background execution
# =============================================================================

# Exit on any error
set -e

# =============================================================================
# CONFIGURATION
# =============================================================================

# Default settings
COMMAND=${1:-start}
PROFILE=${PROFILE:-local}
SERVICE_PORT=4000

# Directory paths
SERVICE_DIR="/Users/giamma/workspace/gymbro-platform/services/apollo-gateway"
PID_FILE="/tmp/apollo-gateway.pid"
LOG_FILE="/tmp/apollo-gateway.log"

# Health check URL
HEALTH_URL="http://localhost:$SERVICE_PORT/health"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_banner() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                 🌐 Apollo Gateway                        ║${NC}"
    echo -e "${BLUE}║              Federation Development Server               ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo -e ""
}

# Check if server is running
is_server_running() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Kill processes on port
kill_processes_on_port() {
    local port=$1
    log_info "Checking for processes on port $port..."
    
    if command -v lsof >/dev/null 2>&1; then
        local pids
        pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            log_warning "Killing processes on port $port: $pids"
            echo "$pids" | xargs kill -TERM 2>/dev/null || true
            sleep 1
            echo "$pids" | xargs kill -KILL 2>/dev/null || true
        fi
    fi
}

# =============================================================================
# PROFILE CONFIGURATION
# =============================================================================

# Function to setup profile configuration
setup_profile() {
    log_info "Configuring profile: $PROFILE"
    
    case $PROFILE in
        local)
            cat > .env << 'EOF'
# Apollo Gateway - LOCAL Profile
NODE_ENV=development
GATEWAY_PORT=4000
GATEWAY_HOST=0.0.0.0
GRAPHQL_PATH=/graphql
POLL_INTERVAL=30000
LOG_LEVEL=info

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173

# Local Subgraph URLs
USER_MANAGEMENT_URL=http://localhost:8001/graphql
CALORIE_BALANCE_URL=http://localhost:8002/graphql

# GraphQL Development Features
ENABLE_INTROSPECTION=true
ENABLE_PLAYGROUND=true
EOF
            log_success "LOCAL profile configured"
            log_info "→ Federating localhost services (ports 8001, 8002)"
            ;;
        prod)
            cat > .env << 'EOF'
# Apollo Gateway - PRODUCTION Profile (Local Gateway → Remote Services)
NODE_ENV=development
GATEWAY_PORT=4000
GATEWAY_HOST=0.0.0.0
GRAPHQL_PATH=/graphql
POLL_INTERVAL=30000
LOG_LEVEL=info

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173

# Production Subgraph URLs
USER_MANAGEMENT_URL=https://nutrifit-user-management.onrender.com/graphql
CALORIE_BALANCE_URL=https://nutrifit-calorie-balance.onrender.com/graphql

# GraphQL Development Features
ENABLE_INTROSPECTION=true
ENABLE_PLAYGROUND=true
EOF
            log_success "PROD profile configured"
            log_info "→ Federating Render.com services"
            ;;
        *)
            log_error "Unknown profile: $PROFILE"
            log_info "Available profiles: local, prod"
            exit 1
            ;;
    esac
    
    # Load environment variables
    if [ -f .env ]; then
        set -a
        source .env
        set +a
    fi
}

# Function to check service health
check_service() {
    local service_name=$1
    local service_url=$2
    local health_url=${service_url/\/graphql/\/health}
    
    if curl -s --max-time 5 "$health_url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name${NC} is running"
        return 0
    else
        echo -e "${YELLOW}⚠️  $service_name${NC} not reachable at $health_url"
        return 1
    fi
}

# =============================================================================
# GATEWAY MANAGEMENT
# =============================================================================

# Function to start gateway
start_gateway() {
    print_banner
    
    # Check if already running
    if is_server_running; then
        local pid
        pid=$(cat "$PID_FILE")
        log_warning "Gateway already running (PID: $pid)"
        log_info "Logs: tail -f $LOG_FILE"
        return 0
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi

    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed. Please install npm"
        exit 1
    fi

    # Setup profile configuration
    log_info "Setting up profile: $PROFILE"
    setup_profile

    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        log_info "Installing dependencies..."
        npm install
    fi

    # Check required services based on profile
    log_info "Checking required services for $PROFILE profile..."
    
    if [ "$PROFILE" = "local" ]; then
        check_service "user-management" "http://localhost:8001/graphql"
        check_service "calorie-balance" "http://localhost:8002/graphql"
        log_warning "If services are not running, start them with:"
        echo -e "${CYAN}   cd ../user-management && ./start-dev.sh${NC}"
        echo -e "${CYAN}   cd ../calorie-balance && ./start-dev.sh${NC}"
    else
        check_service "user-management" "$USER_MANAGEMENT_URL"
        check_service "calorie-balance" "$CALORIE_BALANCE_URL"
    fi

    # Stop any existing processes on port
    kill_processes_on_port $SERVICE_PORT

    # Start the gateway in background
    log_info "Starting Apollo Gateway on port $SERVICE_PORT..."
    log_info "Profile: $PROFILE"
    log_info "Logs: $LOG_FILE"
    
    # Start with nohup and redirect output to log file
    cd "$SERVICE_DIR"
    nohup npm run dev > "$LOG_FILE" 2>&1 &
    
    local initial_pid=$!
    echo "$initial_pid" > "$PID_FILE"
    
    # Wait for health check
    log_info "Waiting for health check..."
    for i in $(seq 1 30); do
        if curl -s "$HEALTH_URL" > /dev/null 2>&1; then
            log_success "Health check OK"
            # Get the actual PID listening on the port
            if command -v lsof >/dev/null 2>&1; then
                local real_pid
                real_pid=$(lsof -ti:$SERVICE_PORT 2>/dev/null | head -n1 || true)
                if [ -n "$real_pid" ]; then
                    echo "$real_pid" > "$PID_FILE"
                    log_info "Service listening PID: $real_pid"
                fi
            fi
            
            log_success "🚀 Apollo Gateway started successfully!"
            echo -e "${BLUE}📊 GraphQL Endpoint: http://localhost:$SERVICE_PORT/graphql${NC}"
            echo -e "${BLUE}🏥 Health Check: http://localhost:$SERVICE_PORT/health${NC}"
            echo -e "${BLUE}📋 Logs: tail -f $LOG_FILE${NC}"
            echo -e "${BLUE}🛑 Stop: $0 stop${NC}"
            return 0
        fi
        
        if ! ps -p "$initial_pid" > /dev/null 2>&1; then
            log_error "Server process died during startup"
            tail -n 40 "$LOG_FILE" || true
            rm -f "$PID_FILE"
            return 1
        fi
        sleep 1
    done
    
    log_error "Health check failed after timeout"
    tail -n 40 "$LOG_FILE" || true
    rm -f "$PID_FILE"
    return 1
}

# Function to stop gateway
stop_gateway() {
    log_info "Stopping Apollo Gateway..."
    
    if is_server_running; then
        local pid
        pid=$(cat "$PID_FILE")
        log_info "Found gateway process: PID $pid"
        
        kill -TERM "$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
        
        # Wait for process to stop
        for i in $(seq 1 10); do
            if ! ps -p "$pid" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p "$pid" > /dev/null 2>&1; then
            log_warning "Force killing process..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
        
        log_success "Gateway stopped"
    else
        log_warning "No gateway process found"
    fi
    
    # Cleanup files
    rm -f "$PID_FILE"
    
    # Kill any remaining processes on port
    kill_processes_on_port $SERVICE_PORT
    
    # Kill any remaining nodemon processes
    pkill -f "nodemon.*apollo-gateway" 2>/dev/null || true
}

# =============================================================================
# STATUS AND LOGS FUNCTIONS
# =============================================================================

# Command functions
show_status() {
    print_banner
    if is_server_running; then
        local pid
        pid=$(cat "$PID_FILE")
        log_success "Apollo Gateway is running (PID: $pid)"
        echo -e "${BLUE}📊 GraphQL Endpoint: http://localhost:$SERVICE_PORT/graphql${NC}"
        echo -e "${BLUE}🏥 Health Check: http://localhost:$SERVICE_PORT/health${NC}"
        echo -e "${BLUE}📋 Logs: $LOG_FILE${NC}"
        
        # Test health endpoint
        if curl -s "$HEALTH_URL" > /dev/null 2>&1; then
            log_success "Health check: OK"
        else
            log_warning "Health check: FAILED"
        fi
    else
        log_warning "Apollo Gateway is not running"
        echo -e "${BLUE}📋 Recent logs: $LOG_FILE${NC}"
    fi
}

show_logs() {
    print_banner
    if [ -f "$LOG_FILE" ]; then
        log_info "Showing logs from: $LOG_FILE"
        echo -e "${BLUE}============================================================${NC}"
        tail -n 50 "$LOG_FILE"
        echo -e "${BLUE}============================================================${NC}"
        echo -e "${CYAN}💡 To follow logs in real-time: tail -f $LOG_FILE${NC}"
    else
        log_warning "No log file found: $LOG_FILE"
    fi
}

# =============================================================================
# ARGUMENT PARSING AND MAIN LOGIC
# =============================================================================

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile|-p)
            PROFILE="$2"
            shift 2
            ;;
        start|stop|restart|status|logs)
            COMMAND="$1"
            shift
            ;;
        --help|-h)
            echo -e "${BLUE}🌐 Apollo Gateway - Development Server${NC}"
            echo -e ""
            echo -e "${CYAN}Usage:${NC}"
            echo -e "  $0 [COMMAND] [OPTIONS]"
            echo -e ""
            echo -e "${CYAN}Commands:${NC}"
            echo -e "  start     Start the gateway (default)"
            echo -e "  stop      Stop the gateway"
            echo -e "  restart   Restart the gateway"
            echo -e "  status    Show gateway status"
            echo -e "  logs      Show recent logs"
            echo -e ""
            echo -e "${CYAN}Options:${NC}"
            echo -e "  -p, --profile PROFILE   Use profile: 'local' or 'prod' (default: local)"
            echo -e "  -h, --help              Show this help"
            echo -e ""
            echo -e "${CYAN}Examples:${NC}"
            echo -e "  $0 start --profile local    # Start with local services"
            echo -e "  $0 start --profile prod     # Start with production services"
            echo -e "  $0 restart --profile prod   # Restart with production services"
            echo -e "  $0 status                   # Check status"
            echo -e "  $0 logs                     # View logs"
            echo -e "  $0 stop                     # Stop the gateway"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo -e "Use '$0 --help' for usage information"
            exit 1
            ;;
    esac
done

# Main command logic
case $COMMAND in
    start)
        start_gateway
        ;;
    stop)
        stop_gateway
        ;;
    restart)
        stop_gateway
        sleep 2
        start_gateway
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        echo -e "Use '$0 --help' for usage information"
        exit 1
        ;;
esac