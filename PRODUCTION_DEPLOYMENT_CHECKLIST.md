# Production Deployment Checklist

## Pre-Deployment Cleanup

### 1. Run Cleanup Script
```bash
# For Linux/Mac
chmod +x cleanup_for_production.sh
./cleanup_for_production.sh

# For Windows (PowerShell)
.\cleanup_for_production.ps1
```

This will remove:
- All `__pycache__` directories
- All `.pyc` and `.pyo` files
- Database file (`db.sqlite3`)
- All migration files (except `__init__.py`)
- Log files
- Staticfiles directory
- Node modules
- WhatsApp session data
- Test coverage files
- Redis dump files
- Celery schedule files

## Environment Configuration

### 2. Create Production .env File

Copy `env.template` to `.env` and update with production values:

```bash
cp env.template .env
```

**Critical settings to update:**

```env
# Security - MUST CHANGE
SECRET_KEY=<generate-strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database - Use PostgreSQL in production
DB_NAME=whatsapp_saas_prod
DB_USER=your_db_user
DB_PASSWORD=<strong-password>
DB_HOST=localhost
DB_PORT=5432

# Redis - Enable for production
USE_REDIS=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Node.js Service
NODE_SERVICE_URL=http://localhost:3000
NODE_SERVICE_API_KEY=<generate-strong-api-key>

# Django Base URL
DJANGO_BASE_URL=https://yourdomain.com

# Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Celery (if using)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Rate Limiting
MAX_MESSAGES_PER_MINUTE=10
MAX_MESSAGES_PER_DAY=1000
```

### 3. Generate Strong SECRET_KEY

```python
# Run this in Python shell
import secrets
print(secrets.token_urlsafe(50))
```

Or use this one-liner:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## Server Setup

### 4. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ and dependencies
sudo apt install python3.11 python3.11-venv python3-pip postgresql postgresql-contrib redis-server nginx -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

### 5. Setup PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE whatsapp_saas_prod;
CREATE USER your_db_user WITH PASSWORD 'strong-password';
ALTER ROLE your_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE whatsapp_saas_prod TO your_db_user;
\q
```

### 6. Setup Redis

```bash
# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
# Should return: PONG
```

## Application Deployment

### 7. Upload Project to Server

```bash
# Option 1: Using Git (Recommended)
git clone <your-repo-url>
cd sanasr

# Option 2: Using SCP
scp -r /local/path/to/sanasr user@server:/path/to/deployment/
```

### 8. Setup Virtual Environment

```bash
cd /path/to/sanasr
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 9. Install Node.js Dependencies

```bash
cd whatsapp-service
npm install
cd ..
```

### 10. Run Database Migrations

```bash
# Make sure .env is configured
python manage.py makemigrations
python manage.py migrate
```

### 11. Create Superuser

```bash
python manage.py createsuperuser
```

### 12. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Service Configuration

### 13. Setup Gunicorn Service

Create `/etc/systemd/system/sanasr.service`:

```ini
[Unit]
Description=Sanasr WhatsApp SaaS Django Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/sanasr
Environment="PATH=/path/to/sanasr/venv/bin"
ExecStart=/path/to/sanasr/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/path/to/sanasr/gunicorn.sock \
    --timeout 120 \
    --access-logfile /path/to/sanasr/logs/gunicorn-access.log \
    --error-logfile /path/to/sanasr/logs/gunicorn-error.log \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 14. Setup WhatsApp Service

Create `/etc/systemd/system/sanasr-whatsapp.service`:

```ini
[Unit]
Description=Sanasr WhatsApp Node.js Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/sanasr/whatsapp-service
Environment="NODE_ENV=production"
ExecStart=/usr/bin/node /path/to/sanasr/whatsapp-service/src/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 15. Setup Celery (Optional)

Create `/etc/systemd/system/sanasr-celery.service`:

