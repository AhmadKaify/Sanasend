# Production Ready Steps

## Quick Start Guide

Follow these steps to prepare your project for production deployment:

---

## Step 1: Run Cleanup Script

### On Windows (PowerShell)
```powershell
.\cleanup_for_production.ps1
```

### On Linux/Mac
```bash
chmod +x cleanup_for_production.sh
./cleanup_for_production.sh
```

**What this does:**
- Removes all `__pycache__` directories
- Deletes `.pyc` and `.pyo` compiled files
- Clears the SQLite database
- Removes all migration files (keeps `__init__.py`)
- Clears log files
- Removes staticfiles directory
- Deletes node_modules (will reinstall on server)
- Removes WhatsApp session data
- Clears test coverage files
- Backs up your `.env` file to `.env.backup`

---

## Step 2: Update Environment Configuration

### Copy the production template:
```bash
cp env.production.template .env
```

### Edit `.env` with your production values:

```env
# MUST CHANGE THESE
SECRET_KEY=<generate-strong-key>  # See Step 3
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended)
DB_NAME=whatsapp_saas_prod
DB_USER=your_db_user
DB_PASSWORD=<strong-password>
DB_HOST=localhost
DB_PORT=5432

# Redis (Required for production)
USE_REDIS=true
REDIS_HOST=localhost
REDIS_PORT=6379

# WhatsApp Service
NODE_SERVICE_URL=http://localhost:3000
NODE_SERVICE_API_KEY=<generate-strong-key>  # See Step 3

# Application URL (use HTTPS)
DJANGO_BASE_URL=https://yourdomain.com
```

---

## Step 3: Generate Strong Keys

### Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Generate NODE_SERVICE_API_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy these keys to your `.env` file.

---

## Step 4: Verify Files Are Ready

Check that these files exist:
- ✅ `.env` (with production settings)
- ✅ `requirements.txt`
- ✅ `Dockerfile` (if using Docker)
- ✅ `nginx.conf` (for reverse proxy)
- ✅ `deploy.sh` (deployment script)

---

## Step 5: Create Deployment Package

### Option A: Using Git (Recommended)
```bash
# Commit your changes
git add .
git commit -m "Prepare for production deployment"
git push origin main

# On server, clone the repo
git clone <your-repo-url>
```

### Option B: Create Archive
```bash
# Create tar.gz archive (excludes venv, __pycache__, etc.)
tar -czf sanasr-production.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='db.sqlite3' \
  --exclude='logs' \
  .

# Upload to server
scp sanasr-production.tar.gz user@server:/path/to/deployment/
```

---

## Step 6: Server Deployment

Follow the complete deployment checklist:
```bash
# Read the comprehensive guide
cat PRODUCTION_DEPLOYMENT_CHECKLIST.md
```

### Quick Server Setup:
```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip python3-venv postgresql redis-server nginx nodejs npm -y

# 2. Setup database
sudo -u postgres createdb whatsapp_saas_prod
sudo -u postgres createuser your_db_user

# 3. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Install Node.js dependencies
cd whatsapp-service
npm install
cd ..

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Start services (see PRODUCTION_DEPLOYMENT_CHECKLIST.md)
```

---

## Step 7: Pre-Deployment Checklist

Before deploying, verify:

### Security
- [ ] `DEBUG=False` in `.env`
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured
- [ ] HTTPS/SSL configured
- [ ] Firewall configured (ports 80, 443 only)

### Database
- [ ] PostgreSQL installed and configured
- [ ] Database created
- [ ] Database user created with password
- [ ] Database credentials in `.env`

### Redis
- [ ] Redis installed and running
- [ ] `USE_REDIS=true` in `.env`
- [ ] Redis accessible

### Services
- [ ] Gunicorn configured
- [ ] WhatsApp service configured
- [ ] Nginx configured
- [ ] Systemd services created

### Files & Permissions
- [ ] Static files collected
- [ ] Proper file permissions set
- [ ] Log directory writable
- [ ] Media directory writable

