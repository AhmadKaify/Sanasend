# Session Persistence & Synchronization Fixes

## Overview
Fixed all critical problems with WhatsApp session storage, persistence, and synchronization between Django and Node.js services.

## Problems Fixed

### 1. ❌ Session State Not Persistent (FIXED ✅)
**Problem**: Sessions stored only in Node.js memory, lost on restart
**Solution**: Implemented automatic session restoration on Node.js startup

### 2. ❌ Database/Node.js Sync Issues (FIXED ✅)
**Problem**: Django DB showed "connected" but Node.js had no active client
**Solution**: 
- Added periodic health checks (every 5 minutes)
- Auto-update database when mismatches detected
- Webhook notifications for status changes

### 3. ❌ No Session Restoration (FIXED ✅)
**Problem**: Manual reconnection required after Node.js restart
**Solution**: Auto-restore all connected sessions from Django DB on startup

### 4. ❌ Error Handling (FIXED ✅)
**Problem**: Generic errors, no session state validation
**Solution**:
- Check actual client state before operations
- Better error messages with reconnection guidance
- Auto-update status on errors

## Implementation Details

### Django Side (Python)

#### 1. New API Endpoint for Session Restoration
**File**: `api/v1/sessions/views.py`
```python
class ActiveSessionsForRestorationView(views.APIView):
    """Get all connected sessions for Node.js restoration"""
```
- Endpoint: `GET /api/v1/sessions/active-sessions/`
- Returns all sessions marked as "connected" in database
- Called by Node.js on startup

#### 2. Enhanced Session Pool
**File**: `sessions/session_pool.py`
- Auto-detect disconnected sessions during message sending
- Update database status when errors indicate disconnection
- Keywords detected: "not found", "reconnect", "closed", "not connected"

#### 3. Celery Tasks Already Configured
**File**: `config/settings/base.py`
- `cleanup-expired-qr-codes`: Every 1 minute
- `sync-session-status`: Every 5 minutes (syncs with Node.js)
- `cleanup-disconnected-sessions`: Daily

### Node.js Side (JavaScript)

#### 1. Session Restoration on Startup
**File**: `whatsapp-service/src/whatsappManager.js`
```javascript
async restoreSessions() {
  // Fetch connected sessions from Django
  // Re-initialize each session with LocalAuth
  // Notify Django of failures via webhook
}
```

#### 2. Improved Error Handling
**File**: `whatsapp-service/src/whatsappManager.js`
- Check `client.getState()` before sending messages
- Detect "Session closed" and "Protocol error" errors
- Auto-update internal status to "disconnected"
- Clear error messages: "Client session closed. Please reconnect the session."

#### 3. Periodic Health Checks
**File**: `whatsapp-service/src/server.js`
```javascript
setInterval(async () => {
  // Check all active sessions
  // Detect disconnected/failed sessions
  // Notify Django via webhook
}, 5 * 60 * 1000); // Every 5 minutes
```

#### 4. Server Startup Restoration
**File**: `whatsapp-service/src/server.js`
```javascript
app.listen(PORT, async () => {
  // Wait 5 seconds for Django to be ready
  // Call restoreSessions()
  // Log restoration results
});
```

#### 5. Auto-configured Webhook URL
**File**: `whatsapp-service/src/config.js`
```javascript
webhookUrl: process.env.WEBHOOK_URL || 
  `${process.env.DJANGO_API_URL}/api/v1/sessions/webhook/`
```

### Webhook Handler
**File**: `api/v1/sessions/webhooks.py`
- Endpoint: `POST /api/v1/sessions/webhook/`
- Receives status updates from Node.js
- Updates session status, phone number, timestamps
- Already implemented, now actively used

## How It Works

### On Node.js Startup:
1. Server starts and waits 5 seconds
2. Calls Django: `GET /api/v1/sessions/active-sessions/`
3. For each connected session:
   - Creates WhatsApp client with LocalAuth
   - If auth exists → reconnects automatically
   - If auth missing → marks as disconnected
4. Logs restoration results

### During Message Sending:
1. Check if client exists in Node.js memory
2. Verify actual client state with `getState()`
3. If disconnected:
   - Return clear error message
   - Update internal status
