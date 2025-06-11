from sqlalchemy.ext.asyncio import AsyncSession
from database.async_base_repository import AsyncBaseRepository
from database.models import JobDefinition, JobRun
from database.repositories.job_repository import JobDefinitionCreate, JobDefinitionUpdate
from database.repositories.job_run_repository import JobRunCreate, JobRunUpdate

class AsyncJobDefinitionRepository(AsyncBaseRepository[JobDefinition, JobDefinitionCreate, JobDefinitionUpdate]):
    """Async repository for job definitions - FastAPI endpoints."""
    
    async def get_eligible_jobs(self):
        """Get jobs eligible for execution - simplified for API access."""
        from sqlalchemy import select, and_, or_
        from datetime import datetime, UTC
        
        current_time = datetime.now(UTC)
        query = select(JobDefinition).where(
            and_(
                JobDefinition.enabled == True,
                or_(
                    JobDefinition.next_run_at <= current_time,
                    JobDefinition.next_run_at.is_(None)
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

class AsyncJobRunRepository(AsyncBaseRepository[JobRun, JobRunCreate, JobRunUpdate]):
    """Async repository for job runs - FastAPI endpoints."""
    
    async def get_runs_by_job(self, job_id, limit: int = 100):
        """Get runs for a specific job."""
        from sqlalchemy import select, desc
        
        query = (
            select(JobRun)
            .where(JobRun.job_id == job_id)
            .order_by(desc(JobRun.start_time))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class AsyncRepositoryFactory:
    """Factory for async repositories used by FastAPI endpoints."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._job_definition_repo = None
        self._job_run_repo = None
        self._satellite_data_repo = None
        self._anomaly_repo = None
        self._alert_repo = None
    
    @property
    def job_definition(self) -> AsyncJobDefinitionRepository:
        """Get async JobDefinitionRepository instance."""
        if self._job_definition_repo is None:
            self._job_definition_repo = AsyncJobDefinitionRepository(self.session, JobDefinition)
        return self._job_definition_repo
    
    @property
    def job_run(self) -> AsyncJobRunRepository:
        """Get async JobRunRepository instance."""
        if self._job_run_repo is None:
            self._job_run_repo = AsyncJobRunRepository(self.session, JobRun)
        return self._job_run_repo
    
    # @property
    # def satellite_data(self) -> AsyncSatelliteDataRepository:
    #     """Get async SatelliteDataRepository instance."""
    #     if self._satellite_data_repo is None:
    #         self._satellite_data_repo = AsyncSatelliteDataRepository(self.session, SatelliteData)
    #     return self._satellite_data_repo
    
    # @property
    # def anomaly(self) -> AsyncAnomalyRepository:
    #     """Get async AnomalyRepository instance."""
    #     if self._anomaly_repo is None:
    #         self._anomaly_repo = AsyncAnomalyRepository(self.session, Anomaly)
    #     return self._anomaly_repo
    
    # @property
    # def alert(self) -> AsyncAlertRepository:
    #     """Get async AlertRepository instance."""
    #     if self._alert_repo is None:
    #         self._alert_repo = AsyncAlertRepository(self.session, Alert)
    #     return self._alert_repo
    
    async def commit(self):
        """Commit the current transaction."""
        await self.session.commit()
    
    async def rollback(self):
        """Rollback the current transaction."""
        await self.session.rollback()
    
    async def close(self):
        """Close the database session."""
        await self.session.close()