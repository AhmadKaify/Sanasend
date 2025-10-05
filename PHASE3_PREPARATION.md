# Phase 3: WhatsApp Integration Preparation Guide

## Overview

Phase 3 involves creating a Node.js service that bridges Django with WhatsApp Web using the `whatsapp-web.js` library.

---

## Architecture Decision

### Option 1: HTTP REST Communication (Recommended)
**Django ← HTTP → Node.js**

**Pros:**
- Simple to implement
- Easy to debug
- Language agnostic
- Can scale separately

**Cons:**
- Slight latency overhead
- Need to handle timeouts

### Option 2: Redis Queue Communication
**Django → Redis → Node.js**

**Pros:**
- Asynchronous
- Better for high load
- Natural queue management

**Cons:**
- More complex
- Requires Redis pub/sub

### Option 3: Socket.io Communication
**Django ← WebSocket → Node.js**

**Pros:**
- Real-time bidirectional
- Good for live updates

**Cons:**
- More complex
- Requires socket library on Django side

**RECOMMENDATION:** Start with Option 1 (HTTP), migrate to Option 2 if needed.

---

## Node.js Service Requirements

### 1. Project Structure

```
nodejs-whatsapp-service/
├── src/
│   ├── server.js          # Express server
│   ├── whatsapp.js        # WhatsApp client management
│   ├── sessions.js        # Session management
│   ├── qrcode.js          # QR code generation
│   ├── messages.js        # Message sending
│   └── config.js          # Configuration
├── .env                    # Environment variables
├── package.json
├── .gitignore
└── README.md
```

### 2. Required npm Packages

```json
{
  "dependencies": {
    "whatsapp-web.js": "^1.23.0",
    "express": "^4.18.2",
    "qrcode": "^1.5.3",
    "dotenv": "^16.3.1",
    "axios": "^1.6.0",
    "redis": "^4.6.0",
    "winston": "^3.11.0"
  }
}
```

---

## Node.js Service Endpoints

### 1. Initialize Session
```
POST /api/session/init
Body: {
  "userId": 123,
  "sessionId": "user_123_session"
}
Response: {
  "success": true,
  "qrCode": "base64_qr_code_here",
  "status": "qr_pending"
}
```

### 2. Get Session Status
```
GET /api/session/status/:sessionId
Response: {
  "success": true,
  "status": "connected|disconnected|qr_pending",
  "phoneNumber": "+1234567890",
  "isReady": true
}
```

### 3. Disconnect Session
```
POST /api/session/disconnect
Body: {
  "sessionId": "user_123_session"
}
Response: {
  "success": true,
  "message": "Session disconnected"
}
```

### 4. Send Text Message
```
POST /api/message/send-text
Body: {
  "sessionId": "user_123_session",
  "recipient": "1234567890@c.us",
  "message": "Hello World"
}
Response: {
  "success": true,
  "messageId": "msg_123456",
  "status": "sent"
}
```

### 5. Send Media Message
```
POST /api/message/send-media
Body: {
  "sessionId": "user_123_session",
  "recipient": "1234567890@c.us",
  "mediaUrl": "http://django-server/media/file.jpg",
  "caption": "Check this out",
  "mediaType": "image"
}
Response: {
  "success": true,
  "messageId": "msg_123456",
  "status": "sent"
}
```

---

## Integration Steps

### Step 1: Create Node.js Project

```bash
mkdir nodejs-whatsapp-service
cd nodejs-whatsapp-service
npm init -y
npm install whatsapp-web.js express qrcode dotenv axios redis winston
```

### Step 2: Create Basic Express Server

```javascript
// src/server.js
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.listen(PORT, () => {
  console.log(`WhatsApp service running on port ${PORT}`);
});
```

### Step 3: Implement WhatsApp Client

```javascript
// src/whatsapp.js
const { Client, LocalAuth } = require('whatsapp-web.js');

class WhatsAppManager {
  constructor() {
    this.clients = new Map();
  }

  async createClient(sessionId) {
    const client = new Client({
      authStrategy: new LocalAuth({ clientId: sessionId }),
      puppeteer: {
        headless: true,
        args: ['--no-sandbox']
      }
    });
    
    this.clients.set(sessionId, client);
    return client;
  }

  getClient(sessionId) {
    return this.clients.get(sessionId);
  }

  async destroyClient(sessionId) {
    const client = this.clients.get(sessionId);
    if (client) {
      await client.destroy();
      this.clients.delete(sessionId);
    }
  }
}

module.exports = new WhatsAppManager();
```

### Step 4: Implement Session Endpoints

```javascript
// src/sessions.js
const whatsappManager = require('./whatsapp');
const QRCode = require('qrcode');

async function initSession(sessionId) {
  const client = await whatsappManager.createClient(sessionId);
  
  return new Promise((resolve, reject) => {
    client.on('qr', async (qr) => {
      const qrCode = await QRCode.toDataURL(qr);
      resolve({ status: 'qr_pending', qrCode });
    });

    client.on('ready', () => {
      console.log(`Client ${sessionId} is ready`);
    });

    client.on('authenticated', () => {
      console.log(`Client ${sessionId} authenticated`);
    });

    client.initialize();
  });
}

module.exports = { initSession };
```

