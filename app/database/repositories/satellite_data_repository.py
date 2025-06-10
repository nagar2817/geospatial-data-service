# from datetime import datetime, timedelta
# from typing import List, Optional, Dict, Any
# from uuid import UUID
# from sqlalchemy.orm import Session
# from sqlalchemy import and_, desc, func
# from database.base_repository import BaseRepository
# from database.models.satellite_data import SatelliteData
# from pydantic import BaseModel

# class SatelliteDataCreate(BaseModel):
#     job_run_id: UUID
#     satellite_type: str
#     acquisition_date: datetime
#     cloud_coverage: Optional[float] = None
#     ndvi_mean: Optional[float] = None
#     ndvi_std: Optional[float] = None
#     ndvi_min: Optional[float] = None
#     ndvi_max: Optional[float] = None
#     ndwi_mean: Optional[float] = None
#     ndwi_std: Optional[float] = None
#     ndmi_mean: Optional[float] = None
#     ndmi_std: Optional[float] = None
#     geometry_geojson: Dict[str, Any]
#     metadata: Optional[Dict[str, Any]] = None
#     image_urls: Optional[Dict[str, Any]] = None
#     processing_status: str = "processed"

# class SatelliteDataUpdate(BaseModel):
#     cloud_coverage: Optional[float] = None
#     ndvi_mean: Optional[float] = None
#     ndvi_std: Optional[float] = None
#     ndvi_min: Optional[float] = None
#     ndvi_max: Optional[float] = None
#     ndwi_mean: Optional[float] = None
#     ndwi_std: Optional[float] = None
#     ndmi_mean: Optional[float] = None
#     ndmi_std: Optional[float] = None
#     metadata: Optional[Dict[str, Any]] = None
#     image_urls: Optional[Dict[str, Any]] = None
#     processing_status: Optional[str] = None

# class SatelliteDataRepository(BaseRepository[SatelliteData, SatelliteDataCreate, SatelliteDataUpdate]):
#     """Repository for satellite data operations."""
    
#     def __init__(self, session: Session):
#         super().__init__(session, SatelliteData)
    
#     def get_by_job_run(self, job_run_id: UUID) -> List[SatelliteData]:
#         """Get all satellite data for a specific job run."""
#         return (
#             self.session.query(SatelliteData)
#             .filter(SatelliteData.job_run_id == job_run_id)
#             .order_by(desc(SatelliteData.acquisition_date))
#             .all()
#         )
    
#     def get_by_satellite_type(self, satellite_type: str, limit: int = 100) -> List[SatelliteData]:
#         """Get satellite data by satellite type."""
#         return (
#             self.session.query(SatelliteData)
#             .filter(SatelliteData.satellite_type == satellite_type)
#             .order_by(desc(SatelliteData.acquisition_date))
#             .limit(limit)
#             .all()
#         )
    
#     def get_by_date_range(
#         self, 
#         start_date: datetime, 
#         end_date: datetime,
#         satellite_type: Optional[str] = None
#     ) -> List[SatelliteData]:
#         """Get satellite data within date range."""
#         query = self.session.query(SatelliteData).filter(
#             and_(
#                 SatelliteData.acquisition_date >= start_date,
#                 SatelliteData.acquisition_date <= end_date
#             )
#         )
        
#         if satellite_type:
#             query = query.filter(SatelliteData.satellite_type == satellite_type)
        
#         return query.order_by(desc(SatelliteData.acquisition_date)).all()
    
#     def get_recent_data(self, days: int = 30, satellite_type: Optional[str] = None) -> List[SatelliteData]:
#         """Get recent satellite data within specified days."""
#         cutoff_date = datetime.utcnow() - timedelta(days=days)
#         return self.get_by_date_range(cutoff_date, datetime.utcnow(), satellite_type)
    
#     def get_by_cloud_coverage(self, max_cloud_coverage: float) -> List[SatelliteData]:
#         """Get satellite data with cloud coverage below threshold."""
#         return (
#             self.session.query(SatelliteData)
#             .filter(
#                 and_(
#                     SatelliteData.cloud_coverage.isnot(None),
#                     SatelliteData.cloud_coverage <= max_cloud_coverage
#                 )
#             )
#             .order_by(desc(SatelliteData.acquisition_date))
#             .all()
#         )
    
#     def get_by_ndvi_range(self, min_ndvi: float, max_ndvi: float) -> List[SatelliteData]:
#         """Get satellite data within NDVI range."""
#         return (
#             self.session.query(SatelliteData)
#             .filter(
#                 and_(
#                     SatelliteData.ndvi_mean.isnot(None),
#                     SatelliteData.ndvi_mean >= min_ndvi,
#                     SatelliteData.ndvi_mean <= max_ndvi
#                 )
#             )
#             .order_by(desc(SatelliteData.acquisition_date))
#             .all()
#         )
    
#     def get_metric_statistics(self, metric_name: str, days: int = 30) -> Dict[str, Any]:
#         """Get statistics for a specific metric over time period."""
#         cutoff_date = datetime.utcnow() - timedelta(days=days)
        
#         metric_column = getattr(SatelliteData, f"{metric_name}_mean", None)
#         if not metric_column:
#             raise ValueError(f"Invalid metric name: {metric_name}")
        
#         stats = (
#             self.session.query(
#                 func.count(metric_column).label('count'),
#                 func.avg(metric_column).label('mean'),
#                 func.min(metric_column).label('min'),
#                 func.max(metric_column).label('max'),
#                 func.stddev(metric_column).label('stddev')
#             )
#             .filter(
#                 and_(
#                     SatelliteData.acquisition_date >= cutoff_date,
#                     metric_column.isnot(None)
#                 )
#             )
#             .first()
#         )
        
#         return {
#             "metric": metric_name,
#             "period_days": days,
#             "count": stats.count if stats else 0,
#             "mean": float(stats.mean) if stats and stats.mean else None,
#             "min": float(stats.min) if stats and stats.min else None,
#             "max": float(stats.max) if stats and stats.max else None,
#             "stddev": float(stats.stddev) if stats and stats.stddev else None
#         }
    
#     def get_processing_failures(self) -> List[SatelliteData]:
#         """Get satellite data with processing failures."""
#         return (
#             self.session.query(SatelliteData)
#             .filter(SatelliteData.processing_status.in_(["failed", "partial"]))
#             .order_by(desc(SatelliteData.created_at))
#             .all()
#         )
    
#     def get_data_with_images(self) -> List[SatelliteData]:
#         """Get satellite data that has associated image URLs."""
#         return (
#             self.session.query(SatelliteData)
#             .filter(SatelliteData.image_urls.isnot(None))
#             .order_by(desc(SatelliteData.acquisition_date))
#             .all()
#         )
    
#     def search_by_geometry(self, geometry_criteria: Dict[str, Any]) -> List[SatelliteData]:
#         """Search satellite data by geometry criteria in GeoJSON."""
#         query = self.session.query(SatelliteData)
        
#         for key, value in geometry_criteria.items():
#             query = query.filter(SatelliteData.geometry_geojson[key].astext == str(value))
        
#         return query.order_by(desc(SatelliteData.acquisition_date)).all()
    
#     def cleanup_old_data(self, days: int = 365) -> int:
#         """Delete satellite data older than specified days. Returns count of deleted records."""
#         cutoff_date = datetime.utcnow() - timedelta(days=days)
#         deleted_count = (
#             self.session.query(SatelliteData)
#             .filter(SatelliteData.acquisition_date < cutoff_date)
#             .delete()
#         )
#         self.session.commit()
#         return deleted_count