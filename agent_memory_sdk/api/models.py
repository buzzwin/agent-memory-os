"""
Pydantic models for the Memory API
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from ..models import MemoryType


class MemoryCreateRequest(BaseModel):
    """Request model for creating a new memory"""
    content: str = Field(..., description="The content of the memory")
    memory_type: MemoryType = Field(..., description="Type of memory")
    agent_id: Optional[str] = Field(None, description="ID of the agent this memory belongs to")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    importance: Optional[float] = Field(1.0, ge=0.0, le=10.0, description="Importance score (0-10)")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


class MemoryUpdateRequest(BaseModel):
    """Request model for updating an existing memory"""
    content: Optional[str] = Field(None, description="The content of the memory")
    memory_type: Optional[MemoryType] = Field(None, description="Type of memory")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    importance: Optional[float] = Field(None, ge=0.0, le=10.0, description="Importance score (0-10)")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


class MemoryResponse(BaseModel):
    """Response model for memory data"""
    id: str = Field(..., description="Unique memory ID")
    content: str = Field(..., description="The content of the memory")
    memory_type: MemoryType = Field(..., description="Type of memory")
    agent_id: Optional[str] = Field(None, description="ID of the agent this memory belongs to")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    importance: float = Field(..., description="Importance score")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    access_count: int = Field(..., description="Number of times accessed")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")


class MemorySearchRequest(BaseModel):
    """Request model for searching memories"""
    query: str = Field(..., description="Search query")
    memory_type: Optional[MemoryType] = Field(None, description="Filter by memory type")
    agent_id: Optional[str] = Field(None, description="Filter by agent ID")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of results")
    min_importance: Optional[float] = Field(None, ge=0.0, le=10.0, description="Minimum importance score")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    include_metadata: bool = Field(True, description="Whether to include metadata in results")


class MemorySearchResponse(BaseModel):
    """Response model for memory search results"""
    memories: List[MemoryResponse] = Field(..., description="List of matching memories")
    total_count: int = Field(..., description="Total number of matching memories")
    query: str = Field(..., description="The search query used")
    search_time_ms: float = Field(..., description="Search execution time in milliseconds")


class AgentMemoryRequest(BaseModel):
    """Request model for agent-specific memory operations"""
    agent_id: str = Field(..., description="ID of the agent")
    content: Optional[str] = Field(None, description="Content for new memory (if creating)")
    memory_type: Optional[MemoryType] = Field(None, description="Type of memory (if creating)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AgentMemoryResponse(BaseModel):
    """Response model for agent memory operations"""
    agent_id: str = Field(..., description="ID of the agent")
    memories: List[MemoryResponse] = Field(..., description="List of agent memories")
    total_count: int = Field(..., description="Total number of agent memories")
    recent_memories: List[MemoryResponse] = Field(..., description="Recently accessed memories")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    memory_count: int = Field(..., description="Total number of memories in storage")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")


class ErrorResponse(BaseModel):
    """Response model for error messages"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling") 