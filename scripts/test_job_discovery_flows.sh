#!/bin/bash

# Test script for all Job Discovery Pipeline flows
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAYGROUND_DIR="$PROJECT_ROOT/playground"

echo -e "${BLUE}🧪 Job Discovery Pipeline Flow Tests${NC}"
echo -e "${BLUE}===================================${NC}"

# Function to run Python test
run_python_test() {
    local test_name="$1"
    local script_path="$2"
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    echo "Script: $script_path"
    
    if [ -f "$script_path" ]; then
        cd "$PROJECT_ROOT"
        if python3 "$script_path"; then
            echo -e "${GREEN}✅ $test_name completed successfully${NC}"
        else
            echo -e "${RED}❌ $test_name failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Script not found: $script_path${NC}"
        return 1
    fi
}

# Test 1: Full playground test suite
echo -e "\n${BLUE}1. Running Full Pipeline Playground${NC}"
run_python_test "Complete Job Discovery Test Suite" "$PLAYGROUND_DIR/job_discovery_pipeline.py"

# Test 2: Individual CRON test
echo -e "\n${BLUE}2. Running CRON Flow Test${NC}"
run_python_test "CRON-triggered Discovery" "$PLAYGROUND_DIR/test_job_discovery_cron.py"

# Test 3: Individual API test
echo -e "\n${BLUE}3. Running API Flow Test${NC}"
run_python_test "API-triggered Discovery" "$PLAYGROUND_DIR/test_job_discovery_api.py"

# Test 4: API endpoint tests (if server is running)
echo -e "\n${BLUE}4. Running API Endpoint Tests${NC}"
if curl -s "$API_BASE/health" > /dev/null 2>&1; then
    echo -e "${GREEN}API server detected, running endpoint tests...${NC}"
    bash "$PROJECT_ROOT/scripts/test_job_discovery_pipeline.sh"
else
    echo -e "${YELLOW}⚠️  API server not running, skipping endpoint tests${NC}"
    echo "To run endpoint tests, start the API server first:"
    echo "  cd app && uvicorn main:app --host 0.0.0.0 --port 8000"
fi

echo -e "\n${BLUE}🎉 All Flow Tests Complete${NC}"