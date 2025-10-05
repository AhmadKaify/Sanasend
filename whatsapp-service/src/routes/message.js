/**
 * Message sending routes
 */
const express = require('express');
const router = express.Router();
const whatsappManager = require('../whatsappManager');
const logger = require('../logger');

/**
 * Send text message
 * POST /api/message/send-text
 */
router.post('/send-text', async (req, res) => {
  try {
    const { sessionId, recipient, message } = req.body;

    if (!sessionId || !recipient || !message) {
      return res.status(400).json({
        success: false,
        error: 'sessionId, recipient, and message are required'
      });
    }

    const result = await whatsappManager.sendTextMessage(sessionId, recipient, message);
    
    if (!result.success) {
      return res.status(400).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error('Error sending text message:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Send media message
 * POST /api/message/send-media
 */
router.post('/send-media', async (req, res) => {
  try {
    const { sessionId, recipient, mediaUrl, caption, mediaType } = req.body;

    if (!sessionId || !recipient || !mediaUrl) {
      return res.status(400).json({
        success: false,
        error: 'sessionId, recipient, and mediaUrl are required'
      });
    }

    const result = await whatsappManager.sendMediaMessage(
      sessionId,
      recipient,
      mediaUrl,
      caption || '',
      mediaType || 'image'
    );
    
    if (!result.success) {
      return res.status(400).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error('Error sending media message:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;

