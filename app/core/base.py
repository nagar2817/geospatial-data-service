from abc import ABC, abstractmethod
from typing import List, Optional, Type
from uuid import uuid4
import logging
from datetime import datetime
from core.schema import PipelineContext, PipelineResult

logger = logging.getLogger(__name__)

class BaseNode(ABC):
    """Base class for all pipeline nodes"""
    
    def __init__(self, node_id: Optional[str] = None):
        self.node_id = node_id or str(uuid4())
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
    @abstractmethod
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process the context and return updated context"""
        pass
    
    def get_next_nodes(self, context: PipelineContext) -> List[Type["BaseNode"]]:
        """Determine next nodes to execute (override for router nodes)"""
        return []
    
    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute node with timing and error handling"""
        self.start_time = datetime.utcnow()
        
        try:
            logger.info(f"Executing node: {self.__class__.__name__}")
            updated_context = await self.process(context)
            logger.info(f"Node {self.__class__.__name__} completed successfully")
            return updated_context
            
        except Exception as e:
            logger.error(f"Node {self.__class__.__name__} failed: {str(e)}")
            context.errors.append(f"{self.__class__.__name__}: {str(e)}")
            raise
            
        finally:
            self.end_time = datetime.utcnow()

class RouterNode(BaseNode):
    """Base class for router nodes that determine execution paths"""
    
    @abstractmethod
    def route(self, context: PipelineContext) -> List[Type[BaseNode]]:
        """Determine which nodes to execute next based on context"""
        pass
    
    def get_next_nodes(self, context: PipelineContext) -> List[Type[BaseNode]]:
        return self.route(context)