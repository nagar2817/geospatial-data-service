#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping Geospatial Data Service...${NC}"

# Function to kill processes by name
kill_processes() {
    local process_name="$1"
    local pids=$(pgrep -f "$process_name")
    
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}Stopping $process_name processes...${NC}"
        for pid in $pids; do
            echo "  Killing PID: $pid"
            kill -TERM "$pid" 2>/dev/null
        done
        
        # Wait for graceful shutdown
        sleep 3
        
        # Force kill if still running
        local remaining_pids=$(pgrep -f "$process_name")
        if [ -n "$remaining_pids" ]; then
            echo -e "${YELLOW}Force killing remaining $process_name processes...${NC}"
            for pid in $remaining_pids; do
                kill -KILL "$pid" 2>/dev/null
            done
        fi
        echo -e "${GREEN}✅ $process_name stopped${NC}"
    else
        echo -e "${GREEN}✅ No $process_name processes found${NC}"
    fi
}

# Stop FastAPI (uvicorn)
echo -e "\n${YELLOW}📡 Stopping FastAPI server...${NC}"
kill_processes "uvicorn"
kill_processes "fastapi"
kill_processes "main:app"

# Stop Celery workers
echo -e "\n${YELLOW}⚙️  Stopping Celery workers...${NC}"
kill_processes "celery.*worker"
kill_processes "celery"

# Stop Celery beat (scheduler)
echo -e "\n${YELLOW}⏰ Stopping Celery beat...${NC}"
kill_processes "celery.*beat"

# Stop any Python processes running our app
echo -e "\n${YELLOW}🐍 Stopping Python app processes...${NC}"
kill_processes "python.*main.py"
kill_processes "python.*playground"

# Check for any remaining processes
echo -e "\n${YELLOW}🔍 Checking for remaining processes...${NC}"
remaining=$(pgrep -f "uvicorn|celery|main:app" | wc -l)
if [ "$remaining" -gt 0 ]; then
    echo -e "${RED}❌ Warning: $remaining processes still running${NC}"
    pgrep -f "uvicorn|celery|main:app" | xargs ps -p
else
    echo -e "${GREEN}✅ All services stopped successfully${NC}"
fi

echo -e "\n${GREEN}🎉 Geospatial Data Service stopped${NC}"