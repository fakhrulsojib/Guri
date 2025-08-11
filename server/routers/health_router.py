from fastapi import APIRouter
import structlog

logger = structlog.get_logger()

health_router = APIRouter(
    prefix="/api/v1/health",
    tags=["Health"],
)

@health_router.get("/", summary="Health Check")
async def health_check():
    logger.info("Health check requested")
    return {"status": "healthy"}