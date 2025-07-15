"""
Memory State for LangGraph Integration

Provides memory state management for LangGraph workflows.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from ...memory import MemoryManager
from ...models import MemoryType


class MemoryState:
    """
    State class that includes memory capabilities for LangGraph workflows.
    
    This state can be used as a base or mixed into other state classes
    to add memory functionality to any LangGraph workflow.
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        agent_id: str,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize memory state.
        
        Args:
            memory_manager: Memory manager instance
            agent_id: Unique identifier for this agent/workflow
            session_id: Session identifier (auto-generated if not provided)
            **kwargs: Additional state fields
        """
        self.memory_manager = memory_manager
        self.agent_id = agent_id
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize other state fields
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def add_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a memory to the state's memory manager."""
        self.memory_manager.add_memory(
            content=content,
            memory_type=memory_type,
            agent_id=self.agent_id,
            session_id=self.session_id,
            metadata=metadata or {}
        )
    
    def search_memories(
        self,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """Search for relevant memories."""
        memories = self.memory_manager.search_memory(query=query, limit=limit)
        return [m.content for m in memories]
    
    def get_timeline(
        self,
        hours: int = 24
    ) -> List[str]:
        """Get recent timeline of activities."""
        from datetime import timedelta
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        memories = self.memory_manager.get_timeline(
            agent_id=self.agent_id,
            start_time=start_time,
            end_time=end_time
        )
        
        return [m.content for m in memories]
    
    def learn_fact(
        self,
        fact: str,
        category: str = "general"
    ) -> None:
        """Learn and store a new fact as semantic memory."""
        self.add_memory(
            content=fact,
            memory_type=MemoryType.SEMANTIC,
            metadata={
                "category": category,
                "learned_at": datetime.now().isoformat()
            }
        )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this state."""
        episodic_memories = self.memory_manager.get_episodic_memories(
            agent_id=self.agent_id,
            limit=1000
        )
        
        semantic_memories = self.memory_manager.search_memory(
            query="",
            memory_type=MemoryType.SEMANTIC,
            limit=1000
        )
        
        return {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "episodic_memories": len(episodic_memories),
            "semantic_memories": len(semantic_memories),
            "total_memories": len(episodic_memories) + len(semantic_memories)
        }


def create_memory_state(
    memory_manager: MemoryManager,
    agent_id: str,
    session_id: Optional[str] = None,
    **state_fields
) -> type:
    """
    Create a custom state class with memory capabilities.
    
    Args:
        memory_manager: Memory manager instance
        agent_id: Unique identifier for this agent/workflow
        session_id: Session identifier
        **state_fields: Additional state fields to include
        
    Returns:
        A state class that can be used with LangGraph
    """
    class CustomMemoryState(MemoryState):
        def __init__(self, **kwargs):
            super().__init__(
                memory_manager=memory_manager,
                agent_id=agent_id,
                session_id=session_id,
                **state_fields,
                **kwargs
            )
    
    return CustomMemoryState 