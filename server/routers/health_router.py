from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()

health_router = APIRouter(
    prefix="/api/v1/health",
    tags=["Health"],
)

@health_router.get("/", summary="Health Check")
async def health_check():
    try:
        logger.info("Health check requested")
        
        return JSONResponse(
            content={"status": "healthy", "message": "Service is running"},
            status_code=200,
            headers={"X-CSRF-Token": "health-check-token"}
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=500
        )