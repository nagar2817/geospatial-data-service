import os
import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

os.environ["DB_HOST"] = "localhost"

from core.schema import TriggerType
from pipelines.registry import PipelineRegistry

"""
Test API-triggered Job Discovery Pipeline
"""

async def test_api_discovery():
    print("🌐 Testing API-triggered Job Discovery...")
    
    pipeline = PipelineRegistry.get_pipeline(TriggerType.API, "job_discovery")
    
    # Test with filters
    result = await pipeline.run(
        trigger_type=TriggerType.API,
        trigger_metadata={
            "execution_host": "api-server",
            "filters": {
                "job_type": "anomaly_detection",
                "enabled": True
            },
            "user_id": "test_api_user"
        }
    )
    
    print(f"✅ Success: {result.success}")
    print(f"📝 Message: {result.message}")
    print(f"🔍 Jobs Processed: {result.jobs_processed}")
    print(f"📤 Jobs Queued: {result.jobs_queued}")
    print(f"⏱️  Execution Time: {result.execution_time_ms:.2f}ms")

if __name__ == "__main__":
    asyncio.run(test_api_discovery())