---

## Step 8: Post-Deployment Verification

### Test the deployment:

```bash
# Check services are running
sudo systemctl status sanasr
sudo systemctl status sanasr-whatsapp

# Test web server
curl -I https://yourdomain.com

# Test API
curl https://yourdomain.com/api/v1/health/

# Check logs
sudo journalctl -u sanasr -n 50
tail -f /path/to/sanasr/logs/django.log
```

---

## Step 9: Monitoring & Maintenance

### Setup monitoring:
```bash
# View live logs
sudo journalctl -u sanasr -f
sudo journalctl -u sanasr-whatsapp -f

# Monitor system resources
htop
```

### Setup backups:
```bash
# Create backup script (see PRODUCTION_DEPLOYMENT_CHECKLIST.md)
# Schedule daily backups with cron
```

---

## Common Issues & Solutions

### Issue: Services won't start
```bash
# Check logs
sudo journalctl -u sanasr -n 100
# Fix permissions
sudo chown -R www-data:www-data /path/to/sanasr
```

### Issue: Static files not loading
```bash
# Recollect static files
python manage.py collectstatic --noinput
# Check Nginx configuration
sudo nginx -t
```

### Issue: Database connection error
```bash
# Test database connection
python manage.py dbshell
# Check PostgreSQL is running
sudo systemctl status postgresql
```

### Issue: Redis connection error
```bash
# Test Redis
redis-cli ping
# Start Redis
sudo systemctl start redis-server
```

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Stop services
sudo systemctl stop sanasr sanasr-whatsapp

# 2. Restore database backup
psql whatsapp_saas_prod < /backup/db_backup.sql

# 3. Restore code
cd /path/to/sanasr
git reset --hard <previous-commit>

# 4. Restart services
sudo systemctl start sanasr sanasr-whatsapp
```

---

## Files You Should Have

After cleanup and before deployment:

```
sanasr/
├── .env                          # Production environment (DO NOT COMMIT)
├── .env.backup                   # Backup of your previous .env
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── manage.py                     # Django management
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose
├── nginx.conf                    # Nginx configuration
├── deploy.sh                     # Deployment script
├── env.template                  # Development env template
├── env.production.template       # Production env template
├── cleanup_for_production.sh     # Cleanup script (Linux/Mac)
├── cleanup_for_production.ps1    # Cleanup script (Windows)
├── PRODUCTION_DEPLOYMENT_CHECKLIST.md  # Full deployment guide
├── README.md                     # Project documentation
├── config/                       # Django configuration
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── staging.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── api/                          # API endpoints
├── users/                        # User management
├── sessions/                     # WhatsApp sessions
├── messages/                     # Message handling
├── api_keys/                     # API key management
├── analytics/                    # Analytics tracking
├── dashboard/                    # Web dashboard
├── core/                         # Core utilities
├── static/                       # Static files
├── logs/                         # Log directory (empty)
└── whatsapp-service/             # Node.js WhatsApp service
    ├── package.json
    └── src/
```

---

## Next Steps

1. ✅ Run cleanup script
2. ✅ Configure `.env` for production
3. ✅ Generate strong keys
4. ✅ Create deployment package
5. ✅ Upload to server
6. ✅ Follow PRODUCTION_DEPLOYMENT_CHECKLIST.md
7. ✅ Test deployment
8. ✅ Setup monitoring
9. ✅ Configure backups

---

## Support

For detailed deployment instructions, see:
- `PRODUCTION_DEPLOYMENT_CHECKLIST.md` - Complete deployment guide
- `DEPLOYMENT_GUIDE.md` - Alternative deployment methods
- `README.md` - General project documentation

For issues, check:
- Service logs: `sudo journalctl -u sanasr -n 100`
- Django logs: `tail -f logs/django.log`
- Nginx logs: `tail -f /var/log/nginx/error.log`

---

**Last Updated**: 2025-10-05

