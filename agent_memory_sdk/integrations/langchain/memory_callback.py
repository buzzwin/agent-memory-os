"""
LangChain Memory Callback Handler

Provides a callback handler that automatically stores memories during
LangChain chain and agent execution.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage

from ...memory import MemoryManager
from ...models import MemoryType


class MemoryCallbackHandler(BaseCallbackHandler):
    """
    A LangChain callback handler that automatically stores memories during execution.
    
    This handler captures various events during chain/agent execution and stores
    them as episodic memories for future reference.
    """
    
    memory_manager: MemoryManager
    agent_id: str
    session_id: Optional[str] = None
    store_llm_inputs: bool = True
    store_llm_outputs: bool = True
    store_agent_actions: bool = True
    store_tool_calls: bool = True
    store_errors: bool = True
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        agent_id: str,
        session_id: Optional[str] = None,
        store_llm_inputs: bool = True,
        store_llm_outputs: bool = True,
        store_agent_actions: bool = True,
        store_tool_calls: bool = True,
        store_errors: bool = True
    ):
        super().__init__()
        self.memory_manager = memory_manager
        self.agent_id = agent_id
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.store_llm_inputs = store_llm_inputs
        self.store_llm_outputs = store_llm_outputs
        self.store_agent_actions = store_agent_actions
        self.store_tool_calls = store_tool_calls
        self.store_errors = store_errors
    
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Store LLM input prompts."""
        if self.store_llm_inputs and prompts:
            for i, prompt in enumerate(prompts):
                self.memory_manager.add_memory(
                    content=f"LLM input {i+1}: {prompt[:200]}{'...' if len(prompt) > 200 else ''}",
                    memory_type=MemoryType.EPISODIC,
                    agent_id=self.agent_id,
                    session_id=self.session_id,
                    metadata={
                        "event_type": "llm_input",
                        "prompt_index": i,
                        "prompt_length": len(prompt)
                    }
                )
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Store LLM outputs."""
        if self.store_llm_outputs and response.generations:
            for i, generation_list in enumerate(response.generations):
                for j, generation in enumerate(generation_list):
                    content = generation.text if hasattr(generation, 'text') else str(generation)
                    self.memory_manager.add_memory(
                        content=f"LLM output {i+1}.{j+1}: {content[:200]}{'...' if len(content) > 200 else ''}",
                        memory_type=MemoryType.EPISODIC,
                        agent_id=self.agent_id,
                        session_id=self.session_id,
                        metadata={
                            "event_type": "llm_output",
                            "generation_index": f"{i}.{j}",
                            "content_length": len(content)
                        }
                    )
    
    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        """Store LLM errors."""
        if self.store_errors:
            self.memory_manager.add_memory(
                content=f"LLM error: {str(error)}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "event_type": "llm_error",
                    "error_type": type(error).__name__
                }
            )
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Store agent actions."""
        if self.store_agent_actions:
            self.memory_manager.add_memory(
                content=f"Agent action: {action.tool} - {action.tool_input}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "event_type": "agent_action",
                    "tool": action.tool,
                    "log": action.log
                }
            )
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Store agent finish events."""
        self.memory_manager.add_memory(
            content=f"Agent finished: {finish.return_values.get('output', 'No output')}",
            memory_type=MemoryType.EPISODIC,
            agent_id=self.agent_id,
            session_id=self.session_id,
            metadata={
                "event_type": "agent_finish",
                "log": finish.log
            }
        )
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Store tool calls."""
        if self.store_tool_calls:
            self.memory_manager.add_memory(
                content=f"Tool called: {serialized.get('name', 'Unknown')} - {input_str[:100]}{'...' if len(input_str) > 100 else ''}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "event_type": "tool_start",
                    "tool_name": serialized.get('name', 'Unknown'),
                    "input_length": len(input_str)
                }
            )
    
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Store tool outputs."""
        if self.store_tool_calls:
            self.memory_manager.add_memory(
                content=f"Tool output: {output[:200]}{'...' if len(output) > 200 else ''}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "event_type": "tool_end",
                    "output_length": len(output)
                }
            )
    
    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        """Store tool errors."""
        if self.store_errors:
            self.memory_manager.add_memory(
                content=f"Tool error: {str(error)}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "event_type": "tool_error",
                    "error_type": type(error).__name__
                }
            )
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        """Store chain start events."""
        input_summary = ", ".join([f"{k}: {str(v)[:50]}" for k, v in inputs.items()])
        chain_name = serialized.get('name', 'Unknown') if isinstance(serialized, dict) and serialized else 'Unknown'
        self.memory_manager.add_memory(
            content=f"Chain started: {chain_name} - {input_summary}",
            memory_type=MemoryType.EPISODIC,
            agent_id=self.agent_id,
            session_id=self.session_id,
            metadata={
                "event_type": "chain_start",
                "chain_name": chain_name
            }
        )
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Store chain end events."""
        output_summary = ", ".join([f"{k}: {str(v)[:50]}" for k, v in outputs.items()])
        self.memory_manager.add_memory(
            content=f"Chain ended: {output_summary}",
            memory_type=MemoryType.EPISODIC,
            agent_id=self.agent_id,
            session_id=self.session_id,
            metadata={
                "event_type": "chain_end"
            }
        )
    
    def on_chain_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        """Store chain errors."""
        if self.store_errors:
            self.memory_manager.add_memory(
                content=f"Chain error: {str(error)}",
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "event_type": "chain_error",
                    "error_type": type(error).__name__
                }
            ) 