# Redis Optional Setup - Fixed!

## The Problem

You were getting:
```
Error: Failed to send message: Error 10061 connecting to localhost:6379. 
No connection could be made because the target machine actively refused it.
```

This happens because the app was trying to connect to Redis, but Redis wasn't running.

## The Solution ✅

I've made Redis **optional** for development. You can now run the app without Redis!

### Quick Fix (Apply Now)

1. **Create `.env` file** (if you don't have one):
   ```bash
   # Copy the template
   copy env.template .env
   ```

2. **Add this line** to your `.env` file:
   ```
   USE_REDIS=false
   ```

3. **Restart Django server**:
   ```bash
   python manage.py runserver
   ```

4. **Test the message sending** - It should work now!

## What Changed?

### Before (Required Redis):
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',  # ❌ Needs Redis
        ...
    }
}
```

### After (Redis Optional):
```python
USE_REDIS = config('USE_REDIS', default='true', cast=bool)

if USE_REDIS:
    # Use Redis if available
    CACHES = {'default': {'BACKEND': 'django_redis.cache.RedisCache', ...}}
else:
    # Use local memory cache (no Redis needed) ✅
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', ...}}
```

## Two Modes

### Development Mode (No Redis Required)
```env
# .env file
USE_REDIS=false
```

**Features:**
- ✅ Send messages
- ✅ Manage sessions  
- ✅ All API endpoints work
- ✅ Dashboard works
- ⚠️ No Celery background tasks
- ⚠️ Cache is in-memory (lost on restart)

**Perfect for:**
- Local development
- Testing
- Quick prototyping

### Production Mode (With Redis)
```env
# .env file
USE_REDIS=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

**Features:**
- ✅ All development features
- ✅ Celery background tasks
- ✅ Persistent cache across restarts
- ✅ Better performance
- ✅ Usage analytics aggregation

**Perfect for:**
- Production deployment
- Multiple servers
- High traffic

## Complete .env Example

```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=whatsapp_saas
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis (IMPORTANT: Set to false if you don't have Redis installed)
USE_REDIS=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Node.js Service
NODE_SERVICE_URL=http://localhost:3000
NODE_SERVICE_API_KEY=change-this-secret-key

# Django Base URL
DJANGO_BASE_URL=http://localhost:8000

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Celery (not used when USE_REDIS=false)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Rate Limiting
MAX_MESSAGES_PER_MINUTE=10
MAX_MESSAGES_PER_DAY=1000
```

## Testing Steps

After setting `USE_REDIS=false`:

1. **Restart Django**:
   ```bash
   python manage.py runserver
   ```

2. **Check Service Status**:
   - Go to: http://localhost:8000/dashboard/service-status/
   - Verify Node.js service is running

3. **Send Test Message**:
   - Go to: http://localhost:8000/dashboard/test-sample/
   - Select your session
   - Enter a phone number
   - Send test message
   - Should work without Redis error ✅

## Installing Redis (Optional)

If you want to enable Redis later for production:

### Windows
```powershell
# Using Chocolatey
choco install redis-64

# Or download from:
# https://github.com/microsoftarchive/redis/releases
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### macOS
```bash
brew install redis
brew services start redis
```

### Docker
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

Then set in `.env`:
```env
USE_REDIS=true
```

## Troubleshooting

### Still getting Redis error?
1. Check if `.env` file exists in project root
2. Verify `USE_REDIS=false` is set
3. Restart Django server completely (Ctrl+C and restart)
4. Clear any environment variables that might override

### Want to verify the setting?
```bash
python manage.py shell
>>> from django.conf import settings
>>> settings.USE_REDIS
False  # Should be False
>>> settings.CACHES
{'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', ...}}
```

### Cache not working?
- In development without Redis, cache is in-memory
- Lost when server restarts (this is normal)
- For persistent cache, use Redis

## What About Celery?

When `USE_REDIS=false`, Celery tasks won't run automatically. This is fine for development.

**Tasks that won't run:**
- Daily usage aggregation
- Cleanup tasks
- Health checks

**This is OK for development** because:
- Manual testing doesn't need these
- Cleanup can be done manually if needed
- Primary features (sending messages) work fine

If you need Celery in development:
1. Install and start Redis
2. Set `USE_REDIS=true`
3. Start Celery worker:
   ```bash
   celery -A config worker -l info
   ```

## Summary

✅ **Problem Fixed**: Redis is now optional  
✅ **Quick Solution**: Add `USE_REDIS=false` to `.env`  
✅ **Message Sending**: Works without Redis  
✅ **All Features**: Available except background tasks  
✅ **Production Ready**: Enable Redis when you deploy  

Your app now works in **development without Redis**!

