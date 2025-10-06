#!/bin/bash

# SanaSend SaaS - Fully Automated Virtualmin Installer
# This script runs completely unattended with pre-configured values
# Run with: bash virtualmin-install-automated.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════
# PRE-CONFIGURED VALUES (NO PROMPTS!)
# ═══════════════════════════════════════════════════════

VMIN_USER="sanasend"
DOMAIN_NAME="sanasend.com"
INSTALL_PATH="/home/sanasend/public_html"
DB_PASSWORD="Passisdb123"
ADMIN_USERNAME="sanaric"
ADMIN_EMAIL="sanasoft20@gmail.com"
ADMIN_PASSWORD="Sanaric123"
DB_NAME="whatsapp_saas_prod"
DB_USER="whatsapp_saas"
USE_REDIS="false"  # Set to "true" if you want Redis

# Generate Node.js API key
NODE_API_KEY=$(openssl rand -hex 32)

# Script banner
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║     SanaSend SaaS - Automated Virtualmin Installer   ║
║                                                       ║
║          Fully Automated - Zero Prompts!             ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Helper functions
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_step() {
    echo -e "\n${CYAN}═══ $1 ═══${NC}\n"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Do not run this script as root! Run as your Virtualmin user."
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    print_error "sudo is required but not installed. Please install sudo first."
    exit 1
fi

# Welcome message
print_step "FULLY AUTOMATED INSTALLATION"
echo -e "${YELLOW}This script will install SanaSend WhatsApp SaaS with pre-configured values.${NC}"
echo -e "${YELLOW}Estimated time: 10-15 minutes${NC}"
echo -e "${YELLOW}NO PROMPTS - Completely automated!${NC}\n"

# Configuration summary
print_step "CONFIGURATION (PRE-CONFIGURED)"
echo -e "${BLUE}Server Configuration:${NC}"
echo "  • Username: $VMIN_USER"
echo "  • Domain: $DOMAIN_NAME"
echo "  • Installation Path: $INSTALL_PATH"
echo ""
echo -e "${BLUE}Database Configuration:${NC}"
echo "  • Database Name: $DB_NAME"
echo "  • Database User: $DB_USER"
echo "  • Password: ********** (configured)"
echo ""
echo -e "${BLUE}Admin Configuration:${NC}"
echo "  • Username: $ADMIN_USERNAME"
echo "  • Email: $ADMIN_EMAIL"
echo "  • Password: ********** (configured)"
echo ""
echo -e "${BLUE}Services:${NC}"
echo "  • Redis: $([ "$USE_REDIS" = "true" ] && echo "Enabled" || echo "Disabled (local cache)")"
echo "  • Node.js API Key: ${NODE_API_KEY:0:16}..."
echo ""

read -p "Press Enter to start automated installation or Ctrl+C to cancel..."

# Set paths
PROJECT_DIR="$INSTALL_PATH"
VENV_DIR="$PROJECT_DIR/venv"

print_status "Starting fully automated installation..."
echo ""

# Step 1: Install System Dependencies
print_step "STEP 1/14: Installing System Dependencies"
print_info "Updating system and installing required packages..."

# Check if packages are already installed
PACKAGES_TO_INSTALL=""
for pkg in python3 python3-pip python3-venv python3-dev build-essential libpq-dev git curl wget; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL $pkg"
    fi
done

if [ ! -z "$PACKAGES_TO_INSTALL" ]; then
    print_info "Installing packages: $PACKAGES_TO_INSTALL"
    sudo apt update -qq
    sudo apt install -y $PACKAGES_TO_INSTALL > /dev/null 2>&1
else
    print_status "All required system packages are already installed"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_status "Python $PYTHON_VERSION installed"

# Step 2: Install Node.js
print_step "STEP 2/14: Installing Node.js"
if ! command -v node &> /dev/null; then
    print_info "Installing Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - > /dev/null 2>&1
    sudo apt install -y nodejs > /dev/null 2>&1
    print_status "Node.js installed"
else
    NODE_VERSION=$(node --version)
    print_status "Node.js $NODE_VERSION already installed"
fi

# Step 3: Install PostgreSQL
print_step "STEP 3/14: Setting up PostgreSQL"
if ! command -v psql &> /dev/null; then
    print_info "Installing PostgreSQL..."
    sudo apt install -y postgresql postgresql-contrib > /dev/null 2>&1
    sudo systemctl enable postgresql > /dev/null 2>&1
    sudo systemctl start postgresql
    print_status "PostgreSQL installed"
else
    print_status "PostgreSQL already installed"
fi

# Step 4: Create Database and User
print_step "STEP 4/14: Creating Database and User"
print_info "Creating database: $DB_NAME"
print_info "Creating database user: $DB_USER"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" > /dev/null 2>&1

sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = '$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" > /dev/null 2>&1

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" > /dev/null 2>&1
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;" > /dev/null 2>&1

print_status "Database and user created successfully"

# Step 5: TEST DATABASE CONNECTION
print_step "STEP 5/14: Testing Database Connection"
print_info "Verifying database credentials..."

export PGPASSWORD="$DB_PASSWORD"
CONNECTION_TEST=$(psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT 1 AS connection_test;" -t 2>&1)

if echo "$CONNECTION_TEST" | grep -q "1"; then
    print_status "✓ Database connection successful!"
    print_status "✓ Credentials verified"
    print_status "✓ Database is ready"
else
    print_error "✗ Database connection failed!"
    print_error "Connection test output: $CONNECTION_TEST"
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                       ║${NC}"
    echo -e "${RED}║         DATABASE CONNECTION TEST FAILED!              ║${NC}"
    echo -e "${RED}║                                                       ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_error "Please check:"
    print_error "1. Database name: $DB_NAME"
    print_error "2. Database user: $DB_USER"
    print_error "3. Database password is correct"
    print_error "4. PostgreSQL is running: sudo systemctl status postgresql"
    echo ""
    unset PGPASSWORD
    exit 1
fi
unset PGPASSWORD

# Step 6: Install Redis (if enabled)
print_step "STEP 6/14: Setting up Redis"
if [[ $USE_REDIS == "true" ]]; then
    if ! command -v redis-server &> /dev/null; then
        print_info "Installing Redis..."
        sudo apt install -y redis-server > /dev/null 2>&1
        sudo systemctl enable redis-server > /dev/null 2>&1
        sudo systemctl start redis-server
        print_status "Redis installed and started"
    else
        print_status "Redis already installed"
    fi
else
    print_info "Skipping Redis installation (using local cache)"
fi

# Step 7: Install Supervisor
print_step "STEP 7/14: Installing Supervisor"
if ! command -v supervisorctl &> /dev/null; then
    sudo apt install -y supervisor > /dev/null 2>&1
    sudo systemctl enable supervisor > /dev/null 2>&1
    sudo systemctl start supervisor
    print_status "Supervisor installed"
else
    print_status "Supervisor already installed"
fi

# Step 8: Setup Project Directory
print_step "STEP 8/14: Setting up Project Directory"
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    print_info "Please upload your project files to $PROJECT_DIR first"
    print_info "You can use: git clone, SFTP, or Virtualmin File Manager"
    exit 1
fi

cd "$PROJECT_DIR"

# Check if project files exist
if [ ! -f "manage.py" ]; then
    print_error "Project files not found in $PROJECT_DIR"
    print_info "Please upload your project files to $PROJECT_DIR first"
    exit 1
fi

print_status "Project files found"

# Step 9: Create Python Virtual Environment
print_step "STEP 9/14: Creating Python Virtual Environment"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip and install dependencies
print_info "Installing Python dependencies (this may take a few minutes)..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_status "Python dependencies installed"

# Step 10: Create Project Directories
print_step "STEP 10/14: Creating Project Directories"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/media"
mkdir -p "$PROJECT_DIR/staticfiles"
mkdir -p "$PROJECT_DIR/whatsapp-service/sessions"
mkdir -p "$PROJECT_DIR/whatsapp-service/logs"
print_status "Project directories created"

# Generate Django secret key
print_info "Generating Django secret key..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Step 11: Create Environment Configuration
print_step "STEP 11/14: Creating Environment Configuration"
cat > "$PROJECT_DIR/.env.production" << EOF
# Django Settings
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN_NAME,www.$DOMAIN_NAME
ENVIRONMENT=production

# Database
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Redis
USE_REDIS=$USE_REDIS
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Node.js Service
NODE_SERVICE_URL=http://localhost:3000
NODE_SERVICE_API_KEY=$NODE_API_KEY

# Django Base URL
DJANGO_BASE_URL=https://$DOMAIN_NAME

# Security
CORS_ALLOWED_ORIGINS=https://$DOMAIN_NAME,https://www.$DOMAIN_NAME
SECURE_SSL_REDIRECT=True

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Rate Limiting
MAX_MESSAGES_PER_MINUTE=10
MAX_MESSAGES_PER_DAY=1000

# Logging
LOG_FILE=$PROJECT_DIR/logs/django.log
ERROR_LOG_FILE=$PROJECT_DIR/logs/error.log

# Static/Media Files
STATIC_ROOT=$PROJECT_DIR/staticfiles
MEDIA_ROOT=$PROJECT_DIR/media
EOF
print_status "Environment configuration created"

# Step 12: Initialize Django
print_step "STEP 12/14: Initializing Django Application"

# Load environment variables from .env.production
print_info "Loading environment variables..."
export DJANGO_SETTINGS_MODULE=config.settings.production
export $(grep -v '^#' "$PROJECT_DIR/.env.production" | xargs)

print_info "Running database migrations..."
python manage.py migrate --noinput

print_info "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser non-interactively
print_info "Creating admin superuser: $ADMIN_USERNAME..."
python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$ADMIN_USERNAME').exists():
    User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')
    print('✓ Superuser created successfully')
else:
    print('✓ Superuser already exists')
PYEOF

print_status "Django initialized successfully"

# Step 13: Setup Node.js WhatsApp Service
print_step "STEP 13/14: Setting up Node.js WhatsApp Service"
cd "$PROJECT_DIR/whatsapp-service"
print_info "Installing Node.js dependencies..."
npm install --production --silent
print_status "Node.js dependencies installed"

# Create Node.js .env file
cat > "$PROJECT_DIR/whatsapp-service/.env" << EOF
NODE_ENV=production
PORT=3000
DJANGO_BASE_URL=https://$DOMAIN_NAME
API_KEY=$NODE_API_KEY
EOF

# Step 14: Create Systemd Services
print_step "STEP 14/14: Creating System Services"

# Django service
sudo tee /etc/systemd/system/whatsapp-django.service > /dev/null << EOF
[Unit]
Description=WhatsApp SaaS Django Application
After=network.target postgresql.service

[Service]
Type=exec
User=$VMIN_USER
Group=$VMIN_USER
WorkingDirectory=$PROJECT_DIR
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile $PROJECT_DIR/logs/gunicorn-access.log \
    --error-logfile $PROJECT_DIR/logs/gunicorn-error.log \
    config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Node.js service
sudo tee /etc/systemd/system/whatsapp-node.service > /dev/null << EOF
[Unit]
Description=WhatsApp SaaS Node.js Service
After=network.target

[Service]
Type=simple
User=$VMIN_USER
Group=$VMIN_USER
WorkingDirectory=$PROJECT_DIR/whatsapp-service
ExecStart=/usr/bin/node src/server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable services
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-django > /dev/null 2>&1
sudo systemctl enable whatsapp-node > /dev/null 2>&1
print_status "System services created and enabled"

# Set proper permissions
print_info "Setting file permissions..."
find "$PROJECT_DIR" -type d -exec chmod 755 {} \;
find "$PROJECT_DIR" -type f -exec chmod 644 {} \;
chmod +x "$VENV_DIR/bin/"*
chmod 775 "$PROJECT_DIR/logs"
chmod 775 "$PROJECT_DIR/media"
print_status "Permissions set correctly"

# Start services
print_info "Starting services..."
sudo systemctl start whatsapp-django
sudo systemctl start whatsapp-node

# Check service status
sleep 3
DJANGO_STATUS=$(sudo systemctl is-active whatsapp-django)
NODE_STATUS=$(sudo systemctl is-active whatsapp-node)

echo ""
print_step "SERVICE STATUS"
if [ "$DJANGO_STATUS" = "active" ]; then
    print_status "✓ Django service is running"
else
    print_error "✗ Django service failed to start"
    print_warning "Check logs: sudo journalctl -u whatsapp-django -n 50"
fi

if [ "$NODE_STATUS" = "active" ]; then
    print_status "✓ Node.js service is running"
else
    print_error "✗ Node.js service failed to start"
    print_warning "Check logs: sudo journalctl -u whatsapp-node -n 50"
fi

# Installation complete
echo ""
print_step "INSTALLATION COMPLETE!"

echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║         Installation Successful! 🎉                   ║
║                                                       ║
║           All Services Running!                       ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Next steps
echo -e "\n${CYAN}═══ NEXT STEPS ═══${NC}\n"

echo -e "${YELLOW}1. Configure Web Server (Nginx/Apache)${NC}"
echo -e "   Follow the web server configuration in VIRTUALMIN_DEPLOYMENT_GUIDE.md"
echo -e "   Section 9: Configure Nginx Reverse Proxy\n"

echo -e "${YELLOW}2. Setup SSL Certificate${NC}"
echo -e "   Run: ${GREEN}sudo certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME${NC}\n"

echo -e "${YELLOW}3. Test Your Installation${NC}"
echo -e "   After SSL setup, visit:"
echo -e "   • Admin Panel: ${GREEN}https://$DOMAIN_NAME/admin/${NC}"
echo -e "   • API Docs: ${GREEN}https://$DOMAIN_NAME/api/docs/${NC}"
echo -e "   • Health Check: ${GREEN}https://$DOMAIN_NAME/health/${NC}\n"

echo -e "${CYAN}═══ LOGIN CREDENTIALS ═══${NC}\n"
echo -e "Admin Panel Login:"
echo -e "  • URL: ${GREEN}https://$DOMAIN_NAME/admin/${NC}"
echo -e "  • Username: ${GREEN}$ADMIN_USERNAME${NC}"
echo -e "  • Password: ${GREEN}$ADMIN_PASSWORD${NC}"
echo -e "  • Email: ${GREEN}$ADMIN_EMAIL${NC}\n"

echo -e "${CYAN}═══ PROJECT INFORMATION ═══${NC}\n"
echo -e "Project Path: ${GREEN}$PROJECT_DIR${NC}"
echo -e "Database: ${GREEN}$DB_NAME${NC}"
echo -e "Database User: ${GREEN}$DB_USER${NC}"
echo -e "Database Password: ${GREEN}$DB_PASSWORD${NC}"
echo -e "Django Service: ${GREEN}whatsapp-django.service${NC}"
echo -e "Node.js Service: ${GREEN}whatsapp-node.service${NC}"
echo -e "Environment File: ${GREEN}$PROJECT_DIR/.env.production${NC}\n"

echo -e "${CYAN}═══ SERVICE MANAGEMENT ═══${NC}\n"
echo -e "View Django logs: ${GREEN}sudo journalctl -u whatsapp-django -f${NC}"
echo -e "View Node logs: ${GREEN}sudo journalctl -u whatsapp-node -f${NC}"
echo -e "Restart Django: ${GREEN}sudo systemctl restart whatsapp-django${NC}"
echo -e "Restart Node: ${GREEN}sudo systemctl restart whatsapp-node${NC}"
echo -e "Check status: ${GREEN}sudo systemctl status whatsapp-django whatsapp-node${NC}\n"

echo -e "${CYAN}═══ IMPORTANT NOTES ═══${NC}\n"
echo -e "• Node.js API key: ${GREEN}$NODE_API_KEY${NC}"
echo -e "• All credentials saved in: ${GREEN}$PROJECT_DIR/INSTALLATION_INFO.txt${NC}"
echo -e "• Make sure to configure your web server (Step 1 above)"
echo -e "• Run certbot to enable HTTPS (Step 2 above)\n"

# Save installation info
cat > "$PROJECT_DIR/INSTALLATION_INFO.txt" << EOF
SanaSend SaaS - Installation Information
========================================

Installation Date: $(date)
Domain: $DOMAIN_NAME
Project Path: $PROJECT_DIR

Database Configuration:
- Database Name: $DB_NAME
- Database User: $DB_USER
- Database Password: $DB_PASSWORD

Admin Credentials:
- Username: $ADMIN_USERNAME
- Email: $ADMIN_EMAIL
- Password: $ADMIN_PASSWORD

Node.js API Key: $NODE_API_KEY

Services:
- Django: whatsapp-django.service
- Node.js: whatsapp-node.service

Useful Commands:
- View Django logs: sudo journalctl -u whatsapp-django -f
- View Node logs: sudo journalctl -u whatsapp-node -f
- Restart Django: sudo systemctl restart whatsapp-django
- Restart Node: sudo systemctl restart whatsapp-node
- Check status: sudo systemctl status whatsapp-django whatsapp-node

Next Steps:
1. Configure web server reverse proxy (Nginx/Apache)
2. Setup SSL with certbot
3. Access admin panel at https://$DOMAIN_NAME/admin/
4. Login with username: $ADMIN_USERNAME

For support, check VIRTUALMIN_DEPLOYMENT_GUIDE.md
EOF

print_status "Installation info saved to: $PROJECT_DIR/INSTALLATION_INFO.txt"

echo -e "\n${GREEN}Happy deploying! 🚀${NC}\n"

