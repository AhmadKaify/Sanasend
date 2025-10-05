# WhatsApp Session Persistence

## ✅ Sessions ARE Preserved During Restarts

Good news! Your WhatsApp sessions **do not require re-scanning QR codes** after a Node.js service restart.

## How It Works

### Authentication Storage
- WhatsApp authentication data is saved to disk in the `.wwebjs_auth/` directory
- Each session has its own folder with persistent authentication files
- These files contain encrypted credentials that survive restarts

### Restart Flow

```
Before Restart:
├── User A - Session 1 [Connected]
├── User B - Session 1 [Connected]  
└── User C - Session 1 [Connected]

During Restart (5-10 seconds):
├── All sessions temporarily disconnected
└── Service restarts

After Restart (Auto-recovery):
├── Service queries Django for active sessions
├── Loads authentication from disk
├── Reconnects to WhatsApp Web
└── All sessions back to [Connected]
```

## Timeline

| Time | What Happens |
|------|--------------|
| 0s | Service stops |
| 2s | Service starts |
| 5s | Session restoration begins |
| 10s | First sessions reconnect |
| 15s | All sessions should be back online |

## What Users Experience

### During Restart
- Brief "disconnected" status (5-10 seconds)
- Cannot send messages during this time
- Dashboard may show yellow warning

### After Restart
- Status automatically returns to "connected"
- No QR code needed
- No user action required
- Messages can be sent again

## When QR Code IS Needed

Sessions need to be re-authenticated (QR scan) only if:

1. **Auth files deleted/corrupted**
   - Manual deletion of `.wwebjs_auth/` directory
   - Disk corruption
   - Deployment that doesn't preserve files

2. **User logged out on phone**
   - User clicked "Log out from all computers" on WhatsApp mobile
   - User uninstalled WhatsApp

3. **Session expired**
   - Very long downtime (weeks/months)
   - WhatsApp security policy

4. **Database out of sync**
   - Django shows session as active but Node.js has no auth files
   - Solution: Reconnect via dashboard

## Service Management UI

### Active Sessions Display
The service status page shows:
- **User**: Who owns the session
- **Instance**: Session name
- **Status**: Current connection state
- **Phone**: WhatsApp number
- **Last Active**: Recent activity

### Restart Confirmation
When you click "Restart", you'll see:
```
Restart will briefly disconnect X active session(s).

They will auto-reconnect in 5-10 seconds.

Proceed with restart?
```

### After Restart
Check the logs section for restoration status:
```
✓ Session restored: user_1_instance_main
✓ Session restored: user_2_instance_personal
Session restoration complete: 2 restored, 0 failed
```

## Best Practices

### 1. Check Active Sessions Before Restart
- View the "Active Sessions" table on service status page
- See how many users will be affected
- Consider restarting during low-usage times

### 2. Monitor Restoration Logs
- After restart, check "Service Logs" section
- Verify all sessions restored successfully
- Look for ✓ or ✗ symbols

### 3. Notify Users (Optional)
- For planned restarts, you can inform users
- Brief 10-second disruption
- No action needed from them

### 4. Preserve Auth Files
- **Never delete** `.wwebjs_auth/` directory
- Include in backups
- Exclude from `.gitignore` or use persistent volumes in Docker

## Technical Details

### LocalAuth Strategy
```javascript
// Node.js uses LocalAuth from whatsapp-web.js
const client = new Client({
  authStrategy: new LocalAuth({ clientId: sessionId }),
  puppeteer: config.puppeteerOptions
});
```

This saves authentication to:
```
whatsapp-service/
└── .wwebjs_auth/
    └── session-{sessionId}/
        ├── Default/
        └── SingletonLock
```

### Restoration API
```javascript
// Automatic restoration on startup
async restoreSessions() {
  // Fetch active sessions from Django
  const sessions = await fetchActiveSessions();
  
  // Restore each one
  for (const session of sessions) {
    await createClient(session.session_id, session.user_id, true);
  }
}
```

### Django Integration
```python
# Django endpoint for active sessions
GET /api/v1/sessions/active-sessions/

Response:
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "user_1_instance_main",
        "user_id": 1,
        "instance_name": "Main",
        "status": "connected"
      }
    ]
  }
}
```

## Docker/Production Considerations

### Docker Volumes
```yaml
services:
  whatsapp-service:
    volumes:
      - ./whatsapp-service/.wwebjs_auth:/app/.wwebjs_auth
      - ./whatsapp-service/.wwebjs_cache:/app/.wwebjs_cache
```

### Kubernetes Persistent Volumes
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: whatsapp-auth-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### Backup Strategy
```bash
# Backup auth files regularly
tar -czf whatsapp-auth-backup-$(date +%Y%m%d).tar.gz \
  whatsapp-service/.wwebjs_auth/

# Restore if needed
tar -xzf whatsapp-auth-backup-20251005.tar.gz
```

## Troubleshooting

### Sessions Not Restoring
1. Check logs for errors:
   ```
   ✗ Failed to restore session user_1_instance_main: Auth file not found
   ```

2. Verify auth files exist:
   ```bash
   ls -la whatsapp-service/.wwebjs_auth/
   ```

3. Check Django API accessibility:
   ```bash
   curl -H "x-api-key: your-key" \
     http://localhost:8000/api/v1/sessions/active-sessions/
   ```

### Partial Restoration
- Some sessions restore, others don't
- Check individual auth file integrity
- Users with failed restoration will see "disconnected" status
- They can reconnect via dashboard (QR scan)

### All Sessions Failed
- Check if `.wwebjs_auth/` directory exists
- Verify file permissions
- Check Node.js logs for authentication errors
- May need to reconnect all sessions

## Summary

✅ **Sessions persist across restarts**  
✅ **No QR scans needed (usually)**  
✅ **Brief 5-10 second disconnection**  
✅ **Automatic reconnection**  
✅ **Service management UI shows impact**  

The service restart is **safe and non-disruptive** for normal operations. Users experience only a brief pause in connectivity, then everything returns to normal automatically.

