"""
Memory Tool Node for LangGraph Integration

Provides a simple wrapper for memory tools in LangGraph workflows.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

from ...memory import MemoryManager
from ...models import MemoryType


class MemoryToolNode:
    """
    A simple wrapper for memory tools in LangGraph workflows.
    
    This class provides easy access to memory operations as tools
    that can be used in any LangGraph workflow.
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        agent_id: str,
        session_id: Optional[str] = None
    ):
        """
        Initialize memory tool node.
        
        Args:
            memory_manager: Memory manager instance
            agent_id: Unique identifier for this agent/workflow
            session_id: Session identifier (auto-generated if not provided)
        """
        self.memory_manager = memory_manager
        self.agent_id = agent_id
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self._tools = self._create_tools()
        self.tool_node = ToolNode(self._tools)
    
    def _create_tools(self):
        """Create and return the list of memory tool functions."""
        
        @tool
        def store_memory(content: str, memory_type: str = "episodic", metadata: str = "{}") -> str:
            """Store a memory entry."""
            try:
                import json
                metadata_dict = json.loads(metadata) if metadata else {}
                
                self.memory_manager.add_memory(
                    content=content,
                    memory_type=MemoryType(memory_type),
                    agent_id=self.agent_id,
                    session_id=self.session_id,
                    metadata=metadata_dict
                )
                return f"Successfully stored memory: {content[:50]}{'...' if len(content) > 50 else ''}"
            except Exception as e:
                return f"Error storing memory: {str(e)}"
        
        @tool
        def search_memories(query: str, limit: int = 5) -> str:
            """Search for relevant memories."""
            try:
                memories = self.memory_manager.search_memory(query=query, limit=limit)
                if not memories:
                    return f"No memories found for query: '{query}'"
                
                results = [f"- {m.content}" for m in memories]
                return f"Found {len(memories)} memories for '{query}':\n" + "\n".join(results)
            except Exception as e:
                return f"Error searching memories: {str(e)}"
        
        @tool
        def get_timeline(hours: int = 24) -> str:
            """Get timeline of recent activities."""
            try:
                from datetime import timedelta
                
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=hours)
                
                memories = self.memory_manager.get_timeline(
                    agent_id=self.agent_id,
                    start_time=start_time,
                    end_time=end_time
                )
                
                if not memories:
                    return f"No activities found in the last {hours} hours"
                
                timeline = [f"- {m.content}" for m in memories]
                return f"Timeline for the last {hours} hours:\n" + "\n".join(timeline)
            except Exception as e:
                return f"Error getting timeline: {str(e)}"
        
        @tool
        def learn_fact(fact: str, category: str = "general") -> str:
            """Learn and store a new fact."""
            try:
                self.memory_manager.add_memory(
                    content=fact,
                    memory_type=MemoryType.SEMANTIC,
                    agent_id=self.agent_id,
                    metadata={
                        "category": category,
                        "learned_at": datetime.now().isoformat()
                    }
                )
                return f"Successfully learned fact: '{fact}' (category: {category})"
            except Exception as e:
                return f"Error learning fact: {str(e)}"
        
        @tool
        def get_memory_stats() -> str:
            """Get memory statistics."""
            try:
                episodic_memories = self.memory_manager.get_episodic_memories(
                    agent_id=self.agent_id,
                    limit=1000
                )
                
                semantic_memories = self.memory_manager.search_memory(
                    query="",
                    memory_type=MemoryType.SEMANTIC,
                    limit=1000
                )
                
                stats = {
                    "episodic_memories": len(episodic_memories),
                    "semantic_memories": len(semantic_memories),
                    "total_memories": len(episodic_memories) + len(semantic_memories)
                }
                
                return f"Memory Statistics:\n" + "\n".join([
                    f"- {key.replace('_', ' ').title()}: {value}" 
                    for key, value in stats.items()
                ])
            except Exception as e:
                return f"Error getting memory stats: {str(e)}"
        
        return [store_memory, search_memories, get_timeline, learn_fact, get_memory_stats]
    
    def get_tools(self) -> List[Any]:
        """Get the list of memory tools."""
        return self._tools
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool node."""
        return self.tool_node(state)


def create_memory_tools(
    memory_manager: MemoryManager,
    agent_id: str,
    session_id: Optional[str] = None
) -> List[Any]:
    """
    Create memory tools for use in LangGraph workflows.
    
    Args:
        memory_manager: Memory manager instance
        agent_id: Unique identifier for this agent/workflow
        session_id: Session identifier
        
    Returns:
        List of memory tools
    """
    tool_node = MemoryToolNode(
        memory_manager=memory_manager,
        agent_id=agent_id,
        session_id=session_id
    )
    
    return tool_node.get_tools() 