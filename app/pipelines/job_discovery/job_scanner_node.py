import logging
from datetime import datetime, UTC
from typing import List, Dict, Any
from database import SessionLocal, RepositoryFactory
from core.base import BaseNode
from core.schema import PipelineContext, TriggerType

logger = logging.getLogger(__name__)

class JobScannerNode(BaseNode):
    """Scans for eligible jobs based on schedule and trigger type"""
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Scan and identify eligible jobs for processing"""
        
        with SessionLocal() as session:
            repo_factory = RepositoryFactory(session)
            
            try:
                if context.trigger_type == TriggerType.CRON:
                    # Cron-triggered: get jobs eligible for scheduled execution
                    eligible_jobs = repo_factory.job_definition.get_eligible_jobs()
                    context.execution_stats["scan_method"] = "scheduled_jobs"
                    
                elif context.trigger_type == TriggerType.API:
                    # API-triggered: get jobs based on API parameters
                    job_filters = context.trigger_metadata.get("filters", {})
                    eligible_jobs = repo_factory.job_definition.get_multi(filters=job_filters)
                    context.execution_stats["scan_method"] = "api_filtered"
                    
                elif context.trigger_type == TriggerType.MANUAL:
                    # Manual trigger: get specific job or all enabled jobs
                    job_id = context.trigger_metadata.get("job_id")
                    if job_id:
                        job = repo_factory.job_definition.get(job_id)
                        eligible_jobs = [job] if job else []
                    else:
                        eligible_jobs = repo_factory.job_definition.get_enabled_jobs()
                    context.execution_stats["scan_method"] = "manual_selection"
                    
                elif context.trigger_type == TriggerType.EVENT:
                    # Event-triggered: get jobs based on event criteria
                    event_criteria = context.trigger_metadata.get("event_criteria", {})
                    eligible_jobs = self._scan_by_event_criteria(repo_factory, event_criteria)
                    context.execution_stats["scan_method"] = "event_driven"
                    
                else:
                    logger.warning(f"Unknown trigger type: {context.trigger_type}")
                    eligible_jobs = []
                
                # Convert to dict format for context
                context.eligible_jobs = [
                    {
                        "job_id": str(job.id),
                        "job_name": job.job_name,
                        "job_type": job.job_type,
                        "schedule_type": job.schedule_type,
                        "enabled": job.enabled,
                        "last_run_at": job.last_run_at.isoformat() if job.last_run_at else None,
                        "next_run_at": job.next_run_at.isoformat() if job.next_run_at else None,
                        "payload": job.payload,
                        "target_function": job.target_function,
                        "retry_policy": job.retry_policy or {}
                    }
                    for job in eligible_jobs
                ]
                
                context.execution_stats.update({
                    "jobs_scanned": len(context.eligible_jobs),
                    "scan_timestamp": datetime.now(UTC).isoformat()
                })
                
                logger.info(f"JobScanner found {len(context.eligible_jobs)} eligible jobs")
                
            except Exception as e:
                logger.error(f"JobScanner failed: {str(e)}")
                context.errors.append(f"JobScanner: {str(e)}")
                raise
                
        return context
    
    def _scan_by_event_criteria(self, repo_factory: RepositoryFactory, event_criteria: Dict[str, Any]) -> List:
        """Scan jobs based on event criteria"""
        
        # Example event criteria handling
        event_type = event_criteria.get("event_type")
        
        if event_type == "anomaly_detected":
            # Get anomaly detection jobs
            return repo_factory.job_definition.get_by_job_type("anomaly_detection")
            
        elif event_type == "data_quality_alert":
            # Get monitoring jobs
            return repo_factory.job_definition.get_by_job_type("monitoring")
            
        elif event_type == "polygon_updated":
            # Get jobs with specific polygon data
            polygon_id = event_criteria.get("polygon_id")
            if polygon_id:
                return repo_factory.job_definition.search_by_payload({"polygon_id": polygon_id})
            
        # Default: return all enabled jobs
        return repo_factory.job_definition.get_enabled_jobs()