"""
Base store interface for Agent Memory OS

Defines the contract that all storage backends must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import MemoryEntry, MemoryType


class BaseStore(ABC):
    """Abstract base class for memory storage backends"""
    
    @abstractmethod
    def save_memory(self, memory: MemoryEntry) -> bool:
        """
        Save a memory entry to storage
        
        Args:
            memory: MemoryEntry to save
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            MemoryEntry if found, None otherwise
        """
        pass
    
    @abstractmethod
    def search_memories(self, query: str = None, memory_type: Optional[MemoryType] = None,
                       agent_id: Optional[str] = None, session_id: Optional[str] = None,
                       limit: int = 50) -> List[MemoryEntry]:
        """
        Search for memories with various filters
        
        Args:
            query: Text search in content (semantic search for vector stores)
            memory_type: Filter by memory type
            agent_id: Filter by agent ID
            session_id: Filter by session ID
            limit: Maximum number of results
            
        Returns:
            List of matching MemoryEntry objects
        """
        pass
    
    @abstractmethod
    def get_timeline(self, agent_id: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    limit: int = 100) -> List[MemoryEntry]:
        """
        Get chronological timeline of memories
        
        Args:
            agent_id: Filter by agent ID
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of results
            
        Returns:
            List of MemoryEntry objects in chronological order
        """
        pass
    
    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_all_memories(self, limit: int = 10000) -> List[MemoryEntry]:
        """
        Get all memories in the system
        
        Args:
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of all MemoryEntry objects
        """
        pass 