# SanaSend SaaS - Virtualmin Deployment Guide

## Overview

This guide walks you through deploying the SanaSend WhatsApp SaaS application on a Virtualmin-managed server. The application consists of:

- **Django Backend** (Python 3.10+)
- **Node.js WhatsApp Service** (Node.js 18+)
- **PostgreSQL Database**
- **Redis** (optional, for production)
- **Nginx/Apache** (reverse proxy)

---

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+ (Virtualmin installed)
- **RAM**: Minimum 2GB, 4GB recommended
- **Storage**: Minimum 20GB SSD
- **Domain**: Your domain pointing to the server
- **Virtualmin**: Installed and configured

### What You'll Need
- SSH access to your server
- Root or sudo access
- Domain name (e.g., `yourdomain.com`)
- Basic Linux command line knowledge

---

## Step 1: Initial Server Setup via Virtualmin

### 1.1 Create Virtual Server in Virtualmin

1. Login to Virtualmin: `https://your-server-ip:10000`
2. Go to **Virtualmin** → **Create Virtual Server**
3. Fill in:
   - **Domain name**: `yourdomain.com`
   - **Administration username**: `whatsapp_admin`
   - **Administration password**: Choose a strong password
4. Click **Create Server**

### 1.2 Install Required Software

SSH into your server:

```bash
ssh root@your-server-ip
```

Install system dependencies:

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.10+ and dependencies
apt install -y python3 python3-pip python3-venv python3-dev \
    build-essential libpq-dev git curl wget

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install PostgreSQL (if not already installed)
apt install -y postgresql postgresql-contrib

# Install Redis (optional for production)
apt install -y redis-server

# Install supervisor for process management
apt install -y supervisor

# Verify installations
python3 --version  # Should be 3.10+
node --version     # Should be 18+
npm --version
psql --version
```

---

## Step 2: Database Setup

### 2.1 Create PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell, run:
CREATE DATABASE whatsapp_saas_prod;
CREATE USER whatsapp_saas WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE whatsapp_saas_prod TO whatsapp_saas;
ALTER USER whatsapp_saas CREATEDB;
\q
```

### 2.2 Configure PostgreSQL for Remote Access (if needed)

```bash
# Edit PostgreSQL config
nano /etc/postgresql/*/main/postgresql.conf
# Find and set: listen_addresses = 'localhost'

# Edit access control
nano /etc/postgresql/*/main/pg_hba.conf
# Add line: local   whatsapp_saas_prod   whatsapp_saas   md5

# Restart PostgreSQL
systemctl restart postgresql
```

---

## Step 3: Deploy Application Files

### 3.1 Navigate to Your Domain Directory

```bash
# Virtualmin creates directories at /home/username/public_html
cd /home/sanasend
mkdir -p public_html
cd public_html
```

### 3.2 Upload Project Files

**Option A: Using Git (Recommended)**

```bash
# Clone your repository
git clone https://github.com/your-username/your-repo.git .
```

**Option B: Using Virtualmin File Manager**

1. Login to Virtualmin
2. Go to **Webmin** → **Others** → **File Manager**
3. Navigate to `/home/sanasend/public_html/`
4. Upload your project files (can upload as .zip and extract)

**Option C: Using SFTP**

Use FileZilla or WinSCP to upload files:
- Host: `your-server-ip`
- Username: `sanasend`
- Port: 22
- Upload to: `/home/sanasend/public_html/`

---

## Step 4: Configure Python Environment

### 4.1 Create Virtual Environment

