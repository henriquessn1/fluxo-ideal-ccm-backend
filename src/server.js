const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const { pgPool, redisClient, connectRedis, testPgConnection } = require('./config/database');
const clientRoutes = require('./routes/clientRoutes');
const healthRoutes = require('./routes/healthRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000,
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
  message: 'Too many requests from this IP, please try again later.'
});
app.use('/api', limiter);

// Routes
app.use('/api/health', healthRoutes);
app.use('/api/clients', clientRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Fluxo Ideal CCM Backend API',
    version: '1.0.0',
    status: 'running',
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: {
      message: err.message || 'Internal Server Error',
      status: err.status || 500,
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: {
      message: 'Route not found',
      status: 404,
      path: req.originalUrl
    }
  });
});

// Start server
const startServer = async () => {
  try {
    // Connect to databases
    await connectRedis();
    await testPgConnection();
    
    // Start Express server
    app.listen(PORT, () => {
      console.log(`
========================================
🚀 Server running on http://localhost:${PORT}
📝 Environment: ${process.env.NODE_ENV}
🔄 API Base: http://localhost:${PORT}/api
========================================
      `);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received. Shutting down gracefully...');
  await pgPool.end();
  await redisClient.quit();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received. Shutting down gracefully...');
  await pgPool.end();
  await redisClient.quit();
  process.exit(0);
});

startServer();

module.exports = app;