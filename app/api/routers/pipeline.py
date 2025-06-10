from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from core.schema import TriggerType, PipelineResult
from pipelines.registry import PipelineRegistry

router = APIRouter(prefix="/pipelines", tags=["pipelines"])

class PipelineExecutionRequest(BaseModel):
    pipeline_name: Optional[str] = "job_discovery"
    trigger_metadata: Dict[str, Any] = {}

@router.post("/execute", response_model=PipelineResult)
async def execute_pipeline(request: PipelineExecutionRequest):
    """Execute pipeline via API trigger"""
    
    try:
        pipeline = PipelineRegistry.get_pipeline(
            trigger_type=TriggerType.API,
            pipeline_name=request.pipeline_name
        )
        
        result = await pipeline.run(
            trigger_type=TriggerType.API,
            trigger_metadata=request.trigger_metadata
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {str(e)}"
        )

@router.post("/discover-jobs", response_model=PipelineResult)
async def discover_jobs(
    job_filters: Optional[Dict[str, Any]] = None,
    execution_host: Optional[str] = None
):
    """Trigger job discovery pipeline"""
    
    trigger_metadata = {
        "filters": job_filters or {},
        "execution_host": execution_host or "api"
    }
    
    request = PipelineExecutionRequest(
        pipeline_name="job_discovery",
        trigger_metadata=trigger_metadata
    )
    
    return await execute_pipeline(request)