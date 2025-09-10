#!/bin/bash
# User Management Service Test Runner
# Runs comprehensive tests for the user management service

set -e

echo "🧪 User Management Service - Test Runner"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the user-management service directory"
    exit 1
fi

# Check if the service is running
echo "🔍 Checking if service is running..."
if ! curl -s http://localhost:8001/health > /dev/null; then
    echo "❌ Error: Service not running on localhost:8001"
    echo "💡 Start the service with: ./start-dev.sh"
    exit 1
fi

echo "✅ Service is running"

# Check Python environment
echo "🐍 Checking Python environment..."
if ! poetry run python -c "import requests" 2>/dev/null; then
    echo "⚠️  Installing requests..."
    poetry add requests
fi

# Run the test suite
echo "🚀 Running test suite..."
echo ""

if poetry run python test_suite.py; then
    echo ""
    echo "🎉 All tests completed successfully!"
    exit 0
else
    echo ""
    echo "❌ Some tests failed. Check the output above."
    exit 1
fi
