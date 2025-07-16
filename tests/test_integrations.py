"""
Integration Test Suite for Agent Memory OS

Tests all framework integrations: LangChain, LangGraph, REST API, etc.
"""

import os
import tempfile
import shutil
import time
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import pytest

from agent_memory_sdk import MemoryManager, MemoryType
from agent_memory_sdk.models import MemoryEntry


class TestLangChainIntegration:
    """Integration tests for LangChain components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "langchain_test.db")
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_memory_chain_import(self):
        """Test that LangChain components can be imported"""
        try:
            from agent_memory_sdk.integrations.langchain import (
                MemoryChain, MemoryTool, MemoryCallbackHandler, MemoryAwareAgent
            )
            assert True  # Import successful
        except ImportError as e:
            pytest.fail(f"Failed to import LangChain components: {e}")
    
    def test_memory_chain_creation(self):
        """Test MemoryChain creation and basic functionality"""
        try:
            from agent_memory_sdk.integrations.langchain import MemoryChain
            from langchain_community.llms import FakeListLLM
            
            memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
            
            # Create fake LLM for testing
            llm = FakeListLLM(responses=["I remember you mentioned Python programming"])
            
            # Create memory chain
            memory_chain = MemoryChain(
                memory_manager=memory_manager,
                llm=llm,
                agent_id="test_agent"
            )
            
            assert memory_chain.memory_manager is not None
            assert memory_chain.agent_id == "test_agent"
            
        except ImportError:
            pytest.skip("LangChain not available")
    
    def test_memory_tool_creation(self):
        """Test MemoryTool creation and functionality"""
        try:
            from agent_memory_sdk.integrations.langchain import MemoryTool
            
            memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
            
            # Create memory tool
            memory_tool = MemoryTool(
                memory_manager=memory_manager,
                agent_id="test_agent"
            )
            
            assert memory_tool.name == "memory_tool"
            assert memory_tool.description is not None
            
            # Test tool execution
            result = memory_tool.run("store_memory: Store this test memory")
            assert "stored" in result.lower() or "saved" in result.lower()
            
        except ImportError:
            pytest.skip("LangChain not available")
    
    def test_memory_callback_handler(self):
        """Test MemoryCallbackHandler functionality"""
        try:
            from agent_memory_sdk.integrations.langchain import MemoryCallbackHandler
            from langchain_core.callbacks import CallbackManager
            
            memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
            
            # Create callback handler
            callback_handler = MemoryCallbackHandler(
                memory_manager=memory_manager,
                agent_id="test_agent"
            )
            
            assert callback_handler.memory_manager is not None
            assert callback_handler.agent_id == "test_agent"
            
        except ImportError:
            pytest.skip("LangChain not available")


class TestLangGraphIntegration:
    """Integration tests for LangGraph components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "langgraph_test.db")
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_langgraph_components_import(self):
        """Test that LangGraph components can be imported"""
        try:
            from agent_memory_sdk.integrations.langgraph import (
                MemoryGraph, MemoryState, MemoryNode, MemoryToolNode,
                create_memory_tools
            )
            assert True  # Import successful
        except ImportError as e:
            pytest.fail(f"Failed to import LangGraph components: {e}")
    
    def test_memory_graph_creation(self):
        """Test MemoryGraph creation and basic functionality"""
        try:
            from agent_memory_sdk.integrations.langgraph import MemoryGraph
            from langgraph.graph import StateGraph, END
            
            memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
            
            # Create memory graph
            memory_graph = MemoryGraph(
                memory_manager=memory_manager,
                agent_id="test_agent",
                session_id="test_session"
            )
            
            assert memory_graph.memory_manager is not None
            assert memory_graph.agent_id == "test_agent"
            assert memory_graph.session_id == "test_session"
            
            # Test graph creation
            graph = memory_graph.create_graph()
            assert isinstance(graph, StateGraph)
            
        except ImportError:
            pytest.skip("LangGraph not available")
    
    def test_memory_state_creation(self):
        """Test MemoryState creation and functionality"""
        try:
            from agent_memory_sdk.integrations.langgraph import MemoryState
            
            memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
            
            # Create memory state
            state = MemoryState(
                memory_manager=memory_manager,
                agent_id="test_agent",
                session_id="test_session"
            )
            
            assert state.memory_manager is not None
            assert state.agent_id == "test_agent"
            assert state.session_id == "test_session"
            
        except ImportError:
            pytest.skip("LangGraph not available")
    
    def test_memory_tools_creation(self):
        """Test memory tools creation for LangGraph"""
        try:
            from agent_memory_sdk.integrations.langgraph import create_memory_tools
            
            memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
            
            # Create memory tools
            tools = create_memory_tools(
                memory_manager=memory_manager,
                agent_id="test_agent"
            )
            
            assert len(tools) > 0
            assert all(hasattr(tool, 'name') for tool in tools)
            
        except ImportError:
            pytest.skip("LangGraph not available")