### Step 5: Connect Django to Node.js

```python
# In Django - sessions/services.py
import requests
from django.conf import settings

class WhatsAppService:
    def __init__(self):
        self.base_url = settings.NODE_SERVICE_URL
    
    def init_session(self, user_id, session_id):
        response = requests.post(
            f'{self.base_url}/api/session/init',
            json={'userId': user_id, 'sessionId': session_id},
            timeout=30
        )
        return response.json()
    
    def get_session_status(self, session_id):
        response = requests.get(
            f'{self.base_url}/api/session/status/{session_id}',
            timeout=10
        )
        return response.json()
    
    def send_text_message(self, session_id, recipient, message):
        response = requests.post(
            f'{self.base_url}/api/message/send-text',
            json={
                'sessionId': session_id,
                'recipient': recipient,
                'message': message
            },
            timeout=30
        )
        return response.json()
```

### Step 6: Update Django Views

```python
# api/v1/sessions/views.py
from sessions.services import WhatsAppService

class InitSessionView(views.APIView):
    permission_classes = [IsActiveUser]
    
    def post(self, request):
        user = request.user
        session_id = f"user_{user.id}_session"
        
        # Call Node.js service
        whatsapp_service = WhatsAppService()
        result = whatsapp_service.init_session(user.id, session_id)
        
        # Update database
        session, created = WhatsAppSession.objects.get_or_create(
            user=user,
            defaults={'session_id': session_id}
        )
        session.status = 'qr_pending'
        session.qr_code = result.get('qrCode')
        session.save()
        
        return APIResponse.success(result)
```

---

## Session Persistence Strategy

### Option 1: File-based (LocalAuth)
- Store session data in files
- Simple but not scalable

### Option 2: Redis-based
- Store session data in Redis
- Scalable and fast

### Recommended: Hybrid
- Use LocalAuth initially
- Move to Redis when scaling

---

## Error Handling

### Django Side
```python
class WhatsAppService:
    def init_session(self, user_id, session_id):
        try:
            response = requests.post(...)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIException(f'WhatsApp service error: {str(e)}')
```

### Node.js Side
```javascript
app.post('/api/session/init', async (req, res) => {
  try {
    const result = await initSession(req.body.sessionId);
    res.json({ success: true, ...result });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});
```

---

## Testing Strategy

### 1. Test Node.js Service Standalone
```bash
curl -X POST http://localhost:3000/api/session/init \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "sessionId": "test_session"}'
```

### 2. Test Django → Node.js Communication
```bash
curl -X POST http://localhost:8000/api/v1/sessions/init/ \
  -H "Authorization: ApiKey YOUR_KEY" \
  -H "Content-Type: application/json"
```

### 3. Test Full Flow
1. Init session → Get QR
2. Scan QR with phone
3. Check status → Should be "connected"
4. Send test message

---

## Security Considerations

### 1. Authentication Between Services
- Add API key for Node.js ← Django communication
- Validate all requests

### 2. Session Isolation
- Each user has separate WhatsApp client
- No cross-user data leakage

### 3. File Storage
- Secure session files
- Regular cleanup of old sessions

---

## Performance Considerations

### 1. Client Lifecycle
- Keep clients alive but disconnected if inactive
- Destroy after X days of inactivity

### 2. Memory Management
- Monitor memory usage per client
- Set max concurrent sessions

### 3. Timeouts
- QR generation: 30s timeout
- Message sending: 10s timeout
- Session init: 60s timeout

---

## Deployment Considerations

### Development
- Node.js on localhost:3000
- Django on localhost:8000
- Both communicate via HTTP

### Production
- Node.js in separate container/server
- Use internal network
- Add load balancer if needed

---

## Next Steps Checklist

Phase 3.1: Node.js Setup
- [ ] Create Node.js project
- [ ] Install dependencies
- [ ] Create basic Express server
- [ ] Test server is running

Phase 3.2: WhatsApp Integration
- [ ] Implement WhatsApp client manager
- [ ] Add QR code generation
- [ ] Add session initialization
- [ ] Test QR code generation

Phase 3.3: Django Integration
- [ ] Create WhatsAppService class
- [ ] Update session views
- [ ] Test Django → Node.js communication
- [ ] Update session models

Phase 3.4: Testing
- [ ] Test session initialization
- [ ] Test QR code scanning
- [ ] Test session persistence
- [ ] Test reconnection

---

## Useful Resources

- **whatsapp-web.js Docs:** https://docs.wwebjs.dev/
- **Express.js Guide:** https://expressjs.com/
- **QR Code NPM:** https://www.npmjs.com/package/qrcode
- **Django Requests:** https://requests.readthedocs.io/

---

**Status:** 📋 Ready to Start
**Estimated Time:** 2-3 days
**Difficulty:** Medium
**Priority:** High (Blocking Phase 4)

