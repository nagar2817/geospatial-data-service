#!/bin/bash

# Test Job Discovery Pipeline in Docker environment
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🐳 Job Discovery Pipeline Docker Test${NC}"

# Start required services
echo -e "${YELLOW}🚀 Starting required services...${NC}"

# Start PostgreSQL
docker run -d --name geodata_postgres_test \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=geodata \
    -p 5433:5432 \
    postgres:15 || echo "PostgreSQL container already running"

# Start Redis
docker run -d --name geodata_redis_test \
    -p 6380:6379 \
    redis:7 || echo "Redis container already running"

# Wait for services
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Set environment variables for test
export DB_HOST=localhost
export DB_PORT=5433
export DB_NAME=geodata
export DB_USER=postgres
export DB_PASSWORD=postgres
export REDIS_HOST=localhost
export REDIS_PORT=6380

# Run migrations
echo -e "${YELLOW}📊 Running database migrations...${NC}"
cd app
alembic upgrade head

# Run pipeline test
echo -e "${YELLOW}🧪 Running pipeline tests...${NC}"
python3 ../playground/job_discovery_pipeline.py

# Cleanup
echo -e "${YELLOW}🧹 Cleaning up test containers...${NC}"
docker stop geodata_postgres_test geodata_redis_test || true
docker rm geodata_postgres_test geodata_redis_test || true

echo -e "${GREEN}✅ Docker test complete${NC}"