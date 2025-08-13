CREATE TABLE IF NOT EXISTS raw_logs (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES log_sources(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL DEFAULT 'INFO',
    message TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    trace_id VARCHAR(100),
    span_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_logs_source_id ON raw_logs(source_id);
CREATE INDEX IF NOT EXISTS idx_raw_logs_timestamp ON raw_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_logs_level ON raw_logs(level);
CREATE INDEX IF NOT EXISTS idx_raw_logs_trace_id ON raw_logs(trace_id);
CREATE INDEX IF NOT EXISTS idx_raw_logs_span_id ON raw_logs(span_id);
CREATE INDEX IF NOT EXISTS idx_raw_logs_created_at ON raw_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_raw_logs_source_timestamp ON raw_logs(source_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_raw_logs_level_timestamp ON raw_logs(level, timestamp DESC);
