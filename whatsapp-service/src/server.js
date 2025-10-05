/**
 * WhatsApp Web Service - Main Server
 */
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const config = require('./config');
const logger = require('./logger');
const { authenticateApiKey } = require('./middleware/auth');
const whatsappManager = require('./whatsappManager');

// Routes
const sessionRoutes = require('./routes/session');
const messageRoutes = require('./routes/message');

// Create Express app
const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`);
  next();
});

// Health check endpoint (no auth required)
app.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'healthy',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// API routes (with authentication)
app.use('/api/session', authenticateApiKey, sessionRoutes);
app.use('/api/message', authenticateApiKey, messageRoutes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found'
  });
});

// Error handler
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// Cleanup inactive sessions periodically (every 30 minutes)
setInterval(() => {
  logger.info('Running session cleanup...');
  whatsappManager.cleanupInactiveSessions();
}, 30 * 60 * 1000);

// Start server
const PORT = config.port;
app.listen(PORT, () => {
  logger.info(`WhatsApp Service running on port ${PORT}`);
  logger.info(`Environment: ${config.nodeEnv}`);
  logger.info(`Max concurrent sessions: ${config.maxConcurrentSessions}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully...');
  // Close all clients
  const sessions = whatsappManager.getActiveSessions();
  for (const session of sessions) {
    await whatsappManager.destroyClient(session.sessionId);
  }
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully...');
  // Close all clients
  const sessions = whatsappManager.getActiveSessions();
  for (const session of sessions) {
    await whatsappManager.destroyClient(session.sessionId);
  }
  process.exit(0);
});

