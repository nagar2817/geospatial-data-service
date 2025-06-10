from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from database import AsyncRepositoryFactory
from database.repositories.job_repository import JobDefinitionCreate as DBJobCreate, JobDefinitionUpdate as DBJobUpdate
from database.repositories.job_run_repository import JobRunCreate as DBJobRunCreate
from api.dependencies import get_repository_factory, validate_job_exists
from api.job_schema import (
    JobDefinitionCreate, JobDefinitionUpdate, JobDefinitionResponse,
    JobRunResponse, JobListResponse, JobRunListResponse,
    JobTriggerRequest, JobStatistics, JobRunStatistics,
    JobType, ScheduleType, JobStatus
)
from config.celery_config import celery_app

router = APIRouter(prefix="/jobs", tags=["jobs"])

class APIEndpointConstant:
    """Constants for API endpoints related to job management."""
    CREATE_JOB = "/"
    LIST_JOBS = "/"
    GET_JOB = "/{job_id}"
    UPDATE_JOB = "/{job_id}"
    DELETE_JOB = "/{job_id}"
    TRIGGER_JOB = "/{job_id}/trigger"
    GET_JOB_RUNS = "/{job_id}/runs"
    GET_JOB_RUN = "/{job_id}/runs/{run_id}"
    ENABLE_JOB = "/{job_id}/enable"
    DISABLE_JOB = "/{job_id}/disable"
    JOB_STATISTICS_OVERVIEW = "/statistics/overview"


@router.post(APIEndpointConstant.CREATE_JOB, response_model=JobDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobDefinitionCreate,
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Create a new geospatial processing job."""
    db_job_data = DBJobCreate(**job_data.model_dump())
    job = await repo_factory.job_definition.create(db_job_data)
    return JobDefinitionResponse.model_validate(job)

@router.get(APIEndpointConstant.LIST_JOBS, response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    job_type: Optional[JobType] = Query(None, description="Filter by job type"),
    schedule_type: Optional[ScheduleType] = Query(None, description="Filter by schedule type"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """List all jobs with optional filtering."""
    filters = {}
    if job_type:
        filters["job_type"] = job_type.value
    if schedule_type:
        filters["schedule_type"] = schedule_type.value
    if enabled is not None:
        filters["enabled"] = enabled

    jobs = await repo_factory.job_definition.get_multi(
        skip=skip,
        limit=limit,
        filters=filters
    )
    total = await repo_factory.job_definition.count(filters)
    
    return JobListResponse(
        jobs=[JobDefinitionResponse.model_validate(job) for job in jobs],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get(APIEndpointConstant.GET_JOB, response_model=JobDefinitionResponse)
async def get_job(
    job_id: UUID,
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Get a specific job by ID."""
    job = await repo_factory.job_definition.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    print("Job retrieved:", job)
    return JobDefinitionResponse.model_validate(job)

@router.put("/{job_id}", response_model=JobDefinitionResponse)
async def update_job(
    job_id: UUID,
    job_data: JobDefinitionUpdate,
    job = Depends(validate_job_exists),
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Update an existing job."""
    db_job_data = DBJobUpdate(**job_data.model_dump(exclude_unset=True))
    updated_job = await repo_factory.job_definition.update(job, db_job_data)
    return JobDefinitionResponse.model_validate(updated_job)

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    job = Depends(validate_job_exists),
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Delete a job and all its runs."""
    await repo_factory.job_definition.delete(job_id)

@router.post("/{job_id}/trigger", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def trigger_job(
    job_id: UUID,
    trigger_data: JobTriggerRequest = JobTriggerRequest(),
    job = Depends(validate_job_exists),
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Manually trigger a job execution."""
    # Create job run record
    job_run_data = DBJobRunCreate(
        job_id=job_id,
        triggered_by="manual",
        execution_host=trigger_data.execution_host
    )
    job_run = await repo_factory.job_run.create(job_run_data)
    
    # Queue job for processing
    task_payload = {
        "job_id": str(job_id),
        "run_id": str(job_run.id),
        "override_payload": trigger_data.override_payload
    }
    
    task = celery_app.send_task(
        "tasks.job_processor.process_geospatial_job",
        args=[task_payload],
        queue="geospatial"
    )
    
    return {
        "message": "Job execution triggered successfully",
        "run_id": job_run.id,
        "task_id": task.id
    }

@router.get("/{job_id}/runs", response_model=JobRunListResponse)
async def get_job_runs(
    job_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status_filter: Optional[JobStatus] = Query(None, description="Filter by run status"),
    job = Depends(validate_job_exists),
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Get execution history for a specific job."""
    runs = await repo_factory.job_run.get_runs_by_job(job_id, limit=limit)
    
    return JobRunListResponse(
        runs=[JobRunResponse.model_validate(run) for run in runs],
        total=len(runs),
        skip=skip,
        limit=limit
    )

@router.get("/{job_id}/runs/{run_id}", response_model=JobRunResponse)
async def get_job_run(
    job_id: UUID,
    run_id: UUID,
    job = Depends(validate_job_exists),
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Get details of a specific job run."""
    job_run = await repo_factory.job_run.get(run_id)
    if not job_run or job_run.job_id != job_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job run with ID {run_id} not found for job {job_id}"
        )
    return JobRunResponse.model_validate(job_run)

@router.put("/{job_id}/enable", response_model=JobDefinitionResponse)
async def enable_job(
    job_id: UUID,
    job = Depends(validate_job_exists),
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Enable a job for execution."""
    update_data = DBJobUpdate(enabled=True)
    updated_job = await repo_factory.job_definition.update(job, update_data)
    return JobDefinitionResponse.model_validate(updated_job)

@router.put("/{job_id}/disable", response_model=JobDefinitionResponse)
async def disable_job(
    job_id: UUID,
    job = Depends(validate_job_exists),
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Disable a job from execution."""
    update_data = DBJobUpdate(enabled=False)
    updated_job = await repo_factory.job_definition.update(job, update_data)
    return JobDefinitionResponse.model_validate(updated_job)

@router.get("/statistics/overview", response_model=JobStatistics)
async def get_job_statistics(
    repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
):
    """Get overall job statistics."""
    all_jobs = await repo_factory.job_definition.get_multi(limit=10000)
    
    total_jobs = len(all_jobs)
    enabled_jobs = sum(1 for job in all_jobs if job.enabled)
    disabled_jobs = total_jobs - enabled_jobs
    
    jobs_by_type = {}
    jobs_by_schedule_type = {}
    
    for job in all_jobs:
        # Count by type
        job_type = job.job_type
        jobs_by_type[job_type] = jobs_by_type.get(job_type, 0) + 1
        
        # Count by schedule type
        schedule_type = job.schedule_type
        jobs_by_schedule_type[schedule_type] = jobs_by_schedule_type.get(schedule_type, 0) + 1
    
    return JobStatistics(
        total_jobs=total_jobs,
        enabled_jobs=enabled_jobs,
        disabled_jobs=disabled_jobs,
        jobs_by_type=jobs_by_type,
        jobs_by_schedule_type=jobs_by_schedule_type
    )