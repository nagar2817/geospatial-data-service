#!/bin/bash

# Quick test runner for Job Discovery Pipeline
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}⚡ Quick Job Discovery Pipeline Test${NC}"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv env
    source env/bin/activate
    pip install -r app/requirements.txt
else
    source env/bin/activate
fi

# Run quick playground test
echo -e "${YELLOW}🏃 Running quick pipeline test...${NC}"
python3 playground/job_discovery_pipeline.py

echo -e "${GREEN}✅ Quick test complete${NC}"