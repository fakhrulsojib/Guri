from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from typing import List, Optional
from services.auth_service import get_current_user
from services.log_source_service import LogSourceService
from model.log_sources import LogSourceCreate, LogSourceUpdate, LogSourceResponse, LogSourceResponseWithKey, LogSourceStatus

router = APIRouter(prefix="/api/v1", tags=["log-sources"])

security = HTTPBearer()

@router.post("/log-sources", response_model=LogSourceResponseWithKey, status_code=status.HTTP_201_CREATED, dependencies=[Depends(security)])
async def create_log_source(
    log_source_data: LogSourceCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        log_source = LogSourceService.create_log_source(log_source_data, current_user["id"])
        return LogSourceResponseWithKey(**log_source.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create log source"
        )

@router.get("/log-sources", response_model=List[LogSourceResponse], dependencies=[Depends(security)])
async def get_log_sources(
    status: Optional[str] = Query(None, description="Filter by status"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    current_user: dict = Depends(get_current_user)
):
    try:
        if status and status not in [s.value for s in LogSourceStatus]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid status value"
            )
        
        log_sources = LogSourceService.get_user_log_sources(
            current_user["id"], 
            status=status, 
            environment=environment
        )
        return [LogSourceResponse(**source.model_dump()) for source in log_sources]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve log sources"
        )

@router.get("/log-sources/{log_source_id}", response_model=LogSourceResponse, dependencies=[Depends(security)])
async def get_log_source(
    log_source_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        log_source = LogSourceService.get_log_source(log_source_id, current_user["id"])
        if not log_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log source not found"
            )
        return LogSourceResponse(**log_source.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve log source"
        )

@router.patch("/log-sources/{log_source_id}", response_model=LogSourceResponse, dependencies=[Depends(security)])
async def update_log_source(
    log_source_id: int,
    update_data: LogSourceUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        log_source = LogSourceService.update_log_source(log_source_id, current_user["id"], update_data)
        if not log_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log source not found"
                )
        return LogSourceResponse(**log_source.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update log source"
        )

@router.delete("/log-sources/{log_source_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(security)])
async def delete_log_source(
    log_source_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        success = LogSourceService.delete_log_source(log_source_id, current_user["id"])
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log source not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete log source"
        ) 

@router.get("/log-sources/{log_source_id}/api-key", response_model=dict, dependencies=[Depends(security)])
async def get_log_source_api_key(
    log_source_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get the API key for a specific log source (only accessible by owner)"""
    try:
        log_source = LogSourceService.get_log_source(log_source_id, current_user["id"])
        if not log_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log source not found"
            )
        return {"api_key": log_source.api_key}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API key"
        ) 