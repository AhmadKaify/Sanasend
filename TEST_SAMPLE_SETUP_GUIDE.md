# Test Sample Setup Guide

## Issue Resolution: "Failed to send message"

### Problem Identified
The message sending was failing due to:
1. Node.js WhatsApp service not running
2. WhatsApp sessions not properly connected
3. API authentication issues

---

## Complete Setup Instructions

### 1. Start the Node.js WhatsApp Service

**Windows (PowerShell):**
```powershell
cd whatsapp-service
node src/server.js
```

**Linux/Mac:**
```bash
cd whatsapp-service
npm start
```

**Verify it's running:**
```powershell
# PowerShell
Test-NetConnection localhost -Port 3000

# Or open browser to:
http://localhost:3000/health
```

### 2. Start Django Development Server

**Windows (PowerShell):**
```powershell
cd "C:\Users\Ahmad K\Downloads\sanasr"
.\venv\Scripts\activate
python manage.py runserver
```

**Linux/Mac:**
```bash
cd /path/to/sanasr
source venv/bin/activate
python manage.py runserver
```

### 3. Set Up WhatsApp Session

1. **Login to Dashboard:**
   - Navigate to: http://localhost:8000/dashboard/login
   - Login with your credentials

2. **Create/Connect WhatsApp Instance:**
   - Go to: http://localhost:8000/dashboard/sessions/
   - Click "Add New Instance" if you don't have one
   - Scan the QR code with WhatsApp mobile app
   - Wait for status to change to "Connected"

3. **Verify Connection:**
   - Check that session status shows "Connected" (green)
   - Note the instance name

### 4. Generate API Key

1. **Go to API Keys page:**
   - Navigate to: http://localhost:8000/dashboard/api-keys/
   
2. **Generate New Key:**
   - Click "Generate New API Key"
   - Give it a name (e.g., "Test Key")
   - **IMPORTANT:** Copy the raw API key immediately (it won't be shown again)
   - Format: `wsk_<timestamp>_<random>`

### 5. Use Test Sample Page

1. **Navigate to Test Page:**
   - Go to: http://localhost:8000/dashboard/test-sample/

2. **Fill in the Form:**
   - **API Key:** Paste your raw API key (from step 4)
   - **Recipient:** Enter phone number with country code (e.g., `+14085551234`)
     - Or WhatsApp chat ID for groups (e.g., `1234567890@g.us`)
   - **Message:** Enter your test message

3. **Send Message:**
   - Click "Send Message"
   - Watch the Response tab for results

---

## Expected Responses

### ✅ Success (200 OK)
```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "messageId": "3EB0C1A1B2C3D4E5F6",
    "timestamp": "2025-10-05T12:34:56Z",
    "dbId": 123
  }
}
```

### ⚠️ Session Not Connected (400 Bad Request)
```json
{
  "success": false,
  "message": "No active WhatsApp sessions. Please connect at least one session.",
  "error_code": "SESSION_NOT_CONNECTED"
}
```

**Solution:** Go to Sessions page and connect a WhatsApp instance.

### 🔒 Invalid API Key (401 Unauthorized)
```json
{
  "success": false,
  "message": "Invalid API key",
  "error_code": "INVALID_API_KEY"
}
```

**Solution:** Generate a new API key and use the raw key shown after generation.

### ❌ Failed to Send (400 Bad Request)
```json
{
  "success": false,
  "message": "Failed to send message",
  "error": "Session not ready or closed"
}
```

**Solution:** Reconnect your WhatsApp session from the Sessions page.

---

## Troubleshooting

### Message Still Failing?

1. **Check Node.js Service Logs:**
```powershell
Get-Content whatsapp-service\logs\error.log -Tail 20
```

2. **Check Django Logs:**
```powershell
Get-Content logs\django.log -Tail 50
```

3. **Verify Session Status in Database:**
```powershell
.\venv\Scripts\activate
python manage.py shell
```
```python
from sessions.models import WhatsAppSession
sessions = WhatsAppSession.objects.all()
for s in sessions:
    print(f"{s.instance_name}: {s.status}")
```

4. **Reconnect Session:**
   - If session shows "connected" but messages fail
   - Go to Sessions page
   - Click "Refresh QR" on the session
   - Scan QR code again with WhatsApp

### Common Issues

**1. "Session closed" Error**
- **Cause:** WhatsApp browser session was closed
- **Fix:** Refresh QR and reconnect on Sessions page

**2. "Node service not responding"**
- **Cause:** Node.js service not running
- **Fix:** Start with `node src/server.js` in whatsapp-service directory

**3. "Invalid phone number format"**
- **Cause:** Missing country code
- **Fix:** Use international format: `+<country_code><number>`

**4. CORS Error**
- **Cause:** Accessing from different domain
- **Fix:** Check CORS_ALLOWED_ORIGINS in settings

---

## Testing Flow Summary

```
1. Start Node.js Service (port 3000)
   ↓
2. Start Django Server (port 8000)
   ↓
3. Login to Dashboard
   ↓
4. Connect WhatsApp Instance (scan QR)
   ↓
5. Generate API Key (copy raw key)
   ↓
6. Open Test Sample Page
   ↓
7. Enter: API Key + Recipient + Message
   ↓
8. Click "Send Message"
   ↓
9. Check Response Tab
```

---

## API Endpoint Details

**Endpoint:** `POST /api/v1/messages/send-text/`

**Headers:**
```
Content-Type: application/json
Authorization: ApiKey <your_raw_api_key>
```

**Body:**
```json
{
  "recipient": "+14085551234",
  "message": "Test message from SanaSend"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "messageId": "3EB0...",
    "timestamp": "2025-10-05T...",
    "dbId": 123
  }
}
```

---

## Quick Checklist

Before sending a test message, verify:

- [ ] Node.js WhatsApp service is running (port 3000)
- [ ] Django development server is running (port 8000)
- [ ] At least one WhatsApp session is "Connected"
- [ ] You have a valid API key (raw format: `wsk_...`)
- [ ] Recipient phone number includes country code
- [ ] Both services can communicate (check firewall)

---

## Support

If issues persist after following this guide:
1. Check both service logs (Django + Node.js)
2. Verify database session status
3. Try refreshing the WhatsApp session
4. Restart both services

The message sending flow involves:
- Django API → Message Service → Session Pool → WhatsApp Service (Node.js) → WhatsApp Web → Recipient

