# WhatsApp Web Service

Node.js service that provides WhatsApp Web functionality for the Django SaaS application using `whatsapp-web.js`.

## Features

- Multi-session management
- QR code generation
- Text message sending
- Media message sending
- Session persistence
- Automatic cleanup of inactive sessions
- API key authentication
- Comprehensive logging

## Requirements

- Node.js 18+
- Chrome/Chromium (for Puppeteer)

## Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
```

## Configuration

Edit `.env` file:

```env
PORT=3000
NODE_ENV=development
DJANGO_API_URL=http://localhost:8000
REDIS_HOST=localhost
REDIS_PORT=6379
API_KEY=your-secret-api-key-here
```

## Running

### Development
```bash
npm run dev
```

### Production
```bash
npm start
```

### With PM2 (Recommended for production)
```bash
npm install -g pm2
pm2 start src/server.js --name whatsapp-service
pm2 save
pm2 startup
```

## API Endpoints

### Health Check
```
GET /health
```

### Initialize Session
```
POST /api/session/init
Headers:
  x-api-key: your-api-key
Body:
  {
    "sessionId": "user_123_session",
    "userId": 123
  }
Response:
  {
    "success": true,
    "sessionId": "user_123_session",
    "status": "qr_pending",
    "qrCode": "data:image/png;base64,..."
  }
```

### Get Session Status
```
GET /api/session/status/:sessionId
Headers:
  x-api-key: your-api-key
Response:
  {
    "success": true,
    "exists": true,
    "status": "connected",
    "phoneNumber": "1234567890",
    "isReady": true
  }
```

### Disconnect Session
```
POST /api/session/disconnect
Headers:
  x-api-key: your-api-key
Body:
  {
    "sessionId": "user_123_session"
  }
```

### Send Text Message
```
POST /api/message/send-text
Headers:
  x-api-key: your-api-key
Body:
  {
    "sessionId": "user_123_session",
    "recipient": "1234567890",
    "message": "Hello World"
  }
Response:
  {
    "success": true,
    "messageId": "msg_123456",
    "timestamp": 1234567890
  }
```

### Send Media Message
```
POST /api/message/send-media
Headers:
  x-api-key: your-api-key
Body:
  {
    "sessionId": "user_123_session",
    "recipient": "1234567890",
    "mediaUrl": "http://localhost:8000/media/file.jpg",
    "caption": "Check this out",
    "mediaType": "image"
  }
```

## Testing

### Test with curl

```bash
# Health check
curl http://localhost:3000/health

# Initialize session
curl -X POST http://localhost:3000/api/session/init \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{"sessionId":"test_123","userId":1}'

# Get status
curl http://localhost:3000/api/session/status/test_123 \
  -H "x-api-key: your-api-key"

# Send message
curl -X POST http://localhost:3000/api/message/send-text \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{"sessionId":"test_123","recipient":"1234567890","message":"Hello"}'
```

## Troubleshooting

### Chrome/Chromium Not Found
Install Chromium:
```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser

# macOS
brew install chromium

# Windows
Download from: https://www.chromium.org/getting-involved/download-chromium
```

### Session Not Connecting
- Check if WhatsApp Web is not already connected on another device
- Try deleting `.wwebjs_auth/` directory and reinitializing
- Check logs in `logs/` directory

### Memory Issues
- Reduce `MAX_CONCURRENT_SESSIONS` in .env
- Implement session cleanup more frequently
- Use PM2 with memory limits:
  ```bash
  pm2 start src/server.js --name whatsapp-service --max-memory-restart 500M
  ```

## Production Deployment

### Using PM2

```bash
# Start with PM2
pm2 start src/server.js --name whatsapp-service

# Monitor
pm2 monit

# Logs
pm2 logs whatsapp-service

# Restart
pm2 restart whatsapp-service
```

### Using Docker (optional)

See `Dockerfile` (to be created) for containerization.

## Logs

Logs are stored in `logs/` directory:
- `combined.log` - All logs
- `error.log` - Error logs only

## Security

- Always use HTTPS in production
- Keep API_KEY secret and strong
- Use firewall rules to restrict access
- Regularly update dependencies

## License

Proprietary

