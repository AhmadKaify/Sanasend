# Multi-Instance WhatsApp Feature

## Overview
You can now manage up to 10 different WhatsApp instances per user account. Each instance can be connected to a different WhatsApp number.

---

## Features Added

### **1. Instance Management Dashboard**
- ✅ View all WhatsApp instances in a grid layout
- ✅ Shows instance status (Connected, QR Pending, Disconnected)
- ✅ Instance counter (X/10 instances)
- ✅ Primary instance indicator
- ✅ Individual action buttons per instance

### **2. Add New Instance**
- ✅ "Add New WhatsApp Instance" button
- ✅ Modal dialog to name the instance
- ✅ Custom instance names (e.g., "Business Account", "Personal", "Support")
- ✅ Maximum 10 instances per user
- ✅ Unique instance name validation

### **3. Per-Instance Actions**
Each instance has its own action buttons:
- **View QR** - Opens modal with QR code and countdown timer
- **Refresh QR** - Generate new QR code if expired
- **Connect** - Connect disconnected instance
- **Disconnect** - Disconnect active instance
- **Set Primary** - Make this the default instance for API calls
- **Delete** - Remove instance permanently

### **4. Primary Instance**
- ✅ One instance marked as "Primary"
- ✅ Primary instance used by default for API message sending
- ✅ First instance automatically set as primary
- ✅ Can change primary to any connected instance
- ✅ Visual indicator (badge and colored border)

---

## User Interface

### **Summary Card**
```
┌─────────────────────────────────────────────┐
│ WhatsApp Instances                    3/10  │
│ Manage up to 10 WhatsApp instances          │
│                                             │
│ [+ Add New WhatsApp Instance]              │
└─────────────────────────────────────────────┘
```

### **Instance Card Example**
```
┌──────────────────────────────────────────┐
│ Business Account          [Primary]  🟢  │
│ user_1_instance_business_123456789       │
│                                          │
│ 📱 +1234567890                           │
│ ─────────────────────────────────────    │
│ [Disconnect] [⭐Set Primary] [🗑️Delete]  │
│                                          │
│ 🕐 Created: Jan 1, 2025 10:00           │
└──────────────────────────────────────────┘
```

---

## How to Use

### **Add New Instance**

1. Click **"Add New WhatsApp Instance"** button
2. Enter a name for the instance (e.g., "Sales Team", "Support")
3. Click **"Add Instance"**
4. QR code will be generated - click **"View QR"** to see it
5. Scan QR code with WhatsApp mobile app
6. Status changes to "Connected" automatically

### **Scan QR Code**

1. Click **"View QR"** button on instance card
2. Modal opens with QR code and 60-second countdown
3. Open WhatsApp on your phone:
   - Go to Menu → Linked Devices
   - Tap "Link a Device"
   - Scan the QR code
4. Page auto-refreshes when connected (1-second polling)

### **Set Primary Instance**

1. Ensure instance is connected
2. Click **"Set Primary"** button
3. This instance will be used by default for API calls

### **Manage Instances**

- **Refresh QR**: If QR expires, click to generate new one
- **Disconnect**: Disconnect active session
- **Reconnect**: Connect a disconnected instance
- **Delete**: Permanently remove instance from database

---

## Technical Implementation

### **Dashboard Template**
`dashboard/templates/dashboard/session.html`:
- Grid layout with 2 columns (responsive)
- Two modals: Add Instance & View QR
- JavaScript for modal management
- Real-time QR countdown timer
- Auto-refresh on connection

### **Dashboard Views**
`dashboard/views.py` - New Actions:
- `add_instance` - Create new instance
- `reconnect` - Reconnect disconnected instance
- `set_primary` - Set primary instance
- `delete` - Delete instance
- `refresh_qr` - Refresh QR code (now accepts session_id)
- `disconnect` - Disconnect instance (now accepts session_id)

### **API Endpoints (Already Exist)**
`/api/v1/sessions/`:
- `POST /init/` - Initialize new session
- `GET /list/` - List all user sessions
- `GET /status/<id>/` - Get specific session status
- `POST /disconnect/<id>/` - Disconnect specific session
- `DELETE /delete/<id>/` - Delete session
- `POST /set-primary/<id>/` - Set primary session

---

## Database Schema

**WhatsAppSession Model** (unchanged):
```python
- user (FK to User)
- instance_name (CharField, max 100)  # "Business", "Personal", etc.
- session_id (CharField, unique)      # Auto-generated
- status (CharField)                  # qr_pending, connected, disconnected
- qr_code (TextField)
- qr_expires_at (DateTime)
- phone_number (CharField)
- connected_at (DateTime)
- last_active_at (DateTime)
- is_primary (Boolean)                # Primary instance flag
- created_at (DateTime)
- updated_at (DateTime)
```

