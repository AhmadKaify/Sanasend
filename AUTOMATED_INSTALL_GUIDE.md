# SanaSend SaaS - Fully Automated Installation Guide

## 🚀 Zero-Prompt Installation

This installer runs **completely unattended** with all values pre-configured!

---

## Pre-Configured Values

✅ **Server Configuration:**
- Username: `sanasend`
- Domain: `sanasend.com`
- Path: `/home/sanasend/public_html`

✅ **Database Configuration:**
- Database Name: `whatsapp_saas_prod`
- Database User: `whatsapp_saas`
- Database Password: `Passisdb123`

✅ **Admin Credentials:**
- Username: `sanaric`
- Email: `sanasoft20@gmail.com`
- Password: `Sanaric123`

✅ **Services:**
- Redis: Disabled (uses local cache)
- Node.js API Key: Auto-generated

---

## Installation Steps

### Step 1: Upload Project Files

```bash
ssh sanasend@your-server-ip
cd /home/sanasend
mkdir -p public_html
cd public_html

# Upload files via Git
git clone https://github.com/your-username/your-repo.git .

# OR upload via SFTP/Virtualmin File Manager
```

### Step 2: Make Script Executable

```bash
cd /home/sanasend/public_html
chmod +x virtualmin-install-automated.sh
```

### Step 3: Run the Automated Installer

```bash
bash virtualmin-install-automated.sh
```

**That's it!** The script will:
1. Display configuration summary
2. Ask you to press Enter to confirm
3. Run completely automated (10-15 minutes)
4. Test database connection before proceeding
5. Create everything automatically
6. Start all services

---

## What the Script Does

### Step 1: System Dependencies ✓
- Installs Python 3, Node.js 18, PostgreSQL, Git, etc.
- Silent installation (no output clutter)

### Step 2: Node.js Installation ✓
- Installs Node.js 18 from official repository

### Step 3: PostgreSQL Setup ✓
- Installs and configures PostgreSQL

### Step 4: Database Creation ✓
- Creates database: `whatsapp_saas_prod`
- Creates user: `whatsapp_saas`
- Grants all privileges

### Step 5: **DATABASE CONNECTION TEST** ✓
- Tests connection with provided credentials
- Verifies database is accessible
- **STOPS if connection fails** with clear error message
- Shows exactly what went wrong

### Step 6-7: Redis & Supervisor ✓
- Installs Supervisor for service management
- Skips Redis (uses local cache)

### Step 8: Project Setup ✓
- Verifies project files exist
- Sets up directory structure

### Step 9: Python Environment ✓
- Creates virtual environment
- Installs all Python dependencies

### Step 10: Directories ✓
- Creates logs, media, staticfiles directories
- Sets up WhatsApp service directories

### Step 11: Configuration ✓
- Generates Django SECRET_KEY
- Creates `.env.production` with all settings

### Step 12: Django Initialization ✓
- Runs database migrations
- Collects static files
- **Creates superuser automatically** (no prompts!)

### Step 13: Node.js Setup ✓
- Installs Node.js dependencies
- Creates Node.js configuration

### Step 14: System Services ✓
- Creates systemd services
- Enables and starts services
- Verifies services are running

---

## Database Connection Testing

The script includes robust database connection testing:

```
═══ STEP 5/14: Testing Database Connection ═══

[ℹ] Verifying database credentials...
[✓] ✓ Database connection successful!
[✓] ✓ Credentials verified
[✓] ✓ Database is ready
```

**If connection fails:**
```
[✗] ✗ Database connection failed!
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║         DATABASE CONNECTION TEST FAILED!              ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

[✗] Please check:
[✗] 1. Database name: whatsapp_saas_prod
[✗] 2. Database user: whatsapp_saas
[✗] 3. Database password is correct
[✗] 4. PostgreSQL is running: sudo systemctl status postgresql
```

The script **STOPS immediately** if database connection fails!

---

## After Installation

### 1. Configure Web Server (Nginx)

