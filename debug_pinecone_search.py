#!/usr/bin/env python3
"""
Debug script for Pinecone search functionality
"""

import os
from agent_memory_sdk import MemoryManager, MemoryType

def debug_pinecone_search():
    """Debug Pinecone search functionality"""
    print("🔍 Pinecone Search Debug")
    print("=" * 50)
    
    # Initialize memory manager
    memory_manager = MemoryManager(store_type="pinecone", index_name="debug-test")
    
    # Add a test memory
    print("📝 Adding test memory...")
    memory = memory_manager.add_memory(
        content="This is a test memory about artificial intelligence and machine learning",
        memory_type=MemoryType.SEMANTIC,
        agent_id="debug-agent",
        importance=8.0,
        tags=["test", "ai", "ml"]
    )
    print(f"✅ Added memory with ID: {memory.id}")
    print(f"   Content: {memory.content}")
    print(f"   Embedding length: {len(memory.embedding) if memory.embedding else 'None'}")
    
    # Try to retrieve the memory directly
    print("\n🔍 Testing direct memory retrieval...")
    retrieved = memory_manager.get_memory(memory.id)
    if retrieved:
        print(f"✅ Memory retrieved: {retrieved.content}")
    else:
        print("❌ Memory not found")
    
    # Try search
    print("\n🔍 Testing search...")
    results = memory_manager.search_memory("artificial intelligence", limit=5)
    print(f"Search results: {len(results)} found")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result.content[:50]}...")
    
    # Try search without query (get all)
    print("\n🔍 Testing search without query...")
    all_results = memory_manager.search_memory("", limit=10)
    print(f"All memories: {len(all_results)} found")
    for i, result in enumerate(all_results):
        print(f"  {i+1}. {result.content[:50]}...")
    
    # Check store directly
    print("\n🔍 Testing store directly...")
    store_results = memory_manager._store.search_memories(limit=10)
    print(f"Store search results: {len(store_results)} found")
    for i, result in enumerate(store_results):
        print(f"  {i+1}. {result.content[:50]}...")

if __name__ == "__main__":
    debug_pinecone_search() 