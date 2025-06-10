from sqlalchemy.orm import Session
from database.repositories.job_repository import JobDefinitionRepository
from database.repositories.job_run_repository import JobRunRepository
# from database.repositories.satellite_data_repository import SatelliteDataRepository
# from database.repositories.anomaly_repository import AnomalyRepository
# from database.repositories.alert_repository import AlertRepository

class RepositoryFactory:
    """Factory class for creating repository instances with a shared database session."""
    
    def __init__(self, session: Session):
        self.session = session
        self._job_definition_repo = None
        self._job_run_repo = None
        self._satellite_data_repo = None
        self._anomaly_repo = None
        self._alert_repo = None
    
    @property
    def job_definition(self) -> JobDefinitionRepository:
        """Get JobDefinitionRepository instance."""
        if self._job_definition_repo is None:
            self._job_definition_repo = JobDefinitionRepository(self.session)
        return self._job_definition_repo
    
    @property
    def job_run(self) -> JobRunRepository:
        """Get JobRunRepository instance."""
        if self._job_run_repo is None:
            self._job_run_repo = JobRunRepository(self.session)
        return self._job_run_repo
    
    # @property
    # def satellite_data(self) -> SatelliteDataRepository:
    #     """Get SatelliteDataRepository instance."""
    #     if self._satellite_data_repo is None:
    #         self._satellite_data_repo = SatelliteDataRepository(self.session)
    #     return self._satellite_data_repo
    
    # @property
    # def anomaly(self) -> AnomalyRepository:
    #     """Get AnomalyRepository instance."""
    #     if self._anomaly_repo is None:
    #         self._anomaly_repo = AnomalyRepository(self.session)
    #     return self._anomaly_repo
    
    # @property
    # def alert(self) -> AlertRepository:
    #     """Get AlertRepository instance."""
    #     if self._alert_repo is None:
    #         self._alert_repo = AlertRepository(self.session)
    #     return self._alert_repo
    
    def commit(self):
        """Commit the current transaction."""
        self.session.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()
    
    def close(self):
        """Close the database session."""
        self.session.close()