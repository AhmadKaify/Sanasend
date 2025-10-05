# How to Get Your API Key for Testing

## ⚠️ IMPORTANT: Two Types of Keys

### 🔴 WRONG Key (What you see in the list):
```
abc123def456789... (16 chars) ❌
```
- This is the **HASHED** version stored in database
- Shown in the API Keys list page
- **CANNOT be used for authentication**
- For display purposes only

### ✅ CORRECT Key (What you need):
```
wsk_1728153600_Wm5kZGlyZnJvbXNlY3JldHVybHNhZmU... (50-60 chars) ✅
```
- This is the **RAW** key
- Shown ONLY ONCE after generation in a pop-up modal
- **This is what you use in the test form**
- Cannot be retrieved later

---

## Step-by-Step: Getting the RAW Key

### Step 1: Go to API Keys Page
**URL:** http://localhost:8000/dashboard/api-keys/

### Step 2: Click "Generate New Key"
Look for the button at the top right

### Step 3: Enter a Name (Optional)
Example: `Test Key` or `My Testing Key`

### Step 4: Click "Generate"

### Step 5: **CRITICAL - Copy from the Modal**

A **GREEN MODAL** will pop up that looks like this:

```
┌─────────────────────────────────────────────┐
│ ✅ API Key Generated Successfully!         │
│                                             │
│ ⚠️ Copy this key now. It won't be shown   │
│    again.                                   │
│                                             │
│ ┌─────────────────────────────────────┐   │
│ │ wsk_1728153600_Wm5kZGlyZnJv...    │   │
│ │                        [Copy] ←────┼───│
│ └─────────────────────────────────────┘   │
│                                             │
│                    [I've Saved My Key]     │
└─────────────────────────────────────────────┘
```

**Click the "Copy" button in this modal!**

### Step 6: Save It Somewhere
- Paste in Notepad
- Or paste directly in the test form
- **You won't see this key again!**

---

## Using the Key

### In Test Sample Page:
```
API Key field: wsk_1728153600_Wm5kZGlyZnJvbXNlY3JldHVybHNhZmU...
```

### In API Requests:
```
Header: Authorization: ApiKey wsk_1728153600_Wm5kZGlyZnJvbXNlY3JldHVybHNhZmU...
```

### In Code:
```python
headers = {
    'Authorization': 'ApiKey wsk_1728153600_Wm5kZGlyZnJv...'
}
```

---

## Common Mistakes

### ❌ Mistake 1: Copying from List
```
Don't copy from here:
┌────────────────────────────────┐
│ API Keys                       │
├────────────────────────────────┤
│ Test Key                       │
│ Created: Oct 5, 2025           │
│ Key ID: 123                    │
│ abc123def456...     [Deactivate]
└────────────────────────────────┘
         ↑
    This won't work!
```

### ✅ Correct: Copy from Modal
```
Copy from the pop-up after generating:
┌─────────────────────────────────┐
│ wsk_1728...  [Copy] ← Click here
└─────────────────────────────────┘
```

### ❌ Mistake 2: Using Old Key
If you generated a key yesterday and didn't save it, **you cannot retrieve it**. Generate a new one.

### ❌ Mistake 3: Missing the Modal
If you miss the modal, the key is lost. Generate a new one.

---

## Verification

Your API key is correct if:
- ✅ Starts with `wsk_`
- ✅ Contains underscore after wsk
- ✅ Has a timestamp (10 digits)
- ✅ Has a long random string after
- ✅ Total length: 50-60+ characters

Example breakdown:
```
wsk_1728153600_Wm5kZGlyZnJvbXNlY3JldHVybHNhZmU
│   │          │
│   │          └─ Random part (32+ chars)
│   └─ Timestamp (10 digits)
└─ Prefix
```

---

## What Happens When You Generate a Key

1. System generates: `wsk_1728153600_Wm5kZGly...` (RAW)
2. System hashes it: `abc123def456...` (HASHED)
3. System stores: HASHED version in database
4. System shows: RAW version in modal (ONCE)
5. You copy: RAW version from modal
6. You use: RAW version for authentication
7. System verifies: Hashes your RAW key and compares with database

**The database NEVER stores the raw key - that's why you must copy it immediately!**

---

## FAQ

**Q: I generated a key yesterday, where can I find it?**  
A: You can't. Generate a new one.

**Q: Can I see my raw key again?**  
A: No. For security, it's shown only once. Generate a new one if needed.

**Q: How many keys can I have?**  
A: Multiple. You can generate as many as you need.

**Q: Should I delete old keys?**  
A: If you've lost the raw key, yes. Deactivate it and generate a new one.

**Q: The modal didn't appear, what now?**  
A: Generate a new key. Make sure popups aren't blocked.

**Q: Can I retrieve a key from the database?**  
A: No. Only the hashed version is stored.

---

## Quick Test

After copying your key:

1. Go to: http://localhost:8000/dashboard/test-sample/
2. Paste your key in "API Key" field
3. Enter recipient: `+9647709910444`
4. Enter message: `Test`
5. Click "Send Message"
6. Check Response tab

**If you get "Invalid API key" → You copied the wrong key or missed the modal**

---

## Summary

✅ **DO:**
- Generate a NEW key each time you test
- Copy from the GREEN MODAL that pops up
- Click the "Copy" button in the modal
- Save it immediately
- Use the full key (wsk_...)

❌ **DON'T:**
- Copy from the list page
- Try to find old keys
- Use keys without `wsk_` prefix
- Close the modal without copying
- Try to "unhash" keys from database

The system is working perfectly - you just need the RAW key from the modal!

