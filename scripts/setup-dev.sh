#!/bin/bash

# 🚀 GymBro Platform - Development Setup Script
# Questo script configura l'ambiente di sviluppo completo

set -e

echo "🏋️ Welcome to GymBro Platform Setup!"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed."
        exit 1
    fi
    
    # Check Make
    if ! command -v make &> /dev/null; then
        print_error "Make is not installed."
        exit 1
    fi
    
    print_success "All prerequisites are satisfied!"
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success "Created .env file from template"
        else
            print_error ".env.example file not found!"
            exit 1
        fi
    else
        print_warning ".env file already exists, skipping..."
    fi
}

# Install Python dependencies for development
install_dev_dependencies() {
    print_status "Installing development dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Created virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install development tools
    pip install --upgrade pip
    pip install black flake8 isort mypy pytest pytest-cov requests
    
    print_success "Development dependencies installed"
}

# Setup pre-commit hooks
setup_pre_commit() {
    print_status "Setting up pre-commit hooks..."
    
    if [ ! -f .git/hooks/pre-commit ]; then
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for GymBro Platform

echo "🔍 Running pre-commit checks..."

# Run linting
make lint
if [ $? -ne 0 ]; then
    echo "❌ Linting failed. Please fix the issues before committing."
    exit 1
fi

# Run tests
make test
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Please fix the issues before committing."
    exit 1
fi

echo "✅ Pre-commit checks passed!"
EOF
        chmod +x .git/hooks/pre-commit
        print_success "Pre-commit hooks installed"
    else
        print_warning "Pre-commit hooks already exist, skipping..."
    fi
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    docker-compose build --no-cache
    
    if [ $? -eq 0 ]; then
        print_success "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    # Start only the database service
    docker-compose up -d postgres redis
    
    # Wait for database to be ready
    sleep 10
    
    # Run migrations (when available)
    # docker-compose exec user-management python -m alembic upgrade head
    
    print_success "Database initialized"
}

# Create development networks
setup_networks() {
    print_status "Setting up Docker networks..."
    
    # Create networks if they don't exist
    docker network create gymbro-network 2>/dev/null || true
    
    print_success "Docker networks configured"
}

# Generate development SSL certificates
generate_ssl_certs() {
    print_status "Generating development SSL certificates..."
    
    mkdir -p infrastructure/ssl
    
    if [ ! -f infrastructure/ssl/cert.pem ]; then
        openssl req -x509 -newkey rsa:4096 -nodes \
            -keyout infrastructure/ssl/key.pem \
            -out infrastructure/ssl/cert.pem \
            -days 365 \
            -subj "/C=IT/ST=Italy/L=Local/O=GymBro/CN=localhost"
        
        print_success "SSL certificates generated"
    else
        print_warning "SSL certificates already exist, skipping..."
    fi
}

# Main setup function
main() {
    echo ""
    print_status "Starting GymBro Platform setup..."
    echo ""
    
    check_prerequisites
    setup_environment
    install_dev_dependencies
    setup_pre_commit
    setup_networks
    generate_ssl_certs
    build_images
    init_database
    
    echo ""
    print_success "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Configure your .env file with API keys"
    echo "2. Run: make start"
    echo "3. Run: make health-check"
    echo ""
    echo "📚 Documentation: docs/"
    echo "🚀 Quick commands: make help"
    echo ""
}

# Run main function
main "$@"
