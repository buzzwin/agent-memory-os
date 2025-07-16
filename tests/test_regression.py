"""
Comprehensive Regression Test Suite for Agent Memory OS

This test suite covers all major components and integrations to ensure
the package is ready for PyPI distribution.
"""

import os
import tempfile
import shutil
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytest

from agent_memory_sdk import MemoryManager, MemoryType
from agent_memory_sdk.models import MemoryEntry
from agent_memory_sdk.store.store_factory import StoreFactory


class TestMemoryManagerRegression:
    """Regression tests for MemoryManager core functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_memory.db")
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_memory_manager_initialization(self):
        """Test MemoryManager initialization with different store types"""
        # Test SQLite initialization
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        assert memory_manager.store_type == "sqlite"
        
        # Test auto-detection (should default to SQLite)
        memory_manager = MemoryManager()
        assert memory_manager.store_type == "sqlite"
    
    def test_memory_crud_operations(self):
        """Test complete CRUD operations for memories"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Create memory
        memory = memory_manager.add_memory(
            content="Test memory content",
            memory_type=MemoryType.SEMANTIC,
            agent_id="test_agent",
            importance=8.0,
            tags=["test", "regression"]
        )
        
        assert memory.id is not None
        assert memory.content == "Test memory content"
        assert memory.memory_type == MemoryType.SEMANTIC
        assert memory.agent_id == "test_agent"
        assert memory.importance == 8.0
        assert "test" in memory.tags
        
        # Read memory
        retrieved = memory_manager.get_memory(memory.id)
        assert retrieved is not None
        assert retrieved.content == memory.content
        
        # Update memory
        updated = memory_manager.update_memory(
            memory.id,
            content="Updated content",
            importance=9.0
        )
        assert updated.content == "Updated content"
        assert updated.importance == 9.0
        
        # Delete memory
        success = memory_manager.delete_memory(memory.id)
        assert success is True
        
        # Verify deletion
        deleted = memory_manager.get_memory(memory.id)
        assert deleted is None
    
    def test_memory_search_functionality(self):
        """Test memory search capabilities"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Add test memories
        memories = [
            ("Python programming language", MemoryType.SEMANTIC),
            ("User asked about machine learning", MemoryType.EPISODIC),
            ("Data science project started", MemoryType.TEMPORAL),
            ("JavaScript web development", MemoryType.SEMANTIC),
            ("User prefers Python over JavaScript", MemoryType.EPISODIC)
        ]
        
        for content, memory_type in memories:
            memory_manager.add_memory(
                content=content,
                memory_type=memory_type,
                agent_id="test_agent"
            )
        
        # Test search by query
        results = memory_manager.search_memory("Python", limit=10)
        assert len(results) >= 2  # Should find Python-related memories
        
        # Test search by memory type
        semantic_results = memory_manager.search_memory(
            query="", 
            memory_type=MemoryType.SEMANTIC,
            limit=10
        )
        assert len(semantic_results) >= 2
        
        # Test search by agent
        agent_results = memory_manager.get_memories_by_agent("test_agent", limit=10)
        assert len(agent_results) == len(memories)
    
    def test_memory_timeline(self):
        """Test timeline functionality"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Add memories with different timestamps
        base_time = datetime.now()
        for i in range(5):
            memory_manager.add_memory(
                content=f"Memory {i}",
                memory_type=MemoryType.EPISODIC,
                agent_id="test_agent"
            )
            time.sleep(0.1)  # Ensure different timestamps
        
        # Test timeline retrieval
        timeline = memory_manager.get_timeline(agent_id="test_agent", limit=10)
        assert len(timeline) == 5
        
        # Verify chronological order
        timestamps = [m.timestamp for m in timeline]
        assert timestamps == sorted(timestamps)
    
    def test_memory_persistence(self):
        """Test memory persistence across sessions"""
        # Create first session
        memory_manager1 = MemoryManager(store_type="sqlite", db_path=self.db_path)
        memory = memory_manager1.add_memory(
            content="Persistent memory",
            memory_type=MemoryType.SEMANTIC,
            agent_id="test_agent"
        )
        
        # Create second session
        memory_manager2 = MemoryManager(store_type="sqlite", db_path=self.db_path)
        retrieved = memory_manager2.get_memory(memory.id)
        
        assert retrieved is not None
        assert retrieved.content == "Persistent memory"
    
    def test_memory_metadata_and_tags(self):
        """Test metadata and tags functionality"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        metadata = {"source": "test", "confidence": 0.95}
        tags = ["important", "test", "metadata"]
        
        memory = memory_manager.add_memory(
            content="Memory with metadata",
            memory_type=MemoryType.SEMANTIC,
            agent_id="test_agent",
            metadata=metadata,
            tags=tags,
            importance=9.5
        )
        
        assert memory.metadata == metadata
        assert memory.tags == tags
        assert memory.importance == 9.5
        
        # Verify persistence
        retrieved = memory_manager.get_memory(memory.id)
        assert retrieved.metadata == metadata
        assert retrieved.tags == tags


class TestStoreFactoryRegression:
    """Regression tests for StoreFactory"""
    
    def test_store_factory_auto_detection(self):
        """Test store type auto-detection"""
        # Test default (should be SQLite)
        store = StoreFactory.create_store()
        assert store is not None
        
        # Test explicit SQLite
        store = StoreFactory.create_store("sqlite")
        assert store is not None
        
        # Test invalid store type
        with pytest.raises(ValueError):
            StoreFactory.create_store("invalid_store")
    
    def test_available_stores(self):
        """Test available stores detection"""
        stores = StoreFactory.get_available_stores()
        assert "sqlite" in stores
        assert isinstance(stores, list)


class TestMemoryEntryRegression:
    """Regression tests for MemoryEntry model"""
    
    def test_memory_entry_creation(self):
        """Test MemoryEntry creation and validation"""
        memory = MemoryEntry(
            content="Test content",
            memory_type=MemoryType.SEMANTIC,
            agent_id="test_agent"
        )
        
        assert memory.id is not None
        assert memory.content == "Test content"
        assert memory.memory_type == MemoryType.SEMANTIC
        assert memory.agent_id == "test_agent"
        assert memory.timestamp is not None
        assert memory.importance == 5.0  # Default value
        assert memory.tags == []  # Default empty list
        assert memory.metadata == {}  # Default empty dict
    
    def test_memory_entry_serialization(self):
        """Test MemoryEntry serialization to/from dict"""
        original = MemoryEntry(
            content="Serialization test",
            memory_type=MemoryType.EPISODIC,
            agent_id="test_agent",
            importance=8.0,
            tags=["test", "serialization"],
            metadata={"test": True}
        )
        
        # Convert to dict
        data = original.to_dict()
        assert data["content"] == original.content
        assert data["memory_type"] == original.memory_type.value
        assert data["agent_id"] == original.agent_id
        assert data["importance"] == original.importance
        assert data["tags"] == original.tags
        assert data["metadata"] == original.metadata
        
        # Convert back from dict
        restored = MemoryEntry.from_dict(data)
        assert restored.content == original.content
        assert restored.memory_type == original.memory_type
        assert restored.agent_id == original.agent_id
        assert restored.importance == original.importance
        assert restored.tags == original.tags
        assert restored.metadata == original.metadata


class TestMemoryTypeRegression:
    """Regression tests for MemoryType enum"""
    
    def test_memory_type_values(self):
        """Test MemoryType enum values"""
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SEMANTIC.value == "semantic"
        assert MemoryType.TEMPORAL.value == "temporal"
    
    def test_memory_type_creation(self):
        """Test MemoryType creation from string"""
        assert MemoryType("episodic") == MemoryType.EPISODIC
        assert MemoryType("semantic") == MemoryType.SEMANTIC
        assert MemoryType("temporal") == MemoryType.TEMPORAL
        
        with pytest.raises(ValueError):
            MemoryType("invalid")


class TestPerformanceRegression:
    """Performance regression tests"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "perf_test.db")
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_bulk_memory_operations(self):
        """Test performance with bulk operations"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Add 100 memories
        start_time = time.time()
        for i in range(100):
            memory_manager.add_memory(
                content=f"Memory {i} with some content for testing",
                memory_type=MemoryType.SEMANTIC,
                agent_id="perf_test_agent"
            )
        add_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert add_time < 10.0  # 10 seconds max for 100 memories
        
        # Test search performance
        start_time = time.time()
        results = memory_manager.search_memory("memory", limit=50)
        search_time = time.time() - start_time
        
        assert search_time < 5.0  # 5 seconds max for search
        assert len(results) > 0
    
    def test_memory_retrieval_performance(self):
        """Test memory retrieval performance"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Add test memory
        memory = memory_manager.add_memory(
            content="Performance test memory",
            memory_type=MemoryType.SEMANTIC,
            agent_id="perf_test_agent"
        )
        
        # Test retrieval performance
        start_time = time.time()
        for _ in range(100):
            retrieved = memory_manager.get_memory(memory.id)
            assert retrieved is not None
        retrieval_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert retrieval_time < 5.0  # 5 seconds max for 100 retrievals


