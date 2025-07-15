"""
LangChain Memory-Aware Agent

Provides a wrapper around LangChain agents that automatically integrates
with Agent Memory OS for persistent memory capabilities.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from langchain.agents import AgentExecutor
from langchain.agents.agent import Agent
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.tools import BaseTool
from langchain.callbacks.manager import CallbackManager

from ...memory import MemoryManager
from ...models import MemoryType
from .memory_tool import MemoryTool
from .memory_callback import MemoryCallbackHandler


class MemoryAwareAgent:
    """
    A wrapper around LangChain agents that provides memory capabilities.
    
    This class enhances any LangChain agent with persistent memory,
    automatic memory storage, and memory-aware responses.
    """
    
    def __init__(
        self,
        agent: Agent,
        memory_manager: MemoryManager,
        agent_id: str,
        session_id: Optional[str] = None,
        include_memory_tool: bool = True,
        enable_memory_callbacks: bool = True,
        **kwargs
    ):
        """
        Initialize a memory-aware agent.
        
        Args:
            agent: The LangChain agent to wrap
            memory_manager: Memory manager instance
            agent_id: Unique identifier for this agent
            session_id: Session identifier (auto-generated if not provided)
            include_memory_tool: Whether to add memory tool to agent's tools
            enable_memory_callbacks: Whether to enable automatic memory storage
            **kwargs: Additional arguments for AgentExecutor
        """
        self.agent = agent
        self.memory_manager = memory_manager
        self.agent_id = agent_id
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.include_memory_tool = include_memory_tool
        self.enable_memory_callbacks = enable_memory_callbacks
        
        # Add memory tool if requested
        if self.include_memory_tool:
            self._add_memory_tool()
        
        # Create callback manager with memory handler if enabled
        callbacks = []
        if self.enable_memory_callbacks:
            memory_callback = MemoryCallbackHandler(
                memory_manager=self.memory_manager,
                agent_id=self.agent_id,
                session_id=self.session_id
            )
            callbacks.append(memory_callback)
        
        # Get tools from agent or use empty list
        tools = []
        if hasattr(self.agent, 'tools') and self.agent.tools:
            tools = self.agent.tools
        elif hasattr(self.agent, 'get_tools'):
            try:
                tools = self.agent.get_tools()
            except:
                tools = []
        
        # Create agent executor with modern pattern
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            callbacks=callbacks,
            **kwargs
        )
    
    def _add_memory_tool(self):
        """Add memory tool to the agent's tool list."""
        memory_tool = MemoryTool(
            memory_manager=self.memory_manager,
            agent_id=self.agent_id,
            session_id=self.session_id
        )
        
        if hasattr(self.agent, 'tools'):
            if self.agent.tools is None:
                self.agent.tools = []
            self.agent.tools.append(memory_tool)
        else:
            # For agents that don't have a tools attribute, we'll need to handle this differently
            print("Warning: Agent doesn't have a tools attribute. Memory tool may not be available.")
    
    def run(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Run the agent with memory integration.
        
        Args:
            input_text: The input text for the agent
            **kwargs: Additional arguments for the executor
            
        Returns:
            Dictionary containing the result and any memory information
        """
        # Store the input as episodic memory
        self.memory_manager.add_memory(
            content=f"User input: {input_text}",
            memory_type=MemoryType.EPISODIC,
            agent_id=self.agent_id,
            session_id=self.session_id,
            metadata={
                "input_type": "user_query",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Retrieve relevant memories
        relevant_memories = self.memory_manager.search_memory(
            query=input_text,
            limit=3
        )
        
        # Build memory context
        memory_context = self._build_memory_context(relevant_memories)
        
        # Run the agent using invoke (new API)
        try:
            # Handle different agent types
            if hasattr(self.executor, 'invoke'):
                # Modern executor
                result = self.executor.invoke({"input": input_text, "memory_context": memory_context}, **kwargs)
                output = result["text"] if isinstance(result, dict) and "text" in result else str(result)
            else:
                # Fallback for older executors
                result = self.executor.run({"input": input_text, "memory_context": memory_context}, **kwargs)
                output = result if isinstance(result, str) else str(result)
            
            # Store the result as episodic memory
            self.memory_manager.add_memory(
                content=f"Agent response: {output}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "input_type": "agent_response",
                    "original_input": input_text,
                    "memories_used": [m.content for m in relevant_memories]
                }
            )
            
            return {
                "output": output,
                "memories_used": [m.content for m in relevant_memories],
                "session_id": self.session_id
            }
            
        except Exception as e:
            # Store error as memory
            self.memory_manager.add_memory(
                content=f"Agent error: {str(e)}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "input_type": "error",
                    "original_input": input_text,
                    "error_type": type(e).__name__
                }
            )
            raise
    
    def _build_memory_context(self, memories: List) -> str:
        """Build memory context string from relevant memories."""
        if not memories:
            return "No relevant past context available."
        
        context_parts = []
        for memory in memories:
            context_parts.append(f"- {memory.content}")
        
        return "\n".join(context_parts)
    
    def learn_fact(self, fact: str, category: str = "general") -> None:
        """Learn and store a new fact as semantic memory."""
        self.memory_manager.add_memory(
            content=fact,
            memory_type=MemoryType.SEMANTIC,
            agent_id=self.agent_id,
            metadata={
                "category": category,
                "learned_at": datetime.now().isoformat()
            }
        )
    
    def get_timeline(self, hours: int = 24) -> List[str]:
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
    
    def search_memories(self, query: str, limit: int = 10) -> List[str]:
        """Search for relevant memories."""
        memories = self.memory_manager.search_memory(query=query, limit=limit)
        return [m.content for m in memories]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this agent."""
        # Get counts by memory type
        episodic_memories = self.memory_manager.get_episodic_memories(
            agent_id=self.agent_id,
            limit=1000  # Large limit to get all
        )
        # Get all semantic memories (no agent_id filter)
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