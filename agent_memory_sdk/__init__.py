"""
Agent Memory OS - A memory layer for AI agents

This package provides persistent, semantic + episodic memory that spans time, 
tools, and multi-agent systems.
"""

__version__ = "0.1.0"
__author__ = "Agent Memory OS Team"

# Check if the package is properly installed
import sys
import os

def check_installation():
    """
    Check if the package is properly installed and provide helpful error messages
    """
    try:
        # Try to import a core module
        from .models import MemoryEntry, MemoryType
    except ImportError as e:
        if "No module named 'agent_memory_sdk'" in str(e):
            print("❌ ERROR: agent_memory_sdk package is not properly installed!")
            print("🔧 SOLUTION:")
            print("1. Make sure you're in the project root directory")
            print("2. Install the package in editable mode:")
            print("   pip install -e .")
            print("\n3. Or activate your virtual environment first:")
            print("   source venv/bin/activate  # On Unix/Mac")
            print("   venv\\Scripts\\activate     # On Windows")
            print("   pip install -e .")
            print("\n4. If you're running from a different directory, make sure")
            print("   the package is installed in your current Python environment.")
            sys.exit(1)
        else:
            # Re-raise other import errors
            raise

def check_pinecone_conflict():
    """
    Check for Pinecone package conflicts and provide helpful error messages
    """
    try:
        import pinecone
    except Exception as e:
        if "pinecone-client" in str(e) and "renamed" in str(e):
            print("❌ ERROR: Pinecone package conflict detected!")
            print("🔧 SOLUTION:")
            print("1. Remove the old pinecone-client package:")
            print("   pip uninstall pinecone-client -y")
            print("\n2. Install the new pinecone package:")
            print("   pip install pinecone>=7.0.0")
            print("\n3. If you are using requirements.txt, update it to use pinecone instead of pinecone-client")
            sys.exit(1)
        else:
            # Re-raise other pinecone errors
            raise

# Run installation checks
check_installation()
check_pinecone_conflict()

from .models import MemoryEntry, MemoryType
from .memory import MemoryManager
from .store import SQLiteStore, PineconeStore, BaseStore, StoreFactory

# LangChain integration
try:
    from .integrations.langchain import (
        MemoryChain,
        MemoryTool,
        MemoryCallbackHandler,
        MemoryAwareAgent
    )
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    MemoryChain = None
    MemoryTool = None
    MemoryCallbackHandler = None
    MemoryAwareAgent = None
    print(f"⚠️Warning: LangChain integration not available: {e}")
    print("   Install with: pip install langchain langchain-community langchain-core")

# LangGraph integration
try:
    from .integrations.langgraph import (
        MemoryGraph,
        MemoryState,
        MemoryNode,
        MemoryToolNode
    )
    from .integrations.langgraph.memory_tool_node import create_memory_tools
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    MemoryGraph = None
    MemoryState = None
    MemoryNode = None
    MemoryToolNode = None
    create_memory_tools = None
    print(f"⚠️Warning: LangGraph integration not available: {e}")
    print("   Install with: pip install langgraph")

# REST API integration
try:
    from .api import (
        create_app,
        MemoryAPI,
        MemoryAPIClient,
        AsyncMemoryAPIClient
    )
    API_AVAILABLE = True
except ImportError as e:
    API_AVAILABLE = False
    create_app = None
    MemoryAPI = None
    MemoryAPIClient = None
    AsyncMemoryAPIClient = None
    print(f"⚠️ Warning: REST API integration not available: {e}")
    print("   Install with: pip install fastapi uvicorn")

__all__ = [
    "MemoryManager", 
    "MemoryEntry", 
    "MemoryType",
    "SQLiteStore",
    "PineconeStore", 
    "BaseStore",
    "StoreFactory",
    "MemoryChain",
    "MemoryTool",
    "MemoryCallbackHandler", 
    "MemoryAwareAgent",
    "LANGCHAIN_AVAILABLE",
    "MemoryGraph",
    "MemoryState",
    "MemoryNode",
    "MemoryToolNode",
    "create_memory_tools",
    "LANGGRAPH_AVAILABLE",
    "create_app",
    "MemoryAPI",
    "MemoryAPIClient",
    "AsyncMemoryAPIClient",
    "API_AVAILABLE"
] 