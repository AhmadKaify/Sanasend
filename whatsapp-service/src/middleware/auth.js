/**
 * Authentication middleware
 */
const config = require('../config');
const logger = require('../logger');

/**
 * Verify API key from request header
 */
function authenticateApiKey(req, res, next) {
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey) {
    logger.warn('API request without API key');
    return res.status(401).json({
      success: false,
      error: 'API key required'
    });
  }
  
  if (apiKey !== config.apiKey) {
    logger.warn('API request with invalid API key');
    return res.status(401).json({
      success: false,
      error: 'Invalid API key'
    });
  }
  
  next();
}

module.exports = { authenticateApiKey };

