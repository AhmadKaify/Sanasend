# Clean Setup Guide

This guide provides instructions for completely cleaning your development environment and performing a fresh setup.

## Quick Start (Automated)

### Windows (PowerShell)
```powershell
.\clean_setup.ps1
```

### Linux/Mac
```bash
chmod +x clean_setup.sh
./clean_setup.sh
```

---

## Manual Cleanup (Step by Step)

If you prefer to run commands manually or the automated script doesn't work:

### Step 1: Clean Python Cache Files

**Windows (PowerShell):**
```powershell
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File | Remove-Item -Force
Get-ChildItem -Path . -Filter "*.pyo" -Recurse -File | Remove-Item -Force
```

**Linux/Mac:**
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

### Step 2: Remove Database

**Windows (PowerShell):**
```powershell
Remove-Item db.sqlite3 -Force
```

**Linux/Mac:**
```bash
rm -f db.sqlite3
```

### Step 3: Clean Migration Files

**Windows (PowerShell):**
```powershell
# Remove all migration files except __init__.py
Remove-Item analytics\migrations\*.py -Exclude __init__.py -Force
Remove-Item api_keys\migrations\*.py -Exclude __init__.py -Force
Remove-Item messages\migrations\*.py -Exclude __init__.py -Force
Remove-Item sessions\migrations\*.py -Exclude __init__.py -Force
Remove-Item users\migrations\*.py -Exclude __init__.py -Force

# Clean migration cache
Remove-Item analytics\migrations\__pycache__ -Recurse -Force
Remove-Item api_keys\migrations\__pycache__ -Recurse -Force
Remove-Item messages\migrations\__pycache__ -Recurse -Force
Remove-Item sessions\migrations\__pycache__ -Recurse -Force
Remove-Item users\migrations\__pycache__ -Recurse -Force
```

**Linux/Mac:**
```bash
# Remove all migration files except __init__.py
find analytics/migrations -type f ! -name "__init__.py" -delete
find api_keys/migrations -type f ! -name "__init__.py" -delete
find messages/migrations -type f ! -name "__init__.py" -delete
find sessions/migrations -type f ! -name "__init__.py" -delete
find users/migrations -type f ! -name "__init__.py" -delete

# Clean migration cache
find */migrations -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

### Step 4: Clear Log Files

**Windows (PowerShell):**
```powershell
Clear-Content logs\django.log
Remove-Item whatsapp-service\logs\* -Force
```

**Linux/Mac:**
```bash
> logs/django.log
rm -rf whatsapp-service/logs/*
```

### Step 5: Remove Static Files

**Windows (PowerShell):**
```powershell
Remove-Item staticfiles -Recurse -Force
```

**Linux/Mac:**
```bash
rm -rf staticfiles
```

### Step 6: Clean WhatsApp Session Data

**Windows (PowerShell):**
```powershell
Remove-Item whatsapp-service\.wwebjs_auth -Recurse -Force
Remove-Item whatsapp-service\.wwebjs_cache -Recurse -Force
```

**Linux/Mac:**
```bash
rm -rf whatsapp-service/.wwebjs_auth
rm -rf whatsapp-service/.wwebjs_cache
```

### Step 7: (Optional) Clean Node Modules

Only if you want to reinstall Node.js dependencies:

**Windows (PowerShell):**
```powershell
Remove-Item whatsapp-service\node_modules -Recurse -Force
```

**Linux/Mac:**
```bash
rm -rf whatsapp-service/node_modules
```

---

## Fresh Setup

After cleaning, perform these steps:

### 1. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Create Fresh Migrations

```bash
python manage.py makemigrations
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user:
- Username: (your choice)
- Email: (your choice)
- Password: (secure password)

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 6. (Optional) Reinstall Node Dependencies

If you removed node_modules:

```bash
cd whatsapp-service
npm install
cd ..
```

---

## Start Services

### Start Django Server

```bash
python manage.py runserver
```

### Start WhatsApp Service

**Terminal 1 (Django already running):**
Open a new terminal:

```bash
cd whatsapp-service
npm start
```

---

## Access Your Application

- **Django Admin**: http://localhost:8000/admin/
- **User Dashboard**: http://localhost:8000/dashboard/
- **API Documentation**: http://localhost:8000/api/v1/
- **Health Check**: http://localhost:8000/health/

---

## What Gets Cleaned

| Item | Description |
|------|-------------|
| `__pycache__/` | Python bytecode cache directories |
| `*.pyc, *.pyo` | Compiled Python files |
| `db.sqlite3` | SQLite database |
| `*/migrations/*.py` | Migration files (except `__init__.py`) |
| `logs/*.log` | Log files (cleared) |
| `staticfiles/` | Collected static files |
| `.wwebjs_auth/` | WhatsApp authentication data |
| `.wwebjs_cache/` | WhatsApp cache data |
| `node_modules/` | Node.js dependencies (optional) |

---

## Troubleshooting

### Script Execution Error on Windows

If you get "script execution disabled" error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Permission Denied on Linux/Mac

Make the script executable:

```bash
chmod +x clean_setup.sh
```

### Migration Errors

If you encounter migration errors:

1. Delete all migration files again
2. Run `python manage.py makemigrations` for each app:
   ```bash
   python manage.py makemigrations users
   python manage.py makemigrations api_keys
   python manage.py makemigrations sessions
   python manage.py makemigrations messages
   python manage.py makemigrations analytics
   ```
3. Then run `python manage.py migrate`

### WhatsApp Service Connection Issues

If WhatsApp service can't connect:

1. Ensure Django is running first
2. Check `whatsapp-service/src/config.js` for correct Django URL
3. Verify port 8000 is not blocked by firewall

---

## Notes

- **Backup Important Data**: This process will delete your database and all sessions
- **API Keys**: You'll need to regenerate API keys after cleanup
- **WhatsApp Sessions**: You'll need to scan QR codes again
- **Git Changes**: This cleanup doesn't affect git-tracked files

