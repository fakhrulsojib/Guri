from fastapi import APIRouter, HTTPException, status
import os
import json
from confluent_kafka import Producer
from model.raw_log import RawLog
from model.log_sources import LogSourceStatus
from services.log_source_service import LogSourceService
from services.redis.api_key_cache_service import api_key_cache_service
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
        cached_data = api_key_cache_service.get_api_key_cache(log.api_key)

        if cached_data:
            source_id = cached_data["source_id"]
            is_active = cached_data["active"]
        else:
            log_source = await LogSourceService.get_log_source_by_api_key(log.api_key)
            if not log_source:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid API key"
                )

            source_id = log_source.id
            is_active = log_source.status == LogSourceStatus.ACTIVE

            api_key_cache_service.set_api_key_cache(log.api_key, source_id, is_active)

        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Log source is not active"
            )

        logger.info("Processing log entry", log_data=log.model_dump(), source_id=source_id)

        log_json = log.model_dump_json(exclude={'api_key'})
        log_data = json.loads(log_json)
        log_data['source_id'] = source_id

        message_bytes = json.dumps(log_data).encode('utf-8')

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
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error adding log to Kafka", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))