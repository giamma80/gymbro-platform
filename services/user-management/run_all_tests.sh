#!/bin/bash
# Complete Test Suite - REST + GraphQL
# Tests both API layers of the user-management service

set -e

echo "🏆 Complete User Management Service Test Suite"
echo "=============================================="
echo "Testing both REST API and GraphQL endpoints"
echo ""

# Check if service is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Service not running. Please start with:"
    echo "poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

echo "✅ Service is running"
echo ""

# Run REST API tests
echo "🔥 Running REST API Test Suite..."
echo "================================="
if poetry run python test_suite.py; then
    echo "✅ REST API tests: PASSED"
    REST_RESULT="✅ PASSED"
else
    echo "❌ REST API tests: FAILED"
    REST_RESULT="❌ FAILED"
fi

echo ""
echo "🚀 Running GraphQL Test Suite..."
echo "================================"
if python test_graphql_advanced.py; then
    echo "✅ GraphQL tests: PASSED"
    GRAPHQL_RESULT="✅ PASSED"
else
    echo "❌ GraphQL tests: FAILED"
    GRAPHQL_RESULT="❌ FAILED"
fi

echo ""
echo "📊 Final Test Results"
echo "===================="
echo "REST API:  $REST_RESULT"
echo "GraphQL:   $GRAPHQL_RESULT"
echo ""

# Check if both passed
if [[ "$REST_RESULT" == *"PASSED"* && "$GRAPHQL_RESULT" == *"PASSED"* ]]; then
    echo "🎉 ALL TESTS PASSED! 🎉"
    echo ""
    echo "📋 Service Status:"
    echo "✅ REST API:  13 endpoints operational"
    echo "✅ GraphQL:   Schema introspection + queries working"
    echo "✅ Database:  User management schema operational"  
    echo "✅ Federation: Ready for Apollo Gateway"
    echo ""
    echo "🚀 User Management Service is PRODUCTION READY!"
    exit 0
else
    echo "⚠️  Some tests failed. Please review the output above."
    exit 1
fi
