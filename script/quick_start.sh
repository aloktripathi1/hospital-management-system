#!/bin/bash

echo "==================================="
echo "Hospital Management System Startup"
echo "==================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    redis-server --daemonize yes
    sleep 2
fi

if pgrep -x "redis-server" > /dev/null; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis failed to start${NC}"
fi

# Check if MailHog is running
if ! docker ps | grep -q mailhog; then
    echo -e "${YELLOW}Starting MailHog...${NC}"
    docker rm mailhog 2>/dev/null
    docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog
    sleep 2
fi

if docker ps | grep -q mailhog; then
    echo -e "${GREEN}✓ MailHog is running${NC}"
else
    echo -e "${RED}✗ MailHog failed to start${NC}"
fi

echo ""
echo "==================================="
echo "Now start these in separate terminals:"
echo "==================================="
echo ""
echo -e "${YELLOW}Terminal 1 - Backend:${NC}"
echo "  cd backend && python3 app.py"
echo ""
echo -e "${YELLOW}Terminal 2 - Celery Worker:${NC}"
echo "  cd backend && celery -A celery_tasks.celery worker --loglevel=info --pool=solo"
echo ""
echo -e "${YELLOW}Terminal 3 - Frontend:${NC}"
echo "  cd frontend && python3 -m http.server 3000"
echo ""
echo "==================================="
echo "Access Points:"
echo "==================================="
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}Backend API:${NC} http://localhost:5000"
echo -e "${GREEN}MailHog UI:${NC} http://localhost:8025"
echo "==================================="
