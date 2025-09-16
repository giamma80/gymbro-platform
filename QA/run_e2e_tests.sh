#!/bin/bash

# GymBro Platform E2E Test Runner
# Simplified execution script for the comprehensive test suite

echo "🚀 GymBro Platform - E2E Test Runner"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

# Check if services are running
echo "🔍 Checking service availability..."

# Function to check service health
check_service() {
    local service_name=$1
    local service_url=$2
    
    if curl -s "$service_url" > /dev/null 2>&1; then
        echo "✅ $service_name is running"
        return 0
    else
        echo "❌ $service_name is not responding at $service_url"
        return 1
    fi
}

# Check all required services
services_ok=true

if ! check_service "User Management" "http://localhost:8001/health"; then
    services_ok=false
fi

if ! check_service "Calorie Balance" "http://localhost:8002/health"; then
    services_ok=false
fi

if ! check_service "Apollo Gateway" "http://localhost:4000/health"; then
    services_ok=false
fi

if [ "$services_ok" = false ]; then
    echo ""
    echo "❌ Some services are not running. Please start all services first:"
    echo "   1. cd services/user-management && ./start-dev.sh"
    echo "   2. cd services/calorie-balance && ./start-dev.sh" 
    echo "   3. cd apollo-gateway && npm start"
    echo ""
    exit 1
fi

echo "✅ All services are running"
echo ""

# Install required Python packages if needed
echo "📦 Checking Python dependencies..."
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing requests package..."
    pip3 install requests
fi

echo ""
echo "🧪 Starting E2E Test Choreography..."
echo "=================================="

# Change to QA directory and run the test suite
cd "$(dirname "$0")" || exit 1

# Make the Python script executable
chmod +x e2e_test_choreography.py

# Run the test suite
python3 e2e_test_choreography.py

# Capture the exit code
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 E2E Test Suite completed successfully!"
    echo "All platform components are working correctly."
else
    echo "⚠️  E2E Test Suite completed with failures."
    echo "Check the test output above for details."
fi

echo ""
echo "📊 Test execution completed."
echo "=================================="

exit $exit_code