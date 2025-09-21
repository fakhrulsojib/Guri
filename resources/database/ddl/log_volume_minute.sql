CREATE TABLE IF NOT EXISTS log_volume_minute (
    source_id     INTEGER NOT NULL
                  REFERENCES log_sources(id) ON DELETE CASCADE,
    bucket_minute TIMESTAMPTZ NOT NULL,
    log_count     INTEGER NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_id, bucket_minute)
);

CREATE INDEX IF NOT EXISTS idx_log_volume_minute_time
    ON log_volume_minute (bucket_minute);
