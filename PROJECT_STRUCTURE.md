# Project Structure - Complete File Tree

## 📁 Full Directory Structure

```
sanasr/
│
├── 📄 manage.py                      # Django management script
├── 📄 requirements.txt               # Python dependencies
├── 📄 env.template                   # Environment variables template
├── 📄 .gitignore                     # Git ignore rules
│
├── 🚀 install.ps1                    # Windows installer script
├── 🚀 install.sh                     # Linux/Mac installer script
│
├── 📚 START_HERE.md                  # 👈 NEW DEVELOPER START HERE!
├── 📚 README.md                      # Project overview
├── 📚 QUICK_START.md                 # Quick setup guide
├── 📚 SETUP.md                       # Detailed setup instructions
├── 📚 PROJECT_STATUS.md              # Current development status
├── 📚 COMPLETION_SUMMARY.md          # Phase 1 & 2 completion details
├── 📚 CHANGELOG.md                   # Version history
├── 📚 Project_Tasks.md               # Task checklist with status
├── 📚 PHASE3_PREPARATION.md          # Guide for Phase 3 (WhatsApp)
├── 📚 PROJECT_STRUCTURE.md           # This file
│
├── 📁 config/                        # Django project configuration
│   ├── __init__.py                   # Celery app initialization
│   ├── asgi.py                       # ASGI configuration
│   ├── wsgi.py                       # WSGI configuration
│   ├── celery.py                     # Celery configuration
│   ├── urls.py                       # Main URL routing
│   └── 📁 settings/                  # Split settings
│       ├── __init__.py
│       ├── base.py                   # Base settings (DRF, JWT, Redis, etc.)
│       ├── development.py            # Development overrides
│       └── production.py             # Production overrides
│
├── 📁 core/                          # Shared utilities & base classes
│   ├── __init__.py
│   ├── apps.py                       # App configuration
│   ├── responses.py                  # ✨ Unified API response structure
│   ├── pagination.py                 # ✨ Custom pagination classes
│   ├── permissions.py                # ✨ IsAdminUser, IsActiveUser
│   ├── exceptions.py                 # ✨ Custom exception handlers
│   ├── middleware.py                 # ✨ API logging middleware
│   └── validators.py                 # ✨ Phone number validation
│
├── 📁 users/                         # ✅ User management app
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                     # 🗄️ User model (extends AbstractUser)
│   └── admin.py                      # 🎛️ User admin interface
│
├── 📁 sessions/                      # ✅ WhatsApp session management
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                     # 🗄️ WhatsAppSession model
│   └── admin.py                      # 🎛️ Session admin interface
│
├── 📁 messages/                      # ✅ Message operations
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                     # 🗄️ Message model (logging)
│   └── admin.py                      # 🎛️ Message admin interface
│
├── 📁 api_keys/                      # ✅ API key authentication
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                     # 🗄️ APIKey model (hashed keys)
│   ├── admin.py                      # 🎛️ API key admin interface
│   └── authentication.py             # 🔐 APIKeyAuthentication class
│
├── 📁 analytics/                     # ✅ Usage tracking & logging
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                     # 🗄️ UsageStats & APILog models
│   └── admin.py                      # 🎛️ Analytics admin interface
│
├── 📁 api/                           # API endpoints (v1)
│   ├── __init__.py
│   └── 📁 v1/                        # Version 1 API
│       ├── __init__.py
│       ├── urls.py                   # Main v1 URL routing
│       │
│       ├── 📁 auth/                  # 🔐 Authentication endpoints
│       │   ├── __init__.py
│       │   ├── serializers.py        # LoginSerializer, UserProfileSerializer
│       │   ├── views.py              # LoginView, LogoutView, MeView
│       │   └── urls.py               # /api/v1/auth/*
│       │
│       ├── 📁 users/                 # 👤 User management (Admin only)
│       │   ├── __init__.py
│       │   ├── serializers.py        # UserSerializer, UserCreateSerializer
│       │   ├── views.py              # UserViewSet (CRUD)
│       │   └── urls.py               # /api/v1/users/*
│       │
│       ├── 📁 api_keys/              # 🔑 API key management (Admin only)
│       │   ├── __init__.py
│       │   ├── serializers.py        # APIKeySerializer, APIKeyCreateSerializer
│       │   ├── views.py              # APIKeyViewSet
│       │   └── urls.py               # /api/v1/api-keys/*
│       │
│       ├── 📁 sessions/              # 📱 WhatsApp session endpoints
│       │   ├── __init__.py
│       │   ├── serializers.py        # WhatsAppSessionSerializer
│       │   ├── views.py              # SessionStatusView, InitSessionView, etc.
│       │   └── urls.py               # /api/v1/sessions/*
│       │
│       ├── 📁 messages/              # 💬 Message sending endpoints
│       │   ├── __init__.py
│       │   ├── serializers.py        # MessageSerializer, SendTextMessageSerializer
│       │   ├── views.py              # SendTextMessageView, SendMediaMessageView
│       │   └── urls.py               # /api/v1/messages/*
│       │
│       └── 📁 analytics/             # 📊 Analytics endpoints (Admin only)
│           ├── __init__.py
│           ├── serializers.py        # UsageStatsSerializer, APILogSerializer
│           ├── views.py              # UsageStatsListView, APILogListView
│           └── urls.py               # /api/v1/analytics/*
│
├── 📁 static/                        # Static files (CSS, JS, images)
│   └── .gitkeep
│
├── 📁 media/                         # User uploaded files
│   └── .gitkeep
│
└── 📁 logs/                          # Application logs
    └── .gitkeep
```

