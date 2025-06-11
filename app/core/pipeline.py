import asyncio
import logging
from datetime import datetime, UTC
from typing import Dict, List, Type, Optional
from core.base import BaseNode, RouterNode
from core.schema import PipelineSchema, PipelineContext, PipelineResult, TriggerType

logger = logging.getLogger(__name__)

class Pipeline:
    """Base pipeline executor"""
    
    pipeline_schema: PipelineSchema = None
    
    def __init__(self):
        if not self.pipeline_schema:
            raise ValueError("Pipeline must define pipeline_schema")
        self._node_registry: Dict[Type[BaseNode], BaseNode] = {}
        
    async def run(self, trigger_type: TriggerType, trigger_metadata: Dict = None) -> PipelineResult:
        """Execute the pipeline"""
        start_time = datetime.now(UTC)
        
        # Initialize context
        context = PipelineContext(
            trigger_type=trigger_type,
            trigger_metadata=trigger_metadata or {}
        )
        
        try:
            # Execute pipeline starting from start node
            await self._execute_node(self.pipeline_schema.start, context)
            
            # Calculate execution time
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            
            return PipelineResult(
                success=len(context.errors) == 0,
                message="Pipeline completed successfully" if len(context.errors) == 0 else "Pipeline completed with errors",
                jobs_processed=len(context.validated_jobs),
                jobs_queued=sum(len(jobs) for jobs in context.routed_jobs.values()),
                errors=context.errors,
                execution_time_ms=execution_time,
                context=context
            )
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            
            return PipelineResult(
                success=False,
                message=f"Pipeline failed: {str(e)}",
                execution_time_ms=execution_time,
                errors=context.errors + [str(e)],
                context=context
            )
    
    async def _execute_node(self, node_class: Type[BaseNode], context: PipelineContext):
        """Execute a single node and its connections"""
        # Get or create node instance
        if node_class not in self._node_registry:
            self._node_registry[node_class] = node_class()
        
        node = self._node_registry[node_class]
        
        # Execute the node
        updated_context = await node.execute(context)
        
        # Get next nodes to execute
        next_nodes = node.get_next_nodes(updated_context)
        if not next_nodes:
            # Find connections from schema
            for node_config in self.pipeline_schema.nodes:
                if node_config.node == node_class:
                    next_nodes = node_config.connections
                    break
        
        # Execute next nodes
        for next_node_class in next_nodes:
            await self._execute_node(next_node_class, updated_context)