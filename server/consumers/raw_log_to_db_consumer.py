import os
import json
import time
import threading
from confluent_kafka import Consumer
from database.database import execute_query
from model.raw_log import RawLog

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9093")
KAFKA_TOPIC_RAW = os.environ.get("KAFKA_TOPIC_RAW", "raw_logs")
KAFKA_GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "raw_log_to_db_consumer_group")

INSERT_LOG_SQL = "INSERT INTO raw_logs (provider, data, timestamp) VALUES (%s, %s, %s);"

class RawLogToDBConsumer:
    def __init__(self):
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            print("Consumer already running.")
            return
        self._running = True
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
        print("RawLogToDBConsumer started.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        print("RawLogToDBConsumer stopped.")

    def _consume_loop(self):
        consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': KAFKA_GROUP_ID,
            'auto.offset.reset': 'earliest',
        })
        consumer.subscribe([KAFKA_TOPIC_RAW])
        print(f"Listening to Kafka topic: {KAFKA_TOPIC_RAW}")
        
        try:
            while self._running:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Kafka error: {msg.error()}")
                    continue
                
                try:
                    log_data = json.loads(msg.value().decode('utf-8'))
                    log = RawLog(**log_data)
                    execute_query(INSERT_LOG_SQL, (log.provider, log.data, log.timestamp))
                    print(f"Saved log: {log.model_dump()}")
                except Exception as e:
                    print(f"Failed to save log: {e}")
                
                time.sleep(0.1)
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