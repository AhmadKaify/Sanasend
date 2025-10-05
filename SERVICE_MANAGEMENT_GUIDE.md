# Node.js Service Management Guide

## Overview

The SanaSend platform now includes a comprehensive service management interface that allows administrators to monitor and control the Node.js WhatsApp service directly from the dashboard UI.

## Features

### 1. Service Status Monitoring
- Real-time service health checks
- Service uptime tracking
- Connection status to the Node.js service
- Process information display
- Service logs viewer

### 2. Service Control Actions
- **Start**: Start the Node.js service when it's stopped
- **Stop**: Gracefully stop the running service
- **Restart**: Restart the service (useful for applying updates or recovering from issues)
- **Refresh**: Check current status without performing any action

### 3. Auto-Refresh
- The service status page automatically refreshes every 30 seconds
- Manual refresh available via the "Refresh" button

## Access

### Requirements
- **Admin privileges required**: Only users with `is_staff=True` can access service management features
- Service management is available at: `/dashboard/service-status/`

### Navigation
1. **Sidebar**: Admin users will see a "Service Status" link under the "Admin" section
2. **Dashboard**: Admin users will see a service status card on the home page with a link to the full management page

## Service Management Interface

### Status Indicators

#### Service Running (Healthy)
- Green indicator
- Shows service uptime
- All control actions available

#### Service Stopped
- Red indicator
- Only "Start" action available
- Shows connection error message

#### Service Unhealthy
- Yellow indicator
- Service is running but not responding properly
- Restart recommended

### Control Actions

#### Start Service
```
Conditions:
- Service must be stopped
- Node.js must be installed
- WhatsApp-service directory must exist

Action:
- Starts the service in the background
- Waits 3 seconds before refreshing status
```

#### Stop Service
```
Conditions:
- Service must be running

Action:
- Attempts graceful shutdown
- Force kills if graceful shutdown fails
- Immediately refreshes status
```

#### Restart Service
```
Conditions:
- Service must be running

Action:
- Stops the service (gracefully or forcefully)
- Starts the service
- Waits 3 seconds before refreshing status
```

## API Endpoints

### View Service Status
```
GET /dashboard/service-status/
```
Returns the service status page with current information

### Perform Service Action
```
POST /dashboard/service-action/
Content-Type: application/json

Body:
{
    "action": "start|stop|restart|status"
}

Response:
{
    "success": true|false,
    "message": "Status message",
    "running": true|false,
    "healthy": true|false
}
```

## Implementation Details

### Service Manager (`core/service_manager.py`)

The `ServiceManager` class provides the following methods:

#### `get_service_status()`
Checks if the Node.js service is responding to health checks
```python
Returns:
{
    'running': bool,
    'healthy': bool,
    'uptime': float,
    'timestamp': str,
    'message': str,
    'url': str
}
```

#### `get_process_info()`
Retrieves process information for running Node.js instances
```python
Returns: List[str] - Process information lines
```

#### `start_service()`
Starts the Node.js service
```python
Returns:
{
    'success': bool,
    'message': str
}
```

#### `stop_service()`
Stops the Node.js service
```python
Returns:
{
    'success': bool,
    'message': str
}
```

#### `restart_service()`
Restarts the Node.js service
```python
Returns:
{
    'success': bool,
    'message': str
}
```

#### `get_service_logs(lines=50)`
Retrieves recent log entries from the service
```python
Returns: List[str] - Log lines
```

### Platform Compatibility

The service manager automatically detects the platform and uses appropriate commands:

#### Windows
- Uses `tasklist` for process information
- Uses `taskkill` for stopping processes
- Starts service with `start cmd /c npm start`

#### Linux/Mac
- Uses `ps aux` for process information
- Uses `pgrep` and `kill` for stopping processes
- Starts service with `nohup npm start &`

## Important Notes

### 1. Permissions
- Service control may require elevated permissions depending on your setup
- On Linux/Mac, ensure the Django process has permission to manage Node.js processes
- On Windows, ensure the user has permission to start/stop processes

