from datetime import datetime, timedelta, UTC
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from database.base_repository import BaseRepository
from database.models.job import JobRun
from pydantic import BaseModel

class JobRunCreate(BaseModel):
    job_id: UUID
    start_time: Optional[datetime] = None
    status: str = "running"
    triggered_by: str = "manual"
    execution_host: Optional[str] = None

class JobRunUpdate(BaseModel):
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    log_message: Optional[Dict[str, Any]] = None
    output_summary: Optional[Dict[str, Any]] = None
    execution_host: Optional[str] = None

class JobRunRepository(BaseRepository[JobRun, JobRunCreate, JobRunUpdate]):
    """Repository for job run operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, JobRun)
    
    def get_runs_by_job(self, job_id: UUID, limit: int = 100) -> List[JobRun]:
        """Get all runs for a specific job."""
        return (
            self.session.query(JobRun)
            .filter(JobRun.job_id == job_id)
            .order_by(desc(JobRun.start_time))
            .limit(limit)
            .all()
        )
    
    def get_running_jobs(self) -> List[JobRun]:
        """Get all currently running jobs."""
        return (
            self.session.query(JobRun)
            .filter(JobRun.status == "running")
            .all()
        )
    
    def get_failed_jobs(self, hours: int = 24) -> List[JobRun]:
        """Get failed jobs within specified hours."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
        return (
            self.session.query(JobRun)
            .filter(
                and_(
                    JobRun.status == "failed",
                    JobRun.start_time >= cutoff_time
                )
            )
            .order_by(desc(JobRun.start_time))
            .all()
        )
    
    def get_successful_jobs(self, hours: int = 24) -> List[JobRun]:
        """Get successful jobs within specified hours."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
        return (
            self.session.query(JobRun)
            .filter(
                and_(
                    JobRun.status == "success",
                    JobRun.start_time >= cutoff_time
                )
            )
            .order_by(desc(JobRun.start_time))
            .all()
        )
    
    def get_runs_by_status(self, status: str, limit: int = 100) -> List[JobRun]:
        """Get runs by status."""
        return (
            self.session.query(JobRun)
            .filter(JobRun.status == status)
            .order_by(desc(JobRun.start_time))
            .limit(limit)
            .all()
        )
    
    def get_runs_by_trigger(self, triggered_by: str, limit: int = 100) -> List[JobRun]:
        """Get runs by trigger type."""
        return (
            self.session.query(JobRun)
            .filter(JobRun.triggered_by == triggered_by)
            .order_by(desc(JobRun.start_time))
            .limit(limit)
            .all()
        )
    
    def mark_as_completed(self, run_id: UUID, status: str, output_summary: Optional[Dict[str, Any]] = None) -> bool:
        """Mark a job run as completed with status and output."""
        job_run = self.get(run_id)
        if job_run:
            job_run.status = status
            job_run.end_time = datetime.now(UTC)
            if output_summary:
                job_run.output_summary = output_summary
            self.session.commit()
            return True
        return False
    
    def mark_as_failed(self, run_id: UUID, error_message: str) -> bool:
        """Mark a job run as failed with error message."""
        job_run = self.get(run_id)
        if job_run:
            job_run.status = "failed"
            job_run.end_time = datetime.now(UTC)
            job_run.log_message = {"error": error_message, "timestamp": datetime.now(UTC).isoformat()}
            self.session.commit()
            return True
        return False
    
    def add_log_entry(self, run_id: UUID, log_entry: Dict[str, Any]) -> bool:
        """Add a log entry to an existing job run."""
        job_run = self.get(run_id)
        if job_run:
            if job_run.log_message is None:
                job_run.log_message = {"logs": []}
            elif "logs" not in job_run.log_message:
                job_run.log_message["logs"] = []
            
            log_entry["timestamp"] = datetime.now(UTC).isoformat()
            job_run.log_message["logs"].append(log_entry)
            self.session.commit()
            return True
        return False
    
    def get_execution_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get execution statistics for the specified time period."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
        
        stats = (
            self.session.query(
                JobRun.status,
                func.count(JobRun.run_id).label('count'),
                func.avg(
                    func.extract('epoch', JobRun.end_time - JobRun.start_time)
                ).label('avg_duration_seconds')
            )
            .filter(JobRun.start_time >= cutoff_time)
            .group_by(JobRun.status)
            .all()
        )
        
        result = {
            "period_hours": hours,
            "stats_by_status": {},
            "total_runs": 0
        }
        
        for stat in stats:
            result["stats_by_status"][stat.status] = {
                "count": stat.count,
                "avg_duration_seconds": float(stat.avg_duration_seconds) if stat.avg_duration_seconds else None
            }
            result["total_runs"] += stat.count
        
        return result
    
    def get_longest_running_jobs(self, limit: int = 10) -> List[JobRun]:
        """Get the longest running jobs that are still in progress."""
        return (
            self.session.query(JobRun)
            .filter(JobRun.status == "running")
            .order_by(JobRun.start_time)
            .limit(limit)
            .all()
        )
    
    def cleanup_old_runs(self, days: int = 30) -> int:
        """Delete job runs older than specified days. Returns count of deleted records."""
        cutoff_time = datetime.now(UTC) - timedelta(days=days)
        deleted_count = (
            self.session.query(JobRun)
            .filter(JobRun.start_time < cutoff_time)
            .delete()
        )
        self.session.commit()
        return deleted_count