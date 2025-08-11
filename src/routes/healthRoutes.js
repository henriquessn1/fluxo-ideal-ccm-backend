const express = require('express');
const router = express.Router();
const { pgPool, redisClient } = require('../config/database');

// Health check endpoint
router.get('/', async (req, res) => {
  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    services: {}
  };

  // Check PostgreSQL
  try {
    const pgResult = await pgPool.query('SELECT 1');
    health.services.postgresql = {
      status: 'connected',
      host: process.env.DB_HOST,
      database: process.env.DB_NAME
    };
  } catch (error) {
    health.services.postgresql = {
      status: 'disconnected',
      error: error.message
    };
    health.status = 'degraded';
  }

  // Check Redis
  try {
    await redisClient.ping();
    health.services.redis = {
      status: 'connected',
      host: process.env.REDIS_HOST
    };
  } catch (error) {
    health.services.redis = {
      status: 'disconnected',
      error: error.message
    };
    health.status = 'degraded';
  }

  const statusCode = health.status === 'ok' ? 200 : 503;
  res.status(statusCode).json(health);
});

module.exports = router;