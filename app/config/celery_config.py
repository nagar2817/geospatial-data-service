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
        "broker_connection_retry": True,
        "broker_connection_max_retries": 10,
        
        # FIXED: Explicit task routing configuration
        "task_routes": {
            # Main geospatial processing tasks
            "tasks.job_processor.process_geospatial_job": {
                "queue": "geospatial",
                "routing_key": "geospatial.process"
            },
            # Periodic job discovery
            "tasks.periodic_tasks.discover_jobs": {
                "queue": "scheduler", 
                "routing_key": "scheduler.discover"
            },
            "tasks.periodic_tasks.discover_jobs_pipeline": {
                "queue": "scheduler",
                "routing_key": "scheduler.pipeline"
            },
            # Health and monitoring tasks
            "tasks.simple_task.health_check": {
                "queue": "monitoring",
                "routing_key": "monitoring.health"
            },
            # Pipeline execution tasks
            "tasks.pipeline_tasks.execute_job_discovery": {
                "queue": "scheduler",
                "routing_key": "scheduler.pipeline"
            },
        },
        
        # FIXED: Default queue configuration
        "task_default_queue": "celery",
        "task_default_exchange": "celery",
        "task_default_exchange_type": "direct",
        "task_default_routing_key": "celery",
        
        # FIXED: Queue definitions to ensure queues exist
        "task_queues": {
            "celery": {
                "exchange": "celery",
                "routing_key": "celery",
            },
            "geospatial": {
                "exchange": "geospatial", 
                "routing_key": "geospatial.*",
            },
            "monitoring": {
                "exchange": "monitoring",
                "routing_key": "monitoring.*",
            },
            "scheduler": {
                "exchange": "scheduler",
                "routing_key": "scheduler.*", 
            },
        },
        
        # Beat schedule
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
        
        # Worker configuration
        "worker_prefetch_multiplier": 1,
        "task_acks_late": True,
        "worker_max_tasks_per_child": 1000,
        
        # FIXED: Task execution settings
        "task_always_eager": False,  # Ensure tasks go to broker
        "task_eager_propagates": False,
        "task_ignore_result": False,
        
        # Retry settings
        "task_default_retry_delay": 60,
        "task_max_retries": 3,
    }

# Create Celery app
celery_app = Celery("geospatial_data_service")
celery_app.config_from_object(get_celery_config())

# FIXED: Configure broker transport options for Redis
if "redis://" in get_rabbitmq_url():
    celery_app.conf.broker_transport_options = {
        "fanout_prefix": True,
        "fanout_patterns": True,
        "visibility_timeout": 3600,
        "retry_policy": {
            "timeout": 5.0
        }
    }

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "tasks",
    "tasks.job_processor", 
    "tasks.periodic_tasks",
    "tasks.simple_task",
    "tasks.pipeline_tasks"
], force=True)