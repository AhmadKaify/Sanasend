# QUICK FIX: "Failed to send message"

## Problem
Getting `{"success": false, "message": "Failed to send message"}` in test sample page.

## Root Cause
**You're using the HASHED API key instead of the RAW key.**

## Solution (3 Minutes)

### 1. Generate New API Key
```
1. Open: http://localhost:8000/dashboard/api-keys/
2. Click "Generate New Key"
3. Name it: "Test"
4. Click "Generate"
5. A MODAL WILL POP UP with your key
6. Click the "Copy" button in the modal
7. Paste it in Notepad temporarily
```

The key looks like:
```
wsk_1728153600_Wm5kZGlyZnJvbXNlY3JldHVybHNhZmU...
```

### 2. Test Message
```
1. Open: http://localhost:8000/dashboard/test-sample/
2. API Key: Paste the key from step 1
3. Recipient: +9647709910444 (or your number with + and country code)
4. Message: Test message
5. Click "Send Message"
```

## Expected Result
```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "messageId": "...",
    "timestamp": "...",
    "dbId": 123
  }
}
```

## Still Failing?

### Check 1: Both Services Running?
```powershell
# Django (should show: port 8000)
Get-Process python -ErrorAction SilentlyContinue

# Node.js (should show process)
Get-Process node -ErrorAction SilentlyContinue
```

If not running:
```powershell
# Terminal 1:
cd "C:\Users\Ahmad K\Downloads\sanasr"
.\venv\Scripts\activate
python manage.py runserver

# Terminal 2:
cd "C:\Users\Ahmad K\Downloads\sanasr\whatsapp-service"
node src/server.js
```

### Check 2: Session Connected?
Go to: http://localhost:8000/dashboard/sessions/

Should show "Connected" (green status). If not, click "Refresh QR" and scan again.

### Check 3: API Key Format?
Your API key MUST:
- Start with `wsk_`
- Be about 50-60 characters long
- Come from the modal after generation

If your key looks like `abc123...` (short, no wsk_), that's the HASHED version - won't work.

## The Issue Explained

When you generate an API key:
1. **Raw key** (wsk_...) is generated → Shown ONCE in modal
2. **Hashed version** (abc123...) is stored in database → Shown in list
3. Only the **raw key** works for authentication
4. The list page shows hashed keys (for security)

**You need the raw key from the generation modal!**

## System Status (Verified)
- ✅ Node.js Service: RUNNING
- ✅ WhatsApp Session: CONNECTED  
- ✅ Phone: 9647709910444
- ✅ Session: "new one"
- ✅ Status: Ready to send

The system works - just need the correct API key!

