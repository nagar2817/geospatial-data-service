import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database.connection import Base

class JobDefinition(Base):
    """Job definitions table for scheduled and on-demand geospatial processing jobs."""
    
    __tablename__ = "job_definitions"
    __table_args__ = {"schema": "carbonleap"}  # Specify schema
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier for the job definition"
    )
    
    job_name = Column(
        Text,
        nullable=False,
        doc="Human-readable job name"
    )
    
    job_type = Column(
        Text,
        nullable=False,
        doc="Type of job: fetch_data, alert_eval, metric_calc, etc."
    )
    
    schedule_cron = Column(
        Text,
        nullable=True,
        doc="Cron expression for scheduling (e.g., '0 6 * * *')"
    )
    
    schedule_type = Column(
        Text,
        nullable=False,
        default="event_triggered",
        doc="Schedule type: cron, interval, or event_triggered"
    )
    
    interval_days = Column(
        Integer,
        nullable=True,
        doc="Interval in days (only used if schedule_type = interval)"
    )
    
    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        doc="Whether the job is active and should be executed"
    )
    
    last_run_at = Column(
        DateTime,
        nullable=True,
        doc="Timestamp of last execution"
    )
    
    next_run_at = Column(
        DateTime,
        nullable=True,
        doc="Timestamp of next scheduled execution"
    )
    
    payload = Column(
        JSONB,
        nullable=False,
        doc="Job parameters including coordinates, satellite type, farm_id, polygon data, etc."
    )
    
    target_function = Column(
        Text,
        nullable=False,
        doc="Pipeline function name to execute (e.g., 'run_sentinel_fetch')"
    )
    
    retry_policy = Column(
        JSONB,
        nullable=True,
        default={"max_retries": 3, "delay": 60},
        doc="Retry configuration: count, delay strategy"
    )
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Job definition creation timestamp"
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Last update timestamp"
    )
    
    # Relationship to job runs
    job_runs = relationship("JobRun", back_populates="job_definition", cascade="all, delete-orphan")

class JobRun(Base):
    """Job execution logs and results."""
    
    __tablename__ = "job_runs"
    __table_args__ = {"schema": "carbonleap"}  # Specify schema
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier for the job run"
    )
    
    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("carbonleap.job_definitions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the job definition being executed"
    )
    
    start_time = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Job execution start timestamp"
    )
    
    end_time = Column(
        DateTime,
        nullable=True,
        doc="Job execution completion timestamp"
    )
    
    status = Column(
        Text,
        nullable=False,
        default="running",
        doc="Execution status: success, failed, running, skipped"
    )
    
    log_message = Column(
        JSONB,
        nullable=True,
        doc="Execution logs, error messages, or stack traces"
    )
    
    output_summary = Column(
        JSONB,
        nullable=True,
        doc="Final output: statistics, image links, alert count, metrics, etc."
    )
    
    triggered_by = Column(
        Text,
        nullable=False,
        default="manual",
        doc="Trigger source: cron, manual, or event"
    )
    
    execution_host = Column(
        Text,
        nullable=True,
        doc="Hostname or worker ID that executed the job"
    )
    
    # Relationship to job definition
    job_definition = relationship("JobDefinition", back_populates="job_runs")