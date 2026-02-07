import json
import os
import structlog
import time
import threading
from typing import List, Dict
from confluent_kafka import Consumer, KafkaError

from ml.rag.rag_service import RAGService

logger = structlog.get_logger()

class RagIngestionConsumer:
    def __init__(self):
        self.broker = os.getenv("KAFKA_BROKER", "kafka:9093")
        self.topic = os.getenv("KAFKA_TOPIC_RAW", "raw_logs")
        self.group_id = "rag_ingestion_group"
        
        self.consumer_config = {
            'bootstrap.servers': self.broker,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }
        
        self._running = False
        self._thread = None
        self.rag_service = RAGService()
        self.batch_size = 100
        self.batch_timeout = 60.0 # seconds

    def start(self):
        if self._running:
            logger.warning("RagIngestionConsumer already running")
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("RagIngestionConsumer started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("RagIngestionConsumer stopped")

    def _run_loop(self):
        consumer = Consumer(self.consumer_config)
        consumer.subscribe([self.topic])
        
        logger.info(f"RAG Ingestion Consumer loop started on topic {self.topic}")
        
        batch = []
        last_flush_time = time.time()
        
        try:
            while self._running:
                msg = consumer.poll(1.0)
                
                if msg is None:
                    # Check timeout flush
                    if batch and (time.time() - last_flush_time > self.batch_timeout):
                        self._process_batch(batch, consumer)
                        batch = []
                        last_flush_time = time.time()
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        continue
                
                try:
                    payload = json.loads(msg.value().decode('utf-8'))
                    batch.append(payload)
                except Exception as e:
                    logger.error(f"Failed to decode message: {e}")
                    continue

                if len(batch) >= self.batch_size:
                    self._process_batch(batch, consumer)
                    batch = []
                    last_flush_time = time.time()
                    
        except Exception as e:
            logger.error(f"Consumer error: {str(e)}")
        finally:
            if batch:
                self._process_batch(batch, consumer)
            consumer.close()

    def _process_batch(self, batch: List[Dict], consumer):
        if not batch:
            return

        try:
            logger.info(f"Processing RAG batch of {len(batch)} logs")
            self.rag_service.ingest_logs(batch)
            consumer.commit()
            logger.info("RAG Batch committed")
        except Exception as e:
            logger.error(f"Failed to process RAG batch: {str(e)}")

# Global instance
rag_ingestion_consumer = RagIngestionConsumer()

def start_rag_ingestion_consumer():
    rag_ingestion_consumer.start()

def stop_rag_ingestion_consumer():
    rag_ingestion_consumer.stop()
