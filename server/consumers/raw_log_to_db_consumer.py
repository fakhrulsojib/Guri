import os
import json
import time
import threading
from confluent_kafka import Consumer
from database.database import execute_query
from model.raw_log import RawLog
import structlog

logger = structlog.get_logger()

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9093")
KAFKA_TOPIC_RAW = os.environ.get("KAFKA_TOPIC_RAW", "raw_logs")
KAFKA_GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "raw_log_to_db_consumer_group")

INSERT_LOG_SQL = """
INSERT INTO raw_logs (source_id, level, message, data, metadata, timestamp, trace_id, span_id) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

UPDATE_LOG_COUNT_SQL = """
UPDATE log_sources 
SET log_count = log_count + 1, 
    last_log_at = GREATEST(COALESCE(last_log_at, %s), %s)
WHERE id = %s;
"""

class RawLogToDBConsumer:
    def __init__(self):
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            logger.warning("Consumer already running")
            return
        self._running = True
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
        logger.info("RawLogToDBConsumer started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        logger.info("RawLogToDBConsumer stopped")

    def _consume_loop(self):
        consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': KAFKA_GROUP_ID,
            'auto.offset.reset': 'earliest',
        })
        consumer.subscribe([KAFKA_TOPIC_RAW])
        logger.info("Listening to Kafka topic", topic=KAFKA_TOPIC_RAW)
        
        try:
            while self._running:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error("Kafka error", error=str(msg.error()))
                    continue
                
                try:
                    log_data = json.loads(msg.value().decode('utf-8'))
                    
                    source_id = log_data.get('source_id')
                    if not source_id:
                        logger.warning("Skipping log without source_id")
                        continue
                    
                    log_data_for_validation = log_data.copy()
                    if 'source_id' in log_data_for_validation:
                        del log_data_for_validation['source_id']
                    log_data_for_validation['api_key'] = 'dummy_for_validation'
                    
                    log = RawLog(**log_data_for_validation)
                    
                    params = (
                        source_id,
                        log.level.value,
                        log.message,
                        json.dumps(log.data),
                        json.dumps(log.metadata) if log.metadata else None,
                        log.timestamp,
                        log.trace_id,
                        log.span_id
                    )
                    
                    execute_query(INSERT_LOG_SQL, params)
                    
                    try:
                        execute_query(UPDATE_LOG_COUNT_SQL, (log.timestamp, log.timestamp, source_id))
                        logger.info("Log count updated", source_id=source_id)
                    except Exception as e:
                        logger.error("Failed to update log count", source_id=source_id, error=str(e))
                    
                    logger.info("Log saved to database", log_data=log.model_dump(), source_id=source_id)
                except Exception as e:
                    logger.error("Failed to save log to database", error=str(e))
        finally:
            consumer.close()

raw_log_to_db_consumer = RawLogToDBConsumer()

def start_raw_log_to_db_consumer():
    raw_log_to_db_consumer.start()

def stop_raw_log_to_db_consumer():
    raw_log_to_db_consumer.stop()

if __name__ == "__main__":
    start_raw_log_to_db_consumer()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_raw_log_to_db_consumer() 