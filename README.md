# SanaSend SaaS

A Django-based SaaS application that provides WhatsApp Web access through a REST API. Admin-managed users only.

## Project Structure

```
whatsapp_saas/
├── config/                 # Django configuration
│   ├── settings/          # Split settings (dev/prod)
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── core/                   # Shared utilities
│   ├── responses.py       # Unified API responses
│   ├── pagination.py      # Custom pagination
│   ├── permissions.py     # Base permissions
│   ├── exceptions.py      # Custom exceptions
│   ├── middleware.py      # Custom middleware
│   └── validators.py      # Reusable validators
├── users/                  # User management
├── sessions/               # WhatsApp session handling
├── messages/               # Message operations
├── api_keys/               # API key management
├── analytics/              # Usage tracking
└── api/v1/                 # API endpoints
    ├── users/
    ├── sessions/
    ├── messages/
    ├── api_keys/
    └── analytics/
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- Node.js 18+ (for WhatsApp bridge)

### Installation

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create .env file:**
```bash
# Copy example and edit with your values
cp .env.example .env
```

Required environment variables:
- `SECRET_KEY` - Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - PostgreSQL credentials
- `REDIS_HOST`, `REDIS_PORT` - Redis connection

4. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py createsuperuser
```

6. **Run development server:**
```bash
python manage.py runserver
```

### Running Celery (for background tasks)

```bash
# Start Celery worker
celery -A config worker -l info

# Start Celery beat (scheduled tasks)
celery -A config beat -l info
```

## API Documentation

Once the server is running, access the API documentation:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **Admin Panel:** http://localhost:8000/admin/

## Authentication

### Admin JWT Authentication

For admin endpoints, use JWT tokens:

```bash
# Login endpoint (to be implemented)
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "password"
}
```

### API Key Authentication

For user endpoints, use API keys:

```
Authorization: ApiKey YOUR_API_KEY_HERE
```

API keys can be generated from the admin panel.

## API Endpoints

### Users (Admin only)
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}/` - Get user
- `PUT /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user
- `POST /api/v1/users/{id}/activate/` - Activate user
- `POST /api/v1/users/{id}/deactivate/` - Deactivate user

### API Keys (Admin only)
- `GET /api/v1/api-keys/` - List API keys
- `POST /api/v1/api-keys/` - Create API key
- `DELETE /api/v1/api-keys/{id}/` - Revoke API key

### Sessions
- `GET /api/v1/sessions/status/` - Get session status
- `POST /api/v1/sessions/init/` - Initialize session
- `POST /api/v1/sessions/disconnect/` - Disconnect session

### Messages
- `POST /api/v1/messages/send-text/` - Send text message
- `POST /api/v1/messages/send-media/` - Send media message
- `GET /api/v1/messages/list/` - List messages

### Analytics (Admin only)
- `GET /api/v1/analytics/usage-stats/` - Get usage statistics
- `GET /api/v1/analytics/api-logs/` - Get API logs

## Development Status

### ✅ Phase 1: Project Setup & Foundation (COMPLETED)
- [x] Django project structure
- [x] Database models
- [x] API endpoints structure
- [x] Admin interface
- [x] Core utilities

### ✅ Phase 2: User Management & Authentication (COMPLETED)
- [x] Custom User model
- [x] API Key system with secure hashing
- [x] JWT authentication endpoints
- [x] Permission classes
- [x] Admin interfaces

### ✅ Phase 3: WhatsApp Session Management (COMPLETED)
- [x] Node.js bridge setup
- [x] Session lifecycle management
- [x] QR code generation
- [x] Session models created
- [x] WhatsApp Web.js integration
- [x] Multi-user support

### ✅ Phase 4: Messaging API (COMPLETED)
- [x] Text message sending implementation
- [x] Media message sending implementation
- [x] Message models created
- [x] API endpoints functional
- [x] Message logging
- [x] Status tracking

### ⏳ Phase 5: Rate Limiting & Analytics (NEXT)
- [ ] Rate limiting implementation
- [ ] Usage tracking with Celery
- [x] Analytics models created

## Contributing

This is a private SaaS project. Contact the admin for contribution guidelines.

## License

Proprietary - All rights reserved

