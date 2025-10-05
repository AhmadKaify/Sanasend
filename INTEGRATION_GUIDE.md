# Integration Guide - Django ← → Node.js

## Overview

This guide explains how the Django backend integrates with the Node.js WhatsApp service.

---

## Architecture

```
┌──────────────┐         HTTP/REST          ┌──────────────────┐
│   Django     │ <──────────────────────> │   Node.js        │
│   Backend    │                            │   WhatsApp       │
│              │                            │   Service        │
│  - User API  │                            │  - WhatsApp      │
│  - Sessions  │                            │    Web.js        │
│  - Messages  │                            │  - QR Codes      │
│  - Auth      │                            │  - Puppeteer     │
└──────┬───────┘                            └───────┬──────────┘
       │                                            │
       │                                            │
   ┌───▼────┐                                  ┌────▼────┐
   │PostGres│                                  │ Session │
   │Database│                                  │  Data   │
   └────────┘                                  └─────────┘
```

---

## Communication Flow

### 1. Session Initialization

```
User → Django API → Node.js Service → WhatsApp Web
                 ←  QR Code       ←

1. User calls POST /api/v1/sessions/init/
2. Django calls Node.js POST /api/session/init
3. Node.js creates WhatsApp client
4. Node.js generates QR code
5. Node.js returns QR code to Django
6. Django stores in database and returns to user
7. User scans QR with phone
8. Node.js detects authentication
9. Session becomes 'connected'
```

### 2. Sending Message

```
User → Django API → Node.js Service → WhatsApp Web → Recipient

1. User calls POST /api/v1/messages/send-text/
2. Django validates user has connected session
3. Django creates Message record (status='pending')
4. Django calls Node.js POST /api/message/send-text
5. Node.js sends via WhatsApp Web
6. Node.js returns message ID
7. Django updates Message record (status='sent')
8. Django returns success to user
```

---

## Installation Steps

### Step 1: Start Django Service

```bash
# Navigate to Django project
cd c:\Users\Ahmad K\Downloads\sanasr

# Activate virtual environment
.\venv\Scripts\activate

# Run migrations (if not done)
py manage.py migrate

# Start Django server
py manage.py runserver
```

### Step 2: Install Node.js Service

```bash
# Navigate to Node.js service
cd whatsapp-service

# Install dependencies
npm install

# Copy environment file
copy .env.example .env

# Edit .env file - SET API_KEY TO MATCH Django's NODE_SERVICE_API_KEY
```

### Step 3: Configure Environment

**Django (.env in root):**
```env
NODE_SERVICE_URL=http://localhost:3000
NODE_SERVICE_API_KEY=your-secret-api-key-here
DJANGO_BASE_URL=http://localhost:8000
```

**Node.js (whatsapp-service/.env):**
```env
PORT=3000
API_KEY=your-secret-api-key-here
DJANGO_API_URL=http://localhost:8000
```

⚠️ **IMPORTANT:** `API_KEY` in Node.js MUST match `NODE_SERVICE_API_KEY` in Django!

### Step 4: Start Node.js Service

```bash
cd whatsapp-service
npm start
```

### Step 5: Verify Connection

```bash
# Check Node.js health
curl http://localhost:3000/health

# Should return:
# {"success":true,"status":"healthy","uptime":...}
```

---

## API Integration Examples

### Initialize WhatsApp Session

```bash
# Step 1: Get API key (from admin panel)
# - Login to Django admin
# - Create API key for user
# - Copy the key (shown only once!)

# Step 2: Initialize session
curl -X POST http://localhost:8000/api/v1/sessions/init/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json"

# Response:
{
  "success": true,
  "data": {
    "sessionId": "user_1_session",
    "status": "qr_pending",
    "qrCode": "data:image/png;base64,...",
    "message": "Session initialized. Please scan the QR code with WhatsApp."
  }
}

# Step 3: Display QR code (in browser or app)
# - Copy the qrCode data URL
# - Display in <img src="...qrCode..." />
# - Scan with WhatsApp mobile app

# Step 4: Check status (poll every 2-3 seconds)
curl -X GET http://localhost:8000/api/v1/sessions/status/ \
  -H "Authorization: ApiKey YOUR_API_KEY"

# When connected:
{
  "success": true,
  "data": {
    "sessionId": "user_1_session",
    "status": "connected",
    "phoneNumber": "1234567890",
    "isReady": true
  }
}
```

### Send Text Message

```bash
curl -X POST http://localhost:8000/api/v1/messages/send-text/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "1234567890",
    "message": "Hello from WhatsApp API!"
  }'

# Response:
{
  "success": true,
  "data": {
    "messageId": "msg_123456",
    "timestamp": 1234567890,
    "dbId": 1,
    "message": "Message sent successfully"
  }
}
```

### Send Media Message

```bash
curl -X POST http://localhost:8000/api/v1/messages/send-media/ \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -F "recipient=1234567890" \
  -F "media_type=image" \
  -F "file=@/path/to/image.jpg" \
  -F "caption=Check this out!"

# Response:
{
  "success": true,
  "data": {
    "messageId": "msg_789012",
    "timestamp": 1234567890,
    "dbId": 2,
    "filePath": "whatsapp_media/1/image.jpg",
    "message": "Media sent successfully"
  }
}
```

---

## Error Handling

### Common Errors