```ini
[Unit]
Description=Sanasr Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/sanasr
Environment="PATH=/path/to/sanasr/venv/bin"
ExecStart=/path/to/sanasr/venv/bin/celery -A config worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

### 16. Configure Nginx

Create `/etc/nginx/sites-available/sanasr`:

```nginx
upstream django {
    server unix:///path/to/sanasr/gunicorn.sock;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /path/to/sanasr/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/sanasr/media/;
        expires 7d;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://django;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/sanasr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 17. Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Start Services

### 18. Enable and Start All Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable sanasr
sudo systemctl enable sanasr-whatsapp
sudo systemctl enable sanasr-celery  # if using Celery

# Start services
sudo systemctl start sanasr
sudo systemctl start sanasr-whatsapp
sudo systemctl start sanasr-celery  # if using Celery

# Check status
sudo systemctl status sanasr
sudo systemctl status sanasr-whatsapp
sudo systemctl status sanasr-celery  # if using Celery
```

## Post-Deployment

### 19. Set Proper Permissions

```bash
# Set ownership
sudo chown -R www-data:www-data /path/to/sanasr

# Set directory permissions
sudo find /path/to/sanasr -type d -exec chmod 755 {} \;

# Set file permissions
sudo find /path/to/sanasr -type f -exec chmod 644 {} \;

# Make scripts executable
sudo chmod +x /path/to/sanasr/*.sh
```

### 20. Configure Firewall

```bash
# Allow necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 21. Setup Log Rotation

Create `/etc/logrotate.d/sanasr`:

```
/path/to/sanasr/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload sanasr > /dev/null 2>&1 || true
    endscript
}
```

### 22. Setup Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Check logs
sudo journalctl -u sanasr -f
sudo journalctl -u sanasr-whatsapp -f
tail -f /path/to/sanasr/logs/*.log
```

## Security Hardening

### 23. Additional Security Measures

1. **Disable Debug Mode**: Ensure `DEBUG=False` in .env
2. **Secure Secret Keys**: Use strong, random keys
3. **Database Security**: Use strong passwords, restrict access
4. **Redis Security**: Configure password authentication
5. **File Permissions**: Ensure proper ownership and permissions
6. **Update System**: Keep system and packages updated
7. **Backup Strategy**: Implement regular backup system
8. **Monitoring**: Set up monitoring and alerting

### 24. Backup Configuration

```bash
# Create backup script
cat > /root/backup-sanasr.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/sanasr"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump whatsapp_saas_prod > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /path/to/sanasr/media

# Keep only last 30 days of backups
find $BACKUP_DIR -type f -mtime +30 -delete
EOF

chmod +x /root/backup-sanasr.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /root/backup-sanasr.sh") | crontab -
```

## Testing

### 25. Verify Deployment

```bash
# Test Django application
curl -I https://yourdomain.com

# Test API endpoints
curl https://yourdomain.com/api/v1/health/

# Test WhatsApp service
curl http://localhost:3000/health

# Check service logs
sudo journalctl -u sanasr -n 100
sudo journalctl -u sanasr-whatsapp -n 100
```

## Maintenance

### Common Commands

```bash
# Restart services
sudo systemctl restart sanasr
sudo systemctl restart sanasr-whatsapp

# View logs
sudo journalctl -u sanasr -f
tail -f /path/to/sanasr/logs/django.log

# Update application
cd /path/to/sanasr
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart sanasr

# Database management
python manage.py dbshell
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

## Troubleshooting

### Check Service Status
```bash
sudo systemctl status sanasr
sudo systemctl status sanasr-whatsapp
```

### View Logs
```bash
sudo journalctl -u sanasr -n 100 --no-pager
sudo journalctl -u sanasr-whatsapp -n 100 --no-pager
```

### Test Configuration
```bash
python manage.py check --deploy
nginx -t
```

### Database Connection Issues
```bash
python manage.py dbshell
```

## Rollback Plan

If deployment fails:
1. Stop services: `sudo systemctl stop sanasr sanasr-whatsapp`
2. Restore database: `psql whatsapp_saas_prod < backup.sql`
3. Restore code: `git reset --hard <previous-commit>`
4. Restart services: `sudo systemctl start sanasr sanasr-whatsapp`

## Support & Resources

- Django Documentation: https://docs.djangoproject.com/
- Gunicorn Documentation: https://docs.gunicorn.org/
- Nginx Documentation: https://nginx.org/en/docs/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Redis Documentation: https://redis.io/documentation

---

**Last Updated**: 2025-10-05
**Version**: 1.0

