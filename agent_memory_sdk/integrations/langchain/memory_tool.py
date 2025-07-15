"""
LangChain Memory Tool Integration

Provides a LangChain tool that allows agents to interact with Agent Memory OS
for storing and retrieving memories.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_core.tools import BaseTool
from langchain_core.output_parsers import BaseOutputParser

from ...memory import MemoryManager
from ...models import MemoryType


class MemoryTool(BaseTool):
    """
    A LangChain tool that provides memory operations for agents.
    
    This tool allows agents to store facts, search memories, and retrieve timelines
    as part of their tool repertoire.
    """
    
    name: str = "memory_tool"
    description: str = """
    A tool for managing persistent memory. Use this tool to:
    - Store facts and knowledge (learn_fact)
    - Search for relevant past information (search_memories)
    - Get timeline of recent activities (get_timeline)
    - Store important information from conversations (store_memory)
    """
    
    memory_manager: MemoryManager
    agent_id: str
    session_id: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.session_id:
            self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _run(self, query: str) -> str:
        """
        Run the memory tool based on the query.
        
        The query should be in the format: <operation>: <parameters>
        Operations: learn_fact, search_memories, get_timeline, store_memory
        """
        try:
            if ":" not in query:
                return "Error: Query must be in format 'operation: parameters'"
            
            operation, params = query.split(":", 1)
            operation = operation.strip().lower()
            params = params.strip()
            
            if operation == "learn_fact":
                return self._learn_fact(params)
            elif operation == "search_memories":
                return self._search_memories(params)
            elif operation == "get_timeline":
                return self._get_timeline(params)
            elif operation == "store_memory":
                return self._store_memory(params)
            else:
                return f"Error: Unknown operation '{operation}'. Available operations: learn_fact, search_memories, get_timeline, store_memory"
                
        except Exception as e:
            return f"Error executing memory tool: {str(e)}"
    
    def _learn_fact(self, params: str) -> str:
        """Learn and store a new fact."""
        try:
            # Parse fact and category from params
            if "|" in params:
                fact, category = params.split("|", 1)
                fact = fact.strip()
                category = category.strip()
            else:
                fact = params
                category = "general"
            
            self.memory_manager.add_memory(
                content=fact,
                memory_type=MemoryType.SEMANTIC,
                agent_id=self.agent_id,
                metadata={
                    "category": category,
                    "learned_at": datetime.now().isoformat(),
                    "source": "memory_tool"
                }
            )
            
            return f"Successfully learned fact: '{fact}' (category: {category})"
            
        except Exception as e:
            return f"Error learning fact: {str(e)}"
    
    def _search_memories(self, query: str) -> str:
        """Search for relevant memories."""
        try:
            memories = self.memory_manager.search_memory(query=query, limit=5)
            
            if not memories:
                return f"No memories found for query: '{query}'"
            
            results = [f"- {m.content} ({m.timestamp.strftime('%Y-%m-%d %H:%M')})" 
                      for m in memories]
            
            return f"Found {len(memories)} relevant memories for '{query}':\n" + "\n".join(results)
            
        except Exception as e:
            return f"Error searching memories: {str(e)}"
    
    def _get_timeline(self, params: str) -> str:
        """Get timeline of recent activities."""
        try:
            # Parse hours from params, default to 24
            try:
                hours = int(params) if params.strip() else 24
            except ValueError:
                hours = 24
            
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
            
            results = [f"- {m.content} ({m.timestamp.strftime('%H:%M')})" 
                      for m in memories]
            
            return f"Timeline for the last {hours} hours:\n" + "\n".join(results)
            
        except Exception as e:
            return f"Error getting timeline: {str(e)}"
    
    def _store_memory(self, content: str) -> str:
        """Store a memory entry."""
        try:
            self.memory_manager.add_memory(
                content=content,
                memory_type=MemoryType.EPISODIC,
                agent_id=self.agent_id,
                session_id=self.session_id,
                metadata={
                    "source": "memory_tool",
                    "stored_at": datetime.now().isoformat()
                }
            )
            
            return f"Successfully stored memory: '{content}'"
            
        except Exception as e:
            return f"Error storing memory: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version of the tool."""
        return self._run(query) 