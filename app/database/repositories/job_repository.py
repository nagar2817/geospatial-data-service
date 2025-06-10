from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.base_repository import BaseRepository
from database.models.job import JobDefinition
from pydantic import BaseModel

class JobDefinitionCreate(BaseModel):
    job_name: str
    job_type: str
    schedule_cron: Optional[str] = None
    schedule_type: str = "event_triggered"
    interval_days: Optional[int] = None
    enabled: bool = True
    next_run_at: Optional[datetime] = None
    payload: Dict[str, Any]
    target_function: str
    retry_policy: Optional[Dict[str, Any]] = None

class JobDefinitionUpdate(BaseModel):
    job_name: Optional[str] = None
    job_type: Optional[str] = None
    schedule_cron: Optional[str] = None
    schedule_type: Optional[str] = None
    interval_days: Optional[int] = None
    enabled: Optional[bool] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    payload: Optional[Dict[str, Any]] = None
    target_function: Optional[str] = None
    retry_policy: Optional[Dict[str, Any]] = None

class JobDefinitionRepository(BaseRepository[JobDefinition, JobDefinitionCreate, JobDefinitionUpdate]):
    """Repository for job definition operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, JobDefinition)
    
    def get_eligible_jobs(self, current_time: Optional[datetime] = None) -> List[JobDefinition]:
        """Get jobs eligible for execution based on schedule."""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return (
            self.session.query(JobDefinition)
            .filter(
                and_(
                    JobDefinition.enabled == True,
                    or_(
                        JobDefinition.next_run_at <= current_time,
                        JobDefinition.next_run_at.is_(None)
                    )
                )
            )
            .all()
        )
    
    def get_by_job_type(self, job_type: str) -> List[JobDefinition]:
        """Get all jobs of a specific type."""
        return (
            self.session.query(JobDefinition)
            .filter(JobDefinition.job_type == job_type)
            .all()
        )
    
    def get_enabled_jobs(self) -> List[JobDefinition]:
        """Get all enabled jobs."""
        return (
            self.session.query(JobDefinition)
            .filter(JobDefinition.enabled == True)
            .all()
        )
    
    def get_jobs_by_schedule_type(self, schedule_type: str) -> List[JobDefinition]:
        """Get jobs by schedule type (cron, interval, event_triggered)."""
        return (
            self.session.query(JobDefinition)
            .filter(JobDefinition.schedule_type == schedule_type)
            .all()
        )
    
    def update_last_run(self, job_id: UUID, run_time: Optional[datetime] = None) -> bool:
        """Update last run timestamp for a job."""
        if run_time is None:
            run_time = datetime.utcnow()
        
        job = self.get(job_id)
        if job:
            job.last_run_at = run_time
            self.session.commit()
            return True
        return False
    
    def update_next_run(self, job_id: UUID, next_run: datetime) -> bool:
        """Update next run timestamp for a job."""
        job = self.get(job_id)
        if job:
            job.next_run_at = next_run
            self.session.commit()
            return True
        return False
    
    def disable_job(self, job_id: UUID) -> bool:
        """Disable a job."""
        job = self.get(job_id)
        if job:
            job.enabled = False
            self.session.commit()
            return True
        return False
    
    def enable_job(self, job_id: UUID) -> bool:
        """Enable a job."""
        job = self.get(job_id)
        if job:
            job.enabled = True
            self.session.commit()
            return True
        return False
    
    def search_by_payload(self, search_criteria: Dict[str, Any]) -> List[JobDefinition]:
        """Search jobs by payload content."""
        query = self.session.query(JobDefinition)
        
        for key, value in search_criteria.items():
            query = query.filter(JobDefinition.payload[key].astext == str(value))
        
        return query.all()
    
    def get_jobs_with_polygon_data(self) -> List[JobDefinition]:
        """Get jobs that contain polygon data in their payload."""
        return (
            self.session.query(JobDefinition)
            .filter(JobDefinition.payload.has_key('polygon'))
            .all()
        )