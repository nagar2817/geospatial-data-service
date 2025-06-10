# import uuid
# from datetime import datetime
# from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, Boolean
# from sqlalchemy.dialects.postgresql import UUID, JSONB
# from sqlalchemy.orm import relationship
# from database.connection import Base

# class Anomaly(Base):
#     """Detected anomalies in satellite data metrics."""
    
#     __tablename__ = "anomalies"
    
#     id = Column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#         doc="Unique identifier for anomaly record"
#     )
    
#     satellite_data_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey("satellite_data.id", ondelete="CASCADE"),
#         nullable=False,
#         doc="Reference to satellite data where anomaly was detected"
#     )
    
#     job_run_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey("job_runs.run_id", ondelete="CASCADE"),
#         nullable=False,
#         doc="Reference to the job run that detected this anomaly"
#     )
    
#     anomaly_type = Column(
#         String(50),
#         nullable=False,
#         doc="Type of anomaly: ndvi_drop, ndwi_spike, seasonal_deviation, etc."
#     )
    
#     metric_name = Column(
#         String(50),
#         nullable=False,
#         doc="Metric where anomaly was detected: ndvi, ndwi, ndmi"
#     )
    
#     severity = Column(
#         String(20),
#         nullable=False,
#         doc="Anomaly severity: low, medium, high, critical"
#     )
    
#     confidence_score = Column(
#         Float,
#         nullable=False,
#         doc="Confidence score for anomaly detection (0.0 to 1.0)"
#     )
    
#     threshold_value = Column(
#         Float,
#         nullable=True,
#         doc="Threshold value that was exceeded"
#     )
    
#     actual_value = Column(
#         Float,
#         nullable=False,
#         doc="Actual metric value that triggered the anomaly"
#     )
    
#     deviation_percent = Column(
#         Float,
#         nullable=True,
#         doc="Percentage deviation from expected/baseline value"
#     )
    
#     baseline_value = Column(
#         Float,
#         nullable=True,
#         doc="Expected or historical baseline value"
#     )
    
#     detection_method = Column(
#         String(50),
#         nullable=False,
#         doc="Method used to detect anomaly: statistical, ml, threshold"
#     )
    
#     description = Column(
#         Text,
#         nullable=True,
#         doc="Human-readable description of the anomaly"
#     )
    
#     metadata = Column(
#         JSONB,
#         nullable=True,
#         doc="Additional anomaly detection metadata and parameters"
#     )
    
#     acknowledged = Column(
#         Boolean,
#         nullable=False,
#         default=False,
#         doc="Whether the anomaly has been acknowledged by an operator"
#     )
    
#     acknowledged_by = Column(
#         String(100),
#         nullable=True,
#         doc="User who acknowledged the anomaly"
#     )
    
#     acknowledged_at = Column(
#         DateTime,
#         nullable=True,
#         doc="Timestamp when anomaly was acknowledged"
#     )
    
#     created_at = Column(
#         DateTime,
#         nullable=False,
#         default=datetime.utcnow,
#         doc="Anomaly detection timestamp"
#     )
    
#     # Relationships
#     satellite_data = relationship("SatelliteData", backref="anomalies")
#     job_run = relationship("JobRun", backref="detected_anomalies")