```bash
cd /home/sanasend/public_html

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 4.2 Install Python Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

---

## Step 5: Configure Environment Variables

### 5.1 Create Production Environment File

```bash
cd /home/sanasend/public_html
nano .env.production
```

### 5.2 Add Configuration

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-generate-a-random-one
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip
ENVIRONMENT=production

# Database
DB_NAME=whatsapp_saas_prod
DB_USER=whatsapp_saas
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Redis (Optional - set USE_REDIS=false if not using Redis)
USE_REDIS=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Node.js Service
NODE_SERVICE_URL=http://localhost:3000
NODE_SERVICE_API_KEY=generate-a-random-api-key-here

# Django Base URL
DJANGO_BASE_URL=https://yourdomain.com

# Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECURE_SSL_REDIRECT=True

# Celery (if using Redis)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Rate Limiting
MAX_MESSAGES_PER_MINUTE=10
MAX_MESSAGES_PER_DAY=1000

# Logging
LOG_FILE=/home/sanasend/public_html/logs/django.log
ERROR_LOG_FILE=/home/sanasend/public_html/logs/error.log

# Static/Media Files
STATIC_ROOT=/home/sanasend/public_html/staticfiles
MEDIA_ROOT=/home/sanasend/public_html/media
```

**Important:** Generate a new SECRET_KEY:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Step 6: Initialize Django Application

### 6.1 Run Migrations

```bash
cd /home/sanasend/public_html
source venv/bin/activate

# Set Django settings
export DJANGO_SETTINGS_MODULE=config.settings.production

# Run migrations
python manage.py migrate

# Create necessary directories
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Collect static files
python manage.py collectstatic --noinput
```

### 6.2 Create Superuser

```bash
python manage.py createsuperuser
# Enter username, email, and password when prompted
```

### 6.3 Test Django

```bash
# Test that Django can start
python manage.py check

# Test with development server temporarily
python manage.py runserver 0.0.0.0:8001
# Press Ctrl+C to stop after verifying it works
```

---

## Step 7: Setup Node.js WhatsApp Service

### 7.1 Install Node.js Dependencies

```bash
cd /home/sanasend/public_html/whatsapp-service

# Install packages
npm install --production

# Create necessary directories
mkdir -p sessions
mkdir -p logs
```

### 7.2 Configure Node.js Service

```bash
cd /home/sanasend/public_html/whatsapp-service
nano .env
```

Add:

```bash
NODE_ENV=production
PORT=3000
DJANGO_BASE_URL=https://yourdomain.com
API_KEY=same-api-key-from-django-env-file
```

### 7.3 Test Node.js Service

```bash
# Test that Node.js service starts
node src/server.js
# Press Ctrl+C to stop after verifying it works
```

---

## Step 8: Setup Systemd Services

### 8.1 Create Django Service

```bash
sudo nano /etc/systemd/system/whatsapp-django.service
```

```ini
[Unit]
Description=WhatsApp SaaS Django Application
After=network.target postgresql.service

[Service]
Type=exec
User=sanasend
Group=sanasend
WorkingDirectory=/home/sanasend/public_html
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
Environment="PATH=/home/sanasend/public_html/venv/bin"
ExecStart=/home/sanasend/public_html/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /home/sanasend/public_html/logs/gunicorn-access.log \
    --error-logfile /home/sanasend/public_html/logs/gunicorn-error.log \
    config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8.2 Create Node.js Service

```bash
sudo nano /etc/systemd/system/whatsapp-node.service
```

```ini
[Unit]
Description=WhatsApp SaaS Node.js Service
After=network.target

[Service]
Type=simple
User=sanasend
Group=sanasend
WorkingDirectory=/home/sanasend/public_html/whatsapp-service
ExecStart=/usr/bin/node src/server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

### 8.3 Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable whatsapp-django
sudo systemctl enable whatsapp-node

# Start services
sudo systemctl start whatsapp-django
sudo systemctl start whatsapp-node

# Check status
sudo systemctl status whatsapp-django
sudo systemctl status whatsapp-node

# View logs if needed
sudo journalctl -u whatsapp-django -f
sudo journalctl -u whatsapp-node -f
```

---

## Step 9: Configure Nginx Reverse Proxy

### 9.1 Check Web Server Type

```bash
# Check if Nginx is running
systemctl status nginx