#### 1. WhatsApp Service Unavailable
```json
{
  "success": false,
  "message": "WhatsApp service unavailable",
  "error_code": null
}
```
**Solution:** Check if Node.js service is running

#### 2. Session Not Connected
```json
{
  "success": false,
  "message": "No active WhatsApp session. Please connect first.",
  "error_code": "SESSION_NOT_CONNECTED"
}
```
**Solution:** Initialize session and scan QR code

#### 3. Invalid API Key
```json
{
  "success": false,
  "error": "Invalid API key"
}
```
**Solution:** Check API key configuration in both services

#### 4. Authentication Failed
**Symptoms:** Node.js logs show "auth_failure"
**Solutions:**
- Delete `.wwebjs_auth/` folder in whatsapp-service
- Reinitialize session
- Make sure WhatsApp Web is not connected elsewhere

---

## Database Synchronization

Django automatically syncs with Node.js service:

1. **Session Status Updates:**
   - When you call `/api/v1/sessions/status/`
   - Django queries Node.js for current status
   - Updates `WhatsAppSession` model in database

2. **Message Logging:**
   - Every sent message is logged in `Message` model
   - Status is tracked (pending → sent/failed)
   - Error messages are stored if sending fails

---

## Monitoring & Logging

### Django Logs
Located in: `logs/django.log`

Watch for:
- API request logs
- WhatsApp service connection errors
- Message sending errors

```bash
# Tail Django logs
tail -f logs/django.log
```

### Node.js Logs
Located in: `whatsapp-service/logs/`
- `combined.log` - All logs
- `error.log` - Errors only

```bash
# Tail Node.js logs
cd whatsapp-service
tail -f logs/combined.log
```

### Check Node.js Service Health
```bash
curl http://localhost:3000/health
```

### List Active Sessions
```bash
curl http://localhost:3000/api/session/list \
  -H "x-api-key: your-api-key"
```

---

## Troubleshooting

### Node.js Service Won't Start

1. **Check port availability:**
   ```bash
   # Windows
   netstat -ano | findstr :3000
   ```

2. **Install Chrome/Chromium:**
   ```bash
   # Required for Puppeteer
   ```

### QR Code Not Generated

1. **Check Node.js logs:**
   ```bash
   cd whatsapp-service
   npm start
   # Watch console output
   ```

2. **Increase timeout:**
   - Default is 30 seconds
   - May need longer on slow connections

### Session Disconnects Frequently

1. **Keep Node.js service running:**
   - Use PM2 for production: `pm2 start src/server.js`

2. **Check memory:**
   - Each session uses ~100-200MB
   - Monitor with `pm2 monit`

3. **Implement auto-reconnect:**
   - Already built into whatsapp-web.js

### Messages Not Sending

1. **Check session status:**
   ```bash
   curl http://localhost:8000/api/v1/sessions/status/ \
     -H "Authorization: ApiKey YOUR_KEY"
   ```

2. **Check database:**
   ```sql
   SELECT * FROM messages ORDER BY sent_at DESC LIMIT 10;
   ```

3. **Check Node.js is receiving requests:**
   - Watch Node.js console logs

---

## Production Deployment

### Docker Compose (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  django:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_SERVICE_URL=http://whatsapp-service:3000
      - NODE_SERVICE_API_KEY=${NODE_SERVICE_API_KEY}
    depends_on:
      - postgres
      - redis
  
  whatsapp-service:
    build: ./whatsapp-service
    ports:
      - "3000:3000"
    environment:
      - API_KEY=${NODE_SERVICE_API_KEY}
      - DJANGO_API_URL=http://django:8000
    volumes:
      - whatsapp-sessions:/app/.wwebjs_auth
  
  postgres:
    image: postgres:15
    ...
  
  redis:
    image: redis:7
    ...

volumes:
  whatsapp-sessions:
```

### Environment Variables

Production `.env`:
```env
# Django
NODE_SERVICE_URL=http://whatsapp-service:3000
NODE_SERVICE_API_KEY=strong-random-key-here
DJANGO_BASE_URL=https://yourdomain.com

# Node.js (in whatsapp-service/.env)
API_KEY=strong-random-key-here
DJANGO_API_URL=http://django:8000
PORT=3000
NODE_ENV=production
```

---

## Security Considerations

1. **API Key Protection:**
   - Use strong, random keys
   - Never commit to git
   - Rotate regularly

2. **Network Security:**
   - Run Node.js on internal network only
   - Don't expose port 3000 to public

3. **Session Data:**
   - Session files contain authentication
   - Protect `.wwebjs_auth/` directory
   - Use volume encryption in production

4. **Rate Limiting:**
   - Implement rate limiting (Phase 5)
   - Prevent abuse

---

## Performance Tips

1. **Max Concurrent Sessions:**
   - Default: 50
   - Each session: ~200MB RAM
   - Adjust based on server capacity

2. **Session Cleanup:**
   - Runs automatically every 30 minutes
   - Removes inactive sessions

3. **Database Optimization:**
   - Add indexes on frequently queried fields
   - Already done in models

4. **Media File Storage:**
   - Consider using S3/CDN for production
   - Clean up old media files regularly

---

## Testing the Integration

See `whatsapp-service/README.md` for detailed testing instructions.

Quick test:
```bash
# 1. Start both services
# 2. Initialize session
# 3. Scan QR code
# 4. Send test message
# 5. Check database for logged message
```

---

**Integration Status:** ✅ Complete & Ready for Testing

