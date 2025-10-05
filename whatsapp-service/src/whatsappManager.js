/**
 * WhatsApp Client Manager
 * Manages multiple WhatsApp Web clients
 */
const { Client, LocalAuth } = require('whatsapp-web.js');
const QRCode = require('qrcode');
const logger = require('./logger');
const config = require('./config');

class WhatsAppManager {
  constructor() {
    this.clients = new Map();
    this.qrCodes = new Map();
    this.sessionStatus = new Map();
  }

  /**
   * Create a new WhatsApp client
   */
  async createClient(sessionId, userId) {
    try {
      if (this.clients.has(sessionId)) {
        logger.warn(`Client ${sessionId} already exists`);
        return { success: false, message: 'Client already exists' };
      }

      if (this.clients.size >= config.maxConcurrentSessions) {
        logger.error('Maximum concurrent sessions reached');
        return { success: false, message: 'Maximum sessions limit reached' };
      }

      const client = new Client({
        authStrategy: new LocalAuth({ clientId: sessionId }),
        puppeteer: config.whatsapp.puppeteerOptions
      });

      // Set up event handlers
      this.setupClientEvents(client, sessionId, userId);

      // Store client
      this.clients.set(sessionId, client);
      this.sessionStatus.set(sessionId, 'initializing');

      // Initialize client
      await client.initialize();

      logger.info(`Client ${sessionId} created successfully`);
      return { success: true, message: 'Client created' };
    } catch (error) {
      logger.error(`Error creating client ${sessionId}:`, error);
      return { success: false, message: error.message };
    }
  }

  /**
   * Set up event handlers for a client
   */
  setupClientEvents(client, sessionId, userId) {
    // QR Code event
    client.on('qr', async (qr) => {
      logger.info(`QR code generated for session ${sessionId}`);
      try {
        const qrCode = await QRCode.toDataURL(qr);
        this.qrCodes.set(sessionId, qrCode);
        this.sessionStatus.set(sessionId, 'qr_pending');
      } catch (error) {
        logger.error(`Error generating QR code for ${sessionId}:`, error);
      }
    });

    // Ready event
    client.on('ready', () => {
      logger.info(`Client ${sessionId} is ready`);
      this.sessionStatus.set(sessionId, 'connected');
      this.qrCodes.delete(sessionId);
    });

    // Authenticated event
    client.on('authenticated', () => {
      logger.info(`Client ${sessionId} authenticated`);
    });

    // Authentication failure
    client.on('auth_failure', (msg) => {
      logger.error(`Authentication failed for ${sessionId}:`, msg);
      this.sessionStatus.set(sessionId, 'auth_failed');
    });

    // Disconnected event
    client.on('disconnected', (reason) => {
      logger.warn(`Client ${sessionId} disconnected:`, reason);
      this.sessionStatus.set(sessionId, 'disconnected');
    });

    // Message received (for future webhook support)
    client.on('message', async (message) => {
      logger.debug(`Message received on ${sessionId} from ${message.from}`);
      // Future: Send to Django webhook
    });
  }

  /**
   * Get client by session ID
   */
  getClient(sessionId) {
    return this.clients.get(sessionId);
  }

  /**
   * Get session status
   */
  async getSessionStatus(sessionId) {
    const client = this.clients.get(sessionId);
    if (!client) {
      return {
        exists: false,
        status: 'not_found',
        qrCode: null,
        phoneNumber: null
      };
    }

    const status = this.sessionStatus.get(sessionId);
    const qrCode = this.qrCodes.get(sessionId);

    let phoneNumber = null;
    if (status === 'connected') {
      try {
        const info = await client.info;
        phoneNumber = info.wid.user;
      } catch (error) {
        logger.error(`Error getting phone number for ${sessionId}:`, error);
      }
    }

    return {
      exists: true,
      status: status || 'unknown',
      qrCode: qrCode || null,
      phoneNumber: phoneNumber,
      isReady: status === 'connected'
    };
  }

  /**
   * Disconnect and destroy client
   */
  async destroyClient(sessionId) {
    try {
      const client = this.clients.get(sessionId);
      if (!client) {
        return { success: false, message: 'Client not found' };
      }

      await client.destroy();
      this.clients.delete(sessionId);
      this.qrCodes.delete(sessionId);
      this.sessionStatus.delete(sessionId);

      logger.info(`Client ${sessionId} destroyed`);
      return { success: true, message: 'Client destroyed' };
    } catch (error) {
      logger.error(`Error destroying client ${sessionId}:`, error);
      return { success: false, message: error.message };
    }
  }

  /**
   * Send text message
   */
  async sendTextMessage(sessionId, recipient, message) {
    try {
      const client = this.clients.get(sessionId);
      if (!client) {
        return { success: false, message: 'Client not found' };
      }

      const status = this.sessionStatus.get(sessionId);
      if (status !== 'connected') {
        return { success: false, message: 'Client not connected' };
      }

      // Format recipient number
      const chatId = recipient.includes('@c.us') ? recipient : `${recipient}@c.us`;

      // Send message
      const result = await client.sendMessage(chatId, message);

      logger.info(`Message sent from ${sessionId} to ${recipient}`);
      return {
        success: true,
        messageId: result.id.id,
        timestamp: result.timestamp
      };
    } catch (error) {
      logger.error(`Error sending message from ${sessionId}:`, error);
      return { success: false, message: error.message };
    }
  }

  /**
   * Send media message
   */
  async sendMediaMessage(sessionId, recipient, mediaUrl, caption, mediaType) {
    try {
      const client = this.clients.get(sessionId);
      if (!client) {
        return { success: false, message: 'Client not found' };
      }

      const status = this.sessionStatus.get(sessionId);
      if (status !== 'connected') {
        return { success: false, message: 'Client not connected' };
      }

      const chatId = recipient.includes('@c.us') ? recipient : `${recipient}@c.us`;

      // Download media from URL
      const axios = require('axios');
      const response = await axios.get(mediaUrl, { responseType: 'arraybuffer' });
      const buffer = Buffer.from(response.data, 'binary');
      const base64 = buffer.toString('base64');

      // Determine mimetype
      const mimeType = response.headers['content-type'];

      // Create MessageMedia
      const { MessageMedia } = require('whatsapp-web.js');
      const media = new MessageMedia(mimeType, base64);

      // Send media
      const result = await client.sendMessage(chatId, media, { caption: caption });

      logger.info(`Media sent from ${sessionId} to ${recipient}`);
      return {
        success: true,
        messageId: result.id.id,
        timestamp: result.timestamp
      };
    } catch (error) {
      logger.error(`Error sending media from ${sessionId}:`, error);
      return { success: false, message: error.message };
    }
  }

  /**
   * Get all active sessions
   */
  getActiveSessions() {
    return Array.from(this.clients.keys()).map(sessionId => ({
      sessionId,
      status: this.sessionStatus.get(sessionId)
    }));
  }

  /**
   * Clean up inactive sessions
   */
  async cleanupInactiveSessions() {
    const now = Date.now();
    for (const [sessionId, client] of this.clients.entries()) {
      const status = this.sessionStatus.get(sessionId);
      if (status === 'disconnected' || status === 'auth_failed') {
        logger.info(`Cleaning up inactive session: ${sessionId}`);
        await this.destroyClient(sessionId);
      }
    }
  }
}

module.exports = new WhatsAppManager();

