"""
Agent Memory OS - A memory layer for AI agents

This package provides persistent, semantic + episodic memory that spans time, 
tools, and multi-agent systems.
"""

__version__ = "0.1.0"
__author__ = "Agent Memory OS Team"

from .models import MemoryEntry, MemoryType
from .memory import MemoryManager

# LangChain integration
try:
    from .integrations.langchain import (
        MemoryChain,
        MemoryTool,
        MemoryCallbackHandler,
        MemoryAwareAgent
    )
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    MemoryChain = None
    MemoryTool = None
    MemoryCallbackHandler = None
    MemoryAwareAgent = None

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
except ImportError:
    LANGGRAPH_AVAILABLE = False
    MemoryGraph = None
    MemoryState = None
    MemoryNode = None
    MemoryToolNode = None
    create_memory_tools = None

# REST API integration
try:
    from .api import (
        create_app,
        MemoryAPI,
        MemoryAPIClient,
        AsyncMemoryAPIClient
    )
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    create_app = None
    MemoryAPI = None
    MemoryAPIClient = None
    AsyncMemoryAPIClient = None

__all__ = [
    "MemoryManager", 
    "MemoryEntry", 
    "MemoryType",
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