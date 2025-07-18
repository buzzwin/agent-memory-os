"""
FastAPI server for Agent Memory OS REST API
"""

import os
import time
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .models import (
    MemoryCreateRequest,
    MemoryUpdateRequest,
    MemoryResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    AgentMemoryRequest,
    AgentMemoryResponse,
    HealthResponse,
    ErrorResponse,
)
from ..memory import MemoryManager
from ..models import MemoryType, MemoryEntry


class MemoryAPI:
    """Main API class for memory operations"""
    
    def __init__(self, db_path: str = "agent_memory.db"):
        # Initialize memory manager with SQLite store and the specified db_path
        self.memory_manager = MemoryManager(store_type="sqlite", db_path=db_path)
        self.start_time = time.time()
        self.version = "1.0.0"
    
    def _memory_to_response(self, memory: MemoryEntry) -> MemoryResponse:
        """Convert MemoryEntry to MemoryResponse"""
        # Handle backward compatibility for old MemoryEntry objects
        importance = getattr(memory, 'importance', 5.0)
        tags = getattr(memory, 'tags', [])
        last_accessed = getattr(memory, 'last_accessed', None)
        
        return MemoryResponse(
            id=memory.id,
            content=memory.content,
            memory_type=memory.memory_type,
            agent_id=memory.agent_id,
            metadata=memory.metadata,
            importance=importance,
            tags=tags,
            created_at=memory.timestamp,  # Use timestamp as created_at
            updated_at=memory.timestamp,  # Use timestamp as updated_at for now
            access_count=0,  # Default to 0 since we don't track this yet
            last_accessed=last_accessed,
        )
    
    def create_memory(self, request: MemoryCreateRequest) -> MemoryResponse:
        """Create a new memory"""
        memory = self.memory_manager.add_memory(
            content=request.content,
            memory_type=request.memory_type,
            agent_id=request.agent_id,
            metadata=request.metadata,
            importance=request.importance,
            tags=request.tags,
        )
        return self._memory_to_response(memory)
    
    def get_memory(self, memory_id: str) -> MemoryResponse:
        """Get a specific memory by ID"""
        memory = self.memory_manager.get_memory(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return self._memory_to_response(memory)
    
    def update_memory(self, memory_id: str, request: MemoryUpdateRequest) -> MemoryResponse:
        """Update an existing memory"""
        # Get existing memory
        memory = self.memory_manager.get_memory(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Update fields
        update_data = {}
        if request.content is not None:
            update_data["content"] = request.content
        if request.memory_type is not None:
            update_data["memory_type"] = request.memory_type
        if request.metadata is not None:
            update_data["metadata"] = request.metadata
        if request.importance is not None:
            update_data["importance"] = request.importance
        if request.tags is not None:
            update_data["tags"] = request.tags
        
        # Update memory
        updated_memory = self.memory_manager.update_memory(memory_id, **update_data)
        return self._memory_to_response(updated_memory)
    
    def delete_memory(self, memory_id: str) -> Dict[str, str]:
        """Delete a memory"""
        success = self.memory_manager.delete_memory(memory_id)
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"message": "Memory deleted successfully"}
    
    def search_memories(self, request: MemorySearchRequest) -> MemorySearchResponse:
        """Search memories with semantic and filtering"""
        start_time = time.time()
        
        # Perform search
        memories = self.memory_manager.search_memory(
            query=request.query,
            memory_type=request.memory_type,
            agent_id=request.agent_id,
            limit=request.limit,
            min_importance=request.min_importance,
        )
        
        # Filter by tags if specified
        if request.tags:
            memories = [
                m for m in memories 
                if m.tags and any(tag in m.tags for tag in request.tags)
            ]
        
        # Convert to response format
        memory_responses = [self._memory_to_response(m) for m in memories]
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return MemorySearchResponse(
            memories=memory_responses,
            total_count=len(memory_responses),
            query=request.query,
            search_time_ms=search_time,
        )
    
    def get_agent_memories(self, agent_id: str, limit: int = 50) -> AgentMemoryResponse:
        """Get all memories for a specific agent"""
        memories = self.memory_manager.get_memories_by_agent(agent_id, limit=limit)
        memory_responses = [self._memory_to_response(m) for m in memories]
        
        # Get recent memories (last 10 accessed)
        recent_memories = sorted(
            memory_responses, 
            key=lambda x: x.last_accessed or x.created_at, 
            reverse=True
        )[:10]
        
        return AgentMemoryResponse(
            agent_id=agent_id,
            memories=memory_responses,
            total_count=len(memory_responses),
            recent_memories=recent_memories,
        )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        all_memories = self.memory_manager.get_all_memories()
        
        stats = {
            "total_memories": len(all_memories),
            "by_type": {},
            "by_agent": {},
            "importance_distribution": {
                "low": 0,      # 0-3
                "medium": 0,   # 4-7
                "high": 0,     # 8-10
            },
        }
        
        for memory in all_memories:
            # Count by type
            type_name = memory.memory_type.value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1
            
            # Count by agent
            agent_id = memory.agent_id or "unknown"
            stats["by_agent"][agent_id] = stats["by_agent"].get(agent_id, 0) + 1
            
            # Count by importance (handle backward compatibility)
            importance = getattr(memory, 'importance', 5.0)
            if importance <= 3:
                stats["importance_distribution"]["low"] += 1
            elif importance <= 7:
                stats["importance_distribution"]["medium"] += 1
            else:
                stats["importance_distribution"]["high"] += 1
        
        return stats
    
    def get_health_status(self) -> HealthResponse:
        """Get API health status"""
        memory_count = len(self.memory_manager.get_all_memories())
        uptime = time.time() - self.start_time
        
        return HealthResponse(
            status="healthy",
            version=self.version,
            memory_count=memory_count,
            uptime_seconds=uptime,
        )


# Global API instance
memory_api: Optional[MemoryAPI] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global memory_api
    # Get db_path from app state or use default
    db_path = getattr(app.state, "db_path", "agent_memory.db")
    memory_api = MemoryAPI(db_path)
    yield
    # Cleanup if needed
    memory_api = None


def create_app(db_path: str = "agent_memory.db") -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Agent Memory OS API",
        description="REST API for persistent, semantic, and episodic memory for AI agents",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Store db_path in app state for lifespan manager
    app.state.db_path = db_path
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="agent_memory_sdk/api/static"), name="static")
    
    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["System"])
    async def health_check():
        """Check API health status"""
        return memory_api.get_health_status()
    
    # Memory CRUD endpoints
    @app.post("/memories", response_model=MemoryResponse, tags=["Memories"])
    async def create_memory(request: MemoryCreateRequest):
        """Create a new memory"""
        return memory_api.create_memory(request)
    
    @app.get("/memories/{memory_id}", response_model=MemoryResponse, tags=["Memories"])
    async def get_memory(memory_id: str = Path(..., description="Memory ID")):
        """Get a specific memory by ID"""
        return memory_api.get_memory(memory_id)
    
    @app.put("/memories/{memory_id}", response_model=MemoryResponse, tags=["Memories"])
    async def update_memory(
        memory_id: str = Path(..., description="Memory ID"),
        request: MemoryUpdateRequest = None,
    ):
        """Update an existing memory"""
        return memory_api.update_memory(memory_id, request)
    
    @app.delete("/memories/{memory_id}", tags=["Memories"])
    async def delete_memory(memory_id: str = Path(..., description="Memory ID")):
        """Delete a memory"""
        return memory_api.delete_memory(memory_id)
    
    # Search endpoint
    @app.post("/memories/search", response_model=MemorySearchResponse, tags=["Search"])
    async def search_memories(request: MemorySearchRequest):
        """Search memories with semantic and filtering"""
        return memory_api.search_memories(request)
    
    # Quick search endpoint
    @app.get("/memories/search", response_model=MemorySearchResponse, tags=["Search"])
    async def quick_search(
        q: str = Query(..., description="Search query"),
        memory_type: Optional[MemoryType] = Query(None, description="Filter by memory type"),
        agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
        limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
        min_importance: Optional[float] = Query(None, ge=0.0, le=10.0, description="Minimum importance score"),
    ):
        """Quick search with query parameters"""
        request = MemorySearchRequest(
            query=q,
            memory_type=memory_type,
            agent_id=agent_id,
            limit=limit,
            min_importance=min_importance,
        )
        return memory_api.search_memories(request)
    
    # Agent-specific endpoints
    @app.get("/agents/{agent_id}/memories", response_model=AgentMemoryResponse, tags=["Agents"])
    async def get_agent_memories(
        agent_id: str = Path(..., description="Agent ID"),
        limit: int = Query(50, ge=1, le=1000, description="Maximum number of memories"),
    ):
        """Get all memories for a specific agent"""
        return memory_api.get_agent_memories(agent_id, limit)
    
    @app.post("/agents/{agent_id}/memories", response_model=MemoryResponse, tags=["Agents"])
    async def create_agent_memory(
        agent_id: str = Path(..., description="Agent ID"),
        request: MemoryCreateRequest = None,
    ):
        """Create a new memory for a specific agent"""
        if request.agent_id and request.agent_id != agent_id:
            raise HTTPException(status_code=400, detail="Agent ID mismatch")
        
        # Override agent_id in request
        request.agent_id = agent_id
        return memory_api.create_memory(request)
    
    # Statistics endpoint
    @app.get("/stats", tags=["System"])
    async def get_stats():
        """Get memory statistics"""
        return memory_api.get_memory_stats()
    
    # Timeline endpoint
    @app.get("/memories/timeline", tags=["Visualization"])
    async def get_timeline(
        agent_id: str = Query(None, description="Filter by agent ID"),
        memory_type: MemoryType = Query(None, description="Filter by memory type"),
        start: str = Query(None, description="Start date (YYYY-MM-DD)"),
        end: str = Query(None, description="End date (YYYY-MM-DD)"),
        limit: int = Query(200, ge=1, le=1000, description="Maximum number of memories")
    ):
        """Get a chronological timeline of memories"""
        memories = memory_api.memory_manager.get_all_memories()
        # Filter by agent
        if agent_id:
            memories = [m for m in memories if m.agent_id == agent_id]
        # Filter by type
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        # Filter by date range
        if start:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start)
            memories = [m for m in memories if m.created_at >= start_dt]
        if end:
            from datetime import datetime
            end_dt = datetime.fromisoformat(end)
            memories = [m for m in memories if m.created_at <= end_dt]
        # Sort by created_at
        memories = sorted(memories, key=lambda m: m.created_at)
        # Limit
        memories = memories[:limit]
        # Convert to dicts
        return {
            "timeline": [memory_api._memory_to_response(m).dict() for m in memories],
            "total_count": len(memories)
        }
    
    # Web UI endpoint
    @app.get("/", tags=["Web UI"])
    async def web_ui():
        """Serve the web UI"""
        return FileResponse("agent_memory_sdk/api/static/index.html")
    
    # List all memories (with pagination)
    @app.get("/memories", tags=["Memories"])
    async def list_memories(
        skip: int = Query(0, ge=0, description="Number of memories to skip"),
        limit: int = Query(50, ge=1, le=1000, description="Maximum number of memories"),
        memory_type: Optional[MemoryType] = Query(None, description="Filter by memory type"),
        agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    ):
        """List all memories with optional filtering and pagination"""
        all_memories = memory_api.memory_manager.get_all_memories()
        
        # Apply filters
        if memory_type:
            all_memories = [m for m in all_memories if m.memory_type == memory_type]
        if agent_id:
            all_memories = [m for m in all_memories if m.agent_id == agent_id]
        
        # Apply pagination
        total_count = len(all_memories)
        memories = all_memories[skip:skip + limit]
        
        return {
            "memories": [memory_api._memory_to_response(m) for m in memories],
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
        }
    
    # Error handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.detail,
                error_code=f"HTTP_{exc.status_code}",
            ).dict(),
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                detail=str(exc),
                error_code="INTERNAL_ERROR",
            ).dict(),
        )
    
    return app 