from fastapi import FastAPI, Request
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from threading import Thread
import secrets
import os
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
from middleware.csrf_middleware import CSRFMiddleware
import structlog

logger = structlog.get_logger()

security_scheme = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_format = os.environ.get("LOG_FORMAT", "json")
    log_dir = os.environ.get("LOG_DIR", "logs/backend")
    
    setup_logging(log_level, log_format, log_dir)
    
    logger.info("Starting application", app_name="Pulse AI")
    
    try:
        if check_database_connection():
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection failed, continuing with limited functionality")
    except Exception as e:
        logger.warning("Database connection check failed, continuing with limited functionality", error=str(e))
    
    try:
        consumer_thread = Thread(target=start_raw_log_to_db_consumer, daemon=True)
        consumer_thread.start()
        logger.info("Started consumer thread")
    except Exception as e:
        logger.warning("Failed to start consumer thread", error=str(e))
    
    yield
    
    logger.info("Shutting down application")
    try:
        stop_raw_log_to_db_consumer()
        consumer_thread.join(timeout=5.0)
    except Exception as e:
        logger.warning("Error during shutdown", error=str(e))

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-CSRF-Token"],
)

app.add_middleware(LoggingMiddleware)

if os.getenv("DISABLE_CSRF_FOR_TESTS") != "1":
    secret_key = os.getenv("CSRF_SECRET_KEY", secrets.token_hex(32))
    app.add_middleware(CSRFMiddleware, secret_key=secret_key)

app.include_router(health_router)
app.include_router(log_router)
app.include_router(auth_router)
app.include_router(log_sources_router)