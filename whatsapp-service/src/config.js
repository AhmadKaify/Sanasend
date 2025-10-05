/**
 * Configuration module
 */
require('dotenv').config();

module.exports = {
  // Server
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  
  // Django Backend
  djangoApiUrl: process.env.DJANGO_API_URL || 'http://localhost:8000',
  
  // Redis
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT) || 6379,
    db: parseInt(process.env.REDIS_DB) || 2
  },
  
  // Session
  sessionTimeout: parseInt(process.env.SESSION_TIMEOUT) || 300000,
  maxConcurrentSessions: parseInt(process.env.MAX_CONCURRENT_SESSIONS) || 50,
  
  // Webhook
  webhookUrl: process.env.WEBHOOK_URL,
  
  // Security
  apiKey: process.env.API_KEY || 'change-this-secret-key',
  
  // WhatsApp
  whatsapp: {
    puppeteerOptions: {
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu'
      ]
    }
  }
};

