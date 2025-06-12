import logging
from typing import Dict, List, Type
from core.base import RouterNode, BaseNode
from core.schema import PipelineContext

logger = logging.getLogger(__name__)

class JobRouterNode(RouterNode):
    """Routes validated jobs to appropriate processing queues"""
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Route jobs based on type, priority, and resources"""
        
        # Initialize routing buckets
        context.routed_jobs = {
            "high_priority": [],
            "normal_priority": [],
            "batch_processing": [],
            "monitoring": [],
            "failed_routing": []
        }
        
        routing_stats = {
            "total_routed": 0,
            "routing_decisions": []
        }
        
        for job in context.validated_jobs:
            try:
                routing_decision = self._route_job(job)
                queue_name = routing_decision["queue"]
                
                # Add routing metadata to job
                job["routing_metadata"] = routing_decision
                
                # Add to appropriate queue
                if queue_name in context.routed_jobs:
                    context.routed_jobs[queue_name].append(job)
                else:
                    context.routed_jobs["failed_routing"].append(job)
                    logger.warning(f"Unknown queue: {queue_name} for job {job['job_name']}")
                
                routing_stats["routing_decisions"].append({
                    "job_id": job["job_id"],
                    "job_name": job["job_name"],
                    "queue": queue_name,
                    "priority": routing_decision["priority"],
                    "estimated_duration": routing_decision["estimated_duration"]
                })
                
                routing_stats["total_routed"] += 1
                
            except Exception as e:
                logger.error(f"Routing failed for job {job['job_id']}: {str(e)}")
                job["routing_error"] = str(e)
                context.routed_jobs["failed_routing"].append(job)
                context.errors.append(f"Routing error for {job['job_name']}: {str(e)}")
        
        context.execution_stats.update({
            "routing_stats": routing_stats,
            "queue_distribution": {
                queue: len(jobs) for queue, jobs in context.routed_jobs.items()
            }
        })
        
        logger.info(f"JobRouter: Routed {routing_stats['total_routed']} jobs across {len(context.routed_jobs)} queues")
        
        return context
    
    def route(self, context: PipelineContext) -> List[Type[BaseNode]]:
        """Determine next nodes based on routing results"""
        from .job_queue_node import JobQueueNode
        from .job_stats_node import JobStatsNode
        
        # Always proceed to queue jobs and collect stats
        return [JobQueueNode, JobStatsNode]
    
    def _route_job(self, job: Dict) -> Dict:
        """Route individual job to appropriate queue"""
        
        job_type = job.get("job_type")
        schedule_type = job.get("schedule_type")
        payload = job.get("payload", {})
        
        # Determine priority
        priority = self._calculate_priority(job)
        
        # Determine queue based on job characteristics
        if priority == "critical":
            queue = "high_priority"
        elif job_type == "monitoring" or schedule_type == "cron":
            queue = "monitoring"
        elif self._is_batch_job(job):
            queue = "batch_processing"
        else:
            queue = "normal_priority"
        
        # Estimate processing duration
        estimated_duration = self._estimate_duration(job)
        
        # Determine Celery queue
        celery_queue = self._get_celery_queue(job_type)
        
        return {
            "queue": queue,
            "priority": priority,
            "estimated_duration": estimated_duration,
            "celery_queue": celery_queue,
            "retry_config": self._get_retry_config(job)
        }
    
    def _calculate_priority(self, job: Dict) -> str:
        """Calculate job priority"""
        
        job_type = job.get("job_type")
        payload = job.get("payload", {})
        
        # Critical: Anomaly detection with high severity
        if job_type == "anomaly_detection":
            severity = payload.get("severity", "medium")
            if severity in ["high", "critical"]:
                return "critical"
        
        # High: Real-time monitoring
        if job_type == "monitoring" and payload.get("real_time", False):
            return "high"
        
        # High: Event-triggered jobs
        if job.get("schedule_type") == "event_triggered":
            return "high"
        
        # Normal: Regular scheduled jobs
        if job.get("schedule_type") in ["cron", "interval"]:
            return "normal"
        
        # Low: Batch analysis jobs
        if job_type == "change_analysis" and payload.get("analysis_scope") == "batch":
            return "low"
        
        return "normal"
    
    def _is_batch_job(self, job: Dict) -> bool:
        """Determine if job should be processed in batch queue"""
        
        payload = job.get("payload", {})
        
        # Large area analysis
        coordinates = payload.get("coordinates", [])
        if len(coordinates) > 100:  # Large polygon
            return True
        
        # Historical analysis over large time periods
        date_range = payload.get("date_range", {})
        if date_range:
            # Check if analysis spans more than 1 year
            start = date_range.get("start")
            end = date_range.get("end")
            if start and end:
                # Simplified check - in production, parse dates properly
                return True
        
        # Batch processing flag
        if payload.get("batch_processing", False):
            return True
        
        return False
    
    def _estimate_duration(self, job: Dict) -> int:
        """Estimate job processing duration in minutes"""
        
        job_type = job.get("job_type")
        payload = job.get("payload", {})
        
        # Base duration by job type
        base_durations = {
            "fetch_data": 5,
            "metric_calc": 10,
            "anomaly_detection": 15,
            "change_analysis": 20,
            "monitoring": 3
        }
        
        base_duration = base_durations.get(job_type, 10)
        
        # Adjust based on payload complexity
        coordinates_count = len(payload.get("coordinates", []))
        complexity_multiplier = 1 + (coordinates_count / 100)  # More coordinates = longer processing
        
        # Adjust based on satellite type
        satellite_multipliers = {
            "Sentinel-2": 1.0,
            "Landsat-8": 1.2,
            "MODIS": 0.8
        }
        satellite_multiplier = satellite_multipliers.get(payload.get("satellite_type"), 1.0)
        
        estimated_duration = int(base_duration * complexity_multiplier * satellite_multiplier)
        
        return max(estimated_duration, 1)  # Minimum 1 minute
    
    def _get_celery_queue(self, job_type: str) -> str:
        """Get Celery queue name for job type"""
        
        queue_mapping = {
            "anomaly_detection": "geospatial",
            "change_analysis": "geospatial", 
            "monitoring": "monitoring",
            "fetch_data": "data_processing",
            "metric_calc": "geospatial"
        }
        
        return queue_mapping.get(job_type, "geospatial")
    
    def _get_retry_config(self, job: Dict) -> Dict:
        """Get retry configuration for job"""
        
        default_retry = job.get("retry_policy", {})
        job_type = job.get("job_type")
        
        # Job type specific retry configs - Celery format
        if job_type == "monitoring":
            return {
                "max_retries": default_retry.get("max_retries", 2),
                "interval_start": 30,  # Initial retry delay in seconds
                "interval_step": 10,   # Increment between retries
                "interval_max": 300    # Maximum retry delay
            }
        elif job_type == "anomaly_detection":
            return {
                "max_retries": default_retry.get("max_retries", 3),
                "interval_start": 60,
                "interval_step": 30,
                "interval_max": 600
            }
        else:
            return {
                "max_retries": default_retry.get("max_retries", 3),
                "interval_start": 60,
                "interval_step": 0,    # No increment for regular jobs
                "interval_max": 60
            }