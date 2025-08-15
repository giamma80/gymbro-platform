#!/bin/bash
# 🚀 GraphQL Gateway v0.2.0 - Quick Health Check Script
# Test both services after deployment

echo "🏋️ GymBro Platform - Service Health Check"
echo "========================================"

echo ""
echo "✅ User Management Service:"
curl -f -s https://gymbro-user-service.onrender.com/ping | jq '.' || echo "❌ User service down"

echo ""
echo "🚀 GraphQL Gateway Service:"
curl -f -s https://gymbro-graphql-gateway.onrender.com/ping | jq '.' || echo "🔄 GraphQL service still building"

echo ""
echo "🏥 Health Check Details:"
echo "User Management: https://gymbro-user-service.onrender.com/health"
echo "GraphQL Gateway: https://gymbro-graphql-gateway.onrender.com/health"

echo ""
echo "📊 API Documentation:"
echo "User Management: https://gymbro-user-service.onrender.com/docs"
echo "GraphQL Gateway: https://gymbro-graphql-gateway.onrender.com/ (minimal server)"

echo ""
echo "💰 Cost: \$0/mese (2 servizi gratuiti Render.com)"
