const { Pool } = require('pg');
const redis = require('redis');
require('dotenv').config();

// PostgreSQL Configuration
const pgPool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Redis Configuration
const redisClient = redis.createClient({
  socket: {
    host: process.env.REDIS_HOST,
    port: process.env.REDIS_PORT,
  },
  password: process.env.REDIS_PASSWORD,
  legacyMode: false,
});

// Redis connection handling
redisClient.on('connect', () => {
  console.log('✅ Redis connected successfully');
});

redisClient.on('error', (err) => {
  console.error('❌ Redis connection error:', err);
});

// Connect to Redis
const connectRedis = async () => {
  try {
    await redisClient.connect();
  } catch (error) {
    console.error('Failed to connect to Redis:', error);
  }
};

// Test PostgreSQL connection
const testPgConnection = async () => {
  try {
    const client = await pgPool.connect();
    const res = await client.query('SELECT NOW()');
    console.log('✅ PostgreSQL connected:', res.rows[0].now);
    client.release();
  } catch (error) {
    console.error('❌ PostgreSQL connection error:', error);
  }
};

module.exports = {
  pgPool,
  redisClient,
  connectRedis,
  testPgConnection
};