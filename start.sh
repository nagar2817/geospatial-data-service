#!/bin/bash

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

# Check if required services are running
echo -e "${YELLOW}📋 Checking required services...${NC}"
if ! docker ps | grep -q myuser_pgvector; then
    echo -e "${RED}❌ PostgreSQL container not found. Please start database first.${NC}"
    echo "Run: docker run --name geodata_postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=geodata -p 5432:5432 -d postgres:15"
    exit 1
fi

if ! docker ps | grep -q redis; then
    echo -e "${RED}❌ Redis container not found. Please start Redis first.${NC}"
    echo "Run: docker run --name geodata_redis -p 6379:6379 -d redis:7"
    exit 1
fi

echo -e "${GREEN}✅ Docker services are running${NC}"

# Navigate to app directory
if [ ! -d "app" ]; then
    echo -e "${RED}❌ app directory not found. Make sure you're in the project root.${NC}"
    exit 1
fi



# Start FastAPI server in new tab
echo -e "${YELLOW}🖥️  Starting FastAPI server...${NC}"
run_in_new_tab "source env/bin/activate && cd app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload" "FastAPI Server"

# Wait for server to start
echo -e "${YELLOW}⏳ Waiting for FastAPI server to start...${NC}"
sleep 5

# Check if server is running
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null; then
        echo -e "${GREEN}✅ FastAPI server is running${NC}"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ FastAPI server failed to start${NC}"
            exit 1
        fi
        echo -e "${YELLOW}⏳ Waiting for server... ($i/10)${NC}"
        sleep 2
    fi
done

# Start Celery worker in new tab
echo -e "${YELLOW}⚙️  Starting Celery worker...${NC}"
run_in_new_tab "source env/bin/activate && cd app && celery -A config.celery_config worker --loglevel=info --concurrency=2" "Celery Worker"

# Wait for worker to start
echo -e "${YELLOW}⏳ Waiting for Celery worker to start...${NC}"
sleep 5

# Start Flower monitoring in new tab
echo -e "${YELLOW}🌼 Starting Flower (Celery Monitoring)...${NC}"
run_in_new_tab "source env/bin/activate && cd app && celery -A config.celery_config flower --port=5555" "Celery Flower"

echo ""
echo -e "${GREEN}🎉 Test setup complete!${NC}"
echo ""
echo "Services running:"
echo "  📡 FastAPI Server: http://localhost:8000"
echo "  📚 API Documentation: http://localhost:8000/docs"
echo "  🔧 API Endpoints: http://localhost:8000/api/v1"
echo ""
echo "Test endpoints:"
echo "  🏥 Health: curl http://localhost:8000/api/v1/health"
echo "  📋 Jobs: curl http://localhost:8000/api/v1/jobs/"
echo ""
echo -e "${YELLOW}💡 Check the new terminal tabs for server and worker logs${NC}"