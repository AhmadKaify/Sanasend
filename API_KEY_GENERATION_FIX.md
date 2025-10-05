# API Key Generation Fix

## Issue
The API key generation button on `/dashboard/api-keys/` was not working when clicked.

## Root Causes

### 1. Missing POST Handler in View
The `api_keys` view in `dashboard/views.py` was only rendering the template without handling POST requests.

### 2. Duplicate save() Method in Model
The `APIKey` model in `api_keys/models.py` had duplicate `save()` methods (lines 58 and 128), causing the key generation logic to be overridden.

## Fixes Applied

### 1. Updated `dashboard/views.py`
- Added POST request handling for two actions:
  - `generate`: Creates a new API key with optional name
  - `deactivate`: Deactivates an existing API key
- The generated raw key is temporarily stored in `_raw_key` attribute
- Success messages include the raw key (shown only once)
- Proper error handling and logging

### 2. Fixed `api_keys/models.py`
- Merged the duplicate `save()` methods
- Key generation logic now executes properly:
  1. Generates secure key with format: `wsk_{timestamp}_{random_part}`
  2. Hashes the key using HMAC-SHA256
  3. Stores hashed version in database
  4. Temporarily stores raw key in `_raw_key` attribute for display
- Validation logic runs before saving

### 3. Enhanced `dashboard/templates/dashboard/api_keys.html`
- Added JavaScript to display generated API key in a modal
- Modal features:
  - Shows the raw API key (only displayed once)
  - Copy to clipboard button with visual feedback
  - Security warning about saving the key
  - Clean, user-friendly interface
- Modal automatically appears when a key is generated

## Testing
- ✅ Django system check passes with no errors
- ✅ No linter errors in modified files
- ✅ Form submission now properly creates API keys
- ✅ Generated keys are displayed to the user once

## Usage
1. Navigate to `/dashboard/api-keys/`
2. Click "Generate New Key" button
3. Optionally enter a key name
4. Click "Generate"
5. Copy and save the displayed API key
6. The key won't be shown again for security reasons

## Files Modified
- `dashboard/views.py` - Added POST handling for API key generation
- `api_keys/models.py` - Fixed duplicate save() method
- `dashboard/templates/dashboard/api_keys.html` - Enhanced UI with key display modal

## Security Notes
- Keys are hashed using HMAC-SHA256 before storage
- Raw keys are only shown once during generation
- Keys are stored securely in the database
- Failed authentication attempts are tracked and rate-limited

