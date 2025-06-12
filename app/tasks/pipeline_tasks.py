import logging
from config.celery_config import celery_app
from core.schema import TriggerType

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.pipeline_tasks.execute_job_discovery")
def execute_job_discovery_pipeline(trigger_metadata: dict = None):
    """Celery task to execute job discovery pipeline"""
    from pipelines.registry import PipelineRegistry
    
    try:
        pipeline = PipelineRegistry.get_pipeline(TriggerType.CRON, "job_discovery")
        
        # Run pipeline synchronously in Celery worker
        import asyncio
        result = asyncio.run(pipeline.run(
            trigger_type=TriggerType.CRON,
            trigger_metadata=trigger_metadata or {}
        ))
        
        logger.info(f"Job discovery pipeline completed: {result.jobs_queued} jobs queued")
        
        return {
            "success": result.success,
            "message": result.message,
            "jobs_processed": result.jobs_processed,
            "jobs_queued": result.jobs_queued,
            "execution_time_ms": result.execution_time_ms
        }
        
    except Exception as e:
        logger.error(f"Job discovery pipeline failed: {str(e)}")
        return {
            "success": False,
            "message": f"Pipeline failed: {str(e)}",
            "jobs_processed": 0,
            "jobs_queued": 0
        }