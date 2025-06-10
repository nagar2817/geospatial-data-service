from core.pipeline import Pipeline
from core.schema import PipelineSchema, NodeConfig
from pipelines.job_discovery.job_scanner_node import JobScannerNode
from pipelines.job_discovery.job_validator_node import JobValidatorNode
from pipelines.job_discovery.job_router_node import JobRouterNode
from pipelines.job_discovery.job_queue_node import JobQueueNode
from pipelines.job_discovery.job_stats_node import JobStatsNode

class JobDiscoveryPipeline(Pipeline):
    """Pipeline for discovering, validating, routing and queuing geospatial processing jobs"""
    
    pipeline_schema = PipelineSchema(
        description="Discovers eligible jobs, validates them, routes to appropriate queues, and tracks execution",
        start=JobScannerNode,
        nodes=[
            NodeConfig(
                node=JobScannerNode,
                connections=[JobValidatorNode],
                description="Scan for eligible jobs based on trigger type and criteria"
            ),
            NodeConfig(
                node=JobValidatorNode,
                connections=[JobRouterNode],
                description="Validate job definitions, payloads and prerequisites"
            ),
            NodeConfig(
                node=JobRouterNode,
                connections=[JobQueueNode, JobStatsNode],
                is_router=True,
                description="Route jobs to appropriate processing queues based on type and priority"
            ),
            NodeConfig(
                node=JobQueueNode,
                connections=[],
                description="Queue validated jobs to Celery for processing"
            ),
            NodeConfig(
                node=JobStatsNode,
                connections=[],
                description="Collect and log pipeline execution statistics"
            )
        ]
    )