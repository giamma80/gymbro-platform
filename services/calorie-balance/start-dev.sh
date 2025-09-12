
#!/usr/bin/env bash
set -euo pipefail

SERVICE_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_NAME="calorie-balance"
SERVICE_PORT=8002
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
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        sleep 1
        pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill -KILL 2>/dev/null || true
        fi
    fi
}

activate_venv() {
    if command -v poetry >/dev/null 2>&1; then
        log_info "Using Poetry (skip venv activation)"
        return 0
    fi
    if [ -f "$VENV/bin/activate" ]; then
        log_info "Activating virtualenv: $VENV"
        # shellcheck disable=SC1090
        source "$VENV/bin/activate"
        return 0
    fi
    log_warning "Virtualenv not found at $VENV"
    return 1
}

install_deps() {
    if [ -f "$SERVICE_DIR/app/requirements.txt" ]; then
        pip install -r "$SERVICE_DIR/app/requirements.txt"
    fi
}

start_server() {
    print_banner
    if is_server_running; then
        local pid
        pid=$(cat "$PID_FILE")
        log_warning "Server already running (PID $pid)"
        return 0
    fi

    stop_server || true
    activate_venv || true
    if [ -f "$SERVICE_DIR/app/requirements.txt" ]; then
        install_deps
    fi

    log_info "Starting ${SERVICE_NAME} on port ${SERVICE_PORT}"
    rm -f "$LOG_FILE"

    # Build uvicorn args; default no reload for stable background runs
    RELOAD=${RELOAD:-0}
    UVICORN_ARGS=(--host 0.0.0.0 --port "$SERVICE_PORT" --log-level info --access-log)
    if [ "$RELOAD" = "1" ]; then
        UVICORN_ARGS+=(--reload --reload-dir app)
    fi

    if command -v poetry >/dev/null 2>&1; then
        nohup poetry run uvicorn $PYTHON_MODULE "${UVICORN_ARGS[@]}" > "$LOG_FILE" 2>&1 &
    else
        # prefer venv python if available
        if [ -x "$VENV/bin/python" ]; then
            nohup "$VENV/bin/python" -m uvicorn $PYTHON_MODULE "${UVICORN_ARGS[@]}" > "$LOG_FILE" 2>&1 &
        else
            nohup python3 -m uvicorn $PYTHON_MODULE "${UVICORN_ARGS[@]}" > "$LOG_FILE" 2>&1 &
        fi
    fi

    # initial PID (may be reloader when --reload used)
    local initial_pid
    initial_pid=$!
    echo "$initial_pid" > "$PID_FILE"

    # Wait for health check
    for i in $(seq 1 30); do
        if curl -s "$HEALTH_URL" | grep -q 'healthy'; then
            log_success "Health check OK"
            # Prefer the PID actually listening on the port
            if command -v lsof >/dev/null 2>&1; then
                local real_pid
                real_pid=$(lsof -ti:$SERVICE_PORT 2>/dev/null | head -n1 || true)
                if [ -n "$real_pid" ]; then
                    echo "$real_pid" > "$PID_FILE"
                    log_info "Service listening PID: $real_pid"
                fi
            fi
            echo "Server started, logs: $LOG_FILE"
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

stop_server() {
    print_banner
    log_info "Stopping ${SERVICE_NAME}..."
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -TERM "$pid" || true
            sleep 1
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -KILL "$pid" || true
            fi
        fi
        rm -f "$PID_FILE"
    fi
    # Ensure port cleaned
    kill_processes_on_port "$SERVICE_PORT"
    pkill -f "uvicorn.*${PYTHON_MODULE}" 2>/dev/null || true
    log_success "Stopped"
}

status_server() {
    print_banner
    if is_server_running; then
        local pid
        pid=$(cat "$PID_FILE")
        log_success "Running (PID $pid)"
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
