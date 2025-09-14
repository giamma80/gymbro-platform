#!/usr/bin/env bash
set -euo pipefail

SERVICE_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_NAME="notifications"
SERVICE_PORT=8005
PYTHON_MODULE="app.main:app"
VENV="$SERVICE_DIR/.venv"
PID_FILE="/tmp/${SERVICE_NAME}-${SERVICE_PORT}.pid"
LOG_FILE="/tmp/${SERVICE_NAME}-${SERVICE_PORT}.log"
HEALTH_URL="http://localhost:${SERVICE_PORT}/health"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo -e "${BLUE}============================================================"
    echo "🚀 ${SERVICE_NAME} - Development Server"
    echo -e "============================================================${NC}"
}

log_info()    { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error()   { echo -e "${RED}❌ $1${NC}"; }

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

kill_processes_on_port() {
    local port=$1
    local pids
    pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        log_warning "Found processes on port $port, terminating..."
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

wait_for_health_check() {
    log_info "Waiting for health check response..."
    local retries=0
    local max_retries=30
    
    while [ $retries -lt $max_retries ]; do
        if curl -s "$HEALTH_URL" >/dev/null 2>&1; then
            log_success "Service is healthy and responding"
            return 0
        fi
        sleep 1
        retries=$((retries + 1))
        printf "."
    done
    echo
    log_warning "Service started but health check not responding after ${max_retries}s"
    return 1
}

setup_python_env() {
    if [ ! -d "$VENV" ]; then
        log_info "Creating virtual environment..."
        python -m venv "$VENV"
    fi
    
    log_info "Activating virtual environment..."
    source "$VENV/bin/activate"
    
    if [ -f "$SERVICE_DIR/pyproject.toml" ]; then
        if ! command -v poetry >/dev/null 2>&1; then
            log_error "Poetry not found. Please install poetry first."
            exit 1
        fi
        log_info "Installing dependencies with Poetry..."
        cd "$SERVICE_DIR"
        poetry install
    else
        log_warning "No pyproject.toml found, skipping dependency installation"
    fi
}

start_server() {
    print_banner
    
    if is_server_running; then
        log_warning "Server is already running (PID: $(cat "$PID_FILE"))"
        log_info "Use '$0 stop' to stop it first, or '$0 restart' to restart"
        exit 1
    fi
    
    kill_processes_on_port $SERVICE_PORT
    setup_python_env
    
    log_info "Starting ${SERVICE_NAME} on port ${SERVICE_PORT}..."
    
    cd "$SERVICE_DIR"
    source "$VENV/bin/activate"
    
    # Start uvicorn in background
    nohup poetry run uvicorn "$PYTHON_MODULE" \
        --host 0.0.0.0 \
        --port $SERVICE_PORT \
        --reload \
        --log-level info \
        > "$LOG_FILE" 2>&1 &
    
    local pid=$!
    echo $pid > "$PID_FILE"
    
    log_success "Server started with PID: $pid"
    log_info "Logs: $LOG_FILE"
    log_info "Health check: $HEALTH_URL"
    
    wait_for_health_check
    
    echo
    log_success "🚀 ${SERVICE_NAME} development server is ready!"
    echo -e "${CYAN}📝 View logs: tail -f $LOG_FILE${NC}"
    echo -e "${CYAN}🛑 Stop server: $0 stop${NC}"
    echo -e "${CYAN}🔄 Restart server: $0 restart${NC}"
    echo
}

stop_server() {
    log_info "Stopping ${SERVICE_NAME} development server..."
    
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            rm -f "$PID_FILE"
            log_success "Server stopped (PID: $pid)"
        else
            log_warning "PID file exists but process not running"
            rm -f "$PID_FILE"
        fi
    else
        log_info "No PID file found"
    fi
    
    kill_processes_on_port $SERVICE_PORT
    log_success "All processes on port $SERVICE_PORT terminated"
}

status_server() {
    log_info "Checking ${SERVICE_NAME} status..."
    
    if is_server_running; then
        local pid
        pid=$(cat "$PID_FILE")
        log_success "Running (PID: $pid, Port: $SERVICE_PORT)"
        
        if curl -s "$HEALTH_URL" >/dev/null 2>&1; then
            log_success "Responding to health checks"
        else
            log_warning "Not responding to health checks"
        fi
    else
        log_info "Not running"
    fi
}

restart_server() {
    stop_server
    sleep 1
    start_server
}

case "${1:-start}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    status)
        status_server
        ;;
    restart)
        restart_server
        ;;
    *)
        echo "Usage: $0 [start|stop|status|restart]"
        exit 1
        ;;
esac

exit 0