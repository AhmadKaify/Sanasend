# User Dashboard Guide

## Overview

The User Dashboard provides a web interface for regular users to manage their WhatsApp sessions, view messages, and manage API keys without needing API calls.

---

## ✅ What's Included

### Dashboard Features

1. **Home Dashboard** (`/dashboard/`)
   - Session status overview
   - Messages sent today vs. limit
   - Total messages count
   - Active API keys count
   - Quick actions

2. **Session Management** (`/dashboard/session/`)
   - Initialize WhatsApp session
   - Display QR code for scanning
   - View session status (connected/disconnected/pending)
   - Refresh session status
   - Disconnect session
   - View session details (phone number, connection time, etc.)

3. **Message History** (`/dashboard/messages/`)
   - View last 100 messages
   - See message type (text/image/document/video)
   - Check message status (sent/pending/failed)
   - View error messages for failed sends
   - Statistics (total, sent, failed)

4. **API Keys** (`/dashboard/api-keys/`)
   - View all API keys
   - Generate new API keys
   - Deactivate API keys
   - See last usage time
   - Copy usage examples

5. **Profile** (`/dashboard/profile/`)
   - View account details
   - See usage limits
   - View usage statistics (last 30 days)
   - Account information

---

## 🚀 How to Access

### URL Structure

```
http://localhost:8000/dashboard/       # Home
http://localhost:8000/dashboard/login/ # Login
```

### Login Credentials

Users login with their Django username and password (the same credentials used for admin access if they have admin rights).

---

## 📸 Features Walkthrough

### 1. Login Page

**URL:** `/dashboard/login/`

- Clean, modern login interface
- Purple gradient background
- WhatsApp icon branding
- Username + password authentication

### 2. Dashboard Home

**What you see:**
- **4 stat cards:**
  - Session Status (with color indicators)
  - Messages Today (with daily limit)
  - Total Messages
  - Active API Keys
  
- **Quick Actions:**
  - Initialize Session
  - Generate API Key
  - View API Documentation
  
- **Session Information:**
  - Session ID
  - Status
  - Phone number (if connected)
  - Connection timestamps

### 3. Session Management

**Initialize Session:**
1. Click "Initialize Session" button
2. QR code is displayed
3. Scan with WhatsApp mobile app:
   - Open WhatsApp → Settings → Linked Devices
   - Tap "Link a Device"
   - Scan the QR code
4. Click "Refresh Status" to check connection
5. Status updates to "Connected" when successful

**View Session Details:**
- Session ID
- Current status with color indicator
- Connected phone number
- Connection timestamps
- Last activity time

**Disconnect:**
- Click "Disconnect" button
- Confirm action
- Session is terminated

### 4. Messages Page

**View:**
- Table of last 100 messages
- Columns: Recipient, Type, Content (truncated), Status, Sent At
- Color-coded status badges:
  - Green: Sent successfully
  - Yellow: Pending
  - Red: Failed
- Error messages displayed for failed sends

**Statistics:**
- Total messages
- Successfully sent
- Failed count

### 5. API Keys Page

**View Keys:**
- List of all API keys
- Active/Inactive status
- Creation date
- Last used date
- Key ID

**Generate New Key:**
1. Click "Generate New Key"
2. Enter optional name
3. Click "Generate"
4. **IMPORTANT:** Copy the key (shown only once!)
5. Use in API requests

**Deactivate Key:**
1. Click "Deactivate" on any active key
2. Confirm action
3. Key is disabled

**Usage Example:**
```bash
Authorization: ApiKey YOUR_API_KEY_HERE
```

### 6. Profile Page

**Account Details:**
- Username
- Email
- First/Last name
- Member since
- Last login

**Usage Limits:**
- Daily message limit visualization
- Current usage percentage

**Usage Statistics:**
- Last 30 days of activity
- Messages sent per day
- API requests per day
- Media sent per day

---

## 🎨 Design Features

### UI/UX
- **Tailwind CSS** for styling
- **Font Awesome** icons
- **Responsive** design (mobile-friendly)
- **Color scheme:** Purple primary with status colors
- **Clean, modern** interface

### Status Indicators
- 🟢 **Green** - Connected/Sent/Active
- 🟡 **Yellow** - Pending/QR Code
- 🔴 **Red** - Disconnected/Failed/Inactive
- ⚪ **Gray** - Not initialized/Inactive

