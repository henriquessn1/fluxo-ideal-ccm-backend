-- Create clients table
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'offline',
    ip_address VARCHAR(45) NOT NULL,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ip_address)
);

-- Create metrics table for historical data
CREATE TABLE IF NOT EXISTS client_metrics (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),
    network_in BIGINT,
    network_out BIGINT,
    response_time INTEGER,
    INDEX idx_client_timestamp (client_id, timestamp)
);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) DEFAULT 'info',
    message TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Create users table (if not using Keycloak)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);
CREATE INDEX IF NOT EXISTS idx_clients_last_seen ON clients(last_seen);
CREATE INDEX IF NOT EXISTS idx_alerts_client_id ON alerts(client_id);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(resolved);

-- Insert sample data
INSERT INTO clients (name, ip_address, status, cpu_usage, memory_usage, disk_usage) VALUES
    ('Server-Web-01', '10.102.1.20', 'online', 45.5, 72.3, 55.0),
    ('Server-DB-01', '10.102.1.21', 'online', 35.2, 85.6, 78.5),
    ('Server-App-01', '10.102.1.22', 'warning', 78.9, 92.1, 45.0),
    ('Server-Cache-01', '10.102.1.23', 'offline', 0.0, 0.0, 0.0),
    ('Server-Mail-01', '10.102.1.24', 'online', 22.1, 45.5, 35.8)
ON CONFLICT (ip_address) DO NOTHING;

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();