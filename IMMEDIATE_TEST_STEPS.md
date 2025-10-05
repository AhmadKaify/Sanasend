# IMMEDIATE Steps to Test Message Sending

## Current Status ✅
- ✅ Node.js WhatsApp service: **RUNNING** (port 3000)
- ✅ WhatsApp session: **CONNECTED** (ready to send)
- ✅ Phone number: **9647709910444**
- ✅ Session name: **new one**

---

## Critical Steps to Fix "Failed to send message"

### Step 1: Get a Fresh API Key

The issue is likely you're using the **hashed key** instead of the **raw key**.

1. Go to: http://localhost:8000/dashboard/api-keys/
2. Click "Generate New API Key"
3. Enter name: "Test Key"
4. Click Generate
5. **CRITICAL:** Copy the ENTIRE key that appears in the green success message
   - Format should be: `wsk_1728153600_abc123xyz789...`
   - This is shown ONLY ONCE - copy it now!

### Step 2: Use Test Sample Page

1. Go to: http://localhost:8000/dashboard/test-sample/
2. Enter the API key you just copied (whole thing)
3. Enter recipient: `+9647709910444` (or any valid WhatsApp number)
4. Message: "Test from SanaSend"
5. Click "Send Message"

---

## If It Still Fails

### Check 1: API Key Format
Your API key should look like:
```
wsk_1728153600_abc123def456ghi789jkl012mno345pqr678stu901vwx234
```

NOT like:
```
a1b2c3d4e5f6... (this is hashed - won't work in test page)
```

### Check 2: Recipient Format
- ✅ Correct: `+9647709910444` (with +)
- ✅ Correct: `+14085551234`
- ❌ Wrong: `9647709910444` (missing +)
- ❌ Wrong: `07709910444` (missing country code)

### Check 3: Browser Console
Open browser Developer Tools (F12) and check Console tab for errors:
- CORS errors?
- Network errors?
- Authentication errors?

---

## Alternative: Test via Command Line

If the web form still fails, test directly:

```powershell
# Get an API key first from dashboard

$apiKey = "wsk_YOUR_ACTUAL_KEY_HERE"
$headers = @{
    'Content-Type' = 'application/json'
    'Authorization' = "ApiKey $apiKey"
}
$body = @{
    recipient = "+9647709910444"
    message = "Test message"
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/messages/send-text/' -Method Post -Headers $headers -Body $body
```

---

## Expected Success Response

```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "messageId": "3EB0C1A1B2...",
    "timestamp": "2025-10-05T...",
    "dbId": 123
  }
}
```

---

## Still Getting "Failed to send message"?

### Quick Diagnostic:

1. **Check if session is really connected:**
```powershell
cd "C:\Users\Ahmad K\Downloads\sanasr"
.\venv\Scripts\activate
python manage.py shell -c "from sessions.models import WhatsAppSession; s = WhatsAppSession.objects.first(); print(f'Status: {s.status}')"
```
Should show: `Status: connected`

2. **Check Django logs:**
```powershell
Get-Content logs\django.log -Tail 20
```
Look for error messages about:
- API key authentication
- Session not found
- WhatsApp service errors

3. **Check Node.js logs:**
```powershell
Get-Content whatsapp-service\logs\error.log -Tail 10
```

---

## Most Common Issue: API Key

**Problem:** You're entering the hashed key from the API Keys list page.

**Solution:** 
1. The raw key is ONLY shown once when you generate it
2. Generate a NEW key
3. Copy the key from the green success message
4. Use that exact key in the test form

**The key in the list view (showing `abc123...`) is hashed and cannot be used for testing.**

---

## Need to Generate a New Key?

Since keys are hashed after creation, if you lost your raw key:
1. Generate a new one
2. Copy it immediately
3. Save it somewhere safe
4. Use it in test form

You can have multiple API keys active at once.

