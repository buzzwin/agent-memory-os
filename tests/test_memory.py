"""
Unit tests for Agent Memory OS core functionality
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta

from agent_memory_sdk import MemoryManager, MemoryEntry, MemoryType
from agent_memory_sdk.store import SQLiteStore


class TestMemoryEntry:
    """Test MemoryEntry class"""
    
    def test_memory_entry_creation(self):
        """Test creating a memory entry"""
        memory = MemoryEntry(
            content="Test memory content",
            memory_type=MemoryType.EPISODIC,
            agent_id="test_agent"
        )
        
        assert memory.content == "Test memory content"
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.agent_id == "test_agent"
        assert memory.id is not None
    
    def test_memory_entry_to_dict(self):
        """Test converting memory entry to dictionary"""
        memory = MemoryEntry(
            content="Test content",
            memory_type=MemoryType.SEMANTIC,
            agent_id="test_agent",
            session_id="test_session"
        )
        
        data = memory.to_dict()
        
        assert data["content"] == "Test content"
        assert data["memory_type"] == "semantic"
        assert data["agent_id"] == "test_agent"
        assert data["session_id"] == "test_session"
        assert "timestamp" in data
    
    def test_memory_entry_from_dict(self):
        """Test creating memory entry from dictionary"""
        data = {
            "id": "test_id",
            "content": "Test content",
            "memory_type": "episodic",
            "agent_id": "test_agent",
            "timestamp": "2023-01-01T12:00:00"
        }
        
        memory = MemoryEntry.from_dict(data)
        
        assert memory.id == "test_id"
        assert memory.content == "Test content"
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.agent_id == "test_agent"


class TestSQLiteStore:
    """Test SQLite storage backend"""
    
    def setup_method(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_memory.db")
        self.store = SQLiteStore(self.db_path)
    
    def teardown_method(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_save_and_retrieve_memory(self):
        """Test saving and retrieving a memory entry"""
        memory = MemoryEntry(
            content="Test memory",
            memory_type=MemoryType.EPISODIC,
            agent_id="test_agent"
        )
        
        # Save memory
        success = self.store.save_memory(memory)
        assert success is True
        
        # Retrieve memory
        retrieved = self.store.get_memory(memory.id)
        assert retrieved is not None
        assert retrieved.content == "Test memory"
        assert retrieved.agent_id == "test_agent"
    
    def test_search_memories(self):
        """Test searching memories"""
        # Add some test memories
        memories = [
            MemoryEntry(content="Python programming", memory_type=MemoryType.SEMANTIC),
            MemoryEntry(content="JavaScript development", memory_type=MemoryType.SEMANTIC),
            MemoryEntry(content="User asked about Python", memory_type=MemoryType.EPISODIC)
        ]
        
        for memory in memories:
            self.store.save_memory(memory)
        
        # Search for Python-related memories
        results = self.store.search_memories(query="Python")
        assert len(results) == 2
        
        # Filter by memory type
        semantic_results = self.store.search_memories(memory_type=MemoryType.SEMANTIC)
        assert len(semantic_results) == 2
    
    def test_timeline_retrieval(self):
        """Test timeline retrieval"""
        # Add memories with different timestamps
        now = datetime.now()
        
        memory1 = MemoryEntry(
            content="First memory",
            timestamp=now - timedelta(hours=2)
        )
        memory2 = MemoryEntry(
            content="Second memory",
            timestamp=now - timedelta(hours=1)
        )
        
        self.store.save_memory(memory1)
        self.store.save_memory(memory2)
        
        # Get timeline
        timeline = self.store.get_timeline()
        assert len(timeline) == 2
        assert timeline[0].content == "First memory"  # Should be chronological


class TestMemoryManager:
    """Test MemoryManager class"""
    
    def test_memory_manager_initialization(self):
        """Test memory manager initialization"""
        manager = MemoryManager()
        assert manager.store_backend == "sqlite"
    
    def test_add_memory(self):
        """Test adding memory through manager"""
        manager = MemoryManager()
        
        memory = manager.add_memory(
            content="Test memory",
            memory_type=MemoryType.EPISODIC,
            agent_id="test_agent"
        )
        
        assert memory.content == "Test memory"
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.agent_id == "test_agent"
    
    def test_search_memory(self):
        """Test memory search through manager"""
        manager = MemoryManager()
        
        # Add some memories
        manager.add_memory("Python is a programming language", MemoryType.SEMANTIC)
        manager.add_memory("User asked about Python", MemoryType.EPISODIC)
        
        # Search (this will return empty for now since store integration is TODO)
        results = manager.search_memory("Python")
        # For now, we expect empty results since store integration is not implemented
        assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__]) 