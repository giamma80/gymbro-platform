#!/bin/bash

# 🧹 GymBro Platform - AGGRESSIVE Docker Cleanup Script
# ⚠️  WARNING: This will remove ALL unused Docker resources!
# Only run this if you want to clean everything and rebuild from scratch

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "\n${RED}================================================${NC}"
    echo -e "${RED} $1${NC}"
    echo -e "${RED}================================================${NC}\n"
}

print_header "⚠️  AGGRESSIVE DOCKER CLEANUP"
print_warning "This will remove ALL unused Docker resources!"
print_warning "Running containers and their images will be preserved."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Ask for confirmation
read -p "Are you sure you want to proceed? (yes/NO): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
print_header "💣 Starting Aggressive Cleanup"

# Show initial usage
echo "Initial Docker disk usage:"
docker system df
echo ""

# Nuclear option - remove everything unused
print_warning "Performing system prune (removes all unused resources)..."
docker system prune -af --volumes

echo ""
print_header "📊 Final Results"
print_success "Aggressive cleanup completed!"
echo ""
echo "Final Docker disk usage:"
docker system df
echo ""

print_success "Remaining images:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
echo ""

echo -e "${GREEN}🚀 Maximum space reclaimed! Only running containers and their images remain.${NC}\n"
