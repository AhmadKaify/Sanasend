/**
 * Session management routes
 */
const express = require('express');
const router = express.Router();
const whatsappManager = require('../whatsappManager');
const logger = require('../logger');

/**
 * Initialize new session
 * POST /api/session/init
 */
router.post('/init', async (req, res) => {
  try {
    const { sessionId, userId } = req.body;

    if (!sessionId || !userId) {
      return res.status(400).json({
        success: false,
        error: 'sessionId and userId are required'
      });
    }

    const result = await whatsappManager.createClient(sessionId, userId);
    
    if (!result.success) {
      return res.status(400).json(result);
    }

    // Wait for QR code generation (max 30 seconds)
    let attempts = 0;
    const maxAttempts = 30;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const status = await whatsappManager.getSessionStatus(sessionId);
      
      if (status.qrCode) {
        return res.json({
          success: true,
          sessionId,
          status: 'qr_pending',
          qrCode: status.qrCode
        });
      }
      
      if (status.status === 'connected') {
        return res.json({
          success: true,
          sessionId,
          status: 'connected',
          phoneNumber: status.phoneNumber
        });
      }
      
      attempts++;
    }

    return res.status(408).json({
      success: false,
      error: 'QR code generation timeout'
    });
  } catch (error) {
    logger.error('Error initializing session:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get session status
 * GET /api/session/status/:sessionId
 */
router.get('/status/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;
    const status = await whatsappManager.getSessionStatus(sessionId);
    
    res.json({
      success: true,
      ...status
    });
  } catch (error) {
    logger.error('Error getting session status:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Disconnect session
 * POST /api/session/disconnect
 */
router.post('/disconnect', async (req, res) => {
  try {
    const { sessionId } = req.body;

    if (!sessionId) {
      return res.status(400).json({
        success: false,
        error: 'sessionId is required'
      });
    }

    const result = await whatsappManager.destroyClient(sessionId);
    res.json(result);
  } catch (error) {
    logger.error('Error disconnecting session:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get all active sessions
 * GET /api/session/list
 */
router.get('/list', (req, res) => {
  try {
    const sessions = whatsappManager.getActiveSessions();
    res.json({
      success: true,
      sessions,
      count: sessions.length
    });
  } catch (error) {
    logger.error('Error listing sessions:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;

