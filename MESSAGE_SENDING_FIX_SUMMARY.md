# Message Sending Fix - Complete Summary

## Status: ✅ SYSTEM IS WORKING

### Current State
- ✅ **Node.js WhatsApp Service:** Running on port 3000
- ✅ **Django Server:** Running on port 8000
- ✅ **WhatsApp Session:** Connected and ready (Phone: 9647709910444)
- ✅ **Session Name:** "new one"
- ✅ **Session Status:** Connected (isReady: true)
- ✅ **User:** admin
- ✅ **Active API Keys:** 2

## Root Cause of "Failed to send message"

### The Issue
You're likely using the **HASHED** API key instead of the **RAW** key.

**What you might be seeing in the API Keys list:**
```
abc123def456... (This is HASHED - won't work!)
```

**What you need (shown only once after generation):**
```
wsk_1728153600_abc123def456ghi789jkl012mno345pqr678stu901vwx234...
```

---

## SOLUTION: Step-by-Step

### Step 1: Generate a Fresh API Key

1. Go to: **http://localhost:8000/dashboard/api-keys/**
2. Click **"Generate New Key"**
3. Enter a name: `Test Key` (optional)
4. Click **"Generate"**
5. **A modal will pop up** with your new key
6. Click **"Copy"** button in the modal
7. Save it somewhere (Notepad, etc.) - **It won't be shown again!**

### Step 2: Test Message Sending

1. Go to: **http://localhost:8000/dashboard/test-sample/**
2. Fill in the form:
   - **API Key:** Paste the FULL key you just copied (starts with `wsk_`)
   - **Recipient:** `+9647709910444` (or any valid WhatsApp number with + and country code)
   - **Message:** `Test from SanaSend`
3. Click **"Send Message"**
4. Check the **"Response"** tab for results

### Expected Success Response:
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

---

## Common Errors & Solutions

### ❌ Error: "Invalid API key" (401)
**Cause:** Using hashed key or wrong format  
**Solution:** Generate a NEW key and copy from the modal that appears

### ❌ Error: "Failed to send message"
**Possible Causes:**
1. **Session disconnected** → Go to Sessions page and reconnect
2. **Wrong recipient format** → Use `+<country_code><number>`
3. **Node.js service down** → Restart: `cd whatsapp-service && node src/server.js`

### ❌ Error: "No active WhatsApp sessions"
**Cause:** No connected WhatsApp instance  
**Solution:** Go to http://localhost:8000/dashboard/sessions/ and connect an instance

---

## API Key Format Guide

### ✅ CORRECT Format (Raw Key):
```
wsk_1728153600_Wm5kZGlyZnJvbXNlY3JldHVybHNhZmU
```
- Starts with `wsk_`
- Contains timestamp
- Long random string
- About 50-60 characters total

### ❌ WRONG Format (Hashed - from list view):
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...
```
- This is what you see in the API Keys list
- This is stored in database (hashed)
- **Cannot be used for authentication**

---

## Testing Checklist

Before sending a test message:

- [ ] Both services running (Django on 8000, Node.js on 3000)
- [ ] At least one WhatsApp session shows "Connected" status
- [ ] Generated a FRESH API key within last 5 minutes
- [ ] Copied the key from the pop-up modal (not from the list)
- [ ] Using correct phone number format: `+<country_code><number>`
- [ ] Phone number has WhatsApp installed

---

## Alternative: Test via Command Line

If web form still fails, test directly with PowerShell:

```powershell
# 1. Generate API key from dashboard first, then:

$apiKey = "wsk_YOUR_ACTUAL_RAW_KEY_HERE"
$headers = @{
    'Content-Type' = 'application/json'
    'Authorization' = "ApiKey $apiKey"
}
$body = @{
    recipient = "+9647709910444"
    message = "Test message from PowerShell"
} | ConvertTo-Json

# 2. Send request
$response = Invoke-RestMethod `
    -Uri 'http://localhost:8000/api/v1/messages/send-text/' `
    -Method Post `
    -Headers $headers `
    -Body $body

# 3. Check response
$response | ConvertTo-Json -Depth 5
```

---

## Diagnostic Commands

### Check Session Status:
```powershell
cd "C:\Users\Ahmad K\Downloads\sanasr"
.\venv\Scripts\activate
python manage.py shell -c "from sessions.models import WhatsAppSession; [print(f'{s.instance_name}: {s.status}') for s in WhatsAppSession.objects.all()]"
```

### Check if Node.js Service is Running:
```powershell
Get-Process node -ErrorAction SilentlyContinue
```

### Check Node.js Service Health:
```powershell
Invoke-WebRequest -Uri "http://localhost:3000/health" -UseBasicParsing
```

### View Recent Django Errors:
```powershell
Get-Content logs\django.log -Tail 30
```

### View Node.js Errors:
```powershell
Get-Content whatsapp-service\logs\error.log -Tail 20
```

---

## Quick Start Both Services

### Windows (PowerShell):

**Terminal 1 - Django:**
```powershell
cd "C:\Users\Ahmad K\Downloads\sanasr"
.\venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 - Node.js:**
```powershell
cd "C:\Users\Ahmad K\Downloads\sanasr\whatsapp-service"
node src/server.js
```

---

## Architecture Flow

When you send a message from the test page:

```
Test Sample Page (Browser)
    ↓ POST /api/v1/messages/send-text/
Django API (API Key Auth)
    ↓ validates API key
Message Service
    ↓ finds connected session
Session Pool Service
    ↓ load balancing
WhatsApp Service (sessions/services.py)
    ↓ HTTP POST to Node.js
Node.js Service (port 3000)
    ↓ whatsapp-web.js
WhatsApp Web
    ↓ sends message
Recipient's WhatsApp
```

Any failure in this chain will result in "Failed to send message".

---

## Files Updated

1. `TEST_SAMPLE_SETUP_GUIDE.md` - Complete setup instructions
2. `IMMEDIATE_TEST_STEPS.md` - Quick fix steps
3. `MESSAGE_SENDING_FIX_SUMMARY.md` - This file

---

## Support

If you're still getting errors:
1. Check both service logs (Django + Node.js)
2. Verify API key format (must start with `wsk_`)
3. Confirm session is actually connected in both Django DB and Node.js
4. Test with command line to isolate browser issues
5. Check browser console (F12) for JavaScript errors

The system is ready and working - the issue is almost certainly with the API key format!

