import logging
from datetime import datetime, UTC
from core.base import BaseNode
from core.schema import PipelineContext

logger = logging.getLogger(__name__)

class JobStatsNode(BaseNode):
    """Collects and logs pipeline execution statistics"""
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Collect final pipeline statistics"""
        
        # Calculate final stats
        final_stats = {
            "pipeline_execution": {
                "trigger_type": context.trigger_type.value,
                "execution_completed_at": datetime.now(UTC).isoformat(),
                "total_errors": len(context.errors)
            },
            "job_processing": {
                "jobs_discovered": len(context.eligible_jobs),
                "jobs_validated": len(context.validated_jobs),
                "jobs_routed": sum(len(jobs) for queue, jobs in context.routed_jobs.items() if queue != "failed_routing"),
                "jobs_failed_routing": len(context.routed_jobs.get("failed_routing", [])),
                "validation_success_rate": self._calculate_success_rate(
                    len(context.validated_jobs), 
                    len(context.eligible_jobs)
                ),
                "routing_success_rate": self._calculate_success_rate(
                    sum(len(jobs) for queue, jobs in context.routed_jobs.items() if queue != "failed_routing"),
                    len(context.validated_jobs)
                )
            },
            "queue_distribution": {
                queue: len(jobs) for queue, jobs in context.routed_jobs.items()
            }
        }
        
        # Merge with existing stats
        context.execution_stats.update(final_stats)
        
        # Log summary
        self._log_pipeline_summary(context)
        
        # Log detailed stats for monitoring
        self._log_detailed_stats(context)
        
        return context
    
    def _calculate_success_rate(self, successful: int, total: int) -> float:
        """Calculate success rate percentage"""
        if total == 0:
            return 100.0
        return round((successful / total) * 100, 2)
    
    def _log_pipeline_summary(self, context: PipelineContext):
        """Log pipeline execution summary"""
        
        stats = context.execution_stats
        job_stats = stats.get("job_processing", {})
        
        logger.info(
            f"Job Discovery Pipeline Summary - "
            f"Trigger: {context.trigger_type.value} | "
            f"Discovered: {job_stats.get('jobs_discovered', 0)} | "
            f"Validated: {job_stats.get('jobs_validated', 0)} | "
            f"Queued: {job_stats.get('jobs_routed', 0)} | "
            f"Errors: {len(context.errors)}"
        )
        
        if context.errors:
            logger.warning(f"Pipeline completed with errors: {context.errors}")
    
    def _log_detailed_stats(self, context: PipelineContext):
        """Log detailed statistics for monitoring and analytics"""
        
        stats = context.execution_stats
        
        # Log queue distribution
        queue_dist = stats.get("queue_distribution", {})
        if queue_dist:
            queue_summary = ", ".join([f"{queue}: {count}" for queue, count in queue_dist.items() if count > 0])
            logger.info(f"Queue Distribution - {queue_summary}")
        
        # Log validation details
        validation_rate = stats.get("job_processing", {}).get("validation_success_rate", 0)
        logger.info(f"Validation Success Rate: {validation_rate}%")
        
        # Log routing details  
        routing_rate = stats.get("job_processing", {}).get("routing_success_rate", 0)
        logger.info(f"Routing Success Rate: {routing_rate}%")
        
        # Log timing information
        scan_time = stats.get("scan_timestamp")
        validation_time = stats.get("validation_timestamp")
        queuing_time = stats.get("queuing_timestamp")
        
        if scan_time and validation_time and queuing_time:
            logger.debug(f"Pipeline Timing - Scan: {scan_time}, Validation: {validation_time}, Queuing: {queuing_time}")