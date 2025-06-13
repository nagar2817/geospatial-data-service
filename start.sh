#!/usr/bin/env bash

# Ensure script runs in bash for associative arrays support
if [ -z "$BASH_VERSION" ]; then
    echo "This script must be run with bash. Restarting with bash..."
    exec bash "$0" "$@"
fi

echo "🚀 Setting up Geospatial Data Service Test Environment"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Exit on any error
set -e

# Function to handle errors
handle_error() {
    echo -e "${RED}❌ Error occurred in script at line $1${NC}"
    echo -e "${RED}❌ Stopping execution${NC}"
    exit 1
}

# Set error handler
trap 'handle_error $LINENO' ERR

# Source AWS credentials for GEE via WIF
source ./scripts/assume.sh


# Function to run command in new terminal tab (cross-platform)
run_in_new_tab() {
    local cmd="$1"
    local title="$2"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && $cmd\""
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - try different terminal emulators
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --tab --title="$title" -- bash -c "$cmd; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -title "$title" -e "$cmd" &
        else
            echo -e "${YELLOW}⚠️  Please run manually in new terminal: $cmd${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Please run manually in new terminal: $cmd${NC}"
    fi
}

# Check if Docker is running
echo -e "${YELLOW}📋 Checking Docker status...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

CONTAINER_IDS=(
  "3dee0df672ffeae08871b80c2e770cd4354ed94c229abe3a05ae95c1653e628e"
  "bc173c2ecd41ac4038fe6d511a633787947cb67582178e2ba01bbf41153e6b60"
  "7349026824cd7470e68f623516b9648c50bb74fa6f73375f6e1755d69e608e88"
)

for cid in "${CONTAINER_IDS[@]}"; do
  if ! docker ps -q --no-trunc | grep -q "$cid"; then
    echo -e "${YELLOW}⚠️  Container [$cid] is not running. Attempting to start...${NC}"
    if docker ps -a -q --no-trunc | grep -q "$cid"; then
      docker start "$cid" >/dev/null && echo -e "${GREEN}✅ Started existing container [$cid]${NC}"
    else
      echo -e "${RED}❌ Container [$cid] not found. Please create it manually.${NC}"
      exit 1
    fi
  fi
done

echo -e "${GREEN}✅ Required containers are running${NC}"

echo -e "${GREEN}✅ Docker services are running${NC}"

# Navigate to app directory
if [ ! -d "app" ]; then
    echo -e "${RED}❌ app directory not found. Make sure you're in the project root.${NC}"
    exit 1
fi

# FastAPI Server
echo -e "${YELLOW}🛰️ Checking FastAPI server on port 8000...${NC}"
if nc -z localhost 8000; then
    echo -e "${GREEN}✅ FastAPI already running on port 8000${NC}"
else
    echo -e "${YELLOW}🚀 Launching FastAPI server...${NC}"
    run_in_new_tab "source env/bin/activate && cd app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload" "FastAPI Server"
    for i in {1..10}; do
        if nc -z localhost 8000; then
            echo -e "${GREEN}✅ FastAPI started successfully${NC}"
            break
        fi
        sleep 2
    done
fi

# Celery Worker
echo -e "${YELLOW}🧩 Checking for Celery worker...${NC}"
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${GREEN}✅ Celery worker already running${NC}"
else
    echo -e "${YELLOW}⚙️  Launching Celery worker...${NC}"
    run_in_new_tab "source env/bin/activate && cd app && celery -A config.celery_config worker --loglevel=info --concurrency=2 -E -Q celery,geospatial,monitoring,scheduler >> ../logs/celery.log 2>&1" "Celery Worker"
    for i in {1..10}; do
        if pgrep -f "celery.*worker" > /dev/null; then
            echo -e "${GREEN}✅ Celery worker started${NC}"
            break
        fi
        sleep 2
    done
fi

# Flower
echo -e "${YELLOW}🌸 Checking for Flower monitoring...${NC}"
if pgrep -f "celery.*flower" > /dev/null; then
    echo -e "${GREEN}✅ Flower is already running${NC}"
else
    echo -e "${YELLOW}🌼 Launching Flower...${NC}"
    run_in_new_tab "source env/bin/activate && cd app && celery -A config.celery_config flower --port=5555" "Celery Flower"
    for i in {1..10}; do
        if pgrep -f "celery.*flower" > /dev/null; then
            echo -e "${GREEN}✅ Flower started${NC}"
            break
        fi
        sleep 2
    done
fi

echo ""
echo -e "${GREEN}🎉 Test setup complete!${NC}"
echo ""
echo "Services running:"
echo "  📡 Data-service Server: http://localhost:8000"
echo "  📚 API Documentation: http://localhost:8000/docs"
echo "  🔧 API Endpoints: http://localhost:8000/api/v1"
echo "  🌼 Celery Flower: http://localhost:5555"
echo "  🐰 RabbitMQ Server: http://localhost:15672 (guest/guest)"
echo ""
echo "Test endpoints:"
echo "  🏥 Health: curl http://localhost:8000/api/v1/health"
echo "  📋 Jobs: curl http://localhost:8000/api/v1/jobs/"
echo ""
echo -e "${YELLOW}💡 Check the new terminal tabs for server logs${NC}"
echo -e "${YELLOW}💡 Celery worker logs are being saved to logs/celery.log${NC}"