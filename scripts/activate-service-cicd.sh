#!/bin/bash

# 🔧 GymBro Platform - CI/CD Service Activator
# Attiva automaticamente un servizio nella pipeline CI/CD
# Usage: ./scripts/activate-service-cicd.sh <service-name>
# Example: ./scripts/activate-service-cicd.sh data-ingestion

set -e

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
    echo "❌ Usage: ./scripts/activate-service-cicd.sh <service-name>"
    echo "📝 Example: ./scripts/activate-service-cicd.sh data-ingestion"
    exit 1
fi

CICD_FILE=".github/workflows/ci-cd.yml"

echo "🔧 Activating $SERVICE_NAME in CI/CD pipeline..."

# Verifica che il servizio esista
if [ ! -d "services/$SERVICE_NAME" ]; then
    echo "❌ Service directory not found: services/$SERVICE_NAME"
    echo "💡 Run: ./scripts/generate-microservice.sh $SERVICE_NAME <runtime> first"
    exit 1
fi

# Backup CI/CD file
cp "$CICD_FILE" "${CICD_FILE}.backup"

# Cerca e decommenta il servizio nella matrix strategy
if grep -q "# ${SERVICE_NAME}," "$CICD_FILE"; then
    # Service found commented, uncomment it
    sed -i.tmp "s/# ${SERVICE_NAME},/${SERVICE_NAME},/" "$CICD_FILE"
    rm "${CICD_FILE}.tmp"
    echo "✅ Service '$SERVICE_NAME' activated in CI/CD pipeline"
elif grep -q "${SERVICE_NAME}," "$CICD_FILE"; then
    echo "⚠️  Service '$SERVICE_NAME' already active in CI/CD pipeline"
else
    echo "❌ Service '$SERVICE_NAME' not found in CI/CD matrix"
    echo "💡 Add manually to .github/workflows/ci-cd.yml in the matrix strategy"
    exit 1
fi

echo ""
echo "🎉 CI/CD activation completed for: $SERVICE_NAME"
echo ""
echo "📋 What happens now:"
echo "✅ GitHub Actions will now:"
echo "   - Run tests for $SERVICE_NAME on every push/PR"
echo "   - Build Docker image for $SERVICE_NAME"
echo "   - Include $SERVICE_NAME in integration tests"
echo "   - Deploy $SERVICE_NAME to staging/production"
echo ""
echo "🔗 Next steps:"
echo "1. 🧪 Push changes to trigger CI/CD: git add . && git commit -m 'feat: activate $SERVICE_NAME in CI/CD'"
echo "2. 🚀 Monitor GitHub Actions: https://github.com/owner/repo/actions"
echo "3. 📊 Check deployment: https://gymbro-$SERVICE_NAME.onrender.com/health"
echo ""
echo "⚠️  Remember: First push will trigger Docker build and deployment!"
