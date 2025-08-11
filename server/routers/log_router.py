from fastapi import APIRouter, HTTPException
import os
from confluent_kafka import Producer
from model.raw_log import RawLog
import structlog

logger = structlog.get_logger()

log_router = APIRouter(
    prefix="/api/v1/logs",
    tags=["Log"],
)

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9093")
KAFKA_TOPIC_RAW = os.environ.get("KAFKA_TOPIC_RAW", "raw_logs")
MAX_KAFKA_PAYLOAD = 1000000

producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def delivery_report(err, msg):
    if err is not None:
        logger.error("Kafka delivery failed", record_key=msg.key(), error=str(err))
    else:
        logger.info("Kafka record delivered", record_key=msg.key(), topic=msg.topic(), partition=msg.partition(), offset=msg.offset())

@log_router.post("/", summary="Add Logs", status_code=201)
async def add_single_log(log: RawLog):
    try:
        logger.info("Processing log entry", log_data=log.model_dump())
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
        
        logger.error("Error adding log to Kafka", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))