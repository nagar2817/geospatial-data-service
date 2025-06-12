import logging
from datetime import datetime, UTC
from config.celery_config import celery_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.monitoring.health_check")
def health_check():
    """Simple health check task for monitoring."""
    logger.info("Health check task executed")
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "geospatial-celery-worker"
    }