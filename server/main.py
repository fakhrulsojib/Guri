from fastapi import FastAPI
from contextlib import asynccontextmanager
from threading import Thread
from routers.health_router import health_router
from routers.log_router import log_router
from routers.auth_router import auth_router
from consumers.raw_log_to_db_consumer import (
    start_raw_log_to_db_consumer,
    stop_raw_log_to_db_consumer
)
from database.database import check_database_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not check_database_connection():
        print("Warning: Database connection failed")
    
    consumer_thread = Thread(target=start_raw_log_to_db_consumer, daemon=True)
    consumer_thread.start()
    
    yield
    
    stop_raw_log_to_db_consumer()
    consumer_thread.join(timeout=5.0)

app = FastAPI(
    title="Pulse AI",
    description="Smart Log Analytics Platform with Google OAuth Authentication",
    version="0.0.0",
    lifespan=lifespan
)

app.include_router(health_router)
app.include_router(log_router)
app.include_router(auth_router)