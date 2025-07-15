"""
Memory Graph for LangGraph Integration

Provides a complete memory-aware LangGraph workflow wrapper.
"""

from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from ...memory import MemoryManager
from ...models import MemoryType
from .memory_state import MemoryState, create_memory_state
from .memory_node import MemoryNode, create_memory_tool_node


class MemoryGraph:
    """
    A memory-aware LangGraph workflow wrapper.
    
    This class provides a complete integration of Agent Memory OS
    with LangGraph, allowing you to create workflows with persistent memory.
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        agent_id: str,
        session_id: Optional[str] = None,
        checkpoint_dir: Optional[str] = None
    ):
        """
        Initialize memory graph.
        
        Args:
            memory_manager: Memory manager instance
            agent_id: Unique identifier for this agent/workflow
            session_id: Session identifier (auto-generated if not provided)
            checkpoint_dir: Directory for LangGraph checkpoints
        """
        self.memory_manager = memory_manager
        self.agent_id = agent_id
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.checkpoint_dir = checkpoint_dir
        
        # Create memory state class
        self.state_class = create_memory_state(
            memory_manager=memory_manager,
            agent_id=agent_id,
            session_id=self.session_id
        )
        
        # Create memory node
        self.memory_node = MemoryNode(
            memory_manager=memory_manager,
            agent_id=agent_id,
            session_id=self.session_id
        )
        
        # Create memory tool node
        self.memory_tool_node = create_memory_tool_node(
            memory_manager=memory_manager,
            agent_id=agent_id,
            session_id=self.session_id
        )
        
        # Initialize graph
        self.graph = None
        self.compiled_graph = None
    
    def create_graph(self, state_fields: Optional[Dict[str, Any]] = None) -> StateGraph:
        """
        Create a new StateGraph with memory capabilities.
        
        Args:
            state_fields: Additional state fields to include
            
        Returns:
            A StateGraph with memory capabilities
        """
        # Create state class with additional fields
        if state_fields:
            self.state_class = create_memory_state(
                memory_manager=self.memory_manager,
                agent_id=self.agent_id,
                session_id=self.session_id,
                **state_fields
            )
        
        # Create graph
        self.graph = StateGraph(self.state_class)
        
        # Add memory node
        self.graph.add_node("memory", self.memory_node)
        
        return self.graph
    
    def add_memory_tools(self, graph: StateGraph) -> StateGraph:
        """
        Add memory tools to an existing graph.
        
        Args:
            graph: Existing StateGraph
            
        Returns:
            Updated graph with memory tools
        """
        # Add memory tool node
        graph.add_node("memory_tools", self.memory_tool_node)
        
        return graph
    
    def compile_graph(self, checkpointer: Optional[MemorySaver] = None) -> Any:
        """
        Compile the graph for execution.
        
        Args:
            checkpointer: Optional checkpointer for state persistence
            
        Returns:
            Compiled graph
        """
        if not self.graph:
            raise ValueError("Graph not created. Call create_graph() first.")
        
        # Set up checkpointer
        if checkpointer is None and self.checkpoint_dir:
            checkpointer = MemorySaver()
        
        # Compile graph
        self.compiled_graph = self.graph.compile(checkpointer=checkpointer)
        
        return self.compiled_graph
    
    def run(
        self,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the memory-aware graph.
        
        Args:
            input_data: Input data for the graph
            config: Optional configuration
            
        Returns:
            Graph execution result
        """
        if not self.compiled_graph:
            self.compile_graph()
        
        # Add memory context to input
        enhanced_input = self._enhance_input_with_memory(input_data)
        
        # Run graph
        result = self.compiled_graph.invoke(enhanced_input, config=config)
        
        # Store execution as memory
        self._store_execution_memory(input_data, result)
        
        return result
    
    def _enhance_input_with_memory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance input with relevant memory context."""
        # Search for relevant memories
        query = input_data.get("input", "")
        if query:
            relevant_memories = self.memory_manager.search_memory(
                query=query,
                limit=3
            )
            
            if relevant_memories:
                memory_context = "\n".join([
                    f"Relevant past context: {m.content}" for m in relevant_memories
                ])
                
                # Add memory context to input
                input_data["memory_context"] = memory_context
                input_data["relevant_memories"] = [m.content for m in relevant_memories]
        
        return input_data
    
    def _store_execution_memory(self, input_data: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Store execution as memory."""
        # Store input
        input_text = input_data.get("input", "")
        if input_text:
            self.memory_manager.add_memory(
                content=f"Graph input: {input_text}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "event_type": "graph_input",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # Store result
        if "output" in result:
            self.memory_manager.add_memory(
                content=f"Graph output: {result['output']}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "event_type": "graph_output",
                    "original_input": input_text
                }
            )
    
    def add_memory_operation(
        self,
        operation_type: str,
        **operation_params
    ) -> Dict[str, Any]:
        """
        Add a memory operation to the graph state.
        
        Args:
            operation_type: Type of memory operation (store, search, timeline, learn_fact, stats)
            **operation_params: Operation-specific parameters
            
        Returns:
            Memory operation configuration
        """
        operation = {
            "type": operation_type,
            **operation_params
        }
        
        return {"memory_operation": operation}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this graph."""
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
    
    def search_memories(self, query: str, limit: int = 5) -> List[str]:
        """Search for relevant memories."""
        memories = self.memory_manager.search_memory(query=query, limit=limit)
        return [m.content for m in memories]
    
    def get_timeline(self, hours: int = 24) -> List[str]:
        """Get timeline of recent activities."""
        from datetime import timedelta
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        memories = self.memory_manager.get_timeline(
            agent_id=self.agent_id,
            start_time=start_time,
            end_time=end_time
        )
        
        return [m.content for m in memories]
    
    def learn_fact(self, fact: str, category: str = "general") -> None:
        """Learn and store a new fact."""
        self.memory_manager.add_memory(
            content=fact,
            memory_type=MemoryType.SEMANTIC,
            agent_id=self.agent_id,
            metadata={
                "category": category,
                "learned_at": datetime.now().isoformat()
            }
        ) 