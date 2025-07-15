"""
Python client library for Agent Memory OS REST API
"""

import requests
import json
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from urllib.parse import urljoin

from .models import (
    MemoryCreateRequest,
    MemoryUpdateRequest,
    MemoryResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    AgentMemoryResponse,
    HealthResponse,
)


class MemoryAPIClient:
    """Client for interacting with the Agent Memory OS REST API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an HTTP request to the API"""
        url = urljoin(self.base_url, endpoint)
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response
    
    def health_check(self) -> HealthResponse:
        """Check API health status"""
        response = self._make_request('GET', '/health')
        return HealthResponse(**response.json())
    
    def create_memory(self, request: MemoryCreateRequest) -> MemoryResponse:
        """Create a new memory"""
        response = self._make_request('POST', '/memories', json=request.dict())
        return MemoryResponse(**response.json())
    
    def get_memory(self, memory_id: str) -> MemoryResponse:
        """Get a specific memory by ID"""
        response = self._make_request('GET', f'/memories/{memory_id}')
        return MemoryResponse(**response.json())
    
    def update_memory(self, memory_id: str, request: MemoryUpdateRequest) -> MemoryResponse:
        """Update an existing memory"""
        response = self._make_request('PUT', f'/memories/{memory_id}', json=request.dict())
        return MemoryResponse(**response.json())
    
    def delete_memory(self, memory_id: str) -> Dict[str, str]:
        """Delete a memory"""
        response = self._make_request('DELETE', f'/memories/{memory_id}')
        return response.json()
    
    def search_memories(self, request: MemorySearchRequest) -> MemorySearchResponse:
        """Search memories with semantic and filtering"""
        response = self._make_request('POST', '/memories/search', json=request.dict())
        return MemorySearchResponse(**response.json())
    
    def quick_search(self, query: str, **kwargs) -> MemorySearchResponse:
        """Quick search with query parameters"""
        params = {'q': query}
        params.update(kwargs)
        response = self._make_request('GET', '/memories/search', params=params)
        return MemorySearchResponse(**response.json())
    
    def get_agent_memories(self, agent_id: str, limit: int = 50) -> AgentMemoryResponse:
        """Get all memories for a specific agent"""
        response = self._make_request('GET', f'/agents/{agent_id}/memories', params={'limit': limit})
        return AgentMemoryResponse(**response.json())
    
    def create_agent_memory(self, agent_id: str, request: MemoryCreateRequest) -> MemoryResponse:
        """Create a new memory for a specific agent"""
        response = self._make_request('POST', f'/agents/{agent_id}/memories', json=request.dict())
        return MemoryResponse(**response.json())
    
    def list_memories(self, skip: int = 0, limit: int = 50, **filters) -> Dict[str, Any]:
        """List all memories with optional filtering and pagination"""
        params = {'skip': skip, 'limit': limit}
        params.update(filters)
        response = self._make_request('GET', '/memories', params=params)
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        response = self._make_request('GET', '/stats')
        return response.json()
    
    def close(self):
        """Close the client session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncMemoryAPIClient:
    """Async client for interacting with the Agent Memory OS REST API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize the async API client
        
        Args:
            base_url: Base URL of the API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            import aiohttp
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                }
            )
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make an async HTTP request to the API"""
        session = await self._get_session()
        url = urljoin(self.base_url, endpoint)
        
        async with session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def health_check(self) -> HealthResponse:
        """Check API health status"""
        data = await self._make_request('GET', '/health')
        return HealthResponse(**data)
    
    async def create_memory(self, request: MemoryCreateRequest) -> MemoryResponse:
        """Create a new memory"""
        data = await self._make_request('POST', '/memories', json=request.dict())
        return MemoryResponse(**data)
    
    async def get_memory(self, memory_id: str) -> MemoryResponse:
        """Get a specific memory by ID"""
        data = await self._make_request('GET', f'/memories/{memory_id}')
        return MemoryResponse(**data)
    
    async def update_memory(self, memory_id: str, request: MemoryUpdateRequest) -> MemoryResponse:
        """Update an existing memory"""
        data = await self._make_request('PUT', f'/memories/{memory_id}', json=request.dict())
        return MemoryResponse(**data)
    
    async def delete_memory(self, memory_id: str) -> Dict[str, str]:
        """Delete a memory"""
        return await self._make_request('DELETE', f'/memories/{memory_id}')
    
    async def search_memories(self, request: MemorySearchRequest) -> MemorySearchResponse:
        """Search memories with semantic and filtering"""
        data = await self._make_request('POST', '/memories/search', json=request.dict())
        return MemorySearchResponse(**data)
    
    async def quick_search(self, query: str, **kwargs) -> MemorySearchResponse:
        """Quick search with query parameters"""
        params = {'q': query}
        params.update(kwargs)
        data = await self._make_request('GET', '/memories/search', params=params)
        return MemorySearchResponse(**data)
    
    async def get_agent_memories(self, agent_id: str, limit: int = 50) -> AgentMemoryResponse:
        """Get all memories for a specific agent"""
        data = await self._make_request('GET', f'/agents/{agent_id}/memories', params={'limit': limit})
        return AgentMemoryResponse(**data)
    
    async def create_agent_memory(self, agent_id: str, request: MemoryCreateRequest) -> MemoryResponse:
        """Create a new memory for a specific agent"""
        data = await self._make_request('POST', f'/agents/{agent_id}/memories', json=request.dict())
        return MemoryResponse(**data)
    
    async def list_memories(self, skip: int = 0, limit: int = 50, **filters) -> Dict[str, Any]:
        """List all memories with optional filtering and pagination"""
        params = {'skip': skip, 'limit': limit}
        params.update(filters)
        return await self._make_request('GET', '/memories', params=params)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return await self._make_request('GET', '/stats')
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close() 