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
    """Queues validated and routed jobs to Celery"""
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Queue jobs to appropriate Celery queues"""
        
        queuing_stats = {
            "total_queued": 0,
            "failed_to_queue": 0,
            "queuing_details": []
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
                        
                        # Queue to Celery with safer approach
                        task_result = self._queue_to_celery_safe(job, job_run)
                        
                        # Update job with queuing info
                        job["job_run_id"] = str(job_run.id)
                        job["task_id"] = task_result.id
                        job["queued_at"] = datetime.now(UTC).isoformat()
                        
                        queuing_stats["queuing_details"].append({
                            "job_id": job["job_id"],
                            "job_name": job["job_name"],
                            "job_run_id": str(job_run.id),
                            "task_id": task_result.id,
                            "queue": queue_name,
                            "celery_queue": job["routing_metadata"]["celery_queue"]
                        })
                        
                        queuing_stats["total_queued"] += 1
                        
                        # Update job definition last run time
                        repo_factory.job_definition.update_last_run(UUID(job["job_id"]))
                        
                        logger.info(f"Queued job {job['job_name']} with task_id: {task_result.id}")
                        
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
        
        return context
    
    def _create_job_run(self, repo_factory: RepositoryFactory, job: Dict, context: PipelineContext):
        """Create job run record in database"""
        
        job_run_data = JobRunCreate(
            job_id=UUID(job["job_id"]),
            triggered_by=context.trigger_type.value,
            execution_host=context.trigger_metadata.get("execution_host", "job-discovery-pipeline")
        )
        
        return repo_factory.job_run.create(job_run_data)
    
    def _queue_to_celery_safe(self, job: Dict, job_run):
        """Queue job to Celery with safe error handling"""
        
        routing_metadata = job.get("routing_metadata", {})
        celery_queue = routing_metadata.get("celery_queue", "geospatial")
        
        # Prepare task payload
        task_payload = {
            "job_id": job["job_id"],
            "run_id": str(job_run.id),
            "override_payload": None
        }
        
        # Send task with minimal parameters to avoid compatibility issues
        try:
            return celery_app.send_task(
                "tasks.job_processor.process_geospatial_job",
                args=[task_payload],
                queue=celery_queue
            )
        except Exception as e:
            logger.error(f"Failed to send task to queue {celery_queue}: {str(e)}")
            # Fallback: try without queue specification
            return celery_app.send_task(
                "tasks.job_processor.process_geospatial_job",
                args=[task_payload]
            )