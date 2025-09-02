import os
import json
import time
import threading
from confluent_kafka import Consumer
from services.redis.base_redis_service import BaseRedisService
from model.raw_log import RawLog
import structlog

logger = structlog.get_logger()

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9093")
KAFKA_TOPIC_RAW = os.environ.get("KAFKA_TOPIC_RAW", "raw_logs")
KAFKA_GROUP_ID = os.environ.get("KAFKA_STREAMER_GROUP_ID", "pub_to_channel_group")

class RawLogToPubSubConsumer:
    def __init__(self):
        self._running = False
        self._thread = None
        self.redis_service = BaseRedisService()

    def start(self):
        if self._running:
            logger.warning("Consumer already running")
            return
        self._running = True
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
        logger.info("RawLogToPubSubConsumer started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        logger.info("RawLogToPubSubConsumer stopped")

    def _has_active_subscribers(self, source_id: str) -> bool:
        try:
            subscription_key = f"subs:source:{source_id}"
            subscriber_count = self.redis_service.client.scard(subscription_key)
            return subscriber_count > 0
        except Exception as e:
            logger.error("Failed to check subscriber count", source_id=source_id, error=str(e))
            return False

    def _publish_to_channel(self, source_id: str, log_data: dict) -> bool:
        try:
            channel_name = f"logs:source:{source_id}"
            message = json.dumps(log_data)
            result = self.redis_service.client.publish(channel_name, message)
            return result > 0
        except Exception as e:
            logger.error("Failed to publish to Redis channel", source_id=source_id, error=str(e))
            return False

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
                    
                    source_id_str = str(source_id)
                    
                    if not self._has_active_subscribers(source_id_str):
                        logger.debug("No active subscribers, skipping publish", source_id=source_id_str)
                        continue
                    
                    if self._publish_to_channel(source_id_str, log_data):
                        logger.info("Log published to Redis channel", source_id=source_id_str)
                    else:
                        logger.warning("Failed to publish log to Redis channel", source_id=source_id_str)
                        
                except Exception as e:
                    logger.error("Failed to process log for pub/sub", error=str(e))
        finally:
            consumer.close()

raw_log_to_pubsub_consumer = RawLogToPubSubConsumer()

def start_raw_log_to_pubsub_consumer():
    raw_log_to_pubsub_consumer.start()

def stop_raw_log_to_pubsub_consumer():
    raw_log_to_pubsub_consumer.stop()

if __name__ == "__main__":
    start_raw_log_to_pubsub_consumer()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_raw_log_to_pubsub_consumer() 