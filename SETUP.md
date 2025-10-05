# Setup Instructions

## Quick Start Guide

### 1. Environment Setup

**Create and activate virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

**PostgreSQL Setup:**

```bash
# Create database and user
psql -U postgres

CREATE DATABASE whatsapp_saas;
CREATE USER whatsapp_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE whatsapp_saas TO whatsapp_user;
\q
```

### 4. Create Environment File

Create `.env` file in project root:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=whatsapp_saas
DB_USER=whatsapp_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Node.js Service
NODE_SERVICE_URL=http://localhost:3000

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Rate Limiting
MAX_MESSAGES_PER_MINUTE=10
MAX_MESSAGES_PER_DAY=1000
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Run Development Server

```bash
python manage.py runserver
```

The server will be available at: http://localhost:8000

### 8. Access Admin Panel

Visit: http://localhost:8000/admin/

Login with your superuser credentials.

### 9. Access API Documentation

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/

## Testing the Setup

### 1. Test Admin Login

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### 2. Create a User via Admin Panel

1. Go to http://localhost:8000/admin/
2. Click on "Users"
3. Click "Add User"
4. Fill in the details and save

### 3. Generate API Key for User

1. In admin panel, go to "API Keys"
2. Click "Add API Key"
3. Select user and optionally add a name
4. Save and copy the generated key (shown only once)

### 4. Test API Key Authentication

```bash
curl -X GET http://localhost:8000/api/v1/sessions/status/ \
  -H "Authorization: ApiKey YOUR_API_KEY_HERE"
```

## Running Background Services

### Redis

**Windows (using WSL or Windows Subsystem for Linux):**
```bash
redis-server
```

**Linux/Mac:**
```bash
redis-server
```

### Celery Worker

```bash
celery -A config worker -l info
```

### Celery Beat (Scheduled Tasks)

```bash
celery -A config beat -l info
```

## Common Issues

### Issue: Database connection error

**Solution:** Make sure PostgreSQL is running and credentials in `.env` are correct.

```bash
# Check PostgreSQL status
# Windows (if using WSL): sudo service postgresql status
# Linux: sudo systemctl status postgresql
# Mac: brew services list
```

### Issue: Redis connection error

**Solution:** Make sure Redis is running:

```bash
redis-cli ping
# Should return: PONG
```

### Issue: Migration errors

**Solution:** Delete migrations and recreate:

```bash
# Delete all migration files except __init__.py
python manage.py makemigrations
python manage.py migrate
```

### Issue: Static files not loading

**Solution:** Collect static files:

```bash
python manage.py collectstatic --noinput
```

## Next Steps

1. ✅ Phase 1 & 2 are complete (project setup and authentication)
2. ⏳ Phase 3: Node.js WhatsApp bridge setup (pending)
3. ⏳ Phase 4: Implement message sending (pending)
4. ⏳ Phase 5: Rate limiting and analytics (pending)

## Development Workflow

1. Always activate virtual environment before working
2. Pull latest changes from git
3. Run migrations if there are new ones: `python manage.py migrate`
4. Make your changes
5. Test your changes
6. Commit with descriptive messages
7. Push to repository

## Production Deployment Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Use production settings: `config.settings.production`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure proper database (not SQLite)
- [ ] Set up Redis for caching
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS
- [ ] Configure static/media file serving
- [ ] Set up logging
- [ ] Configure Celery for background tasks
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure backup strategy