```bash
sudo nano /etc/nginx/sites-available/whatsapp-saas
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name sanasend.com www.sanasend.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sanasend.com www.sanasend.com;

    # SSL will be configured by certbot
    
    client_max_body_size 10M;

    location /static/ {
        alias /home/sanasend/public_html/staticfiles/;
        expires 1y;
    }

    location /media/ {
        alias /home/sanasend/public_html/media/;
        expires 1M;
    }

    location /whatsapp/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and test:
```bash
sudo ln -s /etc/nginx/sites-available/whatsapp-saas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Setup SSL Certificate

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d sanasend.com -d www.sanasend.com
sudo certbot renew --dry-run
```

### 3. Test Installation

Visit these URLs:
- **Admin Panel**: https://sanasend.com/admin/
- **API Docs**: https://sanasend.com/api/docs/
- **Health Check**: https://sanasend.com/health/

### 4. Login to Admin Panel

```
URL: https://sanasend.com/admin/
Username: sanaric
Password: Sanaric123
Email: sanasoft20@gmail.com
```

---

## Service Management

### View Logs
```bash
# Django logs
sudo journalctl -u whatsapp-django -f

# Node.js logs
sudo journalctl -u whatsapp-node -f

# Recent errors
sudo journalctl -u whatsapp-django -n 50
```

### Restart Services
```bash
# Restart Django
sudo systemctl restart whatsapp-django

# Restart Node.js
sudo systemctl restart whatsapp-node

# Check status
sudo systemctl status whatsapp-django whatsapp-node
```

### Update Application
```bash
cd /home/sanasend/public_html
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
cd whatsapp-service && npm install --production && cd ..
sudo systemctl restart whatsapp-django whatsapp-node
```

---

## Installation Info File

All credentials are saved in: `/home/sanasend/public_html/INSTALLATION_INFO.txt`

This file contains:
- Database credentials
- Admin credentials
- Node.js API key
- Service names
- Useful commands

---

## Troubleshooting

### Database Connection Failed

**Check PostgreSQL is running:**
```bash
sudo systemctl status postgresql
```

**Test connection manually:**
```bash
psql -h localhost -U whatsapp_saas -d whatsapp_saas_prod
# Password: Passisdb123
```

**Check PostgreSQL logs:**
```bash
sudo journalctl -u postgresql -n 50
```

### Services Won't Start

**Check Django service:**
```bash
sudo journalctl -u whatsapp-django -n 50
sudo systemctl status whatsapp-django
```

**Check Node.js service:**
```bash
sudo journalctl -u whatsapp-node -n 50
sudo systemctl status whatsapp-node
```

### Can't Access Website

**Check firewall:**
```bash
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443
```

**Check Nginx:**
```bash
sudo systemctl status nginx
sudo nginx -t
```

---

## Security Notes

✅ Database password is configured  
✅ Admin password is configured  
✅ SECRET_KEY auto-generated  
✅ SSL/HTTPS required  
✅ DEBUG mode disabled  
✅ Proper file permissions set  

---

## Comparison: Automated vs Interactive

| Feature | Automated Script | Interactive Script |
|---------|------------------|-------------------|
| Prompts | 0 (zero!) | 7+ prompts |
| Time | 10-15 min | 10-15 min + input time |
| Database Test | Yes ✓ | Yes ✓ |
| Auto Superuser | Yes ✓ | No (interactive) |
| Best For | Production deployment | Custom setups |

---

## What Makes This Different?

### Traditional Installer:
1. Start script
2. Enter username → wait
3. Enter domain → wait
4. Enter password → wait
5. Confirm password → wait
6. Enter email → wait
7. ...more prompts...
8. Finally installs

### Automated Installer:
1. Start script
2. Press Enter once
3. ☕ Coffee break (10 minutes)
4. Done! ✓

---

## Files Created

After installation, you'll have:

```
/home/sanasend/public_html/
├── .env.production              # Environment configuration
├── INSTALLATION_INFO.txt        # All credentials and info
├── logs/                        # Application logs
│   ├── django.log
│   ├── gunicorn-access.log
│   └── gunicorn-error.log
├── media/                       # Uploaded files
├── staticfiles/                 # Static assets
├── whatsapp-service/           
│   ├── .env                     # Node.js configuration
│   ├── sessions/                # WhatsApp sessions
│   └── logs/                    # Node.js logs
└── venv/                        # Python virtual environment
```

---

## Success Criteria

Installation is successful when you see:

```
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║         Installation Successful! 🎉                   ║
║                                                       ║
║           All Services Running!                       ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

[✓] ✓ Django service is running
[✓] ✓ Node.js service is running
```

---

## Next Steps After Installation

1. ✅ Configure Nginx reverse proxy
2. ✅ Setup SSL certificate with certbot
3. ✅ Test admin panel login
4. ✅ Create first API user
5. ✅ Generate API keys
6. ✅ Test WhatsApp integration
7. ✅ Setup automated backups

---

**Total Time: 10-15 minutes + 5 minutes for SSL**

**Ready to deploy? Just run the script! 🚀**

