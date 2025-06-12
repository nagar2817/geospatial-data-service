"""
Task package for Celery tasks.
Import all task modules to register them with Celery.
"""

# Import all task modules to register them with Celery
from . import job_processor
from . import pipeline_tasks
from . import monitoring

# Export specific tasks that might be imported elsewhere
from .job_processor import process_geospatial_job
from .pipeline_tasks import execute_job_discovery_pipeline
from .monitoring import health_check