**Constraints**:
- Max 10 instances per user (enforced in code)
- Unique instance_name per user
- Only one primary instance per user

---

## Session Flow

### **Adding New Instance**
```
User clicks "Add New Instance"
    ↓
Modal opens with name input
    ↓
User enters name & submits
    ↓
Django validates:
  - Name not empty
  - Name unique for user
  - User has < 10 instances
    ↓
Calls Node.js to init session
    ↓
QR code generated
    ↓
Saved in database
    ↓
Page refreshes showing new instance
```

### **Connecting Instance**
```
User clicks "View QR" on instance
    ↓
Modal opens with QR & countdown
    ↓
User scans with WhatsApp mobile
    ↓
JavaScript polls every 1 second
    ↓
Detects "Connected" status
    ↓
Auto-refreshes page (300ms delay)
    ↓
Instance shows as "Connected"
```

---

## Changes Made

### **Files Modified**
1. `dashboard/templates/dashboard/session.html`
   - Replaced single session view with grid view
   - Added "Add Instance" button and modal
   - Added "View QR" modal
   - Updated JavaScript for modal management
   - Reduced polling interval to 1 second (was 3 seconds)

2. `dashboard/views.py`
   - Added `add_instance` action
   - Added `reconnect` action
   - Added `set_primary` action
   - Added `delete` action
   - Updated `refresh_qr` to accept session_id
   - Updated `disconnect` to accept session_id
   - Updated `refresh` to query Node.js for fresh status

### **No Changes Needed**
- `sessions/models.py` - Already supports multi-instance
- `api/v1/sessions/` - Already has full API support
- Database migrations - No new fields needed

---

## User Benefits

1. **Multiple WhatsApp Numbers**: Connect up to 10 different numbers
2. **Organization**: Name instances for easy identification
3. **Flexibility**: Connect/disconnect instances as needed
4. **Primary Selection**: Choose which instance to use by default
5. **Easy Management**: All instances visible in one dashboard
6. **Load Balancing**: API can automatically distribute messages across instances

---

## API Usage with Multiple Instances

### **Send Message to Primary Instance**
```bash
POST /api/v1/messages/send/
{
  "recipient": "1234567890",
  "message": "Hello!"
  # Uses primary instance automatically
}
```

### **Send Message to Specific Instance**
```bash
POST /api/v1/messages/send/
{
  "recipient": "1234567890",
  "message": "Hello!",
  "session_id": "user_1_instance_business"
}
```

### **List All Instances**
```bash
GET /api/v1/sessions/list/
```

Response:
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": 1,
        "instance_name": "Business Account",
        "session_id": "user_1_instance_business",
        "status": "connected",
        "phone_number": "1234567890",
        "is_primary": true,
        "connected_at": "2025-01-01T10:00:00Z"
      },
      {
        "id": 2,
        "instance_name": "Personal",
        "session_id": "user_1_instance_personal",
        "status": "qr_pending",
        "is_primary": false
      }
    ],
    "total_count": 2,
    "connected_count": 1
  }
}
```

---

## Testing

### **Test Multi-Instance Creation**
1. ✅ Add 1st instance → Should be set as primary automatically
2. ✅ Add 2nd instance → Should not be primary
3. ✅ Try to add instance with duplicate name → Should show error
4. ✅ Try to add 11th instance → Should show error

### **Test Instance Actions**
1. ✅ Connect instance → QR code shown, status updates to connected
2. ✅ Set 2nd instance as primary → Primary badge moves
3. ✅ Disconnect instance → Status changes to disconnected
4. ✅ Delete instance → Removed from database
5. ✅ Refresh QR → New QR generated with fresh countdown

### **Test QR Modal**
1. ✅ View QR modal → Opens with countdown
2. ✅ Scan QR code → Status updates within 1-2 seconds
3. ✅ Let QR expire → Countdown shows "EXPIRED"
4. ✅ Close modal → Countdown stops

---

## Troubleshooting

### **"Maximum instances reached"**
- Delete old instances you don't need
- Max 10 instances per user (system limit)

### **"Instance name already exists"**
- Choose a different name for the instance
- Each instance must have unique name per user

### **QR Code Doesn't Work**
- Click "Refresh QR" to generate new one
- Ensure QR hasn't expired (60 second limit)
- Check Node.js service is running

### **Can't Set as Primary**
- Instance must be "Connected" to be set as primary
- Connect the instance first, then set as primary

---

## Summary

✅ **Multi-instance support fully implemented**
✅ **Modern, intuitive UI**
✅ **Up to 10 WhatsApp numbers per user**
✅ **Primary instance selection**
✅ **Real-time status updates (1-second polling)**
✅ **Modal-based QR code viewing**
✅ **Full instance lifecycle management**

**Refresh your browser and start adding instances!**

