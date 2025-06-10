import logging
from typing import Dict, Type
from core.pipeline import Pipeline
from core.schema import TriggerType
from pipelines.job_discovery.pipeline import JobDiscoveryPipeline

logger = logging.getLogger(__name__)

class PipelineRegistry:
    """Registry for managing geospatial data processing pipelines"""
    
    pipelines: Dict[str, Type[Pipeline]] = {
        "job_discovery": JobDiscoveryPipeline,
        # Add other pipelines here
        # "anomaly_detection": AnomalyDetectionPipeline,
        # "change_analysis": ChangeAnalysisPipeline,
    }
    
    @staticmethod
    def get_pipeline_type(trigger_type: TriggerType, pipeline_name: str = None) -> str:
        """Determine pipeline type based on trigger and optional pipeline name"""
        
        if pipeline_name and pipeline_name in PipelineRegistry.pipelines:
            return pipeline_name
        
        # Default routing logic
        if trigger_type in [TriggerType.CRON, TriggerType.API, TriggerType.MANUAL, TriggerType.EVENT]:
            return "job_discovery"
        
        raise ValueError(f"No pipeline found for trigger type: {trigger_type}")
    
    @staticmethod
    def get_pipeline(trigger_type: TriggerType, pipeline_name: str = None) -> Pipeline:
        """Get pipeline instance for execution"""
        
        pipeline_type = PipelineRegistry.get_pipeline_type(trigger_type, pipeline_name)
        pipeline_class = PipelineRegistry.pipelines.get(pipeline_type)
        
        if not pipeline_class:
            raise ValueError(f"Unknown pipeline type: {pipeline_type}")
        
        logger.info(f"Using pipeline: {pipeline_class.__name__} for trigger: {trigger_type.value}")
        return pipeline_class()