# If Apache is running, you'll need to either switch to Nginx or configure Apache
systemctl status apache2
```

### 9.2 Configure Nginx (if using Nginx)

```bash
sudo nano /etc/nginx/sites-available/whatsapp-saas
```

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (Let's Encrypt certificates)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Max upload size
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /home/sanasend/public_html/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/sanasend/public_html/media/;
        expires 1M;
        add_header Cache-Control "public";
    }

    # WhatsApp Node.js Service
    location /whatsapp/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Django Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/whatsapp-saas /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

### 9.3 Configure Apache (if using Apache)

```bash
sudo nano /etc/apache2/sites-available/whatsapp-saas.conf
```

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    
    # Redirect to HTTPS
    Redirect permanent / https://yourdomain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/yourdomain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/yourdomain.com/privkey.pem

    # Static files
    Alias /static /home/sanasend/public_html/staticfiles
    <Directory /home/sanasend/public_html/staticfiles>
        Require all granted
    </Directory>

    # Media files
    Alias /media /home/sanasend/public_html/media
    <Directory /home/sanasend/public_html/media>
        Require all granted
    </Directory>

    # WhatsApp Node.js Service
    ProxyPass /whatsapp/ http://127.0.0.1:3000/
    ProxyPassReverse /whatsapp/ http://127.0.0.1:3000/

    # Django Application
    ProxyPass /static !
    ProxyPass /media !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Port "443"
</VirtualHost>
```

```bash
# Enable required modules
sudo a2enmod proxy proxy_http ssl headers

# Enable site
sudo a2ensite whatsapp-saas

# Test configuration
sudo apache2ctl configtest

# If test passes, reload Apache
sudo systemctl reload apache2
```

---

## Step 10: SSL Certificate with Let's Encrypt

### 10.1 Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx  # For Nginx
# OR
sudo apt install -y certbot python3-certbot-apache  # For Apache
```

### 10.2 Obtain SSL Certificate

**For Nginx:**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**For Apache:**

```bash
sudo certbot --apache -d yourdomain.com -d www.yourdomain.com
```

### 10.3 Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

---

## Step 11: Set File Permissions

```bash
# Set ownership
sudo chown -R sanasend:sanasend /home/sanasend/public_html

# Set proper permissions
find /home/sanasend/public_html -type d -exec chmod 755 {} \;
find /home/sanasend/public_html -type f -exec chmod 644 {} \;

