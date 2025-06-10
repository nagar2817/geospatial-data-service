import os
from functools import lru_cache
from celery import Celery
from config.settings import get_settings

settings = get_settings()

def get_rabbitmq_url():
    """Get RabbitMQ URL for Amazon MQ or local development."""
    if os.getenv("ENVIRONMENT") == "production":
        # Amazon MQ RabbitMQ
        user = os.getenv("RABBITMQ_USER", "admin")
        password = os.getenv("RABBITMQ_PASSWORD")
        host = os.getenv("RABBITMQ_HOST", "localhost")
        port = os.getenv("RABBITMQ_PORT", "5672")
        vhost = os.getenv("RABBITMQ_VHOST", "/")
        return f"pyamqp://{user}:{password}@{host}:{port}/{vhost}"
    else:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", 6379)
        redis_db = os.getenv("REDIS_DB", "0")
        
        return f"redis://{redis_host}:{redis_port}/{redis_db}"

@lru_cache
def get_celery_config():
    """Get Celery configuration for geospatial processing."""
    broker_url = get_rabbitmq_url()
    
    return {
        "broker_url": broker_url,
        "result_backend": broker_url,
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "timezone": "UTC",
        "enable_utc": True,
        "broker_connection_retry_on_startup": True,
        "task_routes": {
            "tasks.job_processor.process_geospatial_job": {"queue": "geospatial"},
            "tasks.periodic_tasks.discover_jobs": {"queue": "scheduler"},
            "tasks.simple_task.health_check": {"queue": "monitoring"},
        },
        "beat_schedule": {
            "job-discovery": {
                "task": "tasks.periodic_tasks.discover_jobs",
                "schedule": 3600.0,  # Every hour
            },
            "health-check": {
                "task": "tasks.simple_task.health_check", 
                "schedule": 300.0,  # Every 5 minutes
            },
        },
        "worker_prefetch_multiplier": 1,
        "task_acks_late": True,
        "worker_max_tasks_per_child": 1000,
    }

celery_app = Celery("geospatial_data_service")
celery_app.config_from_object(get_celery_config())

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "tasks",
    "tasks.job_processor", 
    "tasks.periodic_tasks",
    "tasks.simple_task"
], force=True)