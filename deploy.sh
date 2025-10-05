#!/bin/bash

# WhatsApp Web API SaaS - Production Deployment Script
# This script automates the deployment process for production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="whatsapp_saas"
PROJECT_DIR="/var/www/$PROJECT_NAME"
VENV_DIR="/var/www/$PROJECT_NAME/venv"
LOG_DIR="/var/log/$PROJECT_NAME"
STATIC_DIR="/var/www/$PROJECT_NAME/static"
MEDIA_DIR="/var/www/$PROJECT_NAME/media"
NGINX_DIR="/etc/nginx/sites-available"
SYSTEMD_DIR="/etc/systemd/system"

echo -e "${GREEN}Starting WhatsApp Web API SaaS deployment...${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if user has sudo privileges
if ! sudo -n true 2>/dev/null; then
    print_error "This script requires sudo privileges"
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev \
    nodejs \
    npm \
    certbot \
    python3-certbot-nginx

# Create project directory
print_status "Creating project directory..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Create log directory
print_status "Creating log directory..."
sudo mkdir -p $LOG_DIR
sudo chown $USER:$USER $LOG_DIR

# Create static and media directories
print_status "Creating static and media directories..."
sudo mkdir -p $STATIC_DIR $MEDIA_DIR
sudo chown $USER:$USER $STATIC_DIR $MEDIA_DIR

# Setup PostgreSQL
print_status "Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE whatsapp_saas_prod;"
sudo -u postgres psql -c "CREATE USER whatsapp_saas WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE whatsapp_saas_prod TO whatsapp_saas;"
sudo -u postgres psql -c "ALTER USER whatsapp_saas CREATEDB;"

# Configure Redis
print_status "Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install additional production dependencies
pip install \
    gunicorn \
    whitenoise \
    psycopg2-binary \
    django-redis \
    sentry-sdk

# Copy environment file
print_status "Setting up environment configuration..."
if [ ! -f "$PROJECT_DIR/.env.production" ]; then
    cp env.production.template $PROJECT_DIR/.env.production
    print_warning "Please edit $PROJECT_DIR/.env.production with your actual values"
fi

# Run Django migrations
print_status "Running Django migrations..."
cd $PROJECT_DIR
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Setup Node.js service
print_status "Setting up Node.js WhatsApp service..."
cd $PROJECT_DIR/whatsapp-service
npm install --production

# Create systemd service files
print_status "Creating systemd service files..."

# Django service
sudo tee $SYSTEMD_DIR/whatsapp-saas-django.service > /dev/null <<EOF
[Unit]
Description=WhatsApp SaaS Django Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery worker service
sudo tee $SYSTEMD_DIR/whatsapp-saas-celery.service > /dev/null <<EOF
[Unit]
Description=WhatsApp SaaS Celery Worker
After=network.target redis.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=$VENV_DIR/bin/celery -A config worker --loglevel=info
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery beat service
sudo tee $SYSTEMD_DIR/whatsapp-saas-celerybeat.service > /dev/null <<EOF
[Unit]
Description=WhatsApp SaaS Celery Beat
After=network.target redis.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=$VENV_DIR/bin/celery -A config beat --loglevel=info
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Node.js service
sudo tee $SYSTEMD_DIR/whatsapp-saas-node.service > /dev/null <<EOF
[Unit]
Description=WhatsApp SaaS Node.js Service
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR/whatsapp-service
ExecStart=/usr/bin/node src/server.js
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
print_status "Configuring Nginx..."
sudo tee $NGINX_DIR/whatsapp-saas > /dev/null <<EOF
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com api.yourdomain.com;

    # SSL Configuration (will be set up by certbot)
    # ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Static files
    location /static/ {
        alias $STATIC_DIR/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $MEDIA_DIR/;
        expires 1M;
        add_header Cache-Control "public";
    }

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Node.js service (for WhatsApp operations)
    location /whatsapp/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable and start services
print_status "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-saas-django
sudo systemctl enable whatsapp-saas-celery
sudo systemctl enable whatsapp-saas-celerybeat
sudo systemctl enable whatsapp-saas-node

# Enable Nginx site
sudo ln -sf $NGINX_DIR/whatsapp-saas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

print_status "Deployment completed successfully!"
print_warning "Next steps:"
echo "1. Edit $PROJECT_DIR/.env.production with your actual values"
echo "2. Update Nginx configuration with your domain name"
echo "3. Run: sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com"
echo "4. Start services: sudo systemctl start whatsapp-saas-django whatsapp-saas-celery whatsapp-saas-celerybeat whatsapp-saas-node"
echo "5. Check service status: sudo systemctl status whatsapp-saas-*"

print_status "Deployment script completed!"
