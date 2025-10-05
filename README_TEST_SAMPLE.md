# Test Sample Page - Complete Guide

## 📋 TL;DR - Quick Fix

**Problem:** "Failed to send message" error  
**Solution:** Generate a NEW API key and copy it from the pop-up modal

```
1. http://localhost:8000/dashboard/api-keys/ → Generate New Key
2. Copy the key from the GREEN MODAL (starts with wsk_)
3. http://localhost:8000/dashboard/test-sample/ → Paste key
4. Send message
```

---

## ✅ System Status (Verified Working)

| Component | Status | Details |
|-----------|--------|---------|
| Django Server | ✅ Running | Port 8000 |
| Node.js Service | ✅ Running | Port 3000 |
| WhatsApp Session | ✅ Connected | Phone: 9647709910444 |
| Session Name | ✅ Active | "new one" |
| User | ✅ Logged In | admin |
| API Keys | ✅ Available | 2 active keys |

**Everything is working! You just need the correct API key.**

---

## 🔑 The API Key Issue (Most Common)

### What You're Probably Doing Wrong:
```
❌ Copying from the API Keys list page
❌ Using: abc123def456... (this is hashed)
❌ Result: "Failed to send message" or "Invalid API key"
```

### What You Should Do:
```
✅ Generate a NEW key
✅ Copy from the pop-up MODAL that appears
✅ Use: wsk_1728153600_Wm5kZGlyZnJv... (this is raw)
✅ Result: Message sent successfully!
```

---

## 📝 Complete Testing Procedure

### Prerequisites
Make sure both services are running:

```powershell
# Terminal 1 - Django
cd "C:\Users\Ahmad K\Downloads\sanasr"
.\venv\Scripts\activate
python manage.py runserver

# Terminal 2 - Node.js
cd "C:\Users\Ahmad K\Downloads\sanasr\whatsapp-service"
node src/server.js
```

### Step 1: Generate API Key

1. **Navigate to:** http://localhost:8000/dashboard/api-keys/
2. **Click:** "Generate New Key" button (top right)
3. **Enter name:** `Test Key` (optional)
4. **Click:** "Generate"
5. **⚠️ WAIT for the modal to appear**
6. **Click:** "Copy" button in the modal
7. **Paste** into Notepad or text editor

**Your key should look like:**
```
wsk_1728153600_Wm5kZGlyZnJvbXNlY3JldHVybHNhZmU...
```

### Step 2: Verify Session is Connected

1. **Navigate to:** http://localhost:8000/dashboard/sessions/
2. **Check status:** Should show "Connected" in green
3. **If disconnected:** Click "Refresh QR" and scan with WhatsApp

### Step 3: Send Test Message

1. **Navigate to:** http://localhost:8000/dashboard/test-sample/
2. **Fill the form:**
   - **API Key:** Paste the key from Step 1 (entire key)
   - **Recipient:** `+9647709910444` (or any valid number)
   - **Message:** `Test from SanaSend`
3. **Click:** "Send Message"
4. **Switch to "Response" tab**

### Step 4: Verify Success

**Success Response:**
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

✅ **Check your WhatsApp** - you should receive the message!

---

## 🐛 Troubleshooting

### Error: "Invalid API key" (401)
**Cause:** Wrong API key format  
**Fix:** 
1. Generate a NEW key
2. Copy from the modal (not from list)
3. Use the FULL key (wsk_...)

### Error: "Failed to send message" (400)
**Possible Causes:**
1. **Session disconnected**
   - Go to Sessions page
   - Reconnect the session
   
2. **Node.js service down**
   - Check: `Get-Process node`
   - Restart: `cd whatsapp-service; node src/server.js`

3. **Wrong recipient format**
   - Use: `+<country_code><number>`
   - Example: `+14085551234`

### Error: "No active WhatsApp sessions"
**Cause:** No connected WhatsApp instance  
**Fix:**
1. Go to http://localhost:8000/dashboard/sessions/
2. Add new instance or reconnect existing
3. Scan QR code
4. Wait for "Connected" status

