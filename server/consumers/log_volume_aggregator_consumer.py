import os
import json
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple
from confluent_kafka import Consumer
from database.database import execute_query
import structlog

logger = structlog.get_logger()

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9093")
KAFKA_TOPIC_RAW = os.environ.get("KAFKA_TOPIC_RAW", "raw_logs")
KAFKA_GROUP_ID = os.environ.get("KAFKA_LOG_VOLUME_AGGREGATOR_GROUP_ID", "log_volume_aggregator_group")

# SQL for upserting log volume data
UPSERT_LOG_VOLUME_SQL = """
INSERT INTO log_volume_minute (source_id, bucket_minute, log_count)
VALUES (%s, %s, %s)
ON CONFLICT (source_id, bucket_minute)
DO UPDATE SET log_count = log_volume_minute.log_count + %s;
"""

class LogVolumeAggregatorConsumer:
    def __init__(self):
        self._running = False
        self._thread = None
        self._volume_counts: Dict[Tuple[int, datetime], int] = {}
        self._lock = threading.Lock()
        self._last_cleanup = datetime.now(timezone.utc)
        
        # Import anomaly detection service
        try:
            from services.anomaly_detection_service import anomaly_detection_service
            self.anomaly_service = anomaly_detection_service
            logger.info("Anomaly detection service initialized")
        except Exception as e:
            logger.error("Failed to initialize anomaly detection service", error=str(e))
            self.anomaly_service = None

    def start(self):
        if self._running:
            logger.warning("LogVolumeAggregatorConsumer already running")
            return
        self._running = True
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
        logger.info("LogVolumeAggregatorConsumer started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        logger.info("LogVolumeAggregatorConsumer stopped")

    def _truncate_to_minute_start(self, timestamp: datetime) -> datetime:
        """Truncate timestamp to the start of its UTC minute"""
        return timestamp.replace(second=0, microsecond=0)


    def _flush_volume_counts_to_db(self) -> None:
        """Flush accumulated volume counts to database in batch"""
        if not self._volume_counts:
            return
        
        with self._lock:
            counts_to_flush = self._volume_counts.copy()
            self._volume_counts.clear()
        
        if not counts_to_flush:
            return
        
        try:
            from database.database import get_connection
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    # Prepare batch data
                    batch_data = []
                    for (source_id, bucket_minute), count in counts_to_flush.items():
                        batch_data.append((source_id, bucket_minute, count, count))
                    
                    # Execute batch upsert
                    cursor.executemany(UPSERT_LOG_VOLUME_SQL, batch_data)
                    conn.commit()
            
            logger.info(f"Batch flushed {len(counts_to_flush)} volume counts to database")
        except Exception as e:
            logger.error("Failed to batch flush volume counts to database", error=str(e))
            # Re-add failed counts back to the dictionary
            with self._lock:
                for key, count in counts_to_flush.items():
                    self._volume_counts[key] = self._volume_counts.get(key, 0) + count

    def _cleanup_old_data(self) -> None:
        """Clean up data older than 30 minutes from memory"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        with self._lock:
            keys_to_remove = [
                key for key in self._volume_counts.keys()
                if key[1] < cutoff_time
            ]
            
            for key in keys_to_remove:
                del self._volume_counts[key]
            
            if keys_to_remove:
                logger.info(f"Cleaned up {len(keys_to_remove)} old volume count entries")

    def _run_anomaly_detection(self) -> None:
        """Run anomaly detection on the last 30 minutes of data"""
        if not self.anomaly_service or not self.anomaly_service.is_model_available():
            logger.warning("Anomaly detection service not available")
            return
        
        try:
            anomalies = self.anomaly_service.detect_anomalies(minutes=30)
            
            if anomalies:
                logger.warning(f"Detected {len(anomalies)} anomalies in last 30 minutes")
                
                # Log top anomalies
                for i, anomaly in enumerate(anomalies[:5]):  # Log top 5
                    logger.warning(
                        f"Anomaly #{i+1}: Source {anomaly['source_id']} at {anomaly['timestamp']} "
                        f"with {anomaly['log_count']} logs (score: {anomaly['anomaly_score']:.3f})"
                    )
            else:
                logger.info("No anomalies detected in last 30 minutes")
                
        except Exception as e:
            logger.error("Failed to run anomaly detection", error=str(e))


    def _process_log_batch(self, messages) -> None:
        """Process a batch of log messages"""
        batch_counts = {}
        
        for msg in messages:
            try:
                log_data = json.loads(msg.value().decode('utf-8'))
                
                source_id = log_data.get('source_id')
                timestamp_str = log_data.get('timestamp')
                
                if not source_id or not timestamp_str:
                    logger.warning("Skipping log without source_id or timestamp")
                    continue
                
                # Parse timestamp
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning("Invalid timestamp format", timestamp=timestamp_str)
                    continue
                
                # Truncate to minute start
                bucket_minute = self._truncate_to_minute_start(timestamp)
                key = (source_id, bucket_minute)
                
                # Add to batch counts
                batch_counts[key] = batch_counts.get(key, 0) + 1
                
            except Exception as e:
                logger.error("Failed to process log message", error=str(e))
        
        # Add batch counts to main dictionary
        if batch_counts:
            with self._lock:
                for key, count in batch_counts.items():
                    self._volume_counts[key] = self._volume_counts.get(key, 0) + count
            
            logger.info(f"Processed batch of {len(messages)} logs, aggregated into {len(batch_counts)} minute buckets")

    def _consume_loop(self):
        consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': KAFKA_GROUP_ID,
            'auto.offset.reset': 'earliest',
        })
        consumer.subscribe([KAFKA_TOPIC_RAW])
        logger.info("Listening to Kafka topic for log volume aggregation", topic=KAFKA_TOPIC_RAW)
        
        last_flush_time = time.time()
        last_cleanup_time = time.time()
        last_anomaly_check_time = time.time()
        
        try:
            while self._running:
                # Batch consume logs every 5 minutes
                current_time = time.time()
                
                # Check if it's time to flush, cleanup, or run anomaly detection
                should_flush = current_time - last_flush_time >= 300  # 5 minutes
                should_cleanup = current_time - last_cleanup_time >= 600  # 10 minutes
                should_run_anomaly = current_time - last_anomaly_check_time >= 300  # 5 minutes
                
                if should_flush or should_cleanup or should_run_anomaly:
                    # Process any remaining logs in a small batch before maintenance tasks
                    messages = []
                    for _ in range(100):  # Small batch for remaining logs
                        msg = consumer.poll(timeout=0.01)
                        if msg is None:
                            break
                        if msg.error():
                            logger.error("Kafka error", error=str(msg.error()))
                            continue
                        messages.append(msg)
                    
                    if messages:
                        self._process_log_batch(messages)
                    
                    # Perform maintenance tasks
                    if should_flush:
                        self._flush_volume_counts_to_db()
                        last_flush_time = current_time
                    
                    if should_cleanup:
                        self._cleanup_old_data()
                        last_cleanup_time = current_time
                    
                    if should_run_anomaly:
                        self._run_anomaly_detection()
                        last_anomaly_check_time = current_time
                    
                    continue
                
                # Regular batch processing
                messages = []
                for _ in range(1000):  # Batch size
                    msg = consumer.poll(timeout=0.1)
                    if msg is None:
                        break
                    if msg.error():
                        logger.error("Kafka error", error=str(msg.error()))
                        continue
                    messages.append(msg)
                
                if messages:
                    self._process_log_batch(messages)
                else:
                    # No messages, sleep briefly
                    time.sleep(0.1)
                    
        finally:
            # Flush any remaining counts before closing
            self._flush_volume_counts_to_db()
            consumer.close()

# Global instance
log_volume_aggregator_consumer = LogVolumeAggregatorConsumer()

def start_log_volume_aggregator_consumer():
    log_volume_aggregator_consumer.start()

def stop_log_volume_aggregator_consumer():
    log_volume_aggregator_consumer.stop()

if __name__ == "__main__":
    start_log_volume_aggregator_consumer()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_log_volume_aggregator_consumer()