4. If session not found:
   - Django detects error keywords
   - Updates database status to "disconnected"

### Periodic Health Checks:
1. **Node.js side** (every 5 minutes):
   - Check all active sessions
   - Detect disconnections
   - Notify Django via webhook

2. **Django side** (every 5 minutes):
   - Celery task `sync_session_status`
   - Query Node.js for each "connected" session
   - Update database if mismatch found

### On Status Changes:
1. Node.js event handlers detect:
   - QR code generated
   - Connected
   - Authenticated
   - Auth failed
   - Disconnected
2. Send webhook to Django immediately
3. Django updates database

## Benefits

✅ **No More Manual Reconnection**: Sessions auto-restore on Node.js restart
✅ **Always in Sync**: Database and Node.js stay synchronized
✅ **Clear Error Messages**: Users know exactly what to do
✅ **Automatic Recovery**: Detects and fixes sync issues automatically
✅ **Production Ready**: Handles restarts, crashes, and network issues

## Configuration Required

### Environment Variables
```bash
# Django (.env)
NODE_SERVICE_URL=http://localhost:3000
NODE_SERVICE_API_KEY=your-secret-key

# Node.js (.env)
DJANGO_API_URL=http://localhost:8000
API_KEY=your-secret-key  # Must match Django
WEBHOOK_URL=http://localhost:8000/api/v1/sessions/webhook/  # Optional, auto-configured
```

## Testing the Fixes

### 1. Test Session Restoration
```bash
# In terminal 1: Start Django
python manage.py runserver

# In terminal 2: Create and connect a session via dashboard
# Scan QR code with WhatsApp

# In terminal 3: Restart Node.js
cd whatsapp-service
npm start

# Check logs: Should see "Restoring session..." and "Session restored"
# Test sending: Message should work without reconnection
```

### 2. Test Error Handling
```bash
# Kill Node.js service
# Try sending message from test page
# Error message should be: "Client not found. Please reconnect the session."
# Database status should auto-update to "disconnected"
```

### 3. Test Health Checks
```bash
# Start both services
# Wait 5 minutes
# Check logs for "Running health check and status sync..."
```

## Migration Notes

### For Existing Installations:
1. Pull latest code
2. Restart Django: `python manage.py runserver`
3. Restart Node.js: `cd whatsapp-service && npm start`
4. Restart Celery Beat: `celery -A config beat -l info`
5. Restart Celery Worker: `celery -A config worker -l info`

### No Database Changes Required:
- All existing sessions will work
- Disconnected sessions will be detected and marked
- Users may need to reconnect if Node.js lost their session

## Files Changed

### Django:
- `api/v1/sessions/views.py` - Added ActiveSessionsForRestorationView
- `api/v1/sessions/urls.py` - Added active-sessions endpoint
- `sessions/session_pool.py` - Enhanced error detection
- `sessions/tasks.py` - Already had sync tasks (verified)

### Node.js:
- `whatsapp-service/src/whatsappManager.js` - Added restoration, improved validation
- `whatsapp-service/src/server.js` - Added startup restoration and health checks
- `whatsapp-service/src/config.js` - Auto-configure webhook URL

## Monitoring

### Key Log Messages:
- **Node.js startup**: "Session restoration complete: X restored, Y failed"
- **Health check**: "Health check complete. Checked X sessions."
- **Django sync**: "Session sync complete: X checked, Y updated"
- **Disconnection**: "Session X appears disconnected, updating status"

### Dashboard Indicators:
- Session status badge shows accurate state
- "Reconnect" button appears for disconnected sessions
- Clear error messages in test message page

## Future Enhancements (Optional)

1. **Redis for Session State**: Store session status in Redis for faster access
2. **WebSocket Updates**: Real-time status updates without polling
3. **Session Metrics**: Track session uptime, message throughput
4. **Auto-reconnect UI**: Automatically refresh QR when detected disconnected

---

**Status**: ✅ All Critical Problems Fixed
**Production Ready**: Yes
**Requires Manual Migration**: No
**Breaking Changes**: None

