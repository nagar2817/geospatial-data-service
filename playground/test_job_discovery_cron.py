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
Test CRON-triggered Job Discovery Pipeline
"""

async def test_cron_discovery():
    print("🕐 Testing CRON-triggered Job Discovery...")
    
    pipeline = PipelineRegistry.get_pipeline(TriggerType.CRON, "job_discovery")
    
    result = await pipeline.run(
        trigger_type=TriggerType.CRON,
        trigger_metadata={
            "execution_host": "test-cron-scheduler",
            "cron_expression": "0 */1 * * *"
        }
    )
    
    print(f"✅ Success: {result.success}")
    print(f"📝 Message: {result.message}")
    print(f"🔍 Jobs Processed: {result.jobs_processed}")
    print(f"📤 Jobs Queued: {result.jobs_queued}")
    print(f"⏱️  Execution Time: {result.execution_time_ms:.2f}ms")
    
    if result.errors:
        print("❌ Errors:")
        for error in result.errors:
            print(f"  - {error}")

if __name__ == "__main__":
    asyncio.run(test_cron_discovery())