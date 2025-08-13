CREATE TABLE IF NOT EXISTS log_sources (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('application', 'system', 'security', 'audit', 'performance', 'custom')),
    environment VARCHAR(50) NOT NULL CHECK (environment IN ('development', 'staging', 'production', 'testing')),
    tags TEXT[] DEFAULT '{}',
    api_key VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'deleted')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_log_at TIMESTAMP WITH TIME ZONE,
    log_count BIGINT DEFAULT 0 CHECK (log_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_log_sources_user_id ON log_sources(user_id);
CREATE INDEX IF NOT EXISTS idx_log_sources_api_key ON log_sources(api_key);
CREATE INDEX IF NOT EXISTS idx_log_sources_status ON log_sources(status);
CREATE INDEX IF NOT EXISTS idx_log_sources_environment ON log_sources(environment);
CREATE INDEX IF NOT EXISTS idx_log_sources_source_type ON log_sources(source_type);
CREATE INDEX IF NOT EXISTS idx_log_sources_created_at ON log_sources(created_at);
CREATE INDEX IF NOT EXISTS idx_log_sources_last_log_at ON log_sources(last_log_at);
CREATE INDEX IF NOT EXISTS idx_log_sources_user_status ON log_sources(user_id, status);
CREATE INDEX IF NOT EXISTS idx_log_sources_user_environment ON log_sources(user_id, environment);
CREATE INDEX IF NOT EXISTS idx_log_sources_status_environment ON log_sources(status, environment);
    
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_updated_at ON log_sources;

CREATE TRIGGER trg_set_updated_at
    BEFORE UPDATE ON log_sources
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();