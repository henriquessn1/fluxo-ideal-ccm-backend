const express = require('express');
const router = express.Router();
const { pgPool, redisClient } = require('../config/database');

// Cache configuration
const CACHE_TTL = 300; // 5 minutes in seconds

// GET all clients
router.get('/', async (req, res) => {
  try {
    // Try to get from cache first
    const cacheKey = 'clients:all';
    const cached = await redisClient.get(cacheKey);
    
    if (cached) {
      return res.json({
        source: 'cache',
        data: JSON.parse(cached)
      });
    }

    // Query database
    const result = await pgPool.query(`
      SELECT 
        id,
        name,
        dns,
        api_key,
        is_active,
        description,
        created_at,
        updated_at
      FROM clients
      ORDER BY name ASC
    `);

    // Cache the result
    await redisClient.setEx(cacheKey, CACHE_TTL, JSON.stringify(result.rows));

    res.json({
      source: 'database',
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching clients:', error);
    res.status(500).json({
      error: 'Failed to fetch clients',
      message: error.message
    });
  }
});

// GET single client by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Try cache first
    const cacheKey = `client:${id}`;
    const cached = await redisClient.get(cacheKey);
    
    if (cached) {
      return res.json({
        source: 'cache',
        data: JSON.parse(cached)
      });
    }

    // Query database
    const result = await pgPool.query(`
      SELECT * FROM clients WHERE id = $1
    `, [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Client not found'
      });
    }

    // Cache the result
    await redisClient.setEx(cacheKey, CACHE_TTL, JSON.stringify(result.rows[0]));

    res.json({
      source: 'database',
      data: result.rows[0]
    });
  } catch (error) {
    console.error('Error fetching client:', error);
    res.status(500).json({
      error: 'Failed to fetch client',
      message: error.message
    });
  }
});

// POST create new client
router.post('/', async (req, res) => {
  try {
    const { name, dns, api_key, is_active = true, description } = req.body;

    if (!name || !dns || !api_key) {
      return res.status(400).json({
        error: 'Name, DNS, and API key are required'
      });
    }

    const result = await pgPool.query(`
      INSERT INTO clients (name, dns, api_key, is_active, description)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `, [name, dns, api_key, is_active, description]);

    // Invalidate cache
    await redisClient.del('clients:all');

    res.status(201).json({
      message: 'Client created successfully',
      data: result.rows[0]
    });
  } catch (error) {
    console.error('Error creating client:', error);
    res.status(500).json({
      error: 'Failed to create client',
      message: error.message
    });
  }
});

// PUT update client
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { name, dns, api_key, is_active, description } = req.body;

    const result = await pgPool.query(`
      UPDATE clients 
      SET 
        name = COALESCE($1, name),
        dns = COALESCE($2, dns),
        api_key = COALESCE($3, api_key),
        is_active = COALESCE($4, is_active),
        description = COALESCE($5, description),
        updated_at = NOW()
      WHERE id = $6
      RETURNING *
    `, [name, dns, api_key, is_active, description, id]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Client not found'
      });
    }

    // Invalidate cache
    await redisClient.del('clients:all');
    await redisClient.del(`client:${id}`);

    res.json({
      message: 'Client updated successfully',
      data: result.rows[0]
    });
  } catch (error) {
    console.error('Error updating client:', error);
    res.status(500).json({
      error: 'Failed to update client',
      message: error.message
    });
  }
});

// DELETE client
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pgPool.query(`
      DELETE FROM clients WHERE id = $1 RETURNING id, name
    `, [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Client not found'
      });
    }

    // Invalidate cache
    await redisClient.del('clients:all');
    await redisClient.del(`client:${id}`);

    res.json({
      message: 'Client deleted successfully',
      data: result.rows[0]
    });
  } catch (error) {
    console.error('Error deleting client:', error);
    res.status(500).json({
      error: 'Failed to delete client',
      message: error.message
    });
  }
});

// GET client health checks
router.get('/:id/health', async (req, res) => {
  try {
    const { id } = req.params;
    const { limit = 50 } = req.query;

    const result = await pgPool.query(`
      SELECT 
        hc.id,
        hc.status,
        hc.response_time,
        hc.status_code,
        hc.error_message,
        hc.checked_at,
        s.name as service_name,
        s.endpoint
      FROM health_checks hc
      LEFT JOIN services s ON s.id = hc.service_id
      WHERE hc.client_id = $1 
      ORDER BY hc.checked_at DESC
      LIMIT $2
    `, [id, limit]);

    res.json({
      client_id: id,
      health_checks: result.rows
    });
  } catch (error) {
    console.error('Error fetching health checks:', error);
    res.status(500).json({
      error: 'Failed to fetch health checks',
      message: error.message
    });
  }
});

module.exports = router;