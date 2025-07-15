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

__all__ = [
    "MemoryManager", 
    "MemoryEntry", 
    "MemoryType",
    "MemoryChain",
    "MemoryTool",
    "MemoryCallbackHandler", 
    "MemoryAwareAgent",
    "LANGCHAIN_AVAILABLE"
] 