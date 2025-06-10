from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum

class AlertType(str, Enum):
    ANOMALY = "anomaly"
    THRESHOLD_BREACH = "threshold_breach"
    SYSTEM_ERROR = "system_error"
    DATA_QUALITY = "data_quality"

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    PARTIAL = "partial"

class DeliveryChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"

# Alert Schemas
class AlertCreate(BaseModel):
    anomaly_id: Optional[UUID] = Field(None, description="Related anomaly ID")
    job_run_id: UUID = Field(..., description="Job run that generated this alert")
    alert_type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    title: str = Field(..., max_length=200, description="Alert title")
    message: str = Field(..., description="Detailed alert message")
    recipients: List[str] = Field(..., min_items=1, description="Alert recipients")
    delivery_channels: List[DeliveryChannel] = Field(
        default=[DeliveryChannel.EMAIL],
        description="Delivery channels for the alert"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional alert metadata")

class AlertUpdate(BaseModel):
    delivery_status: Optional[DeliveryStatus] = None
    delivery_attempts: Optional[Dict[str, Any]] = None
    resolved: Optional[bool] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class AlertResponse(BaseModel):
    id: UUID
    anomaly_id: Optional[UUID]
    job_run_id: UUID
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    recipients: List[str]
    delivery_channels: List[DeliveryChannel]
    delivery_status: DeliveryStatus
    delivery_attempts: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    resolved: bool
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# Alert Resolution
class AlertResolveRequest(BaseModel):
    resolved_by: str = Field(..., description="User resolving the alert")
    resolution_notes: Optional[str] = Field(None, description="Optional resolution notes")

class BulkAlertResolveRequest(BaseModel):
    alert_ids: List[UUID] = Field(..., min_items=1, description="List of alert IDs to resolve")
    resolved_by: str = Field(..., description="User resolving the alerts")
    resolution_notes: Optional[str] = Field(None, description="Optional resolution notes")

# Alert Delivery
class AlertDeliveryAttempt(BaseModel):
    channel: DeliveryChannel
    recipient: str
    status: str
    timestamp: datetime
    error_message: Optional[str] = None

class AlertDeliveryUpdate(BaseModel):
    delivery_status: DeliveryStatus
    delivery_details: Dict[str, Any]

# Alert Statistics
class AlertStatistics(BaseModel):
    period_days: int
    total_alerts: int
    resolved_alerts: int
    unresolved_alerts: int
    by_delivery_status: Dict[str, int]
    by_severity: Dict[str, int]
    by_type: Dict[str, int]

class AlertDeliveryStats(BaseModel):
    period_days: int
    channels: Dict[str, Dict[str, Any]]

# Alert List Response
class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    skip: int
    limit: int

# Alert Filters
class AlertFilters(BaseModel):
    alert_type: Optional[AlertType] = None
    severity: Optional[AlertSeverity] = None
    delivery_status: Optional[DeliveryStatus] = None
    resolved: Optional[bool] = None
    job_run_id: Optional[UUID] = None
    anomaly_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None