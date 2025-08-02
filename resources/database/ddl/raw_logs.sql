CREATE TABLE IF NOT EXISTS raw_logs (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(255) NOT NULL,
    data TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_logs_timestamp ON raw_logs(timestamp);

CREATE INDEX IF NOT EXISTS idx_raw_logs_provider ON raw_logs(provider);