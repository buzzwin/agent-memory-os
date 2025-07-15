"""
Agent Memory OS - A memory layer for AI agents

This package provides persistent, semantic + episodic memory that spans time, 
tools, and multi-agent systems.
"""

__version__ = "0.1.0"
__author__ = "Agent Memory OS Team"

from .models import MemoryEntry, MemoryType
from .memory import MemoryManager

__all__ = ["MemoryManager", "MemoryEntry", "MemoryType"] 