class TestErrorHandlingRegression:
    """Error handling regression tests"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "error_test.db")
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_invalid_memory_id(self):
        """Test handling of invalid memory IDs"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Test getting non-existent memory
        result = memory_manager.get_memory("non-existent-id")
        assert result is None
        
        # Test deleting non-existent memory
        result = memory_manager.delete_memory("non-existent-id")
        assert result is False
    
    def test_invalid_memory_type(self):
        """Test handling of invalid memory types"""
        with pytest.raises(ValueError):
            MemoryType("invalid_type")
    
    def test_empty_content(self):
        """Test handling of empty content"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Should handle empty content gracefully
        memory = memory_manager.add_memory(
            content="",
            memory_type=MemoryType.SEMANTIC,
            agent_id="test_agent"
        )
        assert memory.content == ""
    
    def test_large_content(self):
        """Test handling of large content"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Create large content
        large_content = "x" * 10000  # 10KB content
        
        memory = memory_manager.add_memory(
            content=large_content,
            memory_type=MemoryType.SEMANTIC,
            agent_id="test_agent"
        )
        
        assert memory.content == large_content
        
        # Verify retrieval
        retrieved = memory_manager.get_memory(memory.id)
        assert retrieved.content == large_content


class TestIntegrationRegression:
    """Integration regression tests"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "integration_test.db")
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """Test complete workflow from creation to search to deletion"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # 1. Create memories
        memories = []
        for i in range(10):
            memory = memory_manager.add_memory(
                content=f"Integration test memory {i}",
                memory_type=MemoryType.SEMANTIC,
                agent_id="integration_agent",
                importance=7.0 + (i * 0.1),
                tags=[f"tag_{i}", "integration"],
                metadata={"test_id": i, "workflow": "integration"}
            )
            memories.append(memory)
        
        # 2. Verify all memories were created
        all_memories = memory_manager.get_all_memories()
        assert len(all_memories) == 10
        
        # 3. Test search functionality
        search_results = memory_manager.search_memory("integration", limit=20)
        assert len(search_results) == 10
        
        # 4. Test filtered search
        agent_memories = memory_manager.get_memories_by_agent("integration_agent", limit=20)
        assert len(agent_memories) == 10
        
        # 5. Test timeline
        timeline = memory_manager.get_timeline(agent_id="integration_agent", limit=20)
        assert len(timeline) == 10
        
        # 6. Test memory updates
        updated = memory_manager.update_memory(
            memories[0].id,
            content="Updated integration test memory",
            importance=9.0
        )
        assert updated.content == "Updated integration test memory"
        assert updated.importance == 9.0
        
        # 7. Test memory deletion
        success = memory_manager.delete_memory(memories[0].id)
        assert success is True
        
        # 8. Verify deletion
        remaining = memory_manager.get_all_memories()
        assert len(remaining) == 9
        
        # 9. Verify the deleted memory is gone
        deleted = memory_manager.get_memory(memories[0].id)
        assert deleted is None
    
    def test_cross_session_persistence(self):
        """Test memory persistence across multiple sessions"""
        # Session 1: Create memories
        memory_manager1 = MemoryManager(store_type="sqlite", db_path=self.db_path)
        memory_ids = []
        
        for i in range(5):
            memory = memory_manager1.add_memory(
                content=f"Cross-session memory {i}",
                memory_type=MemoryType.EPISODIC,
                agent_id="cross_session_agent"
            )
            memory_ids.append(memory.id)
        
        # Session 2: Verify memories exist
        memory_manager2 = MemoryManager(store_type="sqlite", db_path=self.db_path)
        for memory_id in memory_ids:
            memory = memory_manager2.get_memory(memory_id)
            assert memory is not None
            assert memory.agent_id == "cross_session_agent"
        
        # Session 3: Update and search
        memory_manager3 = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Update a memory
        updated = memory_manager3.update_memory(
            memory_ids[0],
            content="Updated cross-session memory",
            importance=9.0
        )
        assert updated.content == "Updated cross-session memory"
        
        # Search for memories
        results = memory_manager3.search_memory("cross-session", limit=10)
        assert len(results) == 5


def run_regression_tests():
    """Run all regression tests and generate report"""
    print("🧪 Running Agent Memory OS Regression Test Suite")
    print("=" * 60)
    
    # Test categories
    test_categories = [
        "MemoryManager Core Functionality",
        "StoreFactory",
        "MemoryEntry Model",
        "MemoryType Enum",
        "Performance",
        "Error Handling",
        "Integration Workflows"
    ]
    
    # Run tests with pytest
    import subprocess
    import sys
    
    # Run tests and capture output
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_regression.py", 
        "-v", 
        "--tb=short"
    ], capture_output=True, text=True)
    
    # Print results
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    # Generate summary
    print("\n📊 Regression Test Summary")
    print("=" * 60)
    
    if result.returncode == 0:
        print("✅ All regression tests passed!")
        print("🎉 Package is ready for PyPI distribution")
    else:
        print("❌ Some regression tests failed")
        print("🔧 Please fix issues before PyPI distribution")
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_regression_tests()
    exit(0 if success else 1) 