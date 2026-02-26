import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from threading import Thread
import secrets
import structlog

from routers.health_router import health_router
from routers.log_router import log_router
from routers.auth_router import auth_router
from routers.log_sources_router import router as log_sources_router
from routers.websocket_router import websocket_router
from services.websocket import WebSocketManager, initialize_websocket_manager, cleanup_websocket_manager
from services.websocket.state import active_connections
from consumers.raw_log_to_db_consumer import (
    start_raw_log_to_db_consumer,
    stop_raw_log_to_db_consumer
)
from consumers.raw_log_to_pubsub_consumer import (
    start_raw_log_to_pubsub_consumer,
    stop_raw_log_to_pubsub_consumer
)
from consumers.log_volume_aggregator_consumer import (
    start_log_volume_aggregator_consumer,
    stop_log_volume_aggregator_consumer
)
from database.database import init_db_pool, close_db_pool, check_database_connection
from util.logging_config import setup_logging
from middleware.logging_middleware import LoggingMiddleware
from middleware.csrf_middleware import CSRFMiddleware
from middleware.proxy_middleware import ProxyMiddleware

FRONTEND_URL = os.getenv("FRONTEND_URL")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
LOG_DIR = os.getenv("LOG_DIR", "logs/backend")
DISABLE_CSRF_FOR_TESTS = os.getenv("DISABLE_CSRF_FOR_TESTS", "0")
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", secrets.token_hex(32))

logger = structlog.get_logger()

ws_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(LOG_LEVEL, LOG_FORMAT, LOG_DIR)

    logger.info("Starting application", app_name="Pulse AI")

    # --- Async database pool ---
    try:
        await init_db_pool()
        logger.info("Async database pool initialised")
    except Exception as e:
        logger.warning("Failed to initialise async database pool", error=str(e))

    # --- Legacy sync connection check (used by consumers) ---
    try:
        if check_database_connection():
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection failed, continuing with limited functionality")
    except Exception as e:
        logger.warning("Database connection check failed, continuing with limited functionality", error=str(e))

    try:
        db_consumer_thread = Thread(target=start_raw_log_to_db_consumer, daemon=True)
        db_consumer_thread.start()
        logger.info("Started DB consumer thread")

        pubsub_consumer_thread = Thread(target=start_raw_log_to_pubsub_consumer, daemon=True)
        pubsub_consumer_thread.start()
        logger.info("Started PubSub consumer thread")

        volume_aggregator_thread = Thread(target=start_log_volume_aggregator_consumer, daemon=True)
        volume_aggregator_thread.start()
        logger.info("Started log volume aggregator consumer thread")

        await asyncio.sleep(2)
        await initialize_websocket_manager(ws_manager)
    except Exception as e:
        logger.warning("Failed to start consumer threads", error=str(e))

    yield

    logger.info("Shutting down application")
    try:
        stop_raw_log_to_db_consumer()
        stop_raw_log_to_pubsub_consumer()
        stop_log_volume_aggregator_consumer()
        db_consumer_thread.join(timeout=5.0)
        pubsub_consumer_thread.join(timeout=5.0)
        volume_aggregator_thread.join(timeout=5.0)

        await cleanup_websocket_manager(ws_manager, active_connections)
    except Exception as e:
        logger.warning("Error during shutdown", error=str(e))

    # --- Close async database pool ---
    try:
        await close_db_pool()
    except Exception as e:
        logger.warning("Error closing async database pool", error=str(e))

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

# ---------------------------------------------------------------------------
# Global unhandled-exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch any unhandled exception, log full traceback via structlog, and
    return a clean 500 JSON response to the client."""
    logger.error(
        "Unhandled server error",
        path=str(request.url),
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

app.include_router(health_router)
app.include_router(log_router)
app.include_router(auth_router)
app.include_router(log_sources_router)
app.include_router(websocket_router)