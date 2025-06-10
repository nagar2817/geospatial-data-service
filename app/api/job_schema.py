from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

class JobType(str, Enum):
    FETCH_DATA = "fetch_data"
    ALERT_EVAL = "alert_eval"
    METRIC_CALC = "metric_calc"
    ANOMALY_DETECTION = "anomaly_detection"
    CHANGE_ANALYSIS = "change_analysis"
    MONITORING = "monitoring"

class ScheduleType(str, Enum):
    CRON = "cron"
    INTERVAL = "interval"
    EVENT_TRIGGERED = "event_triggered"

class JobStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

class TriggerType(str, Enum):
    CRON = "cron"
    MANUAL = "manual"
    EVENT = "event"

# Job Definition Schemas
class JobDefinitionCreate(BaseModel):
    job_name: str = Field(..., description="Human-readable job name")
    job_type: JobType = Field(..., description="Type of geospatial job")
    schedule_cron: Optional[str] = Field(None, description="Cron expression for scheduling")
    schedule_type: ScheduleType = Field(ScheduleType.EVENT_TRIGGERED, description="Schedule type")
    interval_days: Optional[int] = Field(None, description="Interval in days for interval scheduling")
    enabled: bool = Field(True, description="Whether job is active")
    next_run_at: Optional[datetime] = Field(None, description="Next execution time")
    payload: Dict[str, Any] = Field(..., description="Job parameters including polygon data")
    target_function: str = Field(..., description="Pipeline function to execute")
    retry_policy: Optional[Dict[str, Any]] = Field(
        default={"max_retries": 3, "delay": 60},
        description="Retry configuration"
    )

    @validator('schedule_cron')
    def validate_cron_expression(cls, v, values):
        if values.get('schedule_type') == ScheduleType.CRON and not v:
            raise ValueError('Cron expression required when schedule_type is cron')
        return v

    @validator('interval_days')
    def validate_interval_days(cls, v, values):
        if values.get('schedule_type') == ScheduleType.INTERVAL and not v:
            raise ValueError('Interval days required when schedule_type is interval')
        if v and v <= 0:
            raise ValueError('Interval days must be positive')
        return v

    @validator('payload')
    def validate_payload_structure(cls, v):
        required_fields = ['coordinates', 'satellite_type']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Payload must contain {field}')
        return v

class JobDefinitionUpdate(BaseModel):
    job_name: Optional[str] = None
    job_type: Optional[JobType] = None
    schedule_cron: Optional[str] = None
    schedule_type: Optional[ScheduleType] = None
    interval_days: Optional[int] = None
    enabled: Optional[bool] = None
    next_run_at: Optional[datetime] = None
    payload: Optional[Dict[str, Any]] = None
    target_function: Optional[str] = None
    retry_policy: Optional[Dict[str, Any]] = None

class JobDefinitionResponse(BaseModel):
    id: UUID
    job_name: str
    job_type: JobType
    schedule_cron: Optional[str]
    schedule_type: ScheduleType
    interval_days: Optional[int]
    enabled: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    payload: Dict[str, Any]
    target_function: str
    retry_policy: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Job Run Schemas
class JobRunCreate(BaseModel):
    id: UUID
    triggered_by: TriggerType = TriggerType.MANUAL
    execution_host: Optional[str] = None

class JobRunUpdate(BaseModel):
    status: Optional[JobStatus] = None
    log_message: Optional[Dict[str, Any]] = None
    output_summary: Optional[Dict[str, Any]] = None
    execution_host: Optional[str] = None

class JobRunResponse(BaseModel):
    id: UUID
    job_id: UUID
    start_time: datetime
    end_time: Optional[datetime]
    status: JobStatus
    log_message: Optional[Dict[str, Any]]
    output_summary: Optional[Dict[str, Any]]
    triggered_by: TriggerType
    execution_host: Optional[str]

    class Config:
        from_attributes = True

# Job Statistics
class JobStatistics(BaseModel):
    total_jobs: int
    enabled_jobs: int
    disabled_jobs: int
    jobs_by_type: Dict[str, int]
    jobs_by_schedule_type: Dict[str, int]

class JobRunStatistics(BaseModel):
    period_hours: int
    total_runs: int
    stats_by_status: Dict[str, Dict[str, Any]]

# Job Trigger Request
class JobTriggerRequest(BaseModel):
    execution_host: Optional[str] = Field(None, description="Host identifier for execution")
    override_payload: Optional[Dict[str, Any]] = Field(None, description="Override job payload for this execution")

# Job List Response
class JobListResponse(BaseModel):
    jobs: List[JobDefinitionResponse]
    total: int
    skip: int
    limit: int

class JobRunListResponse(BaseModel):
    runs: List[JobRunResponse]
    total: int
    skip: int
    limit: int