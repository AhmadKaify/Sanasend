# Virtualmin Deployment Quick Checklist

Use this as a quick reference while following the full guide.

## Pre-Deployment Checklist

- [ ] Virtualmin installed and accessible
- [ ] Domain name pointing to server
- [ ] SSH access available
- [ ] Root/sudo access confirmed

## Step-by-Step Deployment

### 1. System Setup (10 min)
```bash
# Update and install packages
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv python3-dev build-essential libpq-dev git
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs postgresql postgresql-contrib redis-server supervisor
```

### 2. Database Setup (5 min)
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE whatsapp_saas_prod;
CREATE USER whatsapp_saas WITH PASSWORD 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE whatsapp_saas_prod TO whatsapp_saas;
ALTER USER whatsapp_saas CREATEDB;
\q
```

### 3. Create Virtual Server in Virtualmin (2 min)
- Login to Virtualmin
- Create Virtual Server → `yourdomain.com`
- Create admin user

### 4. Upload Project Files (5 min)
```bash
cd /home/whatsapp_admin
mkdir whatsapp_saas
cd whatsapp_saas
git clone your-repo-url .
```

### 5. Python Environment (5 min)
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Environment (5 min)
```bash
nano .env.production
```
Copy from template and update:
- SECRET_KEY
- DB_PASSWORD
- ALLOWED_HOSTS
- NODE_SERVICE_API_KEY

### 7. Initialize Django (5 min)
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
mkdir -p logs media staticfiles
```

### 8. Setup Node.js Service (3 min)
```bash
cd whatsapp-service
npm install --production
mkdir -p sessions logs
```

### 9. Create Systemd Services (10 min)

**Django Service:**
```bash
sudo nano /etc/systemd/system/whatsapp-django.service
```
(Copy from full guide)

**Node.js Service:**
```bash
sudo nano /etc/systemd/system/whatsapp-node.service
```
(Copy from full guide)

**Enable & Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-django whatsapp-node
sudo systemctl start whatsapp-django whatsapp-node
sudo systemctl status whatsapp-django whatsapp-node
```

### 10. Configure Nginx/Apache (10 min)

**For Nginx:**
```bash
sudo nano /etc/nginx/sites-available/whatsapp-saas
# Copy config from full guide
sudo ln -s /etc/nginx/sites-available/whatsapp-saas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 11. SSL Certificate (5 min)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo certbot renew --dry-run
```

### 12. Set Permissions (2 min)
```bash
sudo chown -R whatsapp_admin:whatsapp_admin /home/whatsapp_admin/whatsapp_saas
find /home/whatsapp_admin/whatsapp_saas -type d -exec chmod 755 {} \;
find /home/whatsapp_admin/whatsapp_saas -type f -exec chmod 644 {} \;
chmod 775 /home/whatsapp_admin/whatsapp_saas/logs
chmod 775 /home/whatsapp_admin/whatsapp_saas/media
```

### 13. Configure Firewall (2 min)
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 10000/tcp
sudo ufw enable
```

## Post-Deployment Testing

### Test Services
```bash
sudo systemctl status whatsapp-django
sudo systemctl status whatsapp-node
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Test URLs
- [ ] Admin Panel: `https://yourdomain.com/admin/`
- [ ] API Docs: `https://yourdomain.com/api/docs/`
- [ ] Health Check: `https://yourdomain.com/health/`

### Test API
```bash
# Login test
curl -X POST https://yourdomain.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'
```

## Quick Commands Reference

### View Logs
```bash
# Django
tail -f /home/whatsapp_admin/whatsapp_saas/logs/django.log

# Services
sudo journalctl -u whatsapp-django -f
sudo journalctl -u whatsapp-node -f

# Web Server
tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
sudo systemctl restart whatsapp-django
sudo systemctl restart whatsapp-node
sudo systemctl restart nginx
```

### Update Application
```bash
cd /home/whatsapp_admin/whatsapp_saas
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
cd whatsapp-service && npm install --production && cd ..
sudo systemctl restart whatsapp-django whatsapp-node
```

## Common Issues & Quick Fixes

### 502 Bad Gateway
```bash
sudo systemctl restart whatsapp-django
sudo systemctl restart nginx
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Service Won't Start
```bash
sudo journalctl -u whatsapp-django -n 50
# Check logs, verify .env file, check permissions
```

### Database Connection Error
```bash
# Test connection
psql -h localhost -U whatsapp_saas -d whatsapp_saas_prod
# Verify .env.production credentials
```

## Security Checklist
- [ ] Changed all default passwords
- [ ] Generated new SECRET_KEY
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] DEBUG=False
- [ ] File permissions correct
- [ ] Backups configured

## Estimated Total Time: 60-90 minutes

---

**For detailed instructions, see: VIRTUALMIN_DEPLOYMENT_GUIDE.md**