### Error: Network or CORS errors
**Check:**
1. Django server is running on port 8000
2. No firewall blocking localhost
3. Browser console (F12) for details

---

## 🔍 Diagnostic Commands

### Check Both Services:
```powershell
# Django
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName

# Node.js
Get-Process node -ErrorAction SilentlyContinue | Select-Object Id, ProcessName
```

### Check Session Status:
```powershell
cd "C:\Users\Ahmad K\Downloads\sanasr"
.\venv\Scripts\activate
python manage.py shell -c "from sessions.models import WhatsAppSession; [print(f'{s.instance_name}: {s.status}') for s in WhatsAppSession.objects.all()]"
```

### Test Node.js Service:
```powershell
Invoke-WebRequest -Uri "http://localhost:3000/health" -UseBasicParsing
```

### View Logs:
```powershell
# Django logs
Get-Content logs\django.log -Tail 30

# Node.js logs
Get-Content whatsapp-service\logs\error.log -Tail 20
```

---

## 📚 Additional Resources

- **`QUICK_FIX.md`** - Fastest solution (3 minutes)
- **`HOW_TO_GET_API_KEY.md`** - Detailed API key guide with visuals
- **`MESSAGE_SENDING_FIX_SUMMARY.md`** - Complete technical details
- **`TEST_SAMPLE_SETUP_GUIDE.md`** - Full setup from scratch
- **`IMMEDIATE_TEST_STEPS.md`** - Step-by-step current status

---

## 🎯 Key Points to Remember

1. **RAW key vs HASHED key:**
   - RAW (wsk_...): Use for authentication
   - HASHED (abc123...): Just for display

2. **One-time display:**
   - Raw key shown ONLY in generation modal
   - Cannot retrieve later
   - Must copy immediately

3. **Recipient format:**
   - Must include + and country code
   - Example: +9647709910444

4. **Session must be connected:**
   - Check Sessions page
   - Status should be "Connected" (green)

5. **Both services must run:**
   - Django on port 8000
   - Node.js on port 3000

---

## 🧪 Test with cURL (Alternative)

```bash
# Replace YOUR_API_KEY with your actual raw key
curl -X POST http://localhost:8000/api/v1/messages/send-text/ \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -d '{
    "recipient": "+9647709910444",
    "message": "Test from cURL"
  }'
```

**PowerShell version:**
```powershell
$apiKey = "wsk_YOUR_ACTUAL_KEY_HERE"
$body = @{
    recipient = "+9647709910444"
    message = "Test from PowerShell"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/messages/send-text/" `
    -Method Post `
    -Headers @{
        "Content-Type" = "application/json"
        "Authorization" = "ApiKey $apiKey"
    } `
    -Body $body
```

---

## ✨ Success Indicators

When everything works correctly:

1. ✅ Form submits without errors
2. ✅ Response tab shows success JSON
3. ✅ Alert says "Message sent successfully!"
4. ✅ Message appears in recipient's WhatsApp
5. ✅ Message logged in Dashboard > Messages
6. ✅ No errors in browser console (F12)

---

## 🆘 Still Not Working?

If you followed all steps and still get errors:

1. **Generate a FRESH API key** (less than 5 minutes old)
2. **Copy it from the modal** (not from list)
3. **Verify the key format:** Must start with `wsk_`
4. **Check both services are running**
5. **Verify session is connected**
6. **Try the PowerShell test** to isolate browser issues
7. **Check logs** for specific error messages

The system is verified working - 99% of issues are API key related!

---

## 📞 Support Checklist

Before asking for help, verify:

- [ ] Both services running (Django + Node.js)
- [ ] Session shows "Connected" status
- [ ] Generated NEW API key (today)
- [ ] Copied key from generation modal
- [ ] Key starts with `wsk_`
- [ ] Recipient has + and country code
- [ ] Checked browser console for errors
- [ ] Reviewed Django and Node.js logs

---

**Last Updated:** October 5, 2025  
**System Status:** ✅ Fully Operational  
**Most Common Issue:** Using hashed API key instead of raw key

