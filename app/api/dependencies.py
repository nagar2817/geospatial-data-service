from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db, AsyncRepositoryFactory

async def get_repository_factory(
    session: AsyncSession = Depends(get_async_db)
) -> AsyncRepositoryFactory:
    """Get async repository factory for database operations."""
    return AsyncRepositoryFactory(session)

async def validate_job_exists(
    job_id: str,
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Validate that a job exists."""
    job = await repo_factory.job_definition.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    return job

async def validate_job_run_exists(
    run_id: str,
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Validate that a job run exists."""
    job_run = await repo_factory.job_run.get(run_id)
    if not job_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job run with ID {run_id} not found"
        )
    return job_run

async def validate_anomaly_exists(
    anomaly_id: str,
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Validate that an anomaly exists."""
    anomaly = await repo_factory.anomaly.get(anomaly_id)
    if not anomaly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anomaly with ID {anomaly_id} not found"
        )
    return anomaly

async def validate_alert_exists(
    alert_id: str,
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Validate that an alert exists."""
    alert = await repo_factory.alert.get(alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    return alert

# Common query parameters
class CommonQueryParams:
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        self.skip = skip
        self.limit = min(limit, 1000)  # Max 1000 records
        self.sort_by = sort_by
        self.sort_order = sort_order

CommonParams = Depends(CommonQueryParams)