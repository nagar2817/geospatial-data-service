# import uuid
# from datetime import datetime
# from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
# from sqlalchemy.dialects.postgresql import UUID, JSONB
# from sqlalchemy.orm import relationship
# from database.connection import Base

# class Alert(Base):
#     """Alert notifications triggered by anomalies or threshold breaches."""
    
#     __tablename__ = "alerts"
    
#     id = Column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#         doc="Unique identifier for alert"
#     )
    
#     anomaly_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey("anomalies.id", ondelete="CASCADE"),
#         nullable=True,
#         doc="Reference to anomaly that triggered this alert (if applicable)"
#     )
    
#     job_run_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey("carbonleap.job_runs.run_id", ondelete="CASCADE"),
#         nullable=False,
#         doc="Reference to the job run that generated this alert"
#     )
    
#     alert_type = Column(
#         String(50),
#         nullable=False,
#         doc="Type of alert: anomaly, threshold_breach, system_error, data_quality"
#     )
    
#     severity = Column(
#         String(20),
#         nullable=False,
#         doc="Alert severity: info, warning, error, critical"
#     )
    
#     title = Column(
#         String(200),
#         nullable=False,
#         doc="Alert title/subject"
#     )
    
#     message = Column(
#         Text,
#         nullable=False,
#         doc="Detailed alert message"
#     )
    
#     recipients = Column(
#         JSONB,
#         nullable=False,
#         doc="List of alert recipients (emails, webhooks, etc.)"
#     )
    
#     delivery_channels = Column(
#         JSONB,
#         nullable=False,
#         default=["email"],
#         doc="Delivery channels: email, sms, webhook, slack"
#     )
    
#     delivery_status = Column(
#         String(20),
#         nullable=False,
#         default="pending",
#         doc="Delivery status: pending, sent, failed, partial"
#     )
    
#     delivery_attempts = Column(
#         JSONB,
#         nullable=True,
#         doc="Log of delivery attempts with timestamps and results"
#     )
    
#     alert_metadata = Column(
#         JSONB,
#         nullable=True,
#         doc="Additional alert metadata and context"
#     )
    
#     resolved = Column(
#         Boolean,
#         nullable=False,
#         default=False,
#         doc="Whether the alert has been resolved"
#     )
    
#     resolved_by = Column(
#         String(100),
#         nullable=True,
#         doc="User who resolved the alert"
#     )
    
#     resolved_at = Column(
#         DateTime,
#         nullable=True,
#         doc="Timestamp when alert was resolved"
#     )
    
#     created_at = Column(
#         DateTime,
#         nullable=False,
#         default=datetime.utcnow,
#         doc="Alert creation timestamp"
#     )
    
#     # Relationships
#     anomaly = relationship("Anomaly", backref="alerts")
#     job_run = relationship("JobRun", backref="generated_alerts")