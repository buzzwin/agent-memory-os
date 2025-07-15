"""
LangChain Memory Chain Integration

Provides a LangChain chain that automatically stores and retrieves memories
during chain execution.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain.chains.base import Chain
from langchain_core.language_models import BaseLanguageModel
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain_core.runnables import RunnableConfig

from ...memory import MemoryManager
from ...models import MemoryType


class MemoryChain(Chain):
    """
    A LangChain chain that integrates with Agent Memory OS for persistent memory.
    
    This chain automatically stores inputs, outputs, and intermediate steps as memories,
    and can retrieve relevant past memories to enhance the current execution.
    """
    
    memory_manager: MemoryManager
    llm: BaseLanguageModel
    agent_id: str
    session_id: Optional[str] = None
    store_inputs: bool = True
    store_outputs: bool = True
    store_intermediate: bool = False
    retrieve_memories: bool = True
    memory_limit: int = 5
    
    @property
    def input_keys(self) -> List[str]:
        """Input keys for the chain."""
        return ["input"]
    
    @property
    def output_keys(self) -> List[str]:
        """Output keys for the chain."""
        return ["output", "memories_used"]
    
    @property
    def _chain_type(self) -> str:
        """Type of chain."""
        return "memory_chain"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.session_id:
            self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def invoke(
        self,
        inputs: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        """Execute the chain with memory integration."""
        
        user_input = inputs["input"]
        memories_used = []
        
        # Retrieve relevant memories if enabled
        if self.retrieve_memories:
            relevant_memories = self.memory_manager.search_memory(
                query=user_input,
                limit=self.memory_limit
            )
            memories_used = [m.content for m in relevant_memories]
        
        # Build enhanced input with memory context
        enhanced_input = self._build_enhanced_input(user_input, memories_used)
        
        # Store input as episodic memory if enabled
        if self.store_inputs:
            self.memory_manager.add_memory(
                content=f"User input: {user_input}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "input_type": "user_query",
                    "memories_retrieved": len(memories_used)
                }
            )
        
        # Execute the LLM with enhanced input
        try:
            response = self.llm.invoke(enhanced_input)
            output = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            output = f"Error: {str(e)}"
        
        # Store output as episodic memory if enabled
        if self.store_outputs:
            self.memory_manager.add_memory(
                content=f"Generated response: {output}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "input_type": "response",
                    "original_input": user_input,
                    "memories_used": memories_used
                }
            )
        
        return {
            "output": output,
            "memories_used": memories_used
        }
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return self.invoke(inputs)
    
    def _build_enhanced_input(self, user_input: str, memories: List[str]) -> str:
        """Build enhanced input with memory context."""
        if not memories:
            return user_input
        
        memory_context = "\n".join([
            f"Relevant past context: {memory}" for memory in memories
        ])
        
        return f"""Based on the following relevant past context, please respond to the user's query:

{memory_context}

User query: {user_input}

Please provide a helpful response that takes into account the past context when relevant."""
    
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