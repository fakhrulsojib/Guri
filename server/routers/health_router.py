from fastapi import APIRouter

health_router = APIRouter(
    prefix="/api/v1/health",
    tags=["Health"],
)

@health_router.get("/", summary="Health Check")
async def health_check():
    return {"status": "healthy"}