class TestRESTAPIIntegration:
    """Integration tests for REST API components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "api_test.db")
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_api_components_import(self):
        """Test that REST API components can be imported"""
        try:
            from agent_memory_sdk.api import (
                MemoryAPIClient, AsyncMemoryAPIClient
            )
            from agent_memory_sdk.api.models import (
                MemoryCreateRequest, MemoryUpdateRequest, MemoryResponse
            )
            from agent_memory_sdk.api.server import create_app
            assert True  # Import successful
        except ImportError as e:
            pytest.fail(f"Failed to import REST API components: {e}")
    
    def test_api_models_creation(self):
        """Test API model creation and validation"""
        try:
            from agent_memory_sdk.api.models import (
                MemoryCreateRequest, MemoryUpdateRequest
            )
            
            # Test create request
            create_req = MemoryCreateRequest(
                content="Test memory",
                memory_type=MemoryType.SEMANTIC,
                agent_id="test_agent"
            )
            
            assert create_req.content == "Test memory"
            assert create_req.memory_type == MemoryType.SEMANTIC
            assert create_req.agent_id == "test_agent"
            
            # Test update request
            update_req = MemoryUpdateRequest(
                content="Updated memory",
                importance=9.0
            )
            
            assert update_req.content == "Updated memory"
            assert update_req.importance == 9.0
            
        except ImportError:
            pytest.skip("FastAPI not available")
    
    def test_api_client_creation(self):
        """Test API client creation"""
        try:
            from agent_memory_sdk.api import MemoryAPIClient
            
            # Test client creation
            client = MemoryAPIClient("http://localhost:8000")
            assert client.base_url == "http://localhost:8000"
            
        except ImportError:
            pytest.skip("FastAPI not available")
    
    def test_async_api_client_creation(self):
        """Test async API client creation"""
        try:
            from agent_memory_sdk.api import AsyncMemoryAPIClient
            
            # Test async client creation
            client = AsyncMemoryAPIClient("http://localhost:8000")
            assert client.base_url == "http://localhost:8000"
            
        except ImportError:
            pytest.skip("FastAPI not available")


class TestStoreIntegrations:
    """Integration tests for storage backends"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "store_test.db")
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_sqlite_store_integration(self):
        """Test SQLite store integration"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Test basic operations
        memory = memory_manager.add_memory(
            content="SQLite test memory",
            memory_type=MemoryType.SEMANTIC,
            agent_id="test_agent"
        )
        
        assert memory.id is not None
        assert memory.content == "SQLite test memory"
        
        # Test retrieval
        retrieved = memory_manager.get_memory(memory.id)
        assert retrieved is not None
        assert retrieved.content == memory.content
    
    def test_store_factory_integration(self):
        """Test store factory integration"""
        from agent_memory_sdk.store.store_factory import StoreFactory
        
        # Test SQLite store creation
        store = StoreFactory.create_store("sqlite", db_path=self.db_path)
        assert store is not None
        
        # Test available stores
        stores = StoreFactory.get_available_stores()
        assert "sqlite" in stores
    
    def test_pinecone_store_availability(self):
        """Test Pinecone store availability (if configured)"""
        from agent_memory_sdk.store.store_factory import StoreFactory
        
        stores = StoreFactory.get_available_stores()
        
        # Check if Pinecone is available (depends on environment variables)
        if "pinecone" in stores:
            # Test Pinecone store creation
            try:
                store = StoreFactory.create_store("pinecone")
                assert store is not None
            except Exception as e:
                # Pinecone might not be properly configured
                pytest.skip(f"Pinecone not properly configured: {e}")
    
    def test_postgresql_store_availability(self):
        """Test PostgreSQL store availability (if configured)"""
        from agent_memory_sdk.store.store_factory import StoreFactory
        
        stores = StoreFactory.get_available_stores()
        
        # Check if PostgreSQL is available (depends on environment variables)
        if "postgresql" in stores:
            # Test PostgreSQL store creation
            try:
                store = StoreFactory.create_store("postgresql")
                assert store is not None
            except Exception as e:
                # PostgreSQL might not be properly configured
                pytest.skip(f"PostgreSQL not properly configured: {e}")


class TestUtilityIntegrations:
    """Integration tests for utility functions"""
    
    def test_embedding_utils_integration(self):
        """Test embedding utilities integration"""
        try:
            from agent_memory_sdk.utils.embedding_utils import (
                generate_embedding, calculate_similarity
            )
            
            # Test embedding generation
            text = "Test text for embedding"
            embedding = generate_embedding(text)
            assert len(embedding) > 0
            
            # Test similarity calculation
            embedding1 = generate_embedding("Hello world")
            embedding2 = generate_embedding("Hello world")
            similarity = calculate_similarity(embedding1, embedding2)
            assert 0 <= similarity <= 1.000001  # Allow for floating point precision
            
        except ImportError as e:
            pytest.fail(f"Failed to import embedding utilities: {e}")
    
    def test_time_utils_integration(self):
        """Test time utilities integration"""
        try:
            from agent_memory_sdk.utils.time_utils import (
                format_timestamp, parse_timestamp
            )
            
            # Test timestamp formatting
            now = datetime.now()
            formatted = format_timestamp(now)
            assert isinstance(formatted, str)
            
            # Test timestamp parsing
            parsed = parse_timestamp(formatted)
            assert isinstance(parsed, datetime)
            
        except ImportError as e:
            pytest.fail(f"Failed to import time utilities: {e}")


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "e2e_test.db")
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_memory_lifecycle_integration(self):
        """Test complete memory lifecycle across components"""
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # 1. Create memory
        memory = memory_manager.add_memory(
            content="E2E test memory",
            memory_type=MemoryType.SEMANTIC,
            agent_id="e2e_agent",
            importance=8.0,
            tags=["e2e", "test"],
            metadata={"test_type": "integration"}
        )
        
        # 2. Verify memory creation
        assert memory.id is not None
        assert memory.content == "E2E test memory"
        
        # 3. Test search
        results = memory_manager.search_memory("E2E", limit=10)
        assert len(results) >= 1
        assert any(r.id == memory.id for r in results)
        
        # 4. Test timeline
        timeline = memory_manager.get_timeline(agent_id="e2e_agent", limit=10)
        assert len(timeline) >= 1
        assert any(r.id == memory.id for r in timeline)
        
        # 5. Test update
        updated = memory_manager.update_memory(
            memory.id,
            content="Updated E2E test memory",
            importance=9.0
        )
        assert updated.content == "Updated E2E test memory"
        assert updated.importance == 9.0
        
        # 6. Test deletion
        success = memory_manager.delete_memory(memory.id)
        assert success is True
        
        # 7. Verify deletion
        deleted = memory_manager.get_memory(memory.id)
        assert deleted is None
    
    def test_cross_component_integration(self):
        """Test integration between different components"""
        # Test that all components can work together
        memory_manager = MemoryManager(store_type="sqlite", db_path=self.db_path)
        
        # Test with LangChain components (if available)
        try:
            from agent_memory_sdk.integrations.langchain import MemoryTool
            
            memory_tool = MemoryTool(
                memory_manager=memory_manager,
                agent_id="integration_agent"
            )
            
            # Use the tool
            result = memory_tool.run("store_memory: Integration test with LangChain")
            assert "stored" in result.lower() or "saved" in result.lower()
            
        except ImportError:
            # LangChain not available, skip this part
            pass
        
        # Test with LangGraph components (if available)
        try:
            from agent_memory_sdk.integrations.langgraph import create_memory_tools
            
            tools = create_memory_tools(
                memory_manager=memory_manager,
                agent_id="integration_agent"
            )
            
            assert len(tools) > 0
            
        except ImportError:
            # LangGraph not available, skip this part
            pass


def run_integration_tests():
    """Run all integration tests and generate report"""
    print("🔗 Running Agent Memory OS Integration Test Suite")
    print("=" * 60)
    
    # Test categories
    test_categories = [
        "LangChain Integration",
        "LangGraph Integration", 
        "REST API Integration",
        "Storage Backends",
        "Utility Functions",
        "End-to-End Workflows"
    ]
    
    # Run tests with pytest
    import subprocess
    import sys
    
    # Run tests and capture output
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_integrations.py", 
        "-v", 
        "--tb=short"
    ], capture_output=True, text=True)
    
    # Print results
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    # Generate summary
    print("\n📊 Integration Test Summary")
    print("=" * 60)
    
    if result.returncode == 0:
        print("✅ All integration tests passed!")
        print("🎉 All framework integrations are working")
    else:
        print("❌ Some integration tests failed")
        print("🔧 Please check framework dependencies and configurations")
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1) 