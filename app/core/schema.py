from typing import List, Type, Optional, Any, Dict
from pydantic import BaseModel, Field
from enum import Enum

class TriggerType(str, Enum):
    API = "api"
    MANUAL = "manual" 
    CRON = "cron"
    EVENT = "event"

class PipelineContext(BaseModel):
    """Context passed between pipeline nodes"""
    trigger_type: TriggerType
    trigger_metadata: Dict[str, Any] = Field(default_factory=dict)
    eligible_jobs: List[Dict[str, Any]] = Field(default_factory=list)
    validated_jobs: List[Dict[str, Any]] = Field(default_factory=list)
    routed_jobs: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    execution_stats: Dict[str, Any] = Field(default_factory=dict)

class PipelineResult(BaseModel):
    """Result of pipeline execution"""
    success: bool
    message: str
    jobs_processed: int = 0
    jobs_queued: int = 0
    errors: List[str] = Field(default_factory=list)
    execution_time_ms: float = 0
    context: Optional[PipelineContext] = None

class NodeConfig(BaseModel):
    """Configuration for a pipeline node"""
    node: Type["BaseNode"]
    connections: List[Type["BaseNode"]] = Field(default_factory=list)
    is_router: bool = False
    description: str = ""
    
class PipelineSchema(BaseModel):
    """Schema defining pipeline structure"""
    description: str
    start: Type["BaseNode"]
    nodes: List[NodeConfig]