"""
REST API for Agent Memory OS

This module provides a FastAPI-based REST API for remote memory access.
"""

from .server import create_app, MemoryAPI
from .models import (
    MemoryCreateRequest,
    MemoryUpdateRequest,
    MemoryResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    AgentMemoryRequest,
    AgentMemoryResponse,
)
from .client import MemoryAPIClient, AsyncMemoryAPIClient

__all__ = [
    "create_app",
    "MemoryAPI",
    "MemoryCreateRequest",
    "MemoryUpdateRequest", 
    "MemoryResponse",
    "MemorySearchRequest",
    "MemorySearchResponse",
    "AgentMemoryRequest",
    "AgentMemoryResponse",
    "MemoryAPIClient",
    "AsyncMemoryAPIClient",
] 