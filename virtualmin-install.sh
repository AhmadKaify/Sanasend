#!/bin/bash

# SanaSend SaaS - Virtualmin Automated Installer
# This script automates 90% of the Virtualmin deployment process
# Run with: bash virtualmin-install.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script banner
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║        SanaSend SaaS - Virtualmin Installer          ║
║                                                       ║
║   Automated deployment for Virtualmin servers        ║
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
print_step "WELCOME TO VIRTUALMIN INSTALLER"
echo -e "${YELLOW}This script will set up SanaSend WhatsApp SaaS on your Virtualmin server.${NC}"
echo -e "${YELLOW}Estimated time: 10-15 minutes${NC}\n"

# Prompt for configuration
print_step "CONFIGURATION"

# Get Virtualmin username
read -p "Enter Virtualmin username [sanasend]: " VMIN_USER
VMIN_USER=${VMIN_USER:-sanasend}

# Get domain
read -p "Enter your domain name (e.g., example.com): " DOMAIN_NAME
if [ -z "$DOMAIN_NAME" ]; then
    print_error "Domain name is required!"
    exit 1
fi

# Get installation path
DEFAULT_PATH="/home/$VMIN_USER/public_html"
read -p "Enter installation path [$DEFAULT_PATH]: " INSTALL_PATH
INSTALL_PATH=${INSTALL_PATH:-$DEFAULT_PATH}

# Get database password
read -sp "Enter database password (create a strong password): " DB_PASSWORD
echo
if [ -z "$DB_PASSWORD" ]; then
    print_error "Database password is required!"
    exit 1
fi

# Get Node.js API key
read -sp "Enter Node.js service API key (create a random string): " NODE_API_KEY
echo
if [ -z "$NODE_API_KEY" ]; then
    NODE_API_KEY=$(openssl rand -hex 32)
    print_info "Generated random API key: $NODE_API_KEY"
fi

# Configuration summary
print_step "CONFIGURATION SUMMARY"
echo "Username: $VMIN_USER"
echo "Domain: $DOMAIN_NAME"
echo "Database: whatsapp_saas_prod"
echo "DB User: whatsapp_saas"
echo "Installation Path: $INSTALL_PATH"
echo ""
read -p "Continue with this configuration? (y/n): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    print_error "Installation cancelled by user"
    exit 1
fi

# Set paths
PROJECT_DIR="$INSTALL_PATH"
VENV_DIR="$PROJECT_DIR/venv"

# Step 1: Install System Dependencies
print_step "STEP 1/12: Installing System Dependencies"
print_info "This will update your system and install required packages..."

# Check if packages are already installed to avoid unnecessary installations
PACKAGES_TO_INSTALL=""
for pkg in python3 python3-pip python3-venv python3-dev build-essential libpq-dev git curl wget; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL $pkg"
    fi
done

if [ ! -z "$PACKAGES_TO_INSTALL" ]; then
    print_info "Installing packages: $PACKAGES_TO_INSTALL"
    sudo apt update -qq
    sudo apt install -y $PACKAGES_TO_INSTALL
else
    print_status "All required system packages are already installed"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_status "Python $PYTHON_VERSION installed"

# Install Node.js 18 if not present
print_step "STEP 2/12: Installing Node.js"
if ! command -v node &> /dev/null; then
    print_info "Installing Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
else
    NODE_VERSION=$(node --version)
    print_status "Node.js $NODE_VERSION already installed"
fi

# Install PostgreSQL if not present
print_step "STEP 3/12: Setting up PostgreSQL"
if ! command -v psql &> /dev/null; then
    print_info "Installing PostgreSQL..."
    sudo apt install -y postgresql postgresql-contrib
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
else
    print_status "PostgreSQL already installed"
fi

# Create database and user
print_info "Creating database and user..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'whatsapp_saas_prod'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE whatsapp_saas_prod;"

sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = 'whatsapp_saas'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER whatsapp_saas WITH PASSWORD '$DB_PASSWORD';"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE whatsapp_saas_prod TO whatsapp_saas;"
sudo -u postgres psql -c "ALTER USER whatsapp_saas CREATEDB;"
print_status "Database configured successfully"

# Install Redis (optional)
print_step "STEP 4/12: Setting up Redis (Optional)"
read -p "Install Redis for production caching? (y/n, recommended: n for small servers): " INSTALL_REDIS
if [[ $INSTALL_REDIS =~ ^[Yy]$ ]]; then
    if ! command -v redis-server &> /dev/null; then
        sudo apt install -y redis-server
        sudo systemctl enable redis-server
        sudo systemctl start redis-server
        print_status "Redis installed and started"
        USE_REDIS="true"
    else
        print_status "Redis already installed"
        USE_REDIS="true"
    fi
else
    print_info "Skipping Redis installation (using local cache)"
    USE_REDIS="false"
fi

# Install Supervisor
print_step "STEP 5/12: Installing Supervisor"
if ! command -v supervisorctl &> /dev/null; then
    sudo apt install -y supervisor
    sudo systemctl enable supervisor
    sudo systemctl start supervisor
    print_status "Supervisor installed"
else
    print_status "Supervisor already installed"
fi

# Create project directory if doesn't exist
print_step "STEP 6/12: Setting up Project Directory"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    print_status "Project directory created"
else
    print_warning "Project directory already exists"
fi

cd "$PROJECT_DIR"

# Check if project files exist
if [ ! -f "manage.py" ]; then
    print_error "Project files not found in $PROJECT_DIR"
    print_info "Please upload your project files to $PROJECT_DIR first"
    print_info "You can use: git clone, SFTP, or Virtualmin File Manager"
    exit 1
fi

print_status "Project files found"

# Create Python virtual environment
print_step "STEP 7/12: Creating Python Virtual Environment"
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

# Create necessary directories
print_step "STEP 8/12: Creating Project Directories"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/media"
mkdir -p "$PROJECT_DIR/staticfiles"
mkdir -p "$PROJECT_DIR/whatsapp-service/sessions"
mkdir -p "$PROJECT_DIR/whatsapp-service/logs"
print_status "Project directories created"

# Generate Django secret key
print_info "Generating Django secret key..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Create .env.production file
print_step "STEP 9/12: Creating Environment Configuration"
cat > "$PROJECT_DIR/.env.production" << EOF
# Django Settings
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN_NAME,www.$DOMAIN_NAME
ENVIRONMENT=production

# Database
DB_NAME=whatsapp_saas_prod
DB_USER=whatsapp_saas
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

# Initialize Django
print_step "STEP 10/12: Initializing Django Application"
export DJANGO_SETTINGS_MODULE=config.settings.production

print_info "Running database migrations..."
python manage.py migrate --noinput

print_info "Collecting static files..."
python manage.py collectstatic --noinput

print_status "Django initialized successfully"

# Create superuser
print_warning "You need to create an admin user..."
python manage.py createsuperuser

# Install Node.js dependencies
print_step "STEP 11/12: Setting up Node.js WhatsApp Service"
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

# Create systemd service files
print_step "STEP 12/12: Creating System Services"

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
ExecStart=$VENV_DIR/bin/gunicorn \\
    --workers 3 \\
    --bind 127.0.0.1:8000 \\
    --timeout 120 \\
    --access-logfile $PROJECT_DIR/logs/gunicorn-access.log \\
    --error-logfile $PROJECT_DIR/logs/gunicorn-error.log \\
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
sudo systemctl enable whatsapp-django
sudo systemctl enable whatsapp-node
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
if sudo systemctl is-active --quiet whatsapp-django; then
    print_status "Django service started successfully"
else
    print_error "Django service failed to start. Check logs: sudo journalctl -u whatsapp-django -n 50"
fi

if sudo systemctl is-active --quiet whatsapp-node; then
    print_status "Node.js service started successfully"
else
    print_error "Node.js service failed to start. Check logs: sudo journalctl -u whatsapp-node -n 50"
fi

# Installation complete
print_step "INSTALLATION COMPLETE!"

echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║              Installation Successful! 🎉              ║
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

echo -e "${YELLOW}4. Service Management Commands${NC}"
echo -e "   • View Django logs: ${GREEN}sudo journalctl -u whatsapp-django -f${NC}"
echo -e "   • View Node logs: ${GREEN}sudo journalctl -u whatsapp-node -f${NC}"
echo -e "   • Restart Django: ${GREEN}sudo systemctl restart whatsapp-django${NC}"
echo -e "   • Restart Node: ${GREEN}sudo systemctl restart whatsapp-node${NC}\n"

echo -e "${CYAN}═══ PROJECT INFORMATION ═══${NC}\n"
echo -e "Project Path: ${GREEN}$PROJECT_DIR${NC}"
echo -e "Database: ${GREEN}whatsapp_saas_prod${NC}"
echo -e "Database User: ${GREEN}whatsapp_saas${NC}"
echo -e "Django Service: ${GREEN}whatsapp-django.service${NC}"
echo -e "Node.js Service: ${GREEN}whatsapp-node.service${NC}"
echo -e "Environment File: ${GREEN}$PROJECT_DIR/.env.production${NC}\n"

echo -e "${CYAN}═══ IMPORTANT NOTES ═══${NC}\n"
echo -e "• Your Node.js API key: ${GREEN}$NODE_API_KEY${NC}"
echo -e "• Database password: ${GREEN}[saved in .env.production]${NC}"
echo -e "• Make sure to configure your web server (Step 1 above)"
echo -e "• Run certbot to enable HTTPS (Step 2 above)\n"

echo -e "${YELLOW}For detailed documentation, see:${NC}"
echo -e "• ${GREEN}VIRTUALMIN_DEPLOYMENT_GUIDE.md${NC} - Full deployment guide"
echo -e "• ${GREEN}VIRTUALMIN_QUICK_CHECKLIST.md${NC} - Quick reference\n"

# Save installation info
cat > "$PROJECT_DIR/INSTALLATION_INFO.txt" << EOF
SanaSend SaaS - Installation Information
========================================

Installation Date: $(date)
Domain: $DOMAIN_NAME
Project Path: $PROJECT_DIR
Database: whatsapp_saas_prod
Database User: whatsapp_saas

Node.js API Key: $NODE_API_KEY

Services:
- Django: whatsapp-django.service
- Node.js: whatsapp-node.service

Useful Commands:
- View logs: sudo journalctl -u whatsapp-django -f
- Restart Django: sudo systemctl restart whatsapp-django
- Restart Node: sudo systemctl restart whatsapp-node

Next Steps:
1. Configure web server reverse proxy
2. Setup SSL with certbot
3. Access admin panel at https://$DOMAIN_NAME/admin/

For support, check VIRTUALMIN_DEPLOYMENT_GUIDE.md
EOF

print_status "Installation info saved to: $PROJECT_DIR/INSTALLATION_INFO.txt"

echo -e "\n${GREEN}Happy deploying! 🚀${NC}\n"

