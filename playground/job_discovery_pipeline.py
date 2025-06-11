import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

# Set database host to localhost since we're connecting to it outside of docker
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "postgres"
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASSWORD"] = "postgres"

from core.schema import TriggerType  # noqa: E402
from pipelines.registry import PipelineRegistry  # noqa: E402
from database import SessionLocal, RepositoryFactory  # noqa: E402
from database.repositories.job_repository import JobDefinitionCreate  # noqa: E402

"""
Job Discovery Pipeline Playground

This playground tests all four trigger types for the Job Discovery Pipeline:
1. CRON - Scheduled job discovery
2. API - API-triggered job discovery with filters
3. MANUAL - Manual job discovery for specific jobs
4. EVENT - Event-driven job discovery
"""

class JobDiscoveryPlayground:
    """Test harness for Job Discovery Pipeline"""
    
    def __init__(self):
        self.test_jobs_created = []
    
    async def setup_test_data(self):
        """Create test job definitions for playground testing"""
        
        print("🔧 Setting up test data...")
        
        test_jobs = [
            {
                "job_name": "NDVI Monitoring - Field A",
                "job_type": "metric_calc",
                "schedule_type": "cron",
                "schedule_cron": "0 6 * * *",  # Daily at 6 AM
                "enabled": True,
                "next_run_at": datetime.utcnow() - timedelta(hours=1),  # Eligible for execution
                "payload": {
                    "coordinates": [[-122.4194, 37.7749], [-122.4094, 37.7649]],
                    "satellite_type": "Sentinel-2",
                    "metrics": ["ndvi", "evi"],
                    "field_id": "field_a_001"
                },
                "target_function": "process_ndvi_monitoring"
            },
            {
                "job_name": "Anomaly Detection - Critical Farm",
                "job_type": "anomaly_detection",
                "schedule_type": "event_triggered",
                "enabled": True,
                "payload": {
                    "coordinates": [[-121.5194, 36.7749]],
                    "satellite_type": "Sentinel-2",
                    "metrics": ["ndvi", "ndwi"],
                    "threshold_config": {"ndvi_threshold": 0.3},
                    "severity": "high",
                    "farm_id": "farm_critical_001"
                },
                "target_function": "process_anomaly_detection"
            },
            {
                "job_name": "Change Analysis - Large Area",
                "job_type": "change_analysis",
                "schedule_type": "interval",
                "interval_days": 7,
                "enabled": True,
                "next_run_at": datetime.utcnow() - timedelta(days=1),  # Eligible
                "payload": {
                    "coordinates": [[-120.4194, 35.7749] for _ in range(150)],  # Large area
                    "satellite_type": "Landsat-8", 
                    "date_range": {"start": "2023-01-01", "end": "2024-12-31"},
                    "analysis_type": "vegetation_change",
                    "batch_processing": True
                },
                "target_function": "process_change_analysis"
            },
            {
                "job_name": "Health Monitoring",
                "job_type": "monitoring",
                "schedule_type": "cron",
                "schedule_cron": "*/15 * * * *",  # Every 15 minutes
                "enabled": True,
                "next_run_at": datetime.utcnow() - timedelta(minutes=30),  # Eligible
                "payload": {
                    "coordinates": [[-119.4194, 34.7749]],
                    "satellite_type": "MODIS",
                    "validation_rules": ["data_completeness", "cloud_coverage"],
                    "real_time": True
                },
                "target_function": "process_health_monitoring"
            },
            {
                "job_name": "Disabled Test Job",
                "job_type": "metric_calc",
                "schedule_type": "cron",
                "enabled": False,  # This should not be discovered
                "payload": {
                    "coordinates": [[-118.4194, 33.7749]],
                    "satellite_type": "Sentinel-2",
                    "metrics": ["ndvi"]
                },
                "target_function": "process_disabled_job"
            }
        ]
        
        with SessionLocal() as session:
            repo_factory = RepositoryFactory(session)
            
            for job_data in test_jobs:
                try:
                    job_create = JobDefinitionCreate(**job_data)
                    job = repo_factory.job_definition.create(job_create)
                    self.test_jobs_created.append(job.id)
                    print(f"  ✅ Created test job: {job.job_name} (ID: {job.id})")
                except Exception as e:
                    print(f"  ❌ Failed to create job {job_data['job_name']}: {str(e)}")
        
        print(f"🔧 Setup complete: {len(self.test_jobs_created)} test jobs created\n")
    
    async def test_cron_trigger(self):
        """Test CRON-triggered job discovery"""
        
        print("=" * 60)
        print("🕐 Testing CRON-Triggered Job Discovery")
        print("=" * 60)
        
        print("Scenario: Periodic scheduled job discovery (simulating cron execution)")
        print("Expected: Find jobs with next_run_at <= now and enabled = true\n")
        
        try:
            pipeline = PipelineRegistry.get_pipeline(TriggerType.CRON, "job_discovery")
            
            result = await pipeline.run(
                trigger_type=TriggerType.CRON,
                trigger_metadata={
                    "execution_host": "cron-scheduler",
                    "cron_expression": "0 */1 * * *"  # Hourly
                }
            )
            
            self._print_result("CRON", result)
            
        except Exception as e:
            print(f"❌ CRON test failed: {str(e)}")
        
        print()
    
    async def test_api_trigger(self):
        """Test API-triggered job discovery"""
        
        print("=" * 60)
        print("🌐 Testing API-Triggered Job Discovery")
        print("=" * 60)
        
        print("Scenario: API request with job type filter")
        print("Expected: Find jobs matching the specified job_type filter\n")
        
        try:
            pipeline = PipelineRegistry.get_pipeline(TriggerType.API, "job_discovery")
            
            result = await pipeline.run(
                trigger_type=TriggerType.API,
                trigger_metadata={
                    "execution_host": "api-server",
                    "filters": {
                        "job_type": "anomaly_detection",
                        "enabled": True
                    },
                    "user_id": "test_user_123"
                }
            )
            
            self._print_result("API", result)
            
        except Exception as e:
            print(f"❌ API test failed: {str(e)}")
        
        print()
    
    async def test_manual_trigger(self):
        """Test MANUAL-triggered job discovery"""
        
        print("=" * 60)
        print("👤 Testing MANUAL-Triggered Job Discovery")
        print("=" * 60)
        
        print("Scenario: Manual execution for specific job")
        print("Expected: Process only the specified job if it exists and is enabled\n")
        
        try:
            # Get a specific job ID for manual testing
            specific_job_id = None
            if self.test_jobs_created:
                specific_job_id = str(self.test_jobs_created[0])
            
            pipeline = PipelineRegistry.get_pipeline(TriggerType.MANUAL, "job_discovery")
            
            result = await pipeline.run(
                trigger_type=TriggerType.MANUAL,
                trigger_metadata={
                    "execution_host": "admin-workstation",
                    "job_id": specific_job_id,
                    "triggered_by_user": "admin@company.com",
                    "reason": "Manual testing execution"
                }
            )
            
            self._print_result("MANUAL", result)
            
        except Exception as e:
            print(f"❌ MANUAL test failed: {str(e)}")
        
        print()
    
    async def test_event_trigger(self):
        """Test EVENT-triggered job discovery"""
        
        print("=" * 60)
        print("🔔 Testing EVENT-Triggered Job Discovery")  
        print("=" * 60)
        
        print("Scenario: Event-driven discovery (anomaly detected)")
        print("Expected: Find jobs relevant to the anomaly detection event\n")
        
        try:
            pipeline = PipelineRegistry.get_pipeline(TriggerType.EVENT, "job_discovery")
            
            result = await pipeline.run(
                trigger_type=TriggerType.EVENT,
                trigger_metadata={
                    "execution_host": "event-processor",
                    "event_criteria": {
                        "event_type": "anomaly_detected",
                        "severity": "high",
                        "farm_id": "farm_critical_001",
                        "metric": "ndvi"
                    },
                    "event_id": str(uuid4()),
                    "event_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            self._print_result("EVENT", result)
            
        except Exception as e:
            print(f"❌ EVENT test failed: {str(e)}")
        
        print()
    
    async def test_multiple_scenarios(self):
        """Test additional scenarios and edge cases"""
        
        print("=" * 60)
        print("🧪 Testing Additional Scenarios")
        print("=" * 60)
        
        # Test 1: API with no filters (should get all enabled jobs)
        print("Scenario 1: API trigger with no filters")
        try:
            pipeline = PipelineRegistry.get_pipeline(TriggerType.API, "job_discovery")
            result = await pipeline.run(
                trigger_type=TriggerType.API,
                trigger_metadata={"execution_host": "api-test"}
            )
            print(f"  📊 No filters: {result.jobs_processed} jobs discovered")
        except Exception as e:
            print(f"  ❌ No filters test failed: {str(e)}")
        
        # Test 2: Event with different event type
        print("\nScenario 2: Event trigger for data quality alert")
        try:
            pipeline = PipelineRegistry.get_pipeline(TriggerType.EVENT, "job_discovery")
            result = await pipeline.run(
                trigger_type=TriggerType.EVENT,
                trigger_metadata={
                    "event_criteria": {
                        "event_type": "data_quality_alert",
                        "severity": "medium"
                    }
                }
            )
            print(f"  📊 Data quality event: {result.jobs_processed} jobs discovered")
        except Exception as e:
            print(f"  ❌ Data quality test failed: {str(e)}")
        
        # Test 3: Manual with non-existent job
        print("\nScenario 3: Manual trigger with non-existent job ID")
        try:
            pipeline = PipelineRegistry.get_pipeline(TriggerType.MANUAL, "job_discovery")
            result = await pipeline.run(
                trigger_type=TriggerType.MANUAL,
                trigger_metadata={
                    "job_id": str(uuid4()),  # Random non-existent ID
                    "triggered_by_user": "test@company.com"
                }
            )
            print(f"  📊 Non-existent job: {result.jobs_processed} jobs discovered")
        except Exception as e:
            print(f"  ❌ Non-existent job test failed: {str(e)}")
        
        print()
    
    def _print_result(self, trigger_type: str, result):
        """Print formatted pipeline execution result"""
        
        print(f"📊 {trigger_type} Trigger Results:")
        print(f"  ✅ Success: {result.success}")
        print(f"  📝 Message: {result.message}")
        print(f"  🔍 Jobs Processed: {result.jobs_processed}")
        print(f"  📤 Jobs Queued: {result.jobs_queued}")
        print(f"  ⏱️  Execution Time: {result.execution_time_ms:.2f}ms")
        
        if result.errors:
            print(f"  ❌ Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"    - {error}")
        
        if result.context and result.context.execution_stats:
            stats = result.context.execution_stats
            print(f"  📈 Detailed Stats:")
            
            # Print job processing stats
            if "job_processing" in stats:
                job_stats = stats["job_processing"]
                print(f"    🔍 Discovered: {job_stats.get('jobs_discovered', 0)}")
                print(f"    ✅ Validated: {job_stats.get('jobs_validated', 0)}")
                print(f"    🚀 Routed: {job_stats.get('jobs_routed', 0)}")
                print(f"    📊 Validation Rate: {job_stats.get('validation_success_rate', 0)}%")
                print(f"    🎯 Routing Rate: {job_stats.get('routing_success_rate', 0)}%")
            
            # Print queue distribution
            if "queue_distribution" in stats:
                queue_dist = stats["queue_distribution"]
                print(f"    📦 Queue Distribution:")
                for queue, count in queue_dist.items():
                    if count > 0:
                        print(f"      - {queue}: {count} jobs")
    
    async def cleanup_test_data(self):
        """Clean up test job definitions"""
        
        print("🧹 Cleaning up test data...")
        
        with SessionLocal() as session:
            repo_factory = RepositoryFactory(session)
            
            cleaned_count = 0
            for job_id in self.test_jobs_created:
                try:
                    if repo_factory.job_definition.delete(job_id):
                        cleaned_count += 1
                except Exception as e:
                    print(f"  ⚠️  Failed to delete job {job_id}: {str(e)}")
            
            print(f"🧹 Cleanup complete: {cleaned_count} test jobs removed\n")
    
    async def run_all_tests(self):
        """Run all pipeline tests"""
        
        print("🚀 Starting Job Discovery Pipeline Playground")
        print("=" * 80)
        
        try:
            # Setup test data
            await self.setup_test_data()
            
            # Run all trigger type tests
            await self.test_cron_trigger()
            await self.test_api_trigger() 
            await self.test_manual_trigger()
            await self.test_event_trigger()
            await self.test_multiple_scenarios()
            
            print("=" * 80)
            print("🎉 All Job Discovery Pipeline tests completed!")
            print("=" * 80)
            
        finally:
            # Always cleanup
            await self.cleanup_test_data()

# Run the playground tests
async def main():
    playground = JobDiscoveryPlayground()
    await playground.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())