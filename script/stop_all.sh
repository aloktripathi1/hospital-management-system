#!/bin/bash

echo "Stopping all Hospital Management System services..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Stop Redis
if pgrep -x "redis-server" > /dev/null; then
    echo -e "${RED}Stopping Redis...${NC}"
    pkill redis-server
    echo -e "${GREEN}✓ Redis stopped${NC}"
fi

# Stop MailHog
if docker ps | grep -q mailhog; then
    echo -e "${RED}Stopping MailHog...${NC}"
    docker stop mailhog 2>/dev/null
    docker rm mailhog 2>/dev/null
    echo -e "${GREEN}✓ MailHog stopped${NC}"
fi

# Kill Python Flask app
if pgrep -f "python3 app.py" > /dev/null; then
    echo -e "${RED}Stopping Flask Backend...${NC}"
    pkill -f "python3 app.py"
    echo -e "${GREEN}✓ Backend stopped${NC}"
fi

# Kill Celery worker
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${RED}Stopping Celery Worker...${NC}"
    pkill -f "celery.*worker"
    echo -e "${GREEN}✓ Celery stopped${NC}"
fi

# Kill Frontend server
if pgrep -f "http.server" > /dev/null; then
    echo -e "${RED}Stopping Frontend Server...${NC}"
    pkill -f "http.server"
    echo -e "${GREEN}✓ Frontend stopped${NC}"
fi

echo ""
echo -e "${GREEN}All services stopped successfully!${NC}"
