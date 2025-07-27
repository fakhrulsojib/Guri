from fastapi import APIRouter, HTTPException, Request, Response, status
import datetime
import os
import json
from confluent_kafka import Producer, KafkaError
from model.raw_log import RawLog

log_router = APIRouter(
    prefix="/api/v1/log",
    tags=["Log"],
)

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9093")
KAFKA_TOPIC_RAW = os.environ.get("KAFKA_TOPIC_RAW", "raw_logs")
MAX_KAFKA_PAYLOAD = 1000000  # ~1MB

producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

@log_router.post("/", summary="Add Logs", status_code=201)
async def add_single_log(log: RawLog):
    try:
        print(log.model_dump())
        message_bytes = log.model_dump_json().encode('utf-8')

        if len(message_bytes) > MAX_KAFKA_PAYLOAD:
            raise HTTPException(status_code=413, detail="Payload too large for Kafka")

        producer.produce(
            KAFKA_TOPIC_RAW,
            key=None,
            value=message_bytes,
            callback=delivery_report
        )
        producer.flush()

        return {"status": "success", "message": "Log published to Kafka"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        print(f"[HERELOG_ROUTER][ERROR] Error adding log: {e}")
        raise HTTPException(status_code=500, detail=str(e))