### Interactive Elements
- Pulse animations for live status
- Hover effects on cards and buttons
- Modal dialogs for actions
- Success/error messages
- Confirmation dialogs for destructive actions

---

## 🔐 Security

### Authentication
- Login required for all pages
- Django's built-in auth system
- Session-based authentication
- CSRF protection

### Permissions
- Users can only see their own data
- No access to other users' sessions
- Cannot view admin functions
- API keys are hashed (never shown after creation)

---

## 📱 Mobile Responsive

The dashboard is fully responsive:
- Adapts to phone/tablet screens
- Mobile-friendly navigation
- Touch-friendly buttons
- Optimized QR code display

---

## 🔄 Real-time Updates

### Auto-refresh Not Implemented
Currently, users need to manually:
- Click "Refresh Status" to update session
- Reload page to see new messages
- Refresh to see updated statistics

**Future Enhancement:** Add auto-refresh with AJAX

---

## 🆘 Help & Support

### Built-in Help
- Instructions on Session page for scanning QR
- Security notices on API Keys page
- Usage examples included
- Links to API documentation

### Common Issues

**Can't login:**
- Check username/password
- Contact admin if account is inactive

**QR Code not working:**
- Make sure WhatsApp Web isn't already connected
- Try disconnecting and reinitializing
- Check Node.js service is running

**Session disconnects:**
- This is normal after inactivity
- Simply reconnect when needed

---

## 🎯 User Workflow

### First Time Setup

1. **Login** at `/dashboard/login/`
2. **Initialize Session** from dashboard or session page
3. **Scan QR Code** with WhatsApp mobile
4. **Wait for Connection** (status turns green)
5. **Generate API Key** (optional, for API use)
6. **Start Sending Messages** via API

### Daily Use

1. **Check Dashboard** - See stats
2. **Verify Session** - Make sure it's connected
3. **Send Messages** - Via API with your key
4. **Monitor Activity** - Check message history
5. **View Stats** - See usage on profile page

---

## 🔗 Links

### Internal Links
- `/dashboard/` - Home
- `/dashboard/session/` - Session management
- `/dashboard/messages/` - Message history
- `/dashboard/api-keys/` - API keys
- `/dashboard/profile/` - Profile
- `/dashboard/logout/` - Logout

### External Links
- `/api/docs/` - Swagger API documentation
- `/admin/` - Admin panel (if user has access)

---

## ⚙️ Configuration

### Required Settings

```python
# settings/base.py

# Add dashboard to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'dashboard.apps.DashboardConfig',
]

# Login settings
LOGIN_URL = '/dashboard/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/dashboard/login/'
```

### URL Configuration

```python
# config/urls.py

urlpatterns = [
    path('dashboard/', include('dashboard.urls')),
    path('', lambda request: redirect('/dashboard/')),
]
```

---

## 📊 Comparison: Dashboard vs API

| Feature | Dashboard (Web UI) | API |
|---------|-------------------|-----|
| Session Init | ✅ Click button, see QR | ✅ POST /api/v1/sessions/init/ |
| View Status | ✅ Visual indicators | ✅ GET /api/v1/sessions/status/ |
| Send Messages | ❌ Not available | ✅ POST /api/v1/messages/send-* |
| View Messages | ✅ Last 100 in table | ✅ GET /api/v1/messages/list/ |
| API Keys | ✅ Generate & view | ✅ Admin API only |
| Usage Stats | ✅ Visual charts | ✅ GET /api/v1/analytics/* |

**Best Use Case:**
- **Dashboard:** Session setup, monitoring, API key management
- **API:** Automated message sending, integrations, programmatic access

---

## 🚀 Future Enhancements

Potential improvements:
- [ ] Auto-refresh session status
- [ ] Send messages from dashboard
- [ ] Real-time notifications
- [ ] Usage charts/graphs
- [ ] Bulk message interface
- [ ] Contact management
- [ ] Message scheduling
- [ ] Webhook configuration

---

## 📝 Notes

- Dashboard complements the API (doesn't replace it)
- Users still need API keys for sending messages
- Dashboard is for management, API is for automation
- Both use the same backend services
- Session state is shared between dashboard and API

---

**Dashboard Status:** ✅ **COMPLETE & READY TO USE**

Access it at: `http://localhost:8000/dashboard/`


