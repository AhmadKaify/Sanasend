# WhatsApp Web API SaaS - Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Options](#deployment-options)
4. [Manual Deployment](#manual-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Production Configuration](#production-configuration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Overview

This guide covers deploying the WhatsApp Web API SaaS application to production. The application consists of:

- **Django Backend**: REST API and admin interface
- **Node.js Service**: WhatsApp Web integration
- **PostgreSQL**: Database
- **Redis**: Caching and task queue
- **Celery**: Background task processing
- **Nginx**: Reverse proxy and static file serving

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: Minimum 2GB, 4GB recommended
- **Storage**: Minimum 20GB SSD
- **CPU**: 2 cores minimum
- **Network**: Public IP with domain name

### Software Requirements
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js 16+
- Nginx
- SSL Certificate (Let's Encrypt recommended)

### Domain Setup
- Domain name pointing to your server
- SSL certificate (Let's Encrypt recommended)
- DNS records configured

## Deployment Options

### Option 1: Manual Deployment
- Full control over configuration
- Custom server setup
- Best for experienced administrators

### Option 2: Docker Deployment
- Containerized deployment
- Easy scaling and management
- Best for modern infrastructure

## Manual Deployment

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
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

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Step 2: Database Setup

```bash
# Create database and user
sudo -u postgres psql -c "CREATE DATABASE whatsapp_saas_prod;"
sudo -u postgres psql -c "CREATE USER whatsapp_saas WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE whatsapp_saas_prod TO whatsapp_saas;"
sudo -u postgres psql -c "ALTER USER whatsapp_saas CREATEDB;"

# Configure PostgreSQL
sudo nano /etc/postgresql/*/main/postgresql.conf
# Set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add: local   whatsapp_saas_prod   whatsapp_saas   md5
```

### Step 3: Application Deployment

```bash
# Clone repository
git clone <your-repo-url> /var/www/whatsapp_saas
cd /var/www/whatsapp_saas

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.production.template .env.production
nano .env.production  # Edit with your values

# Run migrations
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Setup Node.js service
cd whatsapp-service
npm install --production
cd ..
```

### Step 4: Service Configuration

Create systemd service files:

```bash
# Django service
sudo nano /etc/systemd/system/whatsapp-saas-django.service
```

```ini
[Unit]
Description=WhatsApp SaaS Django Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/whatsapp_saas
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=/var/www/whatsapp_saas/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Celery worker
sudo nano /etc/systemd/system/whatsapp-saas-celery.service
```

```ini
[Unit]
Description=WhatsApp SaaS Celery Worker
After=network.target redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/whatsapp_saas
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=/var/www/whatsapp_saas/venv/bin/celery -A config worker --loglevel=info
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Celery beat
sudo nano /etc/systemd/system/whatsapp-saas-celerybeat.service
```

```ini
[Unit]
Description=WhatsApp SaaS Celery Beat
After=network.target redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/whatsapp_saas
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=/var/www/whatsapp_saas/venv/bin/celery -A config beat --loglevel=info
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Node.js service
sudo nano /etc/systemd/system/whatsapp-saas-node.service
```

```ini
[Unit]
Description=WhatsApp SaaS Node.js Service
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/whatsapp_saas/whatsapp-service
ExecStart=/usr/bin/node src/server.js
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 5: Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/whatsapp-saas
```

```nginx
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
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
        alias /var/www/whatsapp_saas/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/whatsapp_saas/media/;
        expires 1M;
        add_header Cache-Control "public";
    }

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Node.js service
    location /whatsapp/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/whatsapp-saas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: SSL Certificate

```bash
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### Step 7: Start Services

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-saas-django
sudo systemctl enable whatsapp-saas-celery
sudo systemctl enable whatsapp-saas-celerybeat
sudo systemctl enable whatsapp-saas-node

sudo systemctl start whatsapp-saas-django
sudo systemctl start whatsapp-saas-celery
sudo systemctl start whatsapp-saas-celerybeat
sudo systemctl start whatsapp-saas-node

# Check status
sudo systemctl status whatsapp-saas-*
```

## Docker Deployment

### Step 1: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Configure Environment

```bash
# Create environment file
cp env.production.template .env.production
nano .env.production  # Edit with your values
```

### Step 3: Deploy with Docker

```bash
# Build and start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 4: SSL Configuration

```bash
# Copy SSL certificates to ssl directory
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
sudo chown -R $USER:$USER ssl/
```

## Production Configuration

### Environment Variables

Create `.env.production` with the following variables:

```bash
# Django Configuration
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ENVIRONMENT=Production

# Database
DB_NAME=whatsapp_saas_prod
DB_USER=whatsapp_saas
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Security
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
SECURE_SSL_REDIRECT=True
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Static/Media Files
STATIC_ROOT=/var/www/whatsapp_saas/static/
MEDIA_ROOT=/var/www/whatsapp_saas/media/

# Logging
LOG_FILE=/var/log/whatsapp_saas/django.log
ERROR_LOG_FILE=/var/log/whatsapp_saas/error.log

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com

# Node.js Service
NODE_SERVICE_URL=http://localhost:3000
NODE_SERVICE_API_KEY=your-node-service-api-key

# Rate Limiting
MAX_MESSAGES_PER_MINUTE=5
MAX_MESSAGES_PER_DAY=500

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn-here

# Django Base URL
DJANGO_BASE_URL=https://api.yourdomain.com
```

### Security Configuration

1. **Firewall Setup**:
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

2. **Fail2ban Setup**:
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

3. **SSH Security**:
```bash
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
# Set: PasswordAuthentication no
sudo systemctl restart ssh
```

### Backup Configuration

```bash
# Create backup script
sudo nano /usr/local/bin/backup-whatsapp-saas.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -h localhost -U whatsapp_saas whatsapp_saas_prod > $BACKUP_DIR/db_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/whatsapp_saas/media/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-whatsapp-saas.sh

# Add to crontab
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-whatsapp-saas.sh
```

## Monitoring and Maintenance

### Health Checks

The application provides several health check endpoints:

- `/health/` - Comprehensive health check
- `/health/ready/` - Readiness check
- `/health/live/` - Liveness check

### Monitoring Setup

1. **System Monitoring**:
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor logs
tail -f /var/log/whatsapp_saas/django.log
```

2. **Application Monitoring**:
```bash
# Check service status
sudo systemctl status whatsapp-saas-*

# Monitor Celery
celery -A config flower --port=5555
```

### Log Rotation

```bash
sudo nano /etc/logrotate.d/whatsapp-saas
```

```
/var/log/whatsapp_saas/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload whatsapp-saas-django
    endscript
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U whatsapp_saas -d whatsapp_saas_prod
```

2. **Redis Connection Issues**:
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping
```

3. **Service Not Starting**:
```bash
# Check service logs
sudo journalctl -u whatsapp-saas-django -f

# Check for errors
sudo systemctl status whatsapp-saas-django
```

4. **Static Files Not Loading**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data /var/www/whatsapp_saas/staticfiles/
```

### Performance Issues

1. **High Memory Usage**:
```bash
# Check memory usage
free -h
htop

# Restart services if needed
sudo systemctl restart whatsapp-saas-*
```

2. **Database Performance**:
```bash
# Check database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check slow queries
sudo -u postgres psql -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### Security Issues

1. **SSL Certificate Issues**:
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew
```

2. **Firewall Issues**:
```bash
# Check firewall status
sudo ufw status

# Check open ports
sudo netstat -tlnp
```

## Maintenance Tasks

### Regular Maintenance

1. **Update System**:
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Update Application**:
```bash
cd /var/www/whatsapp_saas
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart whatsapp-saas-*
```

3. **Clean Logs**:
```bash
sudo logrotate -f /etc/logrotate.d/whatsapp-saas
```

### Performance Optimization

1. **Database Optimization**:
```bash
# Analyze database
sudo -u postgres psql -d whatsapp_saas_prod -c "ANALYZE;"

# Reindex database
sudo -u postgres psql -d whatsapp_saas_prod -c "REINDEX DATABASE whatsapp_saas_prod;"
```

2. **Cache Optimization**:
```bash
# Clear Redis cache
redis-cli FLUSHALL

# Check Redis memory usage
redis-cli INFO memory
```

## Support and Documentation

- **API Documentation**: `/api/docs/`
- **Health Checks**: `/health/`
- **Admin Interface**: `/admin/`
- **Monitoring**: `/flower/` (if enabled)

For additional support, check the logs and use the health check endpoints to diagnose issues.
