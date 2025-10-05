# Automated Virtualmin Installation

## Quick Install (10-15 minutes)

This automated script handles 90% of the deployment work for you!

---

## What The Script Does Automatically

✅ Installs system dependencies (Python, Node.js, PostgreSQL, Redis)  
✅ Creates database and user  
✅ Sets up Python virtual environment  
✅ Installs all Python packages  
✅ Installs Node.js dependencies  
✅ Generates secure secret keys  
✅ Creates environment configuration  
✅ Runs database migrations  
✅ Collects static files  
✅ Creates systemd services  
✅ Starts Django and Node.js services  
✅ Sets proper file permissions  

---

## Prerequisites (5 minutes)

1. **Virtualmin installed** and accessible
2. **Domain pointed** to your server
3. **SSH access** to your server
4. **Project files uploaded** to server

---

## Step-by-Step Installation

### Step 1: Upload Project Files

**Option A - Using Git (Recommended)**
```bash
ssh sanasend@your-server-ip
cd /home/sanasend
mkdir -p public_html
cd public_html
git clone https://github.com/your-username/your-repo.git .
```

**Option B - Using SFTP/SCP**
- Use FileZilla, WinSCP, or `scp` command
- Upload to: `/home/sanasend/public_html/`

**Option C - Using Virtualmin File Manager**
- Login to Virtualmin
- Go to **Others** → **File Manager**
- Navigate to `/home/sanasend/`
- Create folder `public_html` (if not exists)
- Upload files (can upload ZIP and extract)

### Step 2: Make Script Executable

```bash
cd /home/sanasend/public_html
chmod +x virtualmin-install.sh
```

### Step 3: Run The Installer

```bash
bash virtualmin-install.sh
```

### Step 4: Answer Prompts

The script will ask you for:

1. **Virtualmin username** (default: `sanasend`, press Enter to accept)
2. **Domain name** (e.g., `example.com`)
3. **Installation path** (default: `/home/sanasend/public_html`, press Enter to accept)
4. **Database password** (create a strong password)
5. **Node.js API key** (auto-generated if you press Enter)
6. **Install Redis?** (type `n` for small servers)
7. **Create admin user** (username, email, password)

### Step 5: Configure Web Server

After the script completes, you need to configure your web server:

**For Nginx:**
```bash
sudo nano /etc/nginx/sites-available/whatsapp-saas
```

Paste this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

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

Replace `yourdomain.com` with your actual domain.

Enable and test:
```bash
sudo ln -s /etc/nginx/sites-available/whatsapp-saas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**For Apache:**
See `VIRTUALMIN_DEPLOYMENT_GUIDE.md` Section 9.3

### Step 6: Setup SSL Certificate

```bash
# Install certbot (if not already installed)
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 7: Test Your Installation

Visit these URLs:
- **Admin Panel**: `https://yourdomain.com/admin/`
- **API Documentation**: `https://yourdomain.com/api/docs/`
- **Health Check**: `https://yourdomain.com/health/`

---

## What You Need to Prepare

Before running the script, have these ready:

1. ✅ **Domain name** (e.g., example.com)
2. ✅ **Strong database password** (at least 16 characters)
3. ✅ **Admin username** for Django admin
4. ✅ **Admin email**
5. ✅ **Admin password** for Django admin

---

## Installation Timeline

| Step | Task | Time |
|------|------|------|
| 1 | Upload files | 2-5 min |
| 2 | Run installer script | 5-8 min |
| 3 | Configure web server | 2-3 min |
| 4 | Setup SSL | 2-3 min |
| 5 | Test installation | 2 min |
| **Total** | | **13-21 min** |

---

## Useful Commands After Installation

### View Logs
```bash
# Django application logs
sudo journalctl -u whatsapp-django -f

# Node.js service logs
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
sudo systemctl status whatsapp-django
sudo systemctl status whatsapp-node
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

## Troubleshooting

### Script Fails at Database Creation

**Error**: `database already exists`

**Solution**: Database was already created, this is OK. Continue with the script.

### Service Won't Start

```bash
# Check why it failed
sudo journalctl -u whatsapp-django -n 50

# Common fixes:
# 1. Check .env.production file exists
# 2. Verify database credentials
# 3. Check file permissions
sudo chown -R sanasend:sanasend /home/sanasend/public_html
```

### Can't Access Website

```bash
# Check if services are running
sudo systemctl status whatsapp-django
sudo systemctl status whatsapp-node

# Check web server
sudo systemctl status nginx

# Check firewall
sudo ufw status
```

### 502 Bad Gateway

```bash
# Restart all services
sudo systemctl restart whatsapp-django
sudo systemctl restart whatsapp-node
sudo systemctl restart nginx

# Check Django is listening on port 8000
sudo netstat -tlnp | grep 8000
```

---

## Manual Installation Alternative

If you prefer manual installation or the script fails, follow the complete guide:

📖 **VIRTUALMIN_DEPLOYMENT_GUIDE.md** - Complete step-by-step manual installation

📋 **VIRTUALMIN_QUICK_CHECKLIST.md** - Quick reference checklist

---

## Security Notes

✅ Script generates secure random SECRET_KEY  
✅ Database password is required (not auto-generated)  
✅ SSL/HTTPS setup required (via certbot)  
✅ DEBUG mode automatically disabled  
✅ Proper file permissions set automatically  

---

## What's NOT Automated

You still need to manually:

1. ⚠️ **Upload project files** to server (via Git/SFTP/File Manager)
2. ⚠️ **Configure web server** (Nginx/Apache reverse proxy)
3. ⚠️ **Setup SSL certificate** (via certbot)
4. ⚠️ **Create admin superuser** (interactive prompt during script)

These steps require your input and cannot be safely automated.

---

## Support

### Installation Issues
- Check `INSTALLATION_INFO.txt` in your project directory
- Review logs: `sudo journalctl -u whatsapp-django -f`
- See troubleshooting section above

### Full Documentation
- `VIRTUALMIN_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `INTEGRATION_GUIDE.md` - API integration guide
- `USER_DASHBOARD_GUIDE.md` - Dashboard usage guide

### Test API
```bash
# After installation, test the API
curl -X POST https://yourdomain.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'
```

---

## Script Safety

The script is safe because it:

✅ Checks for existing installations  
✅ Doesn't run as root  
✅ Backs up nothing (doesn't overwrite)  
✅ Uses `set -e` (exits on errors)  
✅ Shows all actions with colored output  
✅ Creates backup of installation info  

---

## Next Steps After Installation

1. ✅ Test admin panel login
2. ✅ Create a test user
3. ✅ Generate API key for user
4. ✅ Test WhatsApp session initiation
5. ✅ Send test message
6. ✅ Setup automated backups (see guide)
7. ✅ Configure monitoring

---

**Congratulations! Your SanaSend SaaS is now deployed! 🎉**

For production use, also see:
- `DEPLOYMENT_CHECKLIST.md` - Pre-launch checklist
- `PROJECT_STATUS.md` - Project status and features

