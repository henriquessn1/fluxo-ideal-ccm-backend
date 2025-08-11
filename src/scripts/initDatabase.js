const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || '10.102.1.16',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'geraldb_user',
  password: process.env.DB_PASSWORD || 'Jk16OFyM6rBebmWJS5YPp6Y9',
  database: process.env.DB_NAME || 'geraldb',
});

async function initDatabase() {
  console.log('🔧 Iniciando configuração do banco de dados...\n');
  
  try {
    // Test connection
    console.log('📡 Testando conexão com PostgreSQL...');
    const testResult = await pool.query('SELECT NOW()');
    console.log('✅ Conectado ao PostgreSQL:', testResult.rows[0].now);
    console.log(`📍 Servidor: ${process.env.DB_HOST || '10.102.1.16'}`);
    console.log(`📦 Database: ${process.env.DB_NAME || 'geraldb'}\n`);

    // Execute SQL commands individually
    const sqlCommands = getSQLCommands();
    console.log(`📝 Executando ${sqlCommands.length} comandos SQL...\n`);

    for (let i = 0; i < sqlCommands.length; i++) {
      const { description, sql } = sqlCommands[i];
      console.log(`[${i + 1}/${sqlCommands.length}] ${description}...`);
      
      try {
        await pool.query(sql);
        console.log(`✅ ${description} - OK`);
      } catch (error) {
        if (error.code === '42P07') { // Duplicate table
          console.log(`⚠️  Objeto já existe, pulando...`);
        } else if (error.code === '23505') { // Duplicate key
          console.log(`⚠️  Registro já existe, pulando...`);
        } else if (error.code === '42P01') { // Table doesn't exist
          console.log(`⚠️  Tabela não existe ainda, será criada em comando posterior...`);
        } else {
          console.log(`❌ Erro: ${error.message}`);
        }
      }
    }

    console.log('\n✅ Configuração do banco de dados concluída!');
    
    // Show table status
    console.log('\n📊 Status das tabelas:');
    const tables = await pool.query(`
      SELECT tablename FROM pg_tables 
      WHERE schemaname = 'public' 
      ORDER BY tablename;
    `);
    
    for (const table of tables.rows) {
      const count = await pool.query(`SELECT COUNT(*) FROM ${table.tablename}`);
      console.log(`   - ${table.tablename}: ${count.rows[0].count} registros`);
    }

  } catch (error) {
    console.error('\n❌ Erro ao configurar banco de dados:', error.message);
    process.exit(1);
  } finally {
    await pool.end();
    console.log('\n👋 Conexão fechada.');
  }
}

function getSQLCommands() {
  return [
    {
      description: 'Habilitar extensão uuid-ossp',
      sql: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`
    },
    {
      description: 'Inserir dados de exemplo para clients',
      sql: `INSERT INTO clients (id, name, dns, api_key, is_active, description) VALUES
        (uuid_generate_v4(), 'Server-Web-01', 'web01.fluxoideal.com', 'web01-api-key-123', true, 'Servidor web principal'),
        (uuid_generate_v4(), 'Server-DB-01', 'db01.fluxoideal.com', 'db01-api-key-456', true, 'Servidor de banco de dados'),
        (uuid_generate_v4(), 'Server-App-01', 'app01.fluxoideal.com', 'app01-api-key-789', true, 'Servidor de aplicação'),
        (uuid_generate_v4(), 'Server-Cache-01', 'cache01.fluxoideal.com', 'cache01-api-key-abc', false, 'Servidor de cache Redis'),
        (uuid_generate_v4(), 'Server-Mail-01', 'mail01.fluxoideal.com', 'mail01-api-key-def', true, 'Servidor de email')
        ON CONFLICT (name) DO NOTHING`
    },
    {
      description: 'Inserir serviços de exemplo',
      sql: `INSERT INTO services (id, client_id, name, endpoint, method, expected_status, timeout, is_active, description)
        SELECT 
          uuid_generate_v4(),
          c.id,
          'Health Check',
          'https://' || c.dns || '/health',
          'GET',
          200,
          30,
          true,
          'Verificação de saúde básica'
        FROM clients c
        WHERE c.is_active = true`
    },
    {
      description: 'Inserir health checks de exemplo',
      sql: `INSERT INTO health_checks (id, client_id, service_id, status, response_time, status_code)
        SELECT 
          uuid_generate_v4(),
          c.id,
          s.id,
          CASE 
            WHEN c.name LIKE '%Cache%' THEN 'DOWN'
            WHEN c.name LIKE '%App%' THEN 'DEGRADED'
            ELSE 'UP'
          END,
          CASE 
            WHEN c.name LIKE '%Cache%' THEN NULL
            ELSE (RANDOM() * 500 + 50)::INTEGER
          END,
          CASE 
            WHEN c.name LIKE '%Cache%' THEN NULL
            WHEN c.name LIKE '%App%' THEN 503
            ELSE 200
          END
        FROM clients c
        JOIN services s ON s.client_id = c.id`
    }
  ];
}

// Run initialization
console.log('========================================');
console.log('  Fluxo Ideal CCM - Database Setup');
console.log('========================================\n');

initDatabase();