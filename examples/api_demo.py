#!/usr/bin/env python3
"""
Demo for Agent Memory OS REST API

This demo shows how to:
1. Start the API server
2. Use the Python client library
3. Make direct HTTP requests
4. Use the async client
"""

import asyncio
import json
import time
import subprocess
import requests
from typing import Dict, Any

from agent_memory_sdk.api import MemoryAPIClient, AsyncMemoryAPIClient
from agent_memory_sdk.api.models import (
    MemoryCreateRequest,
    MemoryUpdateRequest,
    MemorySearchRequest,
)
from agent_memory_sdk.models import MemoryType


def demo_direct_http_requests():
    """Demo using direct HTTP requests"""
    print("🌐 Demo: Direct HTTP Requests")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Health check
    print("1. Health Check")
    response = requests.get(f"{base_url}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Create a memory
    print("2. Create Memory")
    memory_data = {
        "content": "The user prefers dark mode interfaces",
        "memory_type": "semantic",
        "agent_id": "demo_agent",
        "importance": 8.5,
        "tags": ["preferences", "ui"],
        "metadata": {"source": "user_feedback"}
    }
    response = requests.post(f"{base_url}/memories", json=memory_data)
    print(f"   Status: {response.status_code}")
    created_memory = response.json()
    print(f"   Created Memory ID: {created_memory['id']}")
    print()
    
    # Search memories
    print("3. Search Memories")
    search_data = {
        "query": "user preferences",
        "limit": 5
    }
    response = requests.post(f"{base_url}/memories/search", json=search_data)
    print(f"   Status: {response.status_code}")
    search_results = response.json()
    print(f"   Found {search_results['total_count']} memories")
    print(f"   Search time: {search_results['search_time_ms']:.2f}ms")
    print()
    
    # Quick search
    print("4. Quick Search")
    response = requests.get(f"{base_url}/memories/search?q=dark mode")
    print(f"   Status: {response.status_code}")
    quick_results = response.json()
    print(f"   Found {quick_results['total_count']} memories")
    print()
    
    # Get agent memories
    print("5. Get Agent Memories")
    response = requests.get(f"{base_url}/agents/demo_agent/memories")
    print(f"   Status: {response.status_code}")
    agent_memories = response.json()
    print(f"   Agent has {agent_memories['total_count']} memories")
    print()
    
    # Get statistics
    print("6. Get Statistics")
    response = requests.get(f"{base_url}/stats")
    print(f"   Status: {response.status_code}")
    stats = response.json()
    print(f"   Total memories: {stats['total_memories']}")
    print(f"   By type: {stats['by_type']}")
    print()
    
    return created_memory['id']


def demo_python_client():
    """Demo using the Python client library"""
    print("🐍 Demo: Python Client Library")
    print("=" * 50)
    
    with MemoryAPIClient("http://localhost:8000") as client:
        # Health check
        print("1. Health Check")
        health = client.health_check()
        print(f"   Status: {health.status}")
        print(f"   Version: {health.version}")
        print(f"   Memory count: {health.memory_count}")
        print()
        
        # Create memories
        print("2. Create Multiple Memories")
        memories = []
        for i in range(3):
            request = MemoryCreateRequest(
                content=f"Memory {i+1}: This is a test memory for demonstration",
                memory_type=MemoryType.EPISODIC if i % 2 == 0 else MemoryType.SEMANTIC,
                agent_id="python_client_demo",
                importance=7.0 + i,
                tags=[f"demo_{i+1}", "test"],
                metadata={"demo_round": i+1}
            )
            memory = client.create_memory(request)
            memories.append(memory)
            print(f"   Created memory {i+1}: {memory.id}")
        print()
        
        # Search memories
        print("3. Search Memories")
        search_request = MemorySearchRequest(
            query="test memory",
            limit=10,
            min_importance=5.0
        )
        search_results = client.search_memories(search_request)
        print(f"   Found {search_results.total_count} memories")
        for memory in search_results.memories[:3]:  # Show first 3
            print(f"   - {memory.content[:50]}... (importance: {memory.importance})")
        print()
        
        # Update a memory
        print("4. Update Memory")
        if memories:
            update_request = MemoryUpdateRequest(
                content="Updated: This memory has been modified",
                importance=9.0,
                tags=["updated", "demo"]
            )
            updated_memory = client.update_memory(memories[0].id, update_request)
            print(f"   Updated memory: {updated_memory.content[:50]}...")
            print(f"   New importance: {updated_memory.importance}")
            print()
        
        # Get agent memories
        print("5. Get Agent Memories")
        agent_memories = client.get_agent_memories("python_client_demo")
        print(f"   Agent has {agent_memories.total_count} memories")
        print(f"   Recent memories: {len(agent_memories.recent_memories)}")
        print()
        
        # List memories with pagination
        print("6. List Memories with Pagination")
        all_memories = client.list_memories(skip=0, limit=5)
        print(f"   Showing {len(all_memories['memories'])} of {all_memories['total_count']} memories")
        for memory in all_memories['memories']:
            print(f"   - {memory['content'][:40]}...")
        print()


async def demo_async_client():
    """Demo using the async client library"""
    print("⚡ Demo: Async Client Library")
    print("=" * 50)
    
    async with AsyncMemoryAPIClient("http://localhost:8000") as client:
        # Health check
        print("1. Health Check")
        health = await client.health_check()
        print(f"   Status: {health.status}")
        print(f"   Uptime: {health.uptime_seconds:.2f}s")
        print()
        
        # Create memories concurrently
        print("2. Create Memories Concurrently")
        tasks = []
        for i in range(3):
            request = MemoryCreateRequest(
                content=f"Async memory {i+1}: Created concurrently",
                memory_type=MemoryType.SEMANTIC,
                agent_id="async_demo",
                importance=6.0 + i,
                tags=["async", f"batch_{i+1}"],
                metadata={"async_demo": True}
            )
            tasks.append(client.create_memory(request))
        
        memories = await asyncio.gather(*tasks)
        for i, memory in enumerate(memories):
            print(f"   Created async memory {i+1}: {memory.id}")
        print()
        
        # Concurrent search operations
        print("3. Concurrent Search Operations")
        search_queries = ["async", "concurrent", "demo"]
        search_tasks = [client.quick_search(query, limit=5) for query in search_queries]
        search_results = await asyncio.gather(*search_tasks)
        
        for i, (query, results) in enumerate(zip(search_queries, search_results)):
            print(f"   Query '{query}': {results.total_count} results")
        print()
        
        # Get agent memories
        print("4. Get Agent Memories")
        agent_memories = await client.get_agent_memories("async_demo")
        print(f"   Agent has {agent_memories.total_count} memories")
        print(f"   Recent memories: {len(agent_memories.recent_memories)}")
        print()
        
        # Get statistics
        print("5. Get Statistics")
        stats = await client.get_stats()
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Importance distribution: {stats['importance_distribution']}")
        print()


def demo_error_handling():
    """Demo error handling"""
    print("⚠️  Demo: Error Handling")
    print("=" * 50)
    
    with MemoryAPIClient("http://localhost:8000") as client:
        # Try to get non-existent memory
        print("1. Get Non-existent Memory")
        try:
            client.get_memory("non-existent-id")
        except requests.exceptions.HTTPError as e:
            print(f"   Expected error: {e.response.status_code} - {e.response.json()['error']}")
        print()
        
        # Try to update non-existent memory
        print("2. Update Non-existent Memory")
        try:
            update_request = MemoryUpdateRequest(content="This won't work")
            client.update_memory("non-existent-id", update_request)
        except requests.exceptions.HTTPError as e:
            print(f"   Expected error: {e.response.status_code} - {e.response.json()['error']}")
        print()
        
        # Try to delete non-existent memory
        print("3. Delete Non-existent Memory")
        try:
            client.delete_memory("non-existent-id")
        except requests.exceptions.HTTPError as e:
            print(f"   Expected error: {e.response.status_code} - {e.response.json()['error']}")
        print()


def main():
    """Main demo function"""
    print("🚀 Agent Memory OS REST API Demo")
    print("=" * 60)
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running!")
        else:
            print("❌ API server is not responding properly")
            return
    except requests.exceptions.RequestException:
        print("❌ API server is not running!")
        print("   Please start the server first:")
        print("   python run_api.py")
        return
    
    print()
    
    # Run demos
    try:
        # Demo 1: Direct HTTP requests
        memory_id = demo_direct_http_requests()
        print()
        
        # Demo 2: Python client
        demo_python_client()
        print()
        
        # Demo 3: Async client
        asyncio.run(demo_async_client())
        print()
        
        # Demo 4: Error handling
        demo_error_handling()
        print()
        
        print("🎉 All demos completed successfully!")
        print()
        print("📚 Next steps:")
        print("   - Explore the API documentation at http://localhost:8000/docs")
        print("   - Try the interactive API at http://localhost:8000/redoc")
        print("   - Check the health endpoint at http://localhost:8000/health")
        print("   - View statistics at http://localhost:8000/stats")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 