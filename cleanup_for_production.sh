#!/bin/bash
# Production Cleanup Script for Linux/Mac
# This script cleans all development artifacts and prepares the project for production deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Production Cleanup Script${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

items_to_remove=()

# Check for __pycache__ directories
echo -e "${YELLOW}Scanning for __pycache__ directories...${NC}"
while IFS= read -r -d '' dir; do
    items_to_remove+=("$dir")
done < <(find . -type d -name "__pycache__" -print0 2>/dev/null)
echo -e "${NC}Found ${#items_to_remove[@]} __pycache__ directories${NC}"

# Check for .pyc and .pyo files
echo -e "${YELLOW}Scanning for .pyc and .pyo files...${NC}"
pyc_count=0
while IFS= read -r -d '' file; do
    items_to_remove+=("$file")
    ((pyc_count++))
done < <(find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -print0 2>/dev/null)
echo -e "${NC}Found $pyc_count .pyc/.pyo files${NC}"

# Check for database
echo -e "${YELLOW}Checking for database file...${NC}"
[ -f "db.sqlite3" ] && items_to_remove+=("db.sqlite3") && echo -e "${NC}Found db.sqlite3${NC}"
[ -f "db.sqlite3-journal" ] && items_to_remove+=("db.sqlite3-journal") && echo -e "${NC}Found db.sqlite3-journal${NC}"

# Check for logs
echo -e "${YELLOW}Checking for log files...${NC}"
if [ -d "logs" ]; then
    log_count=0
    while IFS= read -r -d '' file; do
        items_to_remove+=("$file")
        ((log_count++))
    done < <(find logs -type f -print0 2>/dev/null)
    echo -e "${NC}Found $log_count log files${NC}"
fi

# Check for staticfiles
echo -e "${YELLOW}Checking for staticfiles directory...${NC}"
[ -d "staticfiles" ] && items_to_remove+=("staticfiles") && echo -e "${NC}Found staticfiles directory${NC}"

# Check for migration files (except __init__.py)
echo -e "${YELLOW}Checking for migration files...${NC}"
migration_count=0
while IFS= read -r -d '' file; do
    if [[ ! $(basename "$file") == "__init__.py" ]]; then
        items_to_remove+=("$file")
        ((migration_count++))
    fi
done < <(find . -type d -name "migrations" -exec find {} -maxdepth 1 -type f -name "*.py" -print0 \; 2>/dev/null)
echo -e "${NC}Found $migration_count migration files${NC}"

# Check for .env file
echo -e "${YELLOW}Checking for .env file...${NC}"
[ -f ".env" ] && echo -e "${YELLOW}Found .env file (will be backed up as .env.backup)${NC}"

# Check for node_modules
echo -e "${YELLOW}Checking for node_modules...${NC}"
[ -d "whatsapp-service/node_modules" ] && items_to_remove+=("whatsapp-service/node_modules") && echo -e "${NC}Found whatsapp-service/node_modules${NC}"

# Check for WhatsApp session data
echo -e "${YELLOW}Checking for WhatsApp session data...${NC}"
[ -d "whatsapp-service/.wwebjs_auth" ] && items_to_remove+=("whatsapp-service/.wwebjs_auth") && echo -e "${NC}Found whatsapp-service/.wwebjs_auth${NC}"
[ -d "whatsapp-service/.wwebjs_cache" ] && items_to_remove+=("whatsapp-service/.wwebjs_cache") && echo -e "${NC}Found whatsapp-service/.wwebjs_cache${NC}"

# Check for test files
echo -e "${YELLOW}Checking for test coverage files...${NC}"
[ -f ".coverage" ] && items_to_remove+=(".coverage") && echo -e "${NC}Found .coverage${NC}"
[ -f "coverage.xml" ] && items_to_remove+=("coverage.xml") && echo -e "${NC}Found coverage.xml${NC}"
[ -d ".pytest_cache" ] && items_to_remove+=(".pytest_cache") && echo -e "${NC}Found .pytest_cache${NC}"
[ -d "htmlcov" ] && items_to_remove+=("htmlcov") && echo -e "${NC}Found htmlcov${NC}"

# Check for Redis dump
echo -e "${YELLOW}Checking for Redis dump...${NC}"
[ -f "dump.rdb" ] && items_to_remove+=("dump.rdb") && echo -e "${NC}Found dump.rdb${NC}"

# Check for Celery files
echo -e "${YELLOW}Checking for Celery files...${NC}"
[ -f "celerybeat-schedule" ] && items_to_remove+=("celerybeat-schedule") && echo -e "${NC}Found celerybeat-schedule${NC}"
[ -f "celerybeat.pid" ] && items_to_remove+=("celerybeat.pid") && echo -e "${NC}Found celerybeat.pid${NC}"

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Summary${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "${YELLOW}Total items to remove: ${#items_to_remove[@]}${NC}"
echo ""

# Ask for confirmation
read -p "Do you want to proceed with cleanup? (yes/no): " confirmation
if [ "$confirmation" != "yes" ]; then
    echo -e "${RED}Cleanup cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}Starting cleanup...${NC}"

# Backup .env if it exists
if [ -f ".env" ]; then
    cp .env .env.backup
    echo -e "${GREEN}✓ Backed up .env to .env.backup${NC}"
fi

# Remove items
removed_count=0
for item in "${items_to_remove[@]}"; do
    if [ -e "$item" ]; then
        rm -rf "$item" && ((removed_count++))
    fi
done

echo -e "${GREEN}✓ Removed $removed_count items${NC}"

# Create fresh logs directory
mkdir -p logs
echo -e "${GREEN}✓ Created fresh logs directory${NC}"

# Create .gitkeep in logs
touch logs/.gitkeep
echo -e "${GREEN}✓ Created logs/.gitkeep${NC}"

# Make sure scripts are executable
chmod +x *.sh 2>/dev/null || true
echo -e "${GREEN}✓ Updated script permissions${NC}"

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps for production deployment:${NC}"
echo -e "${NC}1. Update .env file with production settings${NC}"
echo -e "${NC}2. Set DEBUG=False${NC}"
echo -e "${NC}3. Update ALLOWED_HOSTS with your domain${NC}"
echo -e "${NC}4. Generate a strong SECRET_KEY${NC}"
echo -e "${NC}5. Configure production database (PostgreSQL recommended)${NC}"
echo -e "${NC}6. Set up Redis for production${NC}"
echo -e "${NC}7. Run migrations on production server${NC}"
echo -e "${NC}8. Collect static files: python manage.py collectstatic${NC}"
echo -e "${NC}9. Create superuser: python manage.py createsuperuser${NC}"
echo ""
echo -e "${CYAN}Your .env file has been backed up to .env.backup${NC}"

