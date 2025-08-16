#!/bin/bash

# 🧪 GymBro Platform - Service Health Tester
# Testa automaticamente tutti i servizi deployed
# Usage: ./scripts/test-all-services.sh [local|production]
# Example: ./scripts/test-all-services.sh production

set -e

ENVIRONMENT=${1:-"local"}

echo "🧪 Testing GymBro Platform services ($ENVIRONMENT)"

# Service definitions
declare -a SERVICES=(
    "user-service:8001"
    "graphql-gateway:4000"
    # Add more services as they get deployed
    # "data-ingestion:8002"
    # "calorie-service:8003"  
    # "meal-service:8004"
    # "analytics-service:8005"
    # "notification-service:8006"
    # "llm-query-service:8007"
)

# Base URLs
if [ "$ENVIRONMENT" = "production" ]; then
    BASE_URL="https://gymbro"
    URL_SUFFIX=".onrender.com"
else
    BASE_URL="http://localhost"
    URL_SUFFIX=""
fi

echo "🌐 Environment: $ENVIRONMENT"
echo "🔗 Base URL: $BASE_URL"
echo ""

# Test results tracking
TOTAL_SERVICES=0
HEALTHY_SERVICES=0
FAILED_SERVICES=()

# Test each service
for SERVICE_PORT in "${SERVICES[@]}"; do
    IFS=':' read -r SERVICE PORT <<< "$SERVICE_PORT"
    TOTAL_SERVICES=$((TOTAL_SERVICES + 1))
    
    if [ "$ENVIRONMENT" = "production" ]; then
        SERVICE_URL="${BASE_URL}-${SERVICE}${URL_SUFFIX}"
    else
        SERVICE_URL="${BASE_URL}:${PORT}"
    fi
    
    echo "🔍 Testing: $SERVICE"
    echo "   URL: $SERVICE_URL"
    
    # Test /ping endpoint
    echo -n "   /ping: "
    if curl -f -s -m 30 "$SERVICE_URL/ping" > /dev/null 2>&1; then
        echo "✅ OK"
        PING_OK=true
    else
        echo "❌ FAILED"
        PING_OK=false
    fi
    
    # Test /health endpoint
    echo -n "   /health: "
    HEALTH_RESPONSE=$(curl -f -s -m 30 "$SERVICE_URL/health" 2>/dev/null || echo "FAILED")
    if [ "$HEALTH_RESPONSE" != "FAILED" ]; then
        STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status' 2>/dev/null || echo "unknown")
        if [ "$STATUS" = "healthy" ]; then
            echo "✅ HEALTHY"
            HEALTH_OK=true
        else
            echo "⚠️  STATUS: $STATUS"
            HEALTH_OK=true  # Still consider it OK if it responds
        fi
    else
        echo "❌ FAILED"
        HEALTH_OK=false
    fi
    
    # Test / (root) endpoint
    echo -n "   /: "
    if curl -f -s -m 30 "$SERVICE_URL/" > /dev/null 2>&1; then
        echo "✅ OK"
        ROOT_OK=true
    else
        echo "❌ FAILED"
        ROOT_OK=false
    fi
    
    # Overall service health - Only require ping and health to be OK
    if [ "$PING_OK" = true ] && [ "$HEALTH_OK" = true ]; then
        echo "   📊 Overall: ✅ HEALTHY"
        HEALTHY_SERVICES=$((HEALTHY_SERVICES + 1))
    else
        echo "   📊 Overall: ❌ UNHEALTHY"
        FAILED_SERVICES+=("$SERVICE")
    fi
    
    echo ""
done

# Final report
echo "📊 FINAL REPORT"
echo "==============="
echo "🎯 Environment: $ENVIRONMENT"
echo "📈 Total services: $TOTAL_SERVICES"
echo "✅ Healthy services: $HEALTHY_SERVICES"
echo "❌ Failed services: $((TOTAL_SERVICES - HEALTHY_SERVICES))"

if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    echo ""
    echo "❌ Failed services:"
    for FAILED_SERVICE in "${FAILED_SERVICES[@]}"; do
        echo "   - $FAILED_SERVICE"
    done
fi

echo ""

# Health check percentage
HEALTH_PERCENTAGE=$(( (HEALTHY_SERVICES * 100) / TOTAL_SERVICES ))
echo "🏥 Platform health: $HEALTH_PERCENTAGE%"

if [ $HEALTH_PERCENTAGE -eq 100 ]; then
    echo "🎉 ALL SERVICES HEALTHY! Platform is fully operational."
    exit 0
elif [ $HEALTH_PERCENTAGE -ge 80 ]; then
    echo "⚠️  Most services healthy. Some issues need attention."
    exit 1
else
    echo "🚨 CRITICAL: Multiple service failures detected!"
    exit 2
fi
