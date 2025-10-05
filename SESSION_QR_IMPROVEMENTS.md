# Session QR Code Improvements

## Overview
Enhanced WhatsApp session management with QR code countdown timer and refresh functionality.

## Changes Made

### 1. Database Schema
**File**: `sessions/models.py`
- Added `qr_expires_at` field to track QR code expiration time
- QR codes now expire 60 seconds after generation

### 2. Dashboard UI
**File**: `dashboard/templates/dashboard/session.html`
- Added real-time countdown timer showing time until QR code expires
- Visual countdown changes color when < 15 seconds remaining
- Countdown turns red when expired
- Shows "QR Code Expired" overlay when time runs out
- Added "Request New QR Code" button for easy refresh
- Button pulses when QR code expires
- Auto-refresh page when connection is detected (checks every 3 seconds)

### 3. Dashboard Views
**File**: `dashboard/views.py`
- Added `refresh_qr` action to handle QR code regeneration
- **Disconnects old session first** before generating new QR (prevents "Client already exists" error)
- Sets `qr_expires_at` to 60 seconds from generation time
- Clears `qr_expires_at` when session is disconnected
- Shows appropriate success messages for init vs refresh actions
- Graceful error handling if old session disconnect fails

### 4. API Endpoints
**File**: `api/v1/sessions/views.py`

#### New Endpoint: `POST /api/v1/sessions/refresh-qr/`
Refreshes QR code for pending sessions.

**How it works:**
1. Disconnects the existing session (if any)
2. Initializes a new session with fresh QR code
3. Returns new QR code with 60-second expiration

**Response:**
```json
{
  "success": true,
  "data": {
    "sessionId": "user_1_session",
    "status": "qr_pending",
    "qrCode": "data:image/png;base64,...",
    "qrExpiresAt": "2025-10-04T12:34:56+00:00",
    "message": "QR code refreshed. Please scan within 60 seconds."
  }
}
```

**Error Handling:**
- Returns 404 if no session exists
- Returns 400 if session is already connected
- Gracefully handles disconnect failures

#### Updated Endpoints:
- `POST /api/v1/sessions/init/` - Now includes `qrExpiresAt` in response
- `GET /api/v1/sessions/status/` - Now includes `qrCode` and `qrExpiresAt` fields
- `POST /api/v1/sessions/disconnect/` - Clears `qr_expires_at` field

### 5. URL Configuration
**File**: `api/v1/sessions/urls.py`
- Added route for new refresh QR endpoint

## User Experience Improvements

### Visual Feedback
1. **Live Countdown**: Users see exact time remaining (MM:SS format)
2. **Color Indicators**: 
   - Purple/Blue gradient: Normal state
   - Red: < 15 seconds or expired
3. **Expired State**: Clear visual overlay when QR expires
4. **Animated Button**: Pulsing refresh button when expired

### Auto-Refresh Features
1. **Active Status Polling**: POSTs to refresh action every 3 seconds to fetch real-time status from Node.js service
2. **Visual Feedback**: Shows "Checking connection status..." with spinning icon
3. **Connection Detection**: Shows "Connection detected! Confirming... (1/2)" when WhatsApp connects
4. **Auto-Reload**: Page reloads after 2 consecutive connection confirmations (prevents false positives)
5. **Smart Timeout**: Stops checking after 3 minutes to conserve resources
6. **Timer Cleanup**: All intervals cleaned up properly on page unload

### Button Actions
1. **Initialize Session**: First-time setup
2. **Request New QR Code**: Get fresh QR without full page reload
3. **Refresh Status**: Manual status check
4. **Disconnect**: Clear session with cleanup

## API Usage Examples

### Refresh QR Code
```bash
curl -X POST https://your-domain.com/api/v1/sessions/refresh-qr/ \
  -H "Authorization: Api-Key YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

### Check Session Status with QR Info
```bash
curl -X GET https://your-domain.com/api/v1/sessions/status/ \
  -H "Authorization: Api-Key YOUR_API_KEY"
```

Response includes:
```json
{
  "success": true,
  "data": {
    "sessionId": "user_1_session",
    "status": "qr_pending",
    "qrCode": "data:image/png;base64,...",
    "qrExpiresAt": "2025-10-04T12:35:00+00:00",
    "phoneNumber": null,
    "isReady": false,
    "connectedAt": null,
    "lastActiveAt": "2025-10-04T12:34:00+00:00"
  }
}
```

## Technical Details

### QR Code Expiration
- Default expiration: 60 seconds
- Configurable via `timedelta(seconds=60)` in views
- Server-side validation of expiration time
- Client-side countdown for UX

### Session Refresh Logic
- **Disconnect-First Strategy**: Always disconnects old session before creating new one
- Prevents "Client already exists" errors from WhatsApp service
- Continues even if disconnect fails (session might not exist in Node.js)
- Logs warnings for troubleshooting

### JavaScript Features
- Vanilla JavaScript (no dependencies)
- Efficient interval management
- Proper cleanup to prevent memory leaks
- Graceful handling of time zones

### Security
- All endpoints require authentication
- API keys validated via `IsActiveUser` permission
- Session validation on each request
- No exposed sensitive data in client-side code

## Migration
Run the following to apply database changes:
```bash
python manage.py migrate
```

Migration file: `sessions/migrations/0002_whatsappsession_qr_expires_at.py`

## Browser Compatibility
- Modern browsers with ES6+ support
- Tested on Chrome, Firefox, Safari, Edge
- Responsive design for mobile devices

## Future Enhancements
Consider:
1. Configurable expiration time per user/plan
2. Push notifications when QR expires
3. SMS/Email QR code delivery
4. QR code history tracking
5. Multiple device support

