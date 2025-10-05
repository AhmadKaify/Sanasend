# SanaSend SaaS - Installation Options for Virtualmin

Choose the installation method that best suits your needs:

---

## 🚀 Option 1: AUTOMATED INSTALLATION (Recommended)

**Time**: 10-15 minutes  
**Difficulty**: ⭐ Easy  
**Automation**: 90%

### What You Get
- ✅ Automatic system setup
- ✅ Automatic dependency installation
- ✅ Database creation and configuration
- ✅ Django & Node.js setup
- ✅ Service creation and startup
- ✅ Security configuration

### How To Use

1. **Upload project files to server:**
   ```bash
   ssh sanasend@your-server
   cd /home/sanasend
   mkdir -p public_html
   cd public_html
   git clone your-repo-url .
   ```

2. **Run the installer:**
   ```bash
   chmod +x virtualmin-install.sh
   bash virtualmin-install.sh
   ```

3. **Answer prompts** (domain, passwords, etc.)

4. **Configure web server** (2 minutes)

5. **Setup SSL** (2 minutes)

### What's Automated
- System package installation
- Database setup
- Python environment
- Django initialization
- Node.js setup
- Service creation
- File permissions

### What You Need To Do
- Upload files
- Answer configuration prompts
- Configure Nginx/Apache
- Setup SSL certificate

### Read This Guide
📖 **AUTOMATED_INSTALL_README.md**

---

## 📝 Option 2: MANUAL INSTALLATION (Step-by-Step)

**Time**: 60-90 minutes  
**Difficulty**: ⭐⭐⭐ Intermediate  
**Automation**: 0% (Full Control)

### What You Get
- ✅ Complete understanding of the setup
- ✅ Full control over configuration
- ✅ Custom modifications possible
- ✅ Learning experience

### How To Use

Follow the comprehensive guide with 14 detailed steps:

1. Initial server setup
2. Database configuration
3. File deployment
4. Python environment
5. Environment configuration
6. Django initialization
7. Node.js setup
8. Service configuration
9. Web server setup
10. SSL certificate
11. File permissions
12. Firewall configuration
13. Testing
14. Maintenance setup

### Perfect For
- Learning the system architecture
- Custom server configurations
- Troubleshooting specific issues
- When automated script fails

### Read This Guide
📖 **VIRTUALMIN_DEPLOYMENT_GUIDE.md**

---

## ⚡ Option 3: QUICK CHECKLIST (For Experienced Users)

**Time**: 45-60 minutes  
**Difficulty**: ⭐⭐⭐⭐ Advanced  
**Automation**: 0%

### What You Get
- ✅ Condensed command reference
- ✅ Quick troubleshooting
- ✅ Fast deployment for experts

### How To Use

Use the checklist format with direct commands and minimal explanation.

### Perfect For
- Experienced sysadmins
- Quick deployments
- Reference during installation

### Read This Guide
📋 **VIRTUALMIN_QUICK_CHECKLIST.md**

---

## Comparison Table

| Feature | Automated | Manual | Quick Checklist |
|---------|-----------|--------|-----------------|
| Time Required | 10-15 min | 60-90 min | 45-60 min |
| Difficulty | Easy | Intermediate | Advanced |
| Automation | 90% | 0% | 0% |
| Learning Value | Low | High | Medium |
| Error Prevention | High | Medium | Low |
| Customization | Limited | Full | Full |
| Best For | Quick setup | Learning | Experts |

---

## Which Option Should I Choose?

### Choose AUTOMATED if:
- ✅ You want the fastest installation
- ✅ You're new to Linux server administration
- ✅ You want minimal chance of errors
- ✅ You have standard Virtualmin setup
- ✅ You follow best practices

**→ Start with AUTOMATED_INSTALL_README.md**

### Choose MANUAL if:
- ✅ You want to learn the system deeply
- ✅ You need custom configurations
- ✅ You're troubleshooting an issue
- ✅ You have specific security requirements
- ✅ The automated script failed

**→ Start with VIRTUALMIN_DEPLOYMENT_GUIDE.md**

### Choose QUICK CHECKLIST if:
- ✅ You're an experienced sysadmin
- ✅ You've deployed similar apps before
- ✅ You just need a command reference
- ✅ You know what you're doing

**→ Start with VIRTUALMIN_QUICK_CHECKLIST.md**

---

## All Installation Files

### Main Guides
1. **AUTOMATED_INSTALL_README.md** - Automated installation guide
2. **VIRTUALMIN_DEPLOYMENT_GUIDE.md** - Complete manual guide
3. **VIRTUALMIN_QUICK_CHECKLIST.md** - Quick reference

