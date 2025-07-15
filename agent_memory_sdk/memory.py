"""
Core memory classes for Agent Memory OS

Provides MemoryManager for managing episodic, semantic, and temporal memory across AI agents.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from .models import MemoryEntry, MemoryType
from .store import SQLiteStore
from .utils.embedding_utils import generate_embedding


class MemoryManager:
    """Main memory management class for Agent Memory OS"""
    
    def __init__(self, store_backend: Optional[str] = None, db_path: str = "agent_memory.db"):
        """
        Initialize memory manager
        
        Args:
            store_backend: Backend storage type (default: SQLite)
            db_path: Path to database file (for SQLite)
        """
        self.store_backend = store_backend or "sqlite"
        self._store = SQLiteStore(db_path)
        
    def add_memory(self, content: str, memory_type: MemoryType = MemoryType.EPISODIC,
                   agent_id: Optional[str] = None, session_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> MemoryEntry:
        """
        Add a new memory entry
        
        Args:
            content: The memory content
            memory_type: Type of memory
            agent_id: ID of the agent creating the memory
            session_id: Session identifier
            metadata: Additional metadata
            
        Returns:
            Created MemoryEntry
        """
        memory = MemoryEntry(
            content=content,
            memory_type=memory_type,
            agent_id=agent_id,
            session_id=session_id,
            metadata=metadata or {}
        )
        
        # Generate embedding for semantic search
        try:
            memory.embedding = generate_embedding(content)
        except Exception as e:
            print(f"Warning: Could not generate embedding: {e}")
        
        # Store in backend
        success = self._store.save_memory(memory)
        if not success:
            print(f"Warning: Could not save memory to store: {memory.id}")
        
        return memory
    
    def search_memory(self, query: str, memory_type: Optional[MemoryType] = None,
                     limit: int = 10) -> List[MemoryEntry]:
        """
        Search for memories by semantic similarity
        
        Args:
            query: Search query
            memory_type: Filter by memory type
            limit: Maximum number of results
            
        Returns:
            List of relevant MemoryEntry objects
        """
        return self._store.search_memories(
            query=query,
            memory_type=memory_type,
            limit=limit
        )
    
    def get_episodic_memories(self, agent_id: Optional[str] = None,
                             session_id: Optional[str] = None,
                             limit: int = 50) -> List[MemoryEntry]:
        """
        Get episodic memories for an agent or session
        
        Args:
            agent_id: Filter by agent ID
            session_id: Filter by session ID
            limit: Maximum number of results
            
        Returns:
            List of episodic MemoryEntry objects
        """
        return self._store.search_memories(
            memory_type=MemoryType.EPISODIC,
            agent_id=agent_id,
            session_id=session_id,
            limit=limit
        )
    
    def get_timeline(self, agent_id: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> List[MemoryEntry]:
        """
        Get temporal timeline of memories
        
        Args:
            agent_id: Filter by agent ID
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of MemoryEntry objects in chronological order
        """
        return self._store.get_timeline(
            agent_id=agent_id,
            start_time=start_time,
            end_time=end_time
        ) 