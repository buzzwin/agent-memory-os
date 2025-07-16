#!/usr/bin/env python3
"""
PostgreSQL Memory OS Demo

This demo showcases PostgreSQL backend for Agent Memory OS with:
- Full CRUD operations
- Full-text search capabilities
- Timeline retrieval
- Performance comparisons
"""

import os
import time
from datetime import datetime, timedelta

from agent_memory_sdk import MemoryManager, MemoryType


def check_postgresql_config():
    """Check PostgreSQL configuration"""
    print("🐘 PostgreSQL Memory OS Demo")
    print("=" * 50)
    
    # Check environment variables
    host = os.getenv("POSTGRESQL_HOST")
    port = os.getenv("POSTGRESQL_PORT")
    database = os.getenv("POSTGRESQL_DATABASE")
    user = os.getenv("POSTGRESQL_USER")
    password = os.getenv("POSTGRESQL_PASSWORD")
    connection_string = os.getenv("POSTGRESQL_CONNECTION_STRING")
    
    if connection_string:
        print("✅ PostgreSQL connection string found")
        print(f"   Connection: {connection_string[:20]}...")
    elif host and database and user:
        print("✅ PostgreSQL configuration found")
        print(f"   Host: {host}")
        print(f"   Port: {port or '5432'}")
        print(f"   Database: {database}")
        print(f"   User: {user}")
    else:
        print("❌ PostgreSQL configuration not found")
        print("💡 Set environment variables:")
        print("   export POSTGRESQL_HOST=localhost")
        print("   export POSTGRESQL_PORT=5432")
        print("   export POSTGRESQL_DATABASE=agent_memory")
        print("   export POSTGRESQL_USER=postgres")
        print("   export POSTGRESQL_PASSWORD=your_password")
        print("   OR use connection string:")
        print("   export POSTGRESQL_CONNECTION_STRING=postgresql://user:pass@host:port/db")
        return False
    
    return True


def demo_postgresql_memory():
    """Demo PostgreSQL memory operations"""
    print("\n🚀 PostgreSQL Memory Demo")
    print("=" * 50)
    
    if not check_postgresql_config():
        return
    
    print("\n📦 Initializing PostgreSQL Memory Manager...")
    
    try:
        # Initialize memory manager with PostgreSQL
        memory_manager = MemoryManager(store_type="postgresql")
        print("✅ PostgreSQL Memory Manager initialized")
        
        # Demo 1: Adding Memories
        print("\n📝 Demo 1: Adding Memories")
        print("-" * 30)
        
        # Sample memories
        memories_data = [
            {
                "content": "User asked about PostgreSQL integration and database performance",
                "memory_type": MemoryType.EPISODIC,
                "agent_id": "demo_agent",
                "importance": 8.5,
                "tags": ["postgresql", "database", "performance"]
            },
            {
                "content": "User is interested in full-text search capabilities for memory retrieval",
                "memory_type": MemoryType.EPISODIC,
                "agent_id": "demo_agent",
                "importance": 9.0,
                "tags": ["search", "full-text", "retrieval"]
            },
            {
                "content": "PostgreSQL provides excellent performance for complex queries and large datasets",
                "memory_type": MemoryType.SEMANTIC,
                "agent_id": "demo_agent",
                "importance": 7.5,
                "tags": ["postgresql", "performance", "scalability"]
            },
            {
                "content": "Full-text search in PostgreSQL uses tsvector and tsquery for efficient text matching",
                "memory_type": MemoryType.SEMANTIC,
                "agent_id": "demo_agent",
                "importance": 8.0,
                "tags": ["postgresql", "full-text", "tsvector"]
            },
            {
                "content": "JSONB data type in PostgreSQL allows flexible storage of metadata and tags",
                "memory_type": MemoryType.SEMANTIC,
                "agent_id": "demo_agent",
                "importance": 7.0,
                "tags": ["postgresql", "jsonb", "metadata"]
            }
        ]
        
        # Add memories
        for i, memory_data in enumerate(memories_data, 1):
            memory = memory_manager.add_memory(**memory_data)
            print(f"   {i}. Added {memory_data['memory_type'].value} memory: {memory_data['content'][:50]}...")
        
        # Demo 2: Full-Text Search
        print("\n🔍 Demo 2: Full-Text Search")
        print("-" * 30)
        
        search_queries = [
            "PostgreSQL performance",
            "full-text search",
            "database queries",
            "JSONB metadata"
        ]
        
        for query in search_queries:
            print(f"\n   Query: '{query}'")
            start_time = time.time()
            results = memory_manager.search_memory(query, limit=5)
            search_time = (time.time() - start_time) * 1000
            
            print(f"   Results ({len(results)} found, {search_time:.2f}ms):")
            for i, result in enumerate(results, 1):
                print(f"     {i}. {result.content[:60]}...")
        
        # Demo 3: Filtered Search
        print("\n🎯 Demo 3: Filtered Search")
        print("-" * 30)
        
        print("   Searching only episodic memories:")
        episodic_results = memory_manager.search_memory(
            query="", 
            memory_type=MemoryType.EPISODIC,
            limit=10
        )
        print(f"   Found {len(episodic_results)} episodic memories")
        
        print("\n   Searching only semantic memories:")
        semantic_results = memory_manager.search_memory(
            query="", 
            memory_type=MemoryType.SEMANTIC,
            limit=10
        )
        print(f"   Found {len(semantic_results)} semantic memories")
        
        # Demo 4: Timeline
        print("\n⏰ Demo 4: Timeline")
        print("-" * 30)
        
        timeline = memory_manager.get_timeline(agent_id="demo_agent", limit=10)
        print(f"   Timeline: {len(timeline)} memories in chronological order")
        for i, memory in enumerate(timeline, 1):
            print(f"     {i}. [{memory.timestamp.strftime('%H:%M:%S')}] {memory.content[:50]}...")
        
        # Demo 5: Performance Test
        print("\n⚡ Demo 5: Performance Test")
        print("-" * 30)
        
        # Test search performance
        search_times = []
        for _ in range(10):
            start_time = time.time()
            memory_manager.search_memory("postgresql", limit=5)
            search_time = (time.time() - start_time) * 1000
            search_times.append(search_time)
        
        avg_search_time = sum(search_times) / len(search_times)
        print(f"   Average search time: {avg_search_time:.2f}ms")
        print(f"   Fastest search: {min(search_times):.2f}ms")
        print(f"   Slowest search: {max(search_times):.2f}ms")
        
        print("\n✅ PostgreSQL demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("\n💡 Make sure you have:")
        print("   1. PostgreSQL server running")
        print("   2. Correct connection credentials")
        print("   3. Installed psycopg2-binary: pip install psycopg2-binary")
        print("   4. Created the database: createdb agent_memory")


def main():
    """Main demo function"""
    demo_postgresql_memory()


if __name__ == "__main__":
    main() 