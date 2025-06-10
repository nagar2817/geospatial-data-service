#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Job Discovery Pipeline Test Suite${NC}"
echo -e "${BLUE}====================================${NC}"

# Set API base URL
API_BASE="http://localhost:8000/api/v1"

# Function to test API endpoint
test_api_endpoint() {
    local test_name="$1"
    local endpoint="$2"
    local method="$3"
    local data="$4"
    
    echo -e "\n${YELLOW}Testing: $test_name${NC}"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" "$endpoint")
    fi
    
    # Split response and status code
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 202 ]; then
        echo -e "${GREEN}✅ Success (HTTP $http_code)${NC}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ Failed (HTTP $http_code)${NC}"
        echo "$body"
    fi
}

# Test 1: Health Check
echo -e "\n${BLUE}1. Health Check${NC}"
test_api_endpoint "API Health Check" "$API_BASE/health" "GET"

# Test 2: API-triggered Job Discovery (no filters)
echo -e "\n${BLUE}2. API-Triggered Job Discovery (No Filters)${NC}"
test_api_endpoint "Job Discovery - No Filters" "$API_BASE/pipelines/discover-jobs" "POST" '{}'

# Test 3: API-triggered Job Discovery (with filters)
echo -e "\n${BLUE}3. API-Triggered Job Discovery (With Filters)${NC}"
test_api_endpoint "Job Discovery - Anomaly Detection Filter" "$API_BASE/pipelines/discover-jobs" "POST" '{
    "job_filters": {
        "job_type": "anomaly_detection",
        "enabled": true
    },
    "execution_host": "test-script"
}'

# Test 4: Generic Pipeline Execution
echo -e "\n${BLUE}4. Generic Pipeline Execution${NC}"
test_api_endpoint "Generic Pipeline Execution" "$API_BASE/pipelines/execute" "POST" '{
    "pipeline_name": "job_discovery",
    "trigger_metadata": {
        "execution_host": "test-script",
        "test_run": true
    }
}'

# Test 5: List Jobs (to verify test data)
echo -e "\n${BLUE}5. List All Jobs${NC}"
test_api_endpoint "List All Jobs" "$API_BASE/jobs/" "GET"

echo -e "\n${BLUE}🎉 Test Suite Complete${NC}"