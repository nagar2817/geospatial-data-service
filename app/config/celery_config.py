import os
from functools import lru_cache
from celery import Celery
from config.settings import get_settings

settings = get_settings()

def get_rabbitmq_url():
    """Get RabbitMQ URL for Amazon MQ or local development."""
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = os.getenv("RABBITMQ_PORT", "5672")
    vhost = os.getenv("RABBITMQ_VHOST", "/")
    return f"pyamqp://{user}:{password}@{host}:{port}/{vhost}"

def get_redis_url():
    """Get Redis URL for caching and result backend."""
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", 6379)
    redis_db = os.getenv("REDIS_DB", "0")
    
    return f"redis://{redis_host}:{redis_port}/{redis_db}"

@lru_cache
def get_celery_config():
    """Get Celery configuration for geospatial processing."""
    broker_url = get_rabbitmq_url()
    result_backend = get_redis_url()
    
    return {
        "broker_url": broker_url,
        "result_backend": result_backend,
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "timezone": "UTC",
        "enable_utc": True,
        "broker_connection_retry_on_startup": True,
        "broker_connection_retry": True,
        "broker_connection_max_retries": 10,
        
        "task_routes": {
            "tasks.job_processor.process_geospatial_job": {"queue": "geospatial"},
            "tasks.monitoring.health_check": {"queue": "monitoring"},
            "tasks.pipeline_tasks.execute_job_discovery": {"queue": "scheduler"}
        },
        
        "task_queues": {
            "celery": { "exchange": "celery" },
            "geospatial": { "exchange": "geospatial" },
            "monitoring": { "exchange": "monitoring" },
            "scheduler": { "exchange": "scheduler" },
        },
        
        # Beat schedule
        "beat_schedule": {
            "health-check": {
                "task": "tasks.monitoring.health_check", 
                "schedule": 300.0,  # Every 5 minutes
            },
            "excute-job-discovery-pipeline": {
                "task": "tasks.pipeline_tasks.execute_job_discovery",
                "schedule": 3600.0,  # Every hour
                "args": ({"trigger_type": "CRON"},)  # Example trigger metadata
            }
        },
        
        # Worker configuration
        "worker_prefetch_multiplier": 1,
        "task_acks_late": True,
        "worker_max_tasks_per_child": 1000,
        
        # Retry settings
        "task_default_retry_delay": 60,
        "task_max_retries": 3,
    }

# Create Celery app
celery_app = Celery("geospatial_data_service")
celery_app.config_from_object(get_celery_config())


# Auto-discover tasks
celery_app.autodiscover_tasks([
    "tasks",
    "tasks.job_processor", 
    "tasks.pipeline_tasks",
    "tasks.monitoring"
], force=True)


# *** --- Extra config
# task_annotations = {
#     'tasks.monitoring.health_check': {'rate_limit': '10/m'}
# }