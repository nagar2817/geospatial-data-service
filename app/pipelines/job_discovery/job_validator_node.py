import logging
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List
from core.base import BaseNode
from core.schema import PipelineContext

logger = logging.getLogger(__name__)

class JobValidatorNode(BaseNode):
    """Validates job definitions and prerequisites before execution"""
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Validate eligible jobs"""
        
        validated_jobs = []
        validation_errors = []
        
        for job in context.eligible_jobs:
            try:
                if self._validate_job(job):
                    validated_jobs.append(job)
                else:
                    validation_errors.append(f"Job {job['job_name']} failed validation")
                    
            except Exception as e:
                validation_errors.append(f"Job {job['job_name']} validation error: {str(e)}")
                logger.error(f"Validation error for job {job['job_id']}: {str(e)}")
        
        context.validated_jobs = validated_jobs
        context.errors.extend(validation_errors)
        
        context.execution_stats.update({
            "jobs_validated": len(validated_jobs),
            "validation_errors": len(validation_errors),
            "validation_timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.info(f"JobValidator: {len(validated_jobs)} jobs passed validation, {len(validation_errors)} failed")
        
        return context
    
    def _validate_job(self, job: Dict[str, Any]) -> bool:
        """Validate individual job"""
        
        # Check if job is enabled
        if not job.get("enabled", False):
            logger.debug(f"Job {job['job_name']} is disabled")
            return False
        
        # Validate payload structure
        payload = job.get("payload", {})
        if not self._validate_payload(job["job_type"], payload):
            logger.warning(f"Job {job['job_name']} has invalid payload")
            return False
        
        # Check rate limiting
        if not self._check_rate_limit(job):
            logger.debug(f"Job {job['job_name']} rate limited")
            return False
        
        # Validate target function
        if not job.get("target_function"):
            logger.warning(f"Job {job['job_name']} missing target_function")
            return False
        
        # Check prerequisites
        if not self._check_prerequisites(job):
            logger.debug(f"Job {job['job_name']} prerequisites not met")
            return False
        
        return True
    
    def _validate_payload(self, job_type: str, payload: Dict[str, Any]) -> bool:
        """Validate job payload based on job type"""
        
        # Common required fields
        required_fields = ["coordinates", "satellite_type"]
        
        # Job type specific validations
        if job_type == "anomaly_detection":
            required_fields.extend(["metrics", "threshold_config"])
        elif job_type == "change_analysis":
            required_fields.extend(["date_range", "analysis_type"])
        elif job_type == "monitoring":
            required_fields.extend(["validation_rules"])
        
        # Check required fields
        for field in required_fields:
            if field not in payload:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate coordinates
        coordinates = payload.get("coordinates")
        if not isinstance(coordinates, list) or len(coordinates) == 0:
            logger.warning("Invalid coordinates format")
            return False
        
        # Validate satellite type
        valid_satellites = ["Sentinel-2", "Landsat-8", "MODIS"]
        if payload.get("satellite_type") not in valid_satellites:
            logger.warning(f"Invalid satellite type: {payload.get('satellite_type')}")
            return False
        
        return True
    
    def _check_rate_limit(self, job: Dict[str, Any]) -> bool:
        """Check if job execution respects rate limits"""
        
        last_run_str = job.get("last_run_at")
        if not last_run_str:
            return True  # No previous run, OK to execute
        
        try:
            last_run = datetime.fromisoformat(last_run_str.replace('Z', '+00:00')).astimezone(UTC)
            now = datetime.now(UTC)
            
            # Get minimum interval from job config or default
            retry_policy = job.get("retry_policy", {})
            min_interval_minutes = retry_policy.get("min_interval_minutes", 5)
            
            if (now - last_run) < timedelta(minutes=min_interval_minutes):
                return False
                
        except Exception as e:
            logger.error(f"Error parsing last_run_at: {e}")
            return True  # If we can't parse, allow execution
        
        return True
    
    def _check_prerequisites(self, job: Dict[str, Any]) -> bool:
        """Check job prerequisites (data availability, external services, etc.)"""
        
        # Check if required external services are available
        job_type = job.get("job_type")
        
        if job_type in ["anomaly_detection", "change_analysis"]:
            # Check Google Earth Engine availability (simplified)
            if not self._check_gee_availability():
                return False
        
        # Check database connectivity
        if not self._check_database_health():
            return False
        
        # Check storage availability for results
        if not self._check_storage_availability():
            return False
        
        return True
    
    def _check_gee_availability(self) -> bool:
        """Check Google Earth Engine service availability"""
        # Simplified check - in production, implement actual GEE health check
        return True
    
    def _check_database_health(self) -> bool:
        """Check database health"""
        # Simplified check - in production, implement actual DB health check
        return True
    
    def _check_storage_availability(self) -> bool:
        """Check storage service availability"""
        # Simplified check - in production, implement actual storage health check
        return True