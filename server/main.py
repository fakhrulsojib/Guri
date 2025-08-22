import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from threading import Thread
import secrets
import structlog

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
from middleware.proxy_middleware import ProxyMiddleware

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://fakhrulsojib.mooo.com")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
LOG_DIR = os.getenv("LOG_DIR", "logs/backend")
DISABLE_CSRF_FOR_TESTS = os.getenv("DISABLE_CSRF_FOR_TESTS", "0")
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", secrets.token_hex(32))

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(LOG_LEVEL, LOG_FORMAT, LOG_DIR)
    
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
    ],
    root_path="",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.root_path = ""

app.add_middleware(ProxyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-CSRF-Token"],
)

app.add_middleware(LoggingMiddleware)

if DISABLE_CSRF_FOR_TESTS != "1":
    app.add_middleware(CSRFMiddleware, secret_key=CSRF_SECRET_KEY)

app.include_router(health_router)
app.include_router(log_router)
app.include_router(auth_router)
app.include_router(log_sources_router)