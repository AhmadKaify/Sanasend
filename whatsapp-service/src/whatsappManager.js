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
    this.qrCodeTimestamps = new Map(); // Track when QR codes were created
    this.sessionStatus = new Map();
    
    // Start periodic QR code cleanup (every minute)
    this.startQRCodeCleanup();
  }

  /**
   * Start periodic QR code cleanup
   */
  startQRCodeCleanup() {
    setInterval(() => {
      this.cleanupExpiredQRCodes();
    }, 60000); // Run every 60 seconds
    
    logger.info('Started QR code cleanup task (runs every 60 seconds)');
  }

  /**
   * Clean up QR codes that have been pending for more than 120 seconds
   */
  cleanupExpiredQRCodes() {
    const now = Date.now();
    const maxAge = 120000; // 120 seconds (QR expires at 60s, cleanup at 120s)
    let cleanedCount = 0;
    
    for (const [sessionId, timestamp] of this.qrCodeTimestamps.entries()) {
      const age = now - timestamp;
      
      if (age > maxAge) {
        const status = this.sessionStatus.get(sessionId);
        
        // Only clean up if still in qr_pending state
        if (status === 'qr_pending') {
          logger.info(`Cleaning up expired QR code for session ${sessionId} (age: ${Math.floor(age / 1000)}s)`);
          
          this.qrCodes.delete(sessionId);
          this.qrCodeTimestamps.delete(sessionId);
          cleanedCount++;
        } else {
          // QR code is no longer pending, just remove timestamp
          this.qrCodeTimestamps.delete(sessionId);
        }
      }
    }
    
    if (cleanedCount > 0) {
      logger.info(`QR code cleanup: removed ${cleanedCount} expired QR codes`);
    }
  }

  /**
   * Create a new WhatsApp client
   */
  async createClient(sessionId, userId, isRestoration = false) {
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

      logger.info(`Client ${sessionId} ${isRestoration ? 'restored' : 'created'} successfully`);
      return { success: true, message: 'Client created', isRestoration };
    } catch (error) {
      logger.error(`Error creating client ${sessionId}:`, error);
      
      // Clean up on failure
      this.clients.delete(sessionId);
      this.sessionStatus.delete(sessionId);
      
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
        this.qrCodeTimestamps.set(sessionId, Date.now()); // Track creation time
        this.sessionStatus.set(sessionId, 'qr_pending');
        
        // Notify Django via webhook
        await this.notifyDjangoWebhook(sessionId, userId, {
          status: 'qr_pending',
          qrCode: qrCode
        });
      } catch (error) {
        logger.error(`Error generating QR code for ${sessionId}:`, error);
      }
    });

    // Ready event
    client.on('ready', async () => {
      logger.info(`Client ${sessionId} is ready`);
      this.sessionStatus.set(sessionId, 'connected');
      this.qrCodes.delete(sessionId);
      this.qrCodeTimestamps.delete(sessionId); // Clean up timestamp
      
      // Get phone number
      let phoneNumber = null;
      try {
        const info = client.info;
        phoneNumber = info.wid.user;
      } catch (error) {
        logger.error(`Error getting phone number for ${sessionId}:`, error);
      }
      
      // Notify Django via webhook
      await this.notifyDjangoWebhook(sessionId, userId, {
        status: 'connected',
        phoneNumber: phoneNumber
      });
    });

    // Authenticated event
    client.on('authenticated', () => {
      logger.info(`Client ${sessionId} authenticated`);
    });

    // Authentication failure
    client.on('auth_failure', async (msg) => {
      logger.error(`Authentication failed for ${sessionId}:`, msg);
      this.sessionStatus.set(sessionId, 'auth_failed');
      
      // Notify Django via webhook
      await this.notifyDjangoWebhook(sessionId, userId, {
        status: 'auth_failed',
        error: msg
      });
    });

    // Disconnected event
    client.on('disconnected', async (reason) => {
      logger.warn(`Client ${sessionId} disconnected:`, reason);
      this.sessionStatus.set(sessionId, 'disconnected');
      
      // Notify Django via webhook
      await this.notifyDjangoWebhook(sessionId, userId, {
        status: 'disconnected',
        reason: reason
      });
    });

    // Message received (for future webhook support)
    client.on('message', async (message) => {
      logger.debug(`Message received on ${sessionId} from ${message.from}`);
      // Future: Send to Django webhook
    });
  }
  
  /**
   * Notify Django backend via webhook about session status changes
   */
  async notifyDjangoWebhook(sessionId, userId, data) {
    if (!config.webhookUrl) {
      logger.debug('Webhook URL not configured, skipping notification');
      return;
    }
    
    try {
      const axios = require('axios');
      await axios.post(config.webhookUrl, {
        sessionId: sessionId,
        userId: userId,
        timestamp: new Date().toISOString(),
        ...data
      }, {
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.apiKey
        },
        timeout: 5000
      });
      logger.debug(`Webhook notification sent for session ${sessionId}`);
    } catch (error) {
      logger.error(`Failed to send webhook notification: ${error.message}`);
      // Don't throw - webhook failures shouldn't break the flow
    }
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
        phoneNumber: null,
        isReady: false
      };
    }

    let status = this.sessionStatus.get(sessionId);
    const qrCode = this.qrCodes.get(sessionId);

    // Verify client is actually ready if status says connected
    if (status === 'connected') {
      try {
        const state = await client.getState();
        if (state !== 'CONNECTED') {
          logger.warn(`Client ${sessionId} status mismatch: stored as connected but state is ${state}`);
          status = 'disconnected';
          this.sessionStatus.set(sessionId, 'disconnected');
        }
      } catch (error) {
        logger.error(`Error getting state for ${sessionId}:`, error);
        status = 'disconnected';
        this.sessionStatus.set(sessionId, 'disconnected');
      }
    }

    let phoneNumber = null;
    if (status === 'connected') {
      try {
        const info = client.info;
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
      this.qrCodeTimestamps.delete(sessionId);
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
        logger.error(`Client ${sessionId} not found in memory`);
        return { success: false, message: 'Client not found. Please reconnect the session.' };
      }

      const status = this.sessionStatus.get(sessionId);
      if (status !== 'connected') {
        logger.error(`Client ${sessionId} status is ${status}, not connected`);
        return { success: false, message: `Client not connected (status: ${status}). Please reconnect the session.` };
      }

      // Check if client is actually ready
      try {
        const state = await client.getState();
        if (state !== 'CONNECTED') {
          logger.error(`Client ${sessionId} state is ${state}, not CONNECTED`);
          this.sessionStatus.set(sessionId, 'disconnected');
          return { success: false, message: `Client not ready (state: ${state}). Please reconnect the session.` };
        }
      } catch (stateError) {
        logger.error(`Error checking state for ${sessionId}:`, stateError);
        this.sessionStatus.set(sessionId, 'disconnected');
        return { success: false, message: 'Client session closed. Please reconnect the session.' };
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
      
      // If error is related to closed session, update status
      if (error.message && (error.message.includes('Session closed') || error.message.includes('Protocol error'))) {
        this.sessionStatus.set(sessionId, 'disconnected');
        return { success: false, message: 'Client session closed. Please reconnect the session.' };
      }
      
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
        logger.error(`Client ${sessionId} not found in memory`);
        return { success: false, message: 'Client not found. Please reconnect the session.' };
      }

      const status = this.sessionStatus.get(sessionId);
      if (status !== 'connected') {
        logger.error(`Client ${sessionId} status is ${status}, not connected`);
        return { success: false, message: `Client not connected (status: ${status}). Please reconnect the session.` };
      }

      // Check if client is actually ready
      try {
        const state = await client.getState();
        if (state !== 'CONNECTED') {
          logger.error(`Client ${sessionId} state is ${state}, not CONNECTED`);
          this.sessionStatus.set(sessionId, 'disconnected');
          return { success: false, message: `Client not ready (state: ${state}). Please reconnect the session.` };
        }
      } catch (stateError) {
        logger.error(`Error checking state for ${sessionId}:`, stateError);
        this.sessionStatus.set(sessionId, 'disconnected');
        return { success: false, message: 'Client session closed. Please reconnect the session.' };
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
      
      // If error is related to closed session, update status
      if (error.message && (error.message.includes('Session closed') || error.message.includes('Protocol error'))) {
        this.sessionStatus.set(sessionId, 'disconnected');
        return { success: false, message: 'Client session closed. Please reconnect the session.' };
      }
      
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

  /**
   * Restore sessions from Django on startup
   */
  async restoreSessions() {
    logger.info('Starting session restoration...');
    
    try {
      const axios = require('axios');
      const response = await axios.get(
        `${config.djangoApiUrl}/api/v1/sessions/active-sessions/`,
        {
          headers: {
            'x-api-key': config.apiKey,
            'Content-Type': 'application/json'
          },
          timeout: 10000
        }
      );

      if (!response.data.success) {
        logger.error('Failed to fetch active sessions from Django');
        return { restored: 0, failed: 0 };
      }

      const sessions = response.data.data.sessions || [];
      logger.info(`Found ${sessions.length} sessions to restore`);

      let restored = 0;
      let failed = 0;

      for (const session of sessions) {
        try {
          logger.info(`Restoring session: ${session.session_id} (${session.instance_name})`);
          
          // Try to restore the client
          const result = await this.createClient(session.session_id, session.user_id, true);
          
          if (result.success) {
            restored++;
            logger.info(`✓ Session restored: ${session.session_id}`);
          } else {
            failed++;
            logger.warn(`✗ Failed to restore session ${session.session_id}: ${result.message}`);
            
            // Notify Django via webhook that session couldn't be restored
            await this.notifyDjangoWebhook(session.session_id, session.user_id, {
              status: 'disconnected',
              error: 'Failed to restore session on Node.js restart'
            });
          }
        } catch (error) {
          failed++;
          logger.error(`✗ Error restoring session ${session.session_id}:`, error);
        }
      }

      logger.info(`Session restoration complete: ${restored} restored, ${failed} failed`);
      return { restored, failed, total: sessions.length };

    } catch (error) {
      logger.error('Failed to restore sessions:', error);
      return { restored: 0, failed: 0, error: error.message };
    }
  }
}

module.exports = new WhatsAppManager();

