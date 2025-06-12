import logging
from datetime import datetime, UTC
from typing import Dict
from uuid import UUID
from config.celery_config import celery_app
from database import SessionLocal, RepositoryFactory
from database.repositories.job_run_repository import JobRunCreate
from core.base import BaseNode
from core.schema import PipelineContext

logger = logging.getLogger(__name__)

class JobQueueNode(BaseNode):
    """Queues validated and routed jobs to Celery with proper queue routing"""
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Queue jobs to appropriate Celery queues with explicit routing"""
        
        queuing_stats = {
            "total_queued": 0,
            "failed_to_queue": 0,
            "queuing_details": [],
            "queue_distribution": {}
        }
        
        with SessionLocal() as session:
            repo_factory = RepositoryFactory(session)
            
            # Process each routing queue
            for queue_name, jobs in context.routed_jobs.items():
                if queue_name == "failed_routing":
                    continue  # Skip failed routing jobs
                
                for job in jobs:
                    try:
                        # Create job run record
                        job_run = self._create_job_run(repo_factory, job, context)
                        
                        # Queue to Celery with explicit routing
                        task_result = self._queue_to_celery(job, job_run)
                        
                        # Update job with queuing info
                        job["job_run_id"] = str(job_run.id)
                        job["task_id"] = task_result.id
                        job["queued_at"] = datetime.now(UTC).isoformat()
                        
                        # Get actual queue used
                        actual_queue = job["routing_metadata"]["celery_queue"]
                        
                        queuing_stats["queuing_details"].append({
                            "job_id": job["job_id"],
                            "job_name": job["job_name"],
                            "job_run_id": str(job_run.id),
                            "task_id": task_result.id,
                            "queue": queue_name,
                            "celery_queue": actual_queue,
                            "routing_key": job["routing_metadata"].get("routing_key")
                        })
                        
                        # Track queue distribution
                        if actual_queue not in queuing_stats["queue_distribution"]:
                            queuing_stats["queue_distribution"][actual_queue] = 0
                        queuing_stats["queue_distribution"][actual_queue] += 1
                        
                        queuing_stats["total_queued"] += 1
                        
                        # Update job definition last run time
                        repo_factory.job_definition.update_last_run(UUID(job["job_id"]))
                        
                        logger.info(f"Queued job {job['job_name']} to queue '{actual_queue}' with task_id: {task_result.id}")
                        
                    except Exception as e:
                        logger.error(f"Failed to queue job {job['job_id']}: {str(e)}")
                        queuing_stats["failed_to_queue"] += 1
                        context.errors.append(f"Queue error for {job['job_name']}: {str(e)}")
                        
                        # Move to failed_routing for tracking
                        if "failed_routing" not in context.routed_jobs:
                            context.routed_jobs["failed_routing"] = []
                        context.routed_jobs["failed_routing"].append(job)
        
        context.execution_stats.update({
            "queuing_stats": queuing_stats,
            "queuing_timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.info(f"JobQueue: Queued {queuing_stats['total_queued']} jobs, {queuing_stats['failed_to_queue']} failed")
        logger.info(f"Queue distribution: {queuing_stats['queue_distribution']}")
        
        return context
    
    def _create_job_run(self, repo_factory: RepositoryFactory, job: Dict, context: PipelineContext):
        """Create job run record in database"""
        
        job_run_data = JobRunCreate(
            job_id=UUID(job["job_id"]),
            triggered_by=context.trigger_type.value,
            execution_host=context.trigger_metadata.get("execution_host", "job-discovery-pipeline")
        )
        
        return repo_factory.job_run.create(job_run_data)
    
    def _queue_to_celery(self, job: Dict, job_run):
        """Queue job to Celery with explicit queue and routing configuration"""
        
        routing_metadata = job.get("routing_metadata", {})
        celery_queue = routing_metadata.get("celery_queue", "geospatial")
        routing_key = routing_metadata.get("routing_key", f"geospatial.process")
        
        # Prepare task payload
        task_payload = {
            "job_id": job["job_id"],
            "run_id": str(job_run.id),
            "override_payload": None
        }
        
        logger.info(f"Sending task to queue: {celery_queue}, routing_key: {routing_key}")
        
        # FIXED: Send task with explicit queue and routing
        try:
            # Method 1: Use send_task with explicit routing
            task_result = celery_app.send_task(
                "tasks.job_processor.process_geospatial_job",
                args=[task_payload],
                queue=celery_queue,
                # routing_key=routing_key,
                exchange=celery_queue,  # Use queue name as exchange
                retry=True
            )
            
            logger.info(f"Successfully queued task {task_result.id} to {celery_queue}")
            return task_result
            
        except Exception as e:
            logger.error(f"Failed to send task with routing: {e}")
            
            # Fallback: Use apply_async with explicit routing
            try:
                from tasks.job_processor import process_geospatial_job
                task_result = process_geospatial_job.apply_async(
                    args=[task_payload],
                    queue=celery_queue,
                    routing_key=routing_key,
                    retry=True
                )
                
                logger.info(f"Successfully queued task {task_result.id} via apply_async to {celery_queue}")
                return task_result
                
            except Exception as e2:
                logger.error(f"Fallback routing also failed: {e2}")
                
                # Final fallback: Default queue
                logger.warning(f"Using default queue for task due to routing failures")
                return celery_app.send_task(
                    "tasks.job_processor.process_geospatial_job",
                    args=[task_payload]
                )