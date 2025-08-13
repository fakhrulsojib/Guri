from fastapi import FastAPI
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from threading import Thread
from routers.health_router import health_router
from routers.log_router import log_router
from routers.auth_router import auth_router
from routers.log_sources_router import router as log_sources_router
from consumers.raw_log_to_db_consumer import (
    start_raw_log_to_db_consumer,
    stop_raw_log_to_db_consumer
)
from database.database import check_database_connection
from util.logging_config import setup_logging
from middleware.logging_middleware import LoggingMiddleware
import structlog
import os

logger = structlog.get_logger()

security_scheme = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_format = os.environ.get("LOG_FORMAT", "json")
    log_dir = os.environ.get("LOG_DIR", "logs/backend")
    
    setup_logging(log_level, log_format, log_dir)
    
    logger.info("Starting application", app_name="Pulse AI")
    
    if not check_database_connection():
        logger.error("Database connection failed")
    
    consumer_thread = Thread(target=start_raw_log_to_db_consumer, daemon=True)
    consumer_thread.start()
    logger.info("Started consumer thread")
    
    yield
    
    logger.info("Shutting down application")
    stop_raw_log_to_db_consumer()
    consumer_thread.join(timeout=5.0)

app = FastAPI(
    title="Pulse AI",
    description="Smart Log Analytics Platform with Google OAuth Authentication",
    version="0.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Authentication", "description": "Google OAuth authentication endpoints"},
        {"name": "log-sources", "description": "Log source management endpoints"},
        {"name": "logs", "description": "Log management endpoints"},
        {"name": "health", "description": "Health check endpoints"}
    ]
)

app.add_middleware(LoggingMiddleware)

app.include_router(health_router)
app.include_router(log_router)
app.include_router(auth_router)
app.include_router(log_sources_router)