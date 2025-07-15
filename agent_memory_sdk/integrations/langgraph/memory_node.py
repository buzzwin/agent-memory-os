"""
Memory Node for LangGraph Integration

Provides memory operations as a LangGraph node that can be added to workflows.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

from ...memory import MemoryManager
from ...models import MemoryType


class MemoryNode:
    """
    A LangGraph node that provides memory operations.
    
    This node can be added to any LangGraph workflow to provide
    memory storage, retrieval, and search capabilities.
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        agent_id: str,
        session_id: Optional[str] = None
    ):
        """
        Initialize memory node.
        
        Args:
            memory_manager: Memory manager instance
            agent_id: Unique identifier for this agent/workflow
            session_id: Session identifier (auto-generated if not provided)
        """
        self.memory_manager = memory_manager
        self.agent_id = agent_id
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute memory operations based on state.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with memory operations results
        """
        # Extract memory operation from state
        memory_op = state.get("memory_operation", {})
        op_type = memory_op.get("type")
        
        if op_type == "store":
            return self._store_memory(state, memory_op)
        elif op_type == "search":
            return self._search_memories(state, memory_op)
        elif op_type == "timeline":
            return self._get_timeline(state, memory_op)
        elif op_type == "learn_fact":
            return self._learn_fact(state, memory_op)
        elif op_type == "stats":
            return self._get_stats(state)
        else:
            # No memory operation, return state unchanged
            return state
    
    def _store_memory(self, state: Dict[str, Any], memory_op: Dict[str, Any]) -> Dict[str, Any]:
        """Store a memory entry."""
        content = memory_op.get("content", "")
        memory_type = MemoryType(memory_op.get("memory_type", "episodic"))
        metadata = memory_op.get("metadata", {})
        
        # Add memory
        self.memory_manager.add_memory(
            content=content,
            memory_type=memory_type,
            agent_id=self.agent_id,
            session_id=self.session_id,
            metadata=metadata
        )
        
        # Update state with result
        state["memory_result"] = {
            "success": True,
            "message": f"Stored memory: {content[:50]}{'...' if len(content) > 50 else ''}"
        }
        
        return state
    
    def _search_memories(self, state: Dict[str, Any], memory_op: Dict[str, Any]) -> Dict[str, Any]:
        """Search for relevant memories."""
        query = memory_op.get("query", "")
        limit = memory_op.get("limit", 5)
        
        memories = self.memory_manager.search_memory(query=query, limit=limit)
        memory_contents = [m.content for m in memories]
        
        # Update state with search results
        state["memory_result"] = {
            "success": True,
            "query": query,
            "results": memory_contents,
            "count": len(memory_contents)
        }
        
        return state
    
    def _get_timeline(self, state: Dict[str, Any], memory_op: Dict[str, Any]) -> Dict[str, Any]:
        """Get timeline of recent activities."""
        hours = memory_op.get("hours", 24)
        
        from datetime import timedelta
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        memories = self.memory_manager.get_timeline(
            agent_id=self.agent_id,
            start_time=start_time,
            end_time=end_time
        )
        
        timeline = [m.content for m in memories]
        
        # Update state with timeline
        state["memory_result"] = {
            "success": True,
            "timeline": timeline,
            "hours": hours,
            "count": len(timeline)
        }
        
        return state
    
    def _learn_fact(self, state: Dict[str, Any], memory_op: Dict[str, Any]) -> Dict[str, Any]:
        """Learn and store a new fact."""
        fact = memory_op.get("fact", "")
        category = memory_op.get("category", "general")
        
        self.memory_manager.add_memory(
            content=fact,
            memory_type=MemoryType.SEMANTIC,
            agent_id=self.agent_id,
            metadata={
                "category": category,
                "learned_at": datetime.now().isoformat()
            }
        )
        
        # Update state with result
        state["memory_result"] = {
            "success": True,
            "message": f"Learned fact: {fact}",
            "category": category
        }
        
        return state
    
    def _get_stats(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory statistics."""
        stats = self.memory_manager.get_episodic_memories(
            agent_id=self.agent_id,
            limit=1000
        )
        
        semantic_memories = self.memory_manager.search_memory(
            query="",
            memory_type=MemoryType.SEMANTIC,
            limit=1000
        )
        
        # Update state with stats
        state["memory_result"] = {
            "success": True,
            "stats": {
                "episodic_memories": len(stats),
                "semantic_memories": len(semantic_memories),
                "total_memories": len(stats) + len(semantic_memories)
            }
        }
        
        return state


def create_memory_tool_node(
    memory_manager: MemoryManager,
    agent_id: str,
    session_id: Optional[str] = None
) -> ToolNode:
    """
    Create a memory tool node that can be used with LangGraph's ToolNode.
    
    Args:
        memory_manager: Memory manager instance
        agent_id: Unique identifier for this agent/workflow
        session_id: Session identifier
        
    Returns:
        A ToolNode that provides memory operations
    """
    
    @tool
    def store_memory(content: str, memory_type: str = "episodic", metadata: str = "{}") -> str:
        """Store a memory entry."""
        try:
            import json
            metadata_dict = json.loads(metadata) if metadata else {}
            
            memory_manager.add_memory(
                content=content,
                memory_type=MemoryType(memory_type),
                agent_id=agent_id,
                session_id=session_id,
                metadata=metadata_dict
            )
            return f"Successfully stored memory: {content[:50]}{'...' if len(content) > 50 else ''}"
        except Exception as e:
            return f"Error storing memory: {str(e)}"
    
    @tool
    def search_memories(query: str, limit: int = 5) -> str:
        """Search for relevant memories."""
        try:
            memories = memory_manager.search_memory(query=query, limit=limit)
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
            
            memories = memory_manager.get_timeline(
                agent_id=agent_id,
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
            memory_manager.add_memory(
                content=fact,
                memory_type=MemoryType.SEMANTIC,
                agent_id=agent_id,
                metadata={
                    "category": category,
                    "learned_at": datetime.now().isoformat()
                }
            )
            return f"Successfully learned fact: '{fact}' (category: {category})"
        except Exception as e:
            return f"Error learning fact: {str(e)}"
    
    # Create tool node with memory tools
    return ToolNode([store_memory, search_memories, get_timeline, learn_fact]) 