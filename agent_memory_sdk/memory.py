"""
Core memory classes for Agent Memory OS

Provides MemoryManager for managing episodic, semantic, and temporal memory across AI agents.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import sqlite3

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
                   metadata: Optional[Dict[str, Any]] = None,
                   importance: Optional[float] = None, tags: Optional[list] = None) -> MemoryEntry:
        """
        Add a new memory entry
        
        Args:
            content: The memory content
            memory_type: Type of memory
            agent_id: ID of the agent creating the memory
            session_id: Session identifier
            metadata: Additional metadata
            importance: Importance score (0-10)
            tags: List of tags
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
        if importance is not None:
            memory.importance = importance
        if tags is not None:
            memory.tags = tags
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
    
    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Get a specific memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            MemoryEntry if found, None otherwise
        """
        return self._store.get_memory(memory_id)
    
    def get_all_memories(self) -> List[MemoryEntry]:
        """
        Get all memories in the system
        
        Returns:
            List of all MemoryEntry objects
        """
        return self._store.search_memories(limit=10000)  # Large limit to get all
    
    def get_memories_by_agent(self, agent_id: str, limit: int = 50) -> List[MemoryEntry]:
        """
        Get all memories for a specific agent
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of results
            
        Returns:
            List of MemoryEntry objects for the agent
        """
        return self._store.search_memories(agent_id=agent_id, limit=limit)
    
    def update_memory(self, memory_id: str, **kwargs) -> Optional[MemoryEntry]:
        """
        Update an existing memory
        
        Args:
            memory_id: ID of the memory to update
            **kwargs: Fields to update (content, memory_type, metadata, importance, tags)
            
        Returns:
            Updated MemoryEntry if successful, None otherwise
        """
        # Get existing memory
        memory = self.get_memory(memory_id)
        if not memory:
            return None
        
        # Update fields
        if 'content' in kwargs:
            memory.content = kwargs['content']
        if 'memory_type' in kwargs:
            memory.memory_type = kwargs['memory_type']
        if 'metadata' in kwargs:
            memory.metadata = kwargs['metadata']
        if 'importance' in kwargs:
            memory.importance = kwargs['importance']
        if 'tags' in kwargs:
            memory.tags = kwargs['tags']
        
        # Regenerate embedding if content changed
        if 'content' in kwargs:
            try:
                memory.embedding = generate_embedding(memory.content)
            except Exception as e:
                print(f"Warning: Could not regenerate embedding: {e}")
        
        # Save updated memory
        success = self._store.save_memory(memory)
        return memory if success else None
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self._store.db_path) as conn:
                cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False 