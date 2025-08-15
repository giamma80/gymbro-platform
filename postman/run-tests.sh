#!/bin/bash

# 🏋️ GymBro Platform - Postman Test Runner
# Automated testing script for User Management Service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COLLECTION_FILE="GymBro-Platform.postman_collection.json"
PROD_ENV_FILE="environments/GymBro-Production.postman_environment.json"
DEV_ENV_FILE="environments/GymBro-Development.postman_environment.json"

echo -e "${BLUE}🏋️ GymBro Platform - Postman Test Runner${NC}"
echo "=================================================="

# Check if newman is installed
if ! command -v newman &> /dev/null; then
    echo -e "${RED}❌ Newman is not installed${NC}"
    echo -e "${YELLOW}💡 Install with: npm install -g newman${NC}"
    exit 1
fi

# Check if files exist
if [[ ! -f "$COLLECTION_FILE" ]]; then
    echo -e "${RED}❌ Collection file not found: $COLLECTION_FILE${NC}"
    exit 1
fi

# Function to run tests
run_tests() {
    local env_name=$1
    local env_file=$2
    
    echo -e "${BLUE}🧪 Running tests for $env_name environment...${NC}"
    
    if [[ ! -f "$env_file" ]]; then
        echo -e "${RED}❌ Environment file not found: $env_file${NC}"
        return 1
    fi
    
    # Run health check first
    echo -e "${YELLOW}🏥 Running health check...${NC}"
    newman run "$COLLECTION_FILE" \
        -e "$env_file" \
        --folder "🏥 Health & Status" \
        --reporters cli,json \
        --reporter-json-export "results/health-check-$env_name.json"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        
        # Run full test suite
        echo -e "${YELLOW}🧪 Running full test suite...${NC}"
        newman run "$COLLECTION_FILE" \
            -e "$env_file" \
            --reporters cli,json,html \
            --reporter-json-export "results/full-test-$env_name.json" \
            --reporter-html-export "results/report-$env_name.html"
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ All tests passed for $env_name${NC}"
            return 0
        else
            echo -e "${RED}❌ Some tests failed for $env_name${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Health check failed for $env_name${NC}"
        return 1
    fi
}

# Create results directory
mkdir -p results

# Parse command line arguments
case "${1:-both}" in
    "prod"|"production")
        echo -e "${BLUE}🌐 Testing Production environment only${NC}"
        run_tests "production" "$PROD_ENV_FILE"
        ;;
    "dev"|"development")
        echo -e "${BLUE}🔧 Testing Development environment only${NC}"
        run_tests "development" "$DEV_ENV_FILE"
        ;;
    "both"|"all"|"")
        echo -e "${BLUE}🔄 Testing both environments${NC}"
        
        # Test production first
        echo -e "\n${BLUE}📊 Testing Production Environment${NC}"
        echo "=================================="
        prod_result=0
        run_tests "production" "$PROD_ENV_FILE" || prod_result=1
        
        # Test development
        echo -e "\n${BLUE}🔧 Testing Development Environment${NC}"
        echo "=================================="
        dev_result=0
        run_tests "development" "$DEV_ENV_FILE" || dev_result=1
        
        # Summary
        echo -e "\n${BLUE}📋 Test Summary${NC}"
        echo "==============="
        if [[ $prod_result -eq 0 ]]; then
            echo -e "${GREEN}✅ Production: PASSED${NC}"
        else
            echo -e "${RED}❌ Production: FAILED${NC}"
        fi
        
        if [[ $dev_result -eq 0 ]]; then
            echo -e "${GREEN}✅ Development: PASSED${NC}"
        else
            echo -e "${RED}❌ Development: FAILED${NC}"
        fi
        
        # Exit with error if any tests failed
        if [[ $prod_result -ne 0 || $dev_result -ne 0 ]]; then
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}❌ Invalid argument: $1${NC}"
        echo -e "${YELLOW}💡 Usage: $0 [prod|dev|both]${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}🎉 Test execution completed!${NC}"
echo -e "${BLUE}📄 Reports available in: ./results/${NC}"