---

## 🎯 Key Components Explained

### Configuration (`config/`)
- **settings/base.py** - Core Django & DRF settings, JWT config, CORS, Redis, Celery
- **settings/development.py** - DEBUG=True, relaxed security
- **settings/production.py** - Security hardened, SSL, HSTS
- **celery.py** - Background task configuration
- **urls.py** - Main URL router (admin, API, docs)

### Core Utilities (`core/`)
- **responses.py** - `APIResponse.success()`, `APIResponse.error()`
- **pagination.py** - Standard pagination for list endpoints
- **permissions.py** - `IsAdminUser`, `IsActiveUser` permission classes
- **exceptions.py** - Custom exceptions with consistent error format
- **middleware.py** - Logs all API requests with timing
- **validators.py** - Phone number format validation

### Django Apps (6 apps)

#### 1. Users (`users/`)
- **Purpose:** User account management
- **Model:** User (extends Django's AbstractUser)
- **Key Fields:** max_messages_per_day, created_at, updated_at
- **Admin:** User CRUD with activate/deactivate actions

#### 2. Sessions (`sessions/`)
- **Purpose:** WhatsApp session lifecycle management
- **Model:** WhatsAppSession (OneToOne with User)
- **Key Fields:** session_id, status, qr_code, phone_number
- **Status:** Ready for Node.js integration

#### 3. Messages (`messages/`)
- **Purpose:** Message logging and history
- **Model:** Message
- **Key Fields:** user, recipient, content, status, sent_at
- **Status:** Ready for message sending implementation

#### 4. API Keys (`api_keys/`)
- **Purpose:** API key authentication for users
- **Model:** APIKey
- **Key Fields:** user, key (hashed), is_active, last_used_at
- **Security:** Keys are hashed using Django's password hasher

#### 5. Analytics (`analytics/`)
- **Purpose:** Usage tracking and API logging
- **Models:** UsageStats (daily aggregation), APILog (request logs)
- **Usage:** Admin dashboard statistics

### API Structure (`api/v1/`)

#### Authentication (`api/v1/auth/`)
- `POST /login/` - Admin login (returns JWT tokens)
- `POST /logout/` - Logout (blacklist refresh token)
- `POST /refresh/` - Refresh access token
- `GET /me/` - Get current user profile

#### Users (`api/v1/users/`) [Admin Only]
- `GET /` - List all users (paginated)
- `POST /` - Create new user
- `GET /{id}/` - Get user details
- `PUT /{id}/` - Update user
- `DELETE /{id}/` - Delete user
- `POST /{id}/activate/` - Activate user
- `POST /{id}/deactivate/` - Deactivate user

#### API Keys (`api/v1/api-keys/`) [Admin Only]
- `GET /` - List all API keys
- `POST /` - Generate new API key (returns raw key once)
- `GET /{id}/` - Get key details
- `DELETE /{id}/` - Revoke API key

#### Sessions (`api/v1/sessions/`)
- `GET /status/` - Get current session status
- `POST /init/` - Initialize WhatsApp session
- `POST /disconnect/` - Disconnect session
- **Note:** Currently placeholders, needs Node.js integration

#### Messages (`api/v1/messages/`)
- `POST /send-text/` - Send text message
- `POST /send-media/` - Send media message
- `GET /list/` - List user's messages
- **Note:** Currently placeholders, needs Node.js integration

#### Analytics (`api/v1/analytics/`) [Admin Only]
- `GET /usage-stats/` - Get usage statistics (filterable)
- `GET /api-logs/` - Get API request logs (filterable)

---

## 🔐 Authentication Flow

### Admin Authentication (JWT)
```
1. POST /api/v1/auth/login/ with username/password
2. Receive access_token and refresh_token
3. Use access_token in header: Authorization: Bearer <token>
4. Refresh when expired: POST /api/v1/auth/refresh/
5. Logout: POST /api/v1/auth/logout/ (blacklists token)
```

### User Authentication (API Key)
```
1. Admin generates API key for user
2. Raw key shown once, must be saved
3. User includes in header: Authorization: ApiKey <key>
4. Key is validated and hashed on each request
5. last_used_at timestamp is updated
```

---

## 📊 Database Schema

### User
```
id, username, email, password, first_name, last_name,
is_staff, is_active, max_messages_per_day,
created_at, updated_at
```

### APIKey
```
id, user_id, name, key (hashed), is_active,
last_used_at, created_at
```

### WhatsAppSession
```
id, user_id (OneToOne), session_id, status, qr_code,
phone_number, connected_at, last_active_at,
created_at, updated_at
```

### Message
```
id, user_id, recipient, message_type, content,
status, error_message, sent_at
```

### UsageStats
```
id, user_id, date, messages_sent, api_requests,
media_sent
(unique: user_id, date)
```

### APILog
```
id, user_id, endpoint, method, status_code,
ip_address, timestamp
```

---

## 🎨 Code Organization Principles

### Models
- One model per file in `*/models.py`
- Include `__str__` method
- Add Meta class with db_table, ordering
- Use indexes for frequently queried fields

### Admin
- Custom admin classes in `*/admin.py`
- Add custom actions (activate, deactivate, etc.)
- Use readonly_fields for timestamps
- Add search_fields and list_filter

### Serializers
- Located in `api/v1/*/serializers.py`
- Separate serializers for read/write when needed
- Use validators from `core/validators.py`
- Include only necessary fields

### Views
- Class-based views (APIView, ViewSet)
- Use `APIResponse` from `core/responses.py`
- Apply permission classes
- Handle exceptions gracefully

### URLs
- Modular URL patterns
- Use DRF routers for ViewSets
- Version API endpoints (v1, v2, etc.)
- Clear, RESTful naming

---

## 🧪 Testing Strategy (Phase 9)

### Unit Tests
- Test models in `tests/test_models.py`
- Test serializers in `tests/test_serializers.py`
- Test views in `tests/test_views.py`
- Target: >80% coverage

### Integration Tests
- Test complete flows
- Test authentication
- Test API endpoints
- Test error scenarios

---

## 🚀 Deployment Architecture

```
┌─────────────┐
│   Nginx     │ (Reverse Proxy, SSL)
└──────┬──────┘
       │
┌──────▼──────────────────────┐
│   Django App (Gunicorn)     │
│   - REST API                │
│   - Admin Panel             │
└──────┬─────────┬────────────┘
       │         │
┌──────▼───┐ ┌──▼─────────┐
│PostgreSQL│ │   Redis    │
│          │ │ - Cache    │
│          │ │ - Sessions │
└──────────┘ └────┬───────┘
                  │
       ┌──────────▼────────┐
       │  Celery Workers   │
       │  - Background     │
       │  - Scheduled      │
       └───────────────────┘

┌──────────────────────────┐
│  Node.js Service         │
│  - WhatsApp Web.js       │
│  - QR Code Generation    │
│  - Message Sending       │
└──────────────────────────┘
```

---

## 📈 Statistics

- **Total Files:** 85+
- **Python Files:** 65+
- **Documentation Files:** 10+
- **Configuration Files:** 10+
- **Models:** 6
- **API Endpoints:** 25+
- **Admin Interfaces:** 6
- **Lines of Code:** ~3,000+
- **Dependencies:** 15+

---

## ✅ Quality Checklist

- [x] Follows Django best practices
- [x] PEP 8 compliant
- [x] RESTful API design
- [x] Secure authentication
- [x] Comprehensive documentation
- [x] Error handling
- [x] Logging configured
- [x] Admin interface customized
- [x] API documentation (Swagger/ReDoc)
- [x] Environment-based configuration
- [ ] Unit tests (Phase 9)
- [ ] Integration tests (Phase 9)
- [ ] Performance optimization (Phase 11)
- [ ] Security audit (Phase 11)

---

**This structure is production-ready for Phase 1 & 2. Phase 3 (WhatsApp) will add Node.js service integration.**

