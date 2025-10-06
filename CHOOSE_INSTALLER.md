# Choose Your Installation Method

Two installation scripts are available. Choose based on your needs:

---

## 🚀 Option 1: Fully Automated (Recommended for Your Setup)

**File:** `virtualmin-install-automated.sh`

### Pre-Configured Values
✅ Username: `sanasend`  
✅ Domain: `sanasend.com`  
✅ Admin: `sanaric` / `Sanaric123`  
✅ Email: `sanasoft20@gmail.com`  
✅ DB: `whatsapp_saas_prod` / `whatsapp_saas` / `Passisdb123`  

### Usage
```bash
cd /home/sanasend/public_html
chmod +x virtualmin-install-automated.sh
bash virtualmin-install-automated.sh
# Press Enter once, wait 10-15 minutes, done!
```

### Advantages
- **Zero prompts** during installation
- Database connection tested before proceeding
- Superuser created automatically
- All credentials saved automatically
- Perfect for production deployment
- Can be re-run if needed

### When to Use
✅ You want fastest deployment  
✅ You're using the pre-configured values  
✅ You want zero interruptions  
✅ You trust the configuration  
✅ Production server setup  

**→ See: AUTOMATED_INSTALL_GUIDE.md**

---

## 🛠️ Option 2: Interactive (Customizable)

**File:** `virtualmin-install.sh`

### What It Asks
❓ Username (default: sanasend)  
❓ Domain name  
❓ Installation path  
❓ Database password  
❓ Node.js API key (or auto-generate)  
❓ Install Redis? (y/n)  
❓ Create admin user (interactive)  

### Usage
```bash
cd /home/sanasend/public_html
chmod +x virtualmin-install.sh
bash virtualmin-install.sh
# Answer 7+ prompts during installation
```

### Advantages
- Full control over configuration
- Can customize all values
- Can change paths and names
- Interactive admin creation
- Good for custom setups

### When to Use
✅ You need different values  
✅ You want to customize everything  
✅ You want to see what's being configured  
✅ Testing or development setup  
✅ Non-standard installation  

**→ See: AUTOMATED_INSTALL_README.md**

---

## Quick Comparison

| Feature | Automated | Interactive |
|---------|-----------|-------------|
| **Prompts** | 0 (just press Enter once) | 7+ prompts |
| **Configuration** | Pre-set | Custom |
| **Superuser** | Auto-created | Interactive |
| **Database Test** | ✓ Automatic | ✓ Automatic |
| **Time** | 10-15 min | 10-15 min + input time |
| **Re-runnable** | ✓ Yes | ✓ Yes |
| **Best For** | Production | Development/Custom |

---

## For Your Specific Setup

Since you've provided these specific values:
- Username: `sanasend`
- Domain: `sanasend.com`
- Admin: `sanaric`
- Password: `Sanaric123`
- Email: `sanasoft20@gmail.com`
- DB Password: `Passisdb123`

**→ Use the AUTOMATED script (`virtualmin-install-automated.sh`)**

It's pre-configured with your exact values!

---

## Installation Flow

### Automated Script Flow:
```
Start Script
    ↓
Display Configuration Summary
    ↓
Press Enter to Confirm
    ↓
[Automated Installation - 10-15 min]
    ├─ Install system packages
    ├─ Setup database
    ├─ TEST database connection ← Stops if fails!
    ├─ Create Python environment
    ├─ Initialize Django
    ├─ Create superuser (no prompts!)
    ├─ Setup Node.js
    └─ Start services
    ↓
Done! 🎉
```

### Interactive Script Flow:
```
Start Script
    ↓
Prompt: Username? ⌨️
    ↓
Prompt: Domain? ⌨️
    ↓
Prompt: Path? ⌨️
    ↓
Prompt: DB Password? ⌨️
    ↓
Prompt: API Key? ⌨️
    ↓
Prompt: Redis? ⌨️
    ↓
[Automated Installation - 10-15 min]
    ├─ Install system packages
    ├─ Setup database
    ├─ TEST database connection
    ├─ Create Python environment
    ├─ Initialize Django
    └─ Setup Node.js
    ↓
Prompt: Create superuser ⌨️
    ├─ Username? ⌨️
    ├─ Email? ⌨️
    └─ Password? ⌨️
    ↓
Done! 🎉
```

---

## Decision Tree

```
Do you need custom values?
    │
    ├─ NO → Use AUTOMATED script
    │         • Fast
    │         • Zero prompts
    │         • Pre-configured
    │
    └─ YES → Use INTERACTIVE script
              • Flexible
              • Customizable
              • Full control
```

---

## Recommendation

**For sanasend.com setup:**

Use: `virtualmin-install-automated.sh`

Why?
1. ✅ Pre-configured with your exact values
2. ✅ Zero prompts = faster deployment
3. ✅ Database connection tested automatically
4. ✅ Superuser created automatically
5. ✅ All credentials saved in INSTALLATION_INFO.txt
6. ✅ Can focus on SSL setup instead

---

## Both Scripts Include

✅ System dependency installation  
✅ Database creation and configuration  
✅ Database connection testing  
✅ Python virtual environment setup  
✅ Django initialization  
✅ Static files collection  
✅ Node.js service setup  
✅ Systemd service creation  
✅ Service startup and verification  
✅ Proper file permissions  
✅ Comprehensive error messages  

---

## After Installation (Both Scripts)

Same next steps for both:

1. **Configure Nginx** (2 minutes)
2. **Setup SSL** (2 minutes with certbot)
3. **Test installation**
4. **Login to admin panel**

Total time including SSL: **15-20 minutes**

---

## Files to Read

### For Automated Script:
- `AUTOMATED_INSTALL_GUIDE.md` - Detailed guide
- `virtualmin-install-automated.sh` - The script

### For Interactive Script:
- `AUTOMATED_INSTALL_README.md` - Detailed guide
- `virtualmin-install.sh` - The script

### General Documentation:
- `VIRTUALMIN_DEPLOYMENT_GUIDE.md` - Manual installation
- `VIRTUALMIN_QUICK_CHECKLIST.md` - Quick reference
- `INSTALLATION_OPTIONS.md` - All options

---

## Quick Start (TL;DR)

### Using Automated Script:
```bash
cd /home/sanasend/public_html
chmod +x virtualmin-install-automated.sh
bash virtualmin-install-automated.sh
# Wait 10-15 minutes ☕
```

### Using Interactive Script:
```bash
cd /home/sanasend/public_html
chmod +x virtualmin-install.sh
bash virtualmin-install.sh
# Answer prompts, then wait 10-15 minutes ☕
```

---

**Ready to deploy? Choose your installer above! 🚀**

