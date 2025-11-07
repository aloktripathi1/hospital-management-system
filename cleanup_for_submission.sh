#!/bin/bash

################################################################################
# Cleanup Script for Project Submission
# Removes unnecessary files while keeping essential code and documentation
################################################################################

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Project Cleanup for Submission${NC}"
echo -e "${BLUE}========================================${NC}\n"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Files/directories to DELETE
echo -e "${YELLOW}Files to be DELETED:${NC}\n"
echo "1. Python cache files (__pycache__, *.pyc, *.pyo)"
echo "2. Database file (instance/*.db) - will be recreated"
echo "3. Celery schedule files"
echo "4. Log files"
echo "5. Exports directory (CSV files)"
echo "6. Virtual environment (venv) - will be recreated with start.sh"
echo "7. Temporary test files"
echo "8. .env file (contains sensitive passwords)"
echo "9. Git internal files (.pids, etc.)"
echo ""

echo -e "${GREEN}Files to be KEPT:${NC}\n"
echo "✓ All source code (.py, .js, .html, .css)"
echo "✓ Documentation (.md files)"
echo "✓ Configuration files (requirements.txt)"
echo "✓ Scripts (start.sh, stop-all.sh, etc.)"
echo "✓ .gitignore"
echo "✓ README and guides"
echo ""

read -p "Do you want to proceed with cleanup? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Cleanup cancelled.${NC}"
    exit 0
fi

echo -e "\n${BLUE}Starting cleanup...${NC}\n"

# 1. Remove Python cache files
echo -e "${YELLOW}[1/9] Removing Python cache files...${NC}"
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "${GREEN}✓ Python cache cleaned${NC}"

# 2. Remove database file (will be recreated on first run)
echo -e "${YELLOW}[2/9] Removing database file...${NC}"
if [ -f "$PROJECT_ROOT/backend/instance/hospital-management.db" ]; then
    rm -f "$PROJECT_ROOT/backend/instance/hospital-management.db"
    echo -e "${GREEN}✓ Database file removed (will be recreated on first run)${NC}"
else
    echo -e "${BLUE}○ No database file found${NC}"
fi

# 3. Remove Celery schedule files
echo -e "${YELLOW}[3/9] Removing Celery schedule files...${NC}"
rm -f "$PROJECT_ROOT/backend/celerybeat-schedule" 2>/dev/null || true
rm -rf "$PROJECT_ROOT/backend/celerybeat-schedule.db" 2>/dev/null || true
echo -e "${GREEN}✓ Celery schedule cleaned${NC}"

# 4. Remove log files
echo -e "${YELLOW}[4/9] Removing log files...${NC}"
if [ -d "$PROJECT_ROOT/logs" ]; then
    rm -rf "$PROJECT_ROOT/logs"
    echo -e "${GREEN}✓ Log directory removed${NC}"
else
    echo -e "${BLUE}○ No log directory found${NC}"
fi

# 5. Remove exports directory
echo -e "${YELLOW}[5/9] Removing exports directory...${NC}"
if [ -d "$PROJECT_ROOT/backend/exports" ]; then
    rm -rf "$PROJECT_ROOT/backend/exports"
    echo -e "${GREEN}✓ Exports directory removed${NC}"
else
    echo -e "${BLUE}○ No exports directory found${NC}"
fi

# 6. Remove virtual environment
echo -e "${YELLOW}[6/9] Removing virtual environment...${NC}"
if [ -d "$PROJECT_ROOT/backend/venv" ]; then
    rm -rf "$PROJECT_ROOT/backend/venv"
    echo -e "${GREEN}✓ Virtual environment removed (will be recreated by start.sh)${NC}"
else
    echo -e "${BLUE}○ No virtual environment found${NC}"
fi

# 7. Remove test/temporary files
echo -e "${YELLOW}[7/9] Removing temporary test files...${NC}"
rm -f "$PROJECT_ROOT/test_api.py" 2>/dev/null || true
rm -f "$PROJECT_ROOT/test_jwt.py" 2>/dev/null || true
rm -f "$PROJECT_ROOT/check_duplicates.py" 2>/dev/null || true
rm -f "$PROJECT_ROOT/create_demo_accounts.py" 2>/dev/null || true
rm -f "$PROJECT_ROOT/convert_jsonify.py" 2>/dev/null || true
echo -e "${GREEN}✓ Temporary test files removed${NC}"

# 8. Remove .env file (contains passwords)
echo -e "${YELLOW}[8/9] Handling .env file...${NC}"
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    # Create .env.example as template
    cat > "$PROJECT_ROOT/backend/.env.example" << 'EOF'
# Email Configuration for Gmail
# Create App Password: Google Account > Security > 2-Step Verification > App passwords

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_16_char_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# Flask Environment
FLASK_ENV=development
FLASK_APP=app.py
EOF
    rm -f "$PROJECT_ROOT/backend/.env"
    echo -e "${GREEN}✓ .env removed, .env.example created as template${NC}"
else
    echo -e "${BLUE}○ No .env file found${NC}"
fi

# 9. Remove Git internal tracking files
echo -e "${YELLOW}[9/9] Removing Git tracking files...${NC}"
rm -f "$PROJECT_ROOT/.pids" 2>/dev/null || true
echo -e "${GREEN}✓ Git tracking files cleaned${NC}"

# Clean up large shell scripts that were for automation
echo -e "${YELLOW}[Extra] Removing verbose automation scripts...${NC}"
rm -f "$PROJECT_ROOT/start-all.sh" 2>/dev/null || true
echo -e "${GREEN}✓ Verbose scripts removed (keeping simple start.sh)${NC}"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Cleanup Completed Successfully!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${BLUE}Project is now ready for submission!${NC}\n"

echo -e "${GREEN}What remains:${NC}"
echo "  ✓ Clean source code (backend + frontend)"
echo "  ✓ Documentation (README.md and docs/)"
echo "  ✓ Configuration files (requirements.txt)"
echo "  ✓ Simple startup script (start.sh)"
echo "  ✓ .env.example template"
echo ""

echo -e "${YELLOW}To set up from scratch:${NC}"
echo "  1. Copy .env.example to .env and add your Gmail credentials"
echo "  2. Run: ./start.sh"
echo "  3. Access: http://127.0.0.1:5000"
echo ""

echo -e "${BLUE}Database will be created automatically on first run with:${NC}"
echo "  • Admin user: admin / admin"
echo "  • Sample data ready for demonstration"
echo ""