### Installation Scripts
1. **virtualmin-install.sh** - Automated installer (Linux)
2. **install.sh** - Development setup (Linux)
3. **install.ps1** - Development setup (Windows)
4. **deploy.sh** - Production deployment (Standard servers)

### Support Documents
1. **INTEGRATION_GUIDE.md** - API integration guide
2. **USER_DASHBOARD_GUIDE.md** - Dashboard usage
3. **DEPLOYMENT_CHECKLIST.md** - Pre-launch checklist
4. **START_HERE.md** - Project overview

---

## Installation Flow Chart

```
Start
  │
  ├─ Need quick setup? ─ YES → Use AUTOMATED (virtualmin-install.sh)
  │                       │
  │                       └─ Answer prompts → Configure web server → Setup SSL → Done ✓
  │
  ├─ Want to learn? ─── YES → Use MANUAL (VIRTUALMIN_DEPLOYMENT_GUIDE.md)
  │                       │
  │                       └─ Follow 14 steps → Test → Done ✓
  │
  └─ Are you expert? ── YES → Use CHECKLIST (VIRTUALMIN_QUICK_CHECKLIST.md)
                        │
                        └─ Run commands → Test → Done ✓
```

---

## Prerequisites (All Options)

Before starting any installation method, ensure you have:

### Server Requirements
- [ ] Ubuntu 20.04+ or CentOS 8+
- [ ] Minimum 2GB RAM (4GB recommended)
- [ ] Minimum 20GB SSD storage
- [ ] Virtualmin installed and accessible
- [ ] Root/sudo access

### Access Requirements
- [ ] SSH access to server
- [ ] Domain name pointing to server
- [ ] Virtualmin login credentials

### Prepared Information
- [ ] Domain name (e.g., example.com)
- [ ] Database password (strong, 16+ characters)
- [ ] Admin email
- [ ] Admin password for Django

---

## After Installation (All Options)

Once installed, you'll need to:

1. **Test the installation**
   - Admin panel: `https://yourdomain.com/admin/`
   - API docs: `https://yourdomain.com/api/docs/`
   - Health check: `https://yourdomain.com/health/`

2. **Create first user and API key**
   - Login to admin panel
   - Create user account
   - Generate API key

3. **Test WhatsApp integration**
   - Initialize session
   - Scan QR code
   - Send test message

4. **Setup backups**
   - Configure daily database backups
   - Setup media file backups

5. **Monitor services**
   - Check logs regularly
   - Monitor resource usage
   - Setup alerts (optional)

---

## Getting Help

### For Installation Issues
- Check relevant guide's troubleshooting section
- Review logs: `sudo journalctl -u whatsapp-django -f`
- Check service status: `sudo systemctl status whatsapp-*`

### For API Integration
- See: `INTEGRATION_GUIDE.md`
- API docs: `https://yourdomain.com/api/docs/`

### For Dashboard Usage
- See: `USER_DASHBOARD_GUIDE.md`

### Common Issues
1. **502 Bad Gateway** - Service not running, restart services
2. **Static files not loading** - Run collectstatic, check permissions
3. **Database connection** - Check credentials in .env file
4. **WhatsApp not connecting** - Check Node.js service logs

---

## Quick Start (TL;DR)

**Fastest way to get started:**

```bash
# 1. SSH to server
ssh sanasend@your-server

# 2. Upload files
cd /home/sanasend
mkdir -p public_html
cd public_html
git clone your-repo-url .

# 3. Run automated installer
chmod +x virtualmin-install.sh
bash virtualmin-install.sh

# 4. Follow prompts and configure web server

# 5. Setup SSL
sudo certbot --nginx -d yourdomain.com

# Done! Visit https://yourdomain.com/admin/
```

---

## Success Criteria

Your installation is successful when:

✅ Django service running: `sudo systemctl status whatsapp-django`  
✅ Node.js service running: `sudo systemctl status whatsapp-node`  
✅ Admin panel accessible with HTTPS  
✅ API documentation visible  
✅ Health check returns OK  
✅ Can create users and API keys  
✅ WhatsApp session can be initiated  
✅ Messages can be sent successfully  

---

## Recommendation

**For most users, we recommend:**

1. **Start with AUTOMATED installation** (virtualmin-install.sh)
2. **Keep MANUAL GUIDE handy** for troubleshooting
3. **Use QUICK CHECKLIST** for future updates

This approach gives you:
- ✅ Fast deployment
- ✅ Reference for understanding
- ✅ Easy maintenance

---

**Ready to install? Start with the guide that matches your needs above!**

**Good luck! 🚀**

