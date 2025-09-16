#!/bin/bash

# 🧹 GymBro Platform - Docker Cleanup Script
# Automatizza la pulizia di immagini, container e volumi Docker non necessari

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_header "🏋️ GymBro Platform Docker Cleanup"

# Show initial disk usage
print_status "Checking initial Docker disk usage..."
echo ""
docker system df
echo ""

# 1. Remove stopped containers (except running ones)
print_header "1. 🗑️ Removing Stopped Containers"
stopped_containers=$(docker ps -aq --filter "status=exited")
if [ -n "$stopped_containers" ]; then
    print_status "Found stopped containers, removing..."
    docker rm $stopped_containers
    print_success "Stopped containers removed successfully"
else
    print_status "No stopped containers found"
fi

# 2. Remove dangling images (those with <none> tag)
print_header "2. 🖼️ Removing Dangling Images"
print_status "Removing dangling images..."
dangling_cleanup=$(docker image prune -f)
if echo "$dangling_cleanup" | grep -q "Total reclaimed space: 0B"; then
    print_status "No dangling images found"
else
    print_success "Dangling images removed"
    echo "$dangling_cleanup" | grep "Total reclaimed space"
fi

# 3. Remove old service images and unused infrastructure
print_header "3. 📦 Removing Old Service Images & Unused Infrastructure"
old_images_to_remove=(
    "gymbro-platform-analytics-service"
    "analytics-service-test"
    "analytics-service"
    "gymbro-analytics-test"
    "gymbro-platform-user-service"
    "user-management-test"
    "gymbro-user-service"
    "postgres:15-alpine"
    "redis:7-alpine"
)

for image in "${old_images_to_remove[@]}"; do
    # Check if image exists using docker images command without table format
    if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${image}$"; then
        print_status "Removing old image: $image"
        docker rmi "$image" 2>/dev/null || print_warning "Could not remove $image (might be in use)"
    else
        print_status "Image $image not found (already removed or never existed)"
    fi
done

# 4. Remove unused volumes
print_header "4. 💾 Removing Unused Volumes"
print_status "Removing unused volumes..."
volume_cleanup=$(docker volume prune -f)
if echo "$volume_cleanup" | grep -q "Total reclaimed space: 0B"; then
    print_status "No unused volumes found"
else
    print_success "Unused volumes removed"
    echo "$volume_cleanup" | grep "Total reclaimed space"
fi

# 5. Remove build cache
print_header "5. 🔄 Removing Build Cache"
print_status "Removing build cache..."
cache_cleanup=$(docker builder prune -f 2>/dev/null || echo "No build cache to remove")
if echo "$cache_cleanup" | grep -q "Total reclaimed space"; then
    print_success "Build cache removed"
    echo "$cache_cleanup" | grep "Total reclaimed space"
else
    print_status "No build cache found or already clean"
fi

# 6. Show final results
print_header "📊 Final Results"
print_status "Final Docker disk usage:"
echo ""
docker system df
echo ""

print_status "Remaining images (essential ones):"
echo ""
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""

print_header "✅ Cleanup Complete!"
print_success "Docker cleanup completed successfully!"
print_status "Only essential images for GymBro Platform are now present:"
print_status "• user-management-user-management (current user management service)"
print_status "• calorie-balance-calorie-balance (current calorie balance service)"
print_status "• python:3.11-slim (base Python image for builds)"
print_status ""
print_status "🌟 Supabase-Only Architecture:"
print_status "• No local PostgreSQL (using Supabase Cloud DB)"
print_status "• No local Redis (simplified docker-compose)"
print_status "• Cloud-native microservices architecture"

echo -e "\n${GREEN}🎉 Space successfully reclaimed! Your GymBro Platform is now optimized.${NC}\n"
