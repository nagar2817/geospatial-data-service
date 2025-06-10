# from datetime import datetime, timedelta
# from typing import List, Optional, Dict, Any
# from uuid import UUID
# from sqlalchemy.orm import Session
# from sqlalchemy import and_, desc, func
# from database.base_repository import BaseRepository
# from database.models.anomaly import Anomaly
# from pydantic import BaseModel

# class AnomalyCreate(BaseModel):
#     satellite_data_id: UUID
#     job_run_id: UUID
#     anomaly_type: str
#     metric_name: str
#     severity: str
#     confidence_score: float
#     threshold_value: Optional[float] = None
#     actual_value: float
#     deviation_percent: Optional[float] = None
#     baseline_value: Optional[float] = None
#     detection_method: str
#     description: Optional[str] = None
#     metadata: Optional[Dict[str, Any]] = None

# class AnomalyUpdate(BaseModel):
#     severity: Optional[str] = None
#     description: Optional[str] = None
#     metadata: Optional[Dict[str, Any]] = None
#     acknowledged: Optional[bool] = None
#     acknowledged_by: Optional[str] = None
#     acknowledged_at: Optional[datetime] = None

# class AnomalyRepository(BaseRepository[Anomaly, AnomalyCreate, AnomalyUpdate]):
#     """Repository for anomaly operations."""
    
#     def __init__(self, session: Session):
#         super().__init__(session, Anomaly)
    
#     def get_by_job_run(self, job_run_id: UUID) -> List[Anomaly]:
#         """Get all anomalies detected in a specific job run."""
#         return (
#             self.session.query(Anomaly)
#             .filter(Anomaly.job_run_id == job_run_id)
#             .order_by(desc(Anomaly.created_at))
#             .all()
#         )
    
#     def get_by_satellite_data(self, satellite_data_id: UUID) -> List[Anomaly]:
#         """Get all anomalies for specific satellite data."""
#         return (
#             self.session.query(Anomaly)
#             .filter(Anomaly.satellite_data_id == satellite_data_id)
#             .order_by(desc(Anomaly.created_at))
#             .all()
#         )
    
#     def get_by_severity(self, severity: str, limit: int = 100) -> List[Anomaly]:
#         """Get anomalies by severity level."""
#         return (
#             self.session.query(Anomaly)
#             .filter(Anomaly.severity == severity)
#             .order_by(desc(Anomaly.created_at))
#             .limit(limit)
#             .all()
#         )
    
#     def get_by_anomaly_type(self, anomaly_type: str, limit: int = 100) -> List[Anomaly]:
#         """Get anomalies by type."""
#         return (
#             self.session.query(Anomaly)
#             .filter(Anomaly.anomaly_type == anomaly_type)
#             .order_by(desc(Anomaly.created_at))
#             .limit(limit)
#             .all()
#         )
    
#     def get_by_metric(self, metric_name: str, limit: int = 100) -> List[Anomaly]:
#         """Get anomalies for a specific metric."""
#         return (
#             self.session.query(Anomaly)
#             .filter(Anomaly.metric_name == metric_name)
#             .order_by(desc(Anomaly.created_at))
#             .limit(limit)
#             .all()
#         )
    
#     def get_unacknowledged(self) -> List[Anomaly]:
#         """Get all unacknowledged anomalies."""
#         return (
#             self.session.query(Anomaly)
#             .filter(Anomaly.acknowledged == False)
#             .order_by(desc(Anomaly.created_at))
#             .all()
#         )
    
#     def get_recent_anomalies(self, hours: int = 24) -> List[Anomaly]:
#         """Get anomalies detected within specified hours."""
#         cutoff_time = datetime.utcnow() - timedelta(hours=hours)
#         return (
#             self.session.query(Anomaly)
#             .filter(Anomaly.created_at >= cutoff_time)
#             .order_by(desc(Anomaly.created_at))
#             .all()
#         )
    
#     def get_high_confidence_anomalies(self, min_confidence: float = 0.8) -> List[Anomaly]:
#         """Get anomalies with confidence score above threshold."""
#         return (
#             self.session.query(Anomaly)
#             .filter(Anomaly.confidence_score >= min_confidence)
#             .order_by(desc(Anomaly.confidence_score))
#             .all()
#         )
    