### 2. Service Configuration
The service manager uses the following Django settings:
```python
NODE_SERVICE_URL = 'http://localhost:3000'  # From settings
```

### 3. Sessions Impact & Persistence
- **Sessions are preserved** - WhatsApp authentication is saved to disk
- **Brief disconnection** during restart (~5-10 seconds)
- **Auto-reconnect** - Sessions automatically restore after service starts
- **No QR scan needed** - Existing auth is reused if files are intact
- Users may see a temporary "disconnected" status during the restart
- Session restoration starts 5 seconds after Node.js service starts

### 4. Logs Location
Service logs are read from:
```
BASE_DIR/whatsapp-service/logs/combined.log
```

### 5. Health Check Endpoint
The Node.js service must provide a health check endpoint:
```
GET /health

Response:
{
    "success": true,
    "status": "healthy",
    "uptime": 123.45,
    "timestamp": "2025-10-05T12:00:00.000Z"
}
```

## Session Restoration Process

When the Node.js service restarts, it automatically attempts to restore all active sessions:

### How It Works

1. **Service Startup** (0-5 seconds)
   - Node.js service initializes
   - WhatsApp client manager starts
   - Health endpoint becomes available

2. **Restoration Phase** (5-15 seconds)
   - Service queries Django for active sessions
   - For each session, attempts to restore using saved auth files
   - Auth files are stored in: `whatsapp-service/.wwebjs_auth/`

3. **Reconnection** (10-20 seconds)
   - WhatsApp Web protocol reconnects
   - Session status updates to "connected"
   - Django receives webhook notifications

### Viewing Restoration Status

1. **Service Logs**: Check the "Service Logs" section for restoration messages:
   ```
   Starting session restoration...
   Found X sessions to restore
   ✓ Session restored: user_123_instance_main
   Session restoration complete: X restored, Y failed
   ```

2. **Active Sessions Table**: Shows which sessions will be restored
   - User who owns the session
   - Instance name
   - Current status
   - Last active time

### Why Sessions Might Not Restore

1. **Auth files missing or corrupted**
   - Location: `whatsapp-service/.wwebjs_auth/session_[sessionId]/`
   - Solution: User needs to scan QR code again

2. **WhatsApp Web logged out**
   - User logged out from phone
   - Solution: Reconnect via QR code

3. **Session expired**
   - Long downtime (weeks/months)
   - Solution: Reconnect via QR code

4. **Database/API connection issue**
   - Django not reachable during restoration
   - Check Django logs and API connectivity

## Troubleshooting

### Service Won't Start
1. Check if Node.js is installed: `node --version`
2. Check if npm is installed: `npm --version`
3. Verify the whatsapp-service directory exists
4. Check service logs for errors
5. Ensure port 3000 (or configured port) is not in use

### Service Won't Stop
1. Try the restart action instead
2. Manually check for Node.js processes:
   - Windows: `tasklist | findstr node`
   - Linux/Mac: `ps aux | grep node`
3. Manually kill processes if needed

### Service Unhealthy
1. Check service logs for errors
2. Verify database connectivity
3. Check Redis connectivity (if used)
4. Try restarting the service

### Cannot Access Service Status Page
1. Verify you're logged in as an admin user
2. Check that `user.is_staff = True`
3. Check Django logs for permission errors

## Security Considerations

1. **Admin-Only Access**: Service management is restricted to staff users
2. **CSRF Protection**: All POST requests require CSRF token
3. **Action Confirmation**: Destructive actions (stop/restart) require user confirmation
4. **Audit Logging**: All service actions are logged to Django logs

## Future Enhancements

Potential improvements for future versions:
- Service metrics and statistics
- Historical uptime tracking
- Email notifications for service failures
- Scheduled service maintenance windows
- Multiple service management (if scaling to multiple Node.js instances)
- Integration with system process managers (systemd, PM2, etc.)