# Make scripts executable
chmod +x /home/sanasend/public_html/venv/bin/*

# Ensure log directory is writable
chmod 775 /home/sanasend/public_html/logs
chmod 775 /home/sanasend/public_html/media
```

---

## Step 12: Configure Firewall

```bash
# Check if UFW is active
sudo ufw status

# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 10000/tcp # Virtualmin

# Enable firewall if not already enabled
sudo ufw enable

# Verify rules
sudo ufw status verbose
```

---

## Step 13: Testing Your Deployment

### 13.1 Check Services

```bash
# Check all services are running
sudo systemctl status whatsapp-django
sudo systemctl status whatsapp-node
sudo systemctl status nginx  # or apache2
sudo systemctl status postgresql
```

### 13.2 Test Website Access

1. **Admin Panel**: Visit `https://yourdomain.com/admin/`
   - Login with your superuser credentials

2. **API Documentation**: Visit `https://yourdomain.com/api/docs/`

3. **Health Check**: Visit `https://yourdomain.com/health/`

### 13.3 Test API Endpoints

```bash
# Test admin login
curl -X POST https://yourdomain.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# Test session status (after getting API key)
curl https://yourdomain.com/api/v1/sessions/status/ \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

---

## Step 14: Ongoing Maintenance

### 14.1 View Logs

```bash
# Django logs
tail -f /home/sanasend/public_html/logs/django.log

# Gunicorn logs
tail -f /home/sanasend/public_html/logs/gunicorn-error.log

# Node.js logs
sudo journalctl -u whatsapp-node -f

# Nginx/Apache logs
tail -f /var/log/nginx/error.log
tail -f /var/log/apache2/error.log
```

### 14.2 Restart Services

```bash
# Restart Django
sudo systemctl restart whatsapp-django

# Restart Node.js
sudo systemctl restart whatsapp-node

# Restart Web Server
sudo systemctl restart nginx  # or apache2
```

### 14.3 Update Application

```bash
cd /home/sanasend/public_html

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Update Node.js dependencies
cd whatsapp-service
npm install --production
cd ..

# Restart services
sudo systemctl restart whatsapp-django
sudo systemctl restart whatsapp-node
```

### 14.4 Database Backup

```bash
# Create backup script
nano /home/sanasend/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/sanasend/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U whatsapp_saas whatsapp_saas_prod > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/sanasend/public_html/media/

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
chmod +x /home/sanasend/backup.sh

# Add to crontab for daily backups at 2 AM
crontab -e
# Add line:
0 2 * * * /home/sanasend/backup.sh >> /home/sanasend/backup.log 2>&1
```

---

## Troubleshooting

### Issue: Services Won't Start

```bash
# Check service status
sudo systemctl status whatsapp-django
sudo systemctl status whatsapp-node

# Check logs
sudo journalctl -u whatsapp-django -n 50
sudo journalctl -u whatsapp-node -n 50

# Common fixes:
# 1. Check file permissions
# 2. Verify .env.production file exists and is correct
# 3. Check database connection
# 4. Ensure all dependencies are installed
```

### Issue: 502 Bad Gateway

```bash
# Check if Django service is running
sudo systemctl status whatsapp-django

# Check Nginx/Apache logs
tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart whatsapp-django
sudo systemctl restart nginx
```

### Issue: Database Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test database connection
psql -h localhost -U whatsapp_saas -d whatsapp_saas_prod

# Verify credentials in .env.production
```

### Issue: Static Files Not Loading

```bash
# Collect static files again
cd /home/whatsapp_admin/whatsapp_saas
source venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
chmod -R 755 /home/whatsapp_admin/whatsapp_saas/staticfiles/

# Restart web server
sudo systemctl restart nginx
```

### Issue: WhatsApp Service Not Working

```bash
# Check Node.js service
sudo systemctl status whatsapp-node

# Check logs
sudo journalctl -u whatsapp-node -f

# Verify Node.js dependencies
cd /home/whatsapp_admin/whatsapp_saas/whatsapp-service
npm install

# Restart service
sudo systemctl restart whatsapp-node
```

---

## Security Checklist

- [ ] Changed all default passwords
- [ ] Generated new SECRET_KEY
- [ ] SSL certificate installed and working
- [ ] Firewall configured (UFW)
- [ ] DEBUG=False in production
- [ ] Database user has limited privileges
- [ ] File permissions set correctly
- [ ] Disabled root SSH login (optional but recommended)
- [ ] Regular backups configured
- [ ] Monitoring set up

---

## Performance Optimization

### For Low-Resource Servers (2GB RAM)

1. **Reduce Gunicorn Workers**:
   Edit `/etc/systemd/system/whatsapp-django.service`:
   ```
   --workers 2  # Instead of 3
   ```

2. **Disable Redis** (use local cache):
   In `.env.production`:
   ```
   USE_REDIS=false
   ```

3. **Monitor Resources**:
   ```bash
   htop
   free -h
   df -h
   ```

---

## Next Steps

1. **Create First User**:
   - Login to admin panel
   - Create a user account
   - Generate API key for the user

2. **Test WhatsApp Integration**:
   - Use the dashboard or API to initiate a session
   - Scan QR code with WhatsApp
   - Send test message

3. **Monitor Application**:
   - Check logs regularly
   - Monitor service status
   - Set up automated backups

4. **Read Documentation**:
   - `INTEGRATION_GUIDE.md` - For API usage
   - `USER_DASHBOARD_GUIDE.md` - For dashboard features
   - `API_DOCUMENTATION` - Available at `/api/docs/`

---

## Support

For issues specific to:
- **Virtualmin**: Check Virtualmin documentation
- **Application**: Check project logs and documentation
- **SSL**: Check Certbot documentation

---

**Congratulations! Your SanaSend WhatsApp SaaS is now deployed on Virtualmin! 🎉**

