# Quick Start Guide

## For Developers Just Joining the Project

### What's Been Done ✅

**Phase 1 & 2 are COMPLETE:**
- Full Django project structure
- 6 Django apps with models, admin, and APIs
- JWT + API Key authentication
- Complete API endpoint structure
- Admin interface ready

**Current Version:** 0.1.0 - Foundation Complete

### What You Need to Do Right Now

#### 1. Install & Setup (5 minutes)

```bash
# Run the installer
.\install.ps1          # Windows
# OR
bash install.sh        # Linux/Mac
```

#### 2. Configure Database (2 minutes)

Edit `.env` file:
```env
DB_NAME=whatsapp_saas
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
```

#### 3. Run Migrations (1 minute)

```bash
py manage.py makemigrations      # Windows
py manage.py migrate

# OR
python manage.py makemigrations  # Linux/Mac
python manage.py migrate
```

#### 4. Create Admin User (1 minute)

```bash
py manage.py createsuperuser
```

#### 5. Start Server (1 minute)

```bash
py manage.py runserver
```

Visit: http://localhost:8000/admin/

### Quick Test

**Test 1: Login via API**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

**Test 2: Create User (Admin Panel)**
1. Go to http://localhost:8000/admin/
2. Click "Users" → "Add User"
3. Fill in details and save

**Test 3: Generate API Key**
1. In admin, click "API Keys" → "Add API Key"
2. Select a user
3. Save and copy the key (shown only once!)

**Test 4: Test API Key**
```bash
curl -X GET http://localhost:8000/api/v1/sessions/status/ \
  -H "Authorization: ApiKey YOUR_KEY_HERE"
```

### What's Next? (Phase 3)

You need to create the Node.js service for WhatsApp integration.

**See:** `docs/PHASE3_NODEJS_GUIDE.md` (to be created)

### Project Structure Overview

```
sanasr/
├── config/              # Django settings
├── core/                # Utilities (responses, permissions, etc.)
├── users/               # User management
├── sessions/            # WhatsApp sessions (models ready)
├── messages/            # Messages (models ready)
├── api_keys/            # API key auth
├── analytics/           # Usage tracking
├── api/v1/              # API endpoints
│   ├── auth/           # Login, logout, me
│   ├── users/          # User CRUD
│   ├── sessions/       # Session management
│   ├── messages/       # Send messages
│   ├── api_keys/       # Key management
│   └── analytics/      # Stats & logs
└── manage.py
```

### Key Files to Know

- `config/settings/base.py` - Main settings
- `config/settings/development.py` - Dev settings
- `core/responses.py` - API response format
- `api_keys/authentication.py` - API key auth logic
- `api/v1/*/views.py` - API endpoints

### Common Commands

```bash
# Start dev server
py manage.py runserver

# Create migrations
py manage.py makemigrations

# Run migrations
py manage.py migrate

# Create superuser
py manage.py createsuperuser

# Start Django shell
py manage.py shell

# Run Celery worker
celery -A config worker -l info

# Run Celery beat
celery -A config beat -l info
```

### API Documentation

Once server is running:
- **Swagger:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/

### Need Help?

1. **Setup Issues:** See `SETUP.md`
2. **Full Documentation:** See `PROJECT_STATUS.md`
3. **Tasks Checklist:** See `Project_Tasks.md`
4. **Changes Log:** See `CHANGELOG.md`

### Environment Check

Make sure these are running before starting:
- [ ] PostgreSQL (port 5432)
- [ ] Redis (port 6379)
- [ ] Python virtual environment activated

### Troubleshooting

**Issue:** Django not found
**Fix:** Activate virtual environment
```bash
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

**Issue:** Database connection error
**Fix:** Check PostgreSQL is running and .env credentials are correct

**Issue:** Redis connection error
**Fix:** Start Redis server
```bash
redis-server
```

---

**You're all set!** The foundation is solid. Now it's time to build the WhatsApp integration (Phase 3).

