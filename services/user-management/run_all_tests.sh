#!/bin/bash

# Enhanced test runner for user-management service
# Comprehensive testing with improved output

cd "$(dirname "$0")" || exit 1

echo "🧪 User Management Service - Complete Test Suite"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo_colored() {
    echo -e "${1}${2}${NC}"
}

# Check if server is running
echo_colored $BLUE "🔍 Checking server status..."
if ! curl -s http://localhost:8001/health > /dev/null; then
    echo_colored $RED "❌ Server not running on port 8001"
    echo_colored $YELLOW "💡 Please start the server first with: ./start-dev.sh"
    exit 1
fi

echo_colored $GREEN "✅ Server is running"
echo ""

# Determine which test suite to run
TEST_OPTION=${1:-"comprehensive"}

case $TEST_OPTION in
    "basic")
        echo_colored $BLUE "🎯 Running basic test suite..."
        poetry run python test_suite.py
        MAIN_EXIT=$?
        
        echo ""
        echo_colored $BLUE "🎯 Running GraphQL tests..."
        poetry run python test_graphql_advanced.py
        GRAPHQL_EXIT=$?
        
        # Summary for basic tests
        echo ""
        echo_colored $PURPLE "📊 Basic Test Summary"
        echo "===================="
        
        if [ $MAIN_EXIT -eq 0 ]; then
            echo_colored $GREEN "✅ Main test suite: PASSED"
        else
            echo_colored $RED "❌ Main test suite: FAILED"
        fi
        
        if [ $GRAPHQL_EXIT -eq 0 ]; then
            echo_colored $GREEN "✅ GraphQL tests: PASSED"
        else
            echo_colored $RED "❌ GraphQL tests: FAILED"
        fi
        
        if [ $MAIN_EXIT -eq 0 ] && [ $GRAPHQL_EXIT -eq 0 ]; then
            echo ""
            echo_colored $GREEN "🎉 All basic tests PASSED!"
            exit 0
        else
            echo ""
            echo_colored $RED "⚠️  Some basic tests FAILED"
            exit 1
        fi
        ;;
        
    "comprehensive"|*)
        echo_colored $PURPLE "🚀 Running COMPREHENSIVE test suite..."
        echo_colored $CYAN "📋 This will test ALL endpoints:"
        echo "   • 15+ Authentication endpoints"
        echo "   • User CRUD operations"
        echo "   • Profile & Privacy management"
        echo "   • 4 GraphQL queries + 3 mutations"
        echo "   • Error handling & edge cases"
        echo ""
        
        # Run comprehensive test suite
        poetry run python comprehensive_test_suite.py
        COMPREHENSIVE_EXIT=$?
        
        # Summary for comprehensive tests
        echo ""
        echo_colored $PURPLE "� Comprehensive Test Summary"
        echo "============================"
        
        if [ $COMPREHENSIVE_EXIT -eq 0 ]; then
            echo_colored $GREEN "✅ Comprehensive test suite: PASSED"
            echo_colored $GREEN "🎉 ALL endpoints tested successfully!"
        else
            echo_colored $RED "❌ Comprehensive test suite: FAILED"
            echo_colored $YELLOW "💡 Some endpoints may need attention"
        fi
        
        exit $COMPREHENSIVE_EXIT
        ;;
esac