#     def acknowledge_anomaly(self, anomaly_id: UUID, acknowledged_by: str) -> bool:
#         """Acknowledge an anomaly."""
#         anomaly = self.get(anomaly_id)
#         if anomaly:
#             anomaly.acknowledged = True
#             anomaly.acknowledged_by = acknowledged_by
#             anomaly.acknowledged_at = datetime.utcnow()
#             self.session.commit()
#             return True
#         return False
    
#     def acknowledge_multiple(self, anomaly_ids: List[UUID], acknowledged_by: str) -> int:
#         """Acknowledge multiple anomalies. Returns count of acknowledged anomalies."""
#         updated_count = (
#             self.session.query(Anomaly)
#             .filter(Anomaly.id.in_(anomaly_ids))
#             .update({
#                 "acknowledged": True,
#                 "acknowledged_by": acknowledged_by,
#                 "acknowledged_at": datetime.utcnow()
#             }, synchronize_session=False)
#         )
#         self.session.commit()
#         return updated_count
    
#     def get_anomaly_statistics(self, days: int = 30) -> Dict[str, Any]:
#         """Get anomaly statistics for specified time period."""
#         cutoff_time = datetime.utcnow() - timedelta(days=days)
        
#         # Count by severity
#         severity_stats = (
#             self.session.query(
#                 Anomaly.severity,
#                 func.count(Anomaly.id).label('count')
#             )
#             .filter(Anomaly.created_at >= cutoff_time)
#             .group_by(Anomaly.severity)
#             .all()
#         )
        
#         # Count by type
#         type_stats = (
#             self.session.query(
#                 Anomaly.anomaly_type,
#                 func.count(Anomaly.id).label('count')
#             )
#             .filter(Anomaly.created_at >= cutoff_time)
#             .group_by(Anomaly.anomaly_type)
#             .all()
#         )
        
#         # Count by metric
#         metric_stats = (
#             self.session.query(
#                 Anomaly.metric_name,
#                 func.count(Anomaly.id).label('count')
#             )
#             .filter(Anomaly.created_at >= cutoff_time)
#             .group_by(Anomaly.metric_name)
#             .all()
#         )
        
#         # Total and acknowledged counts
#         total_count = (
#             self.session.query(func.count(Anomaly.id))
#             .filter(Anomaly.created_at >= cutoff_time)
#             .scalar()
#         )
        
#         acknowledged_count = (
#             self.session.query(func.count(Anomaly.id))
#             .filter(
#                 and_(
#                     Anomaly.created_at >= cutoff_time,
#                     Anomaly.acknowledged == True
#                 )
#             )
#             .scalar()
#         )
        
#         return {
#             "period_days": days,
#             "total_anomalies": total_count,
#             "acknowledged_anomalies": acknowledged_count,
#             "unacknowledged_anomalies": total_count - acknowledged_count,
#             "by_severity": {stat.severity: stat.count for stat in severity_stats},
#             "by_type": {stat.anomaly_type: stat.count for stat in type_stats},
#             "by_metric": {stat.metric_name: stat.count for stat in metric_stats}
#         }
    
#     def get_detection_method_performance(self, days: int = 30) -> Dict[str, Any]:
#         """Get performance statistics by detection method."""
#         cutoff_time = datetime.utcnow() - timedelta(days=days)
        
#         stats = (
#             self.session.query(
#                 Anomaly.detection_method,
#                 func.count(Anomaly.id).label('count'),
#                 func.avg(Anomaly.confidence_score).label('avg_confidence'),
#                 func.min(Anomaly.confidence_score).label('min_confidence'),
#                 func.max(Anomaly.confidence_score).label('max_confidence')
#             )
#             .filter(Anomaly.created_at >= cutoff_time)
#             .group_by(Anomaly.detection_method)
#             .all()
#         )
        
#         return {
#             "period_days": days,
#             "methods": {
#                 stat.detection_method: {
#                     "count": stat.count,
#                     "avg_confidence": float(stat.avg_confidence) if stat.avg_confidence else None,
#                     "min_confidence": float(stat.min_confidence) if stat.min_confidence else None,
#                     "max_confidence": float(stat.max_confidence) if stat.max_confidence else None
#                 }
#                 for stat in stats
#             }
#         }