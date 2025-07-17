#!/usr/bin/env python3
"""
Pinecone Memory Demo

Demonstrates the Pinecone integration for semantic memory storage and search.
Requires PINECONE_API_KEY and PINECONE_ENVIRONMENT environment variables.
"""

import os
import time
from datetime import datetime, timedelta

from agent_memory_sdk import MemoryManager, MemoryType, StoreFactory


def check_pinecone_setup():
    """Check if Pinecone is properly configured"""
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    
    if not api_key:
        print("❌ PINECONE_API_KEY environment variable not set")
        print("   Get your API key from: https://app.pinecone.io/")
        return False
    
    if not environment:
        print("❌ PINECONE_ENVIRONMENT environment variable not set")
        print("   Get your environment from: https://app.pinecone.io/")
        return False
    
    print("✅ Pinecone configuration found")
    print(f"   API Key: {api_key[:8]}...")
    print(f"   Environment: {environment}")
    return True


def demo_pinecone_memory():
    """Demonstrate Pinecone memory functionality"""
    print("\n🚀 Pinecone Memory Demo")
    print("=" * 50)
    
    # Check setup
    if not check_pinecone_setup():
        print("\n💡 To run this demo:")
        print("   1. Sign up at https://app.pinecone.io/")
        print("   2. Create an index")
        print("   3. Set environment variables:")
        print("      export PINECONE_API_KEY='your-api-key'")
        print("      export PINECONE_ENVIRONMENT='your-environment'")
        print("   4. Install pinecone: pip install pinecone>=7.0.0")
        return
    
    try:
        # Initialize memory manager with Pinecone
        print("\n📦 Initializing Pinecone Memory Manager...")
        memory_manager = MemoryManager(store_type="pinecone", index_name="agent-memory-demo")
        print("✅ Pinecone Memory Manager initialized")
        
        # Demo 1: Add different types of memories
        print("\n📝 Demo 1: Adding Memories")
        print("-" * 30)
        
        # Episodic memories
        episodic_memories = [
            "I had a conversation with John about machine learning yesterday",
            "We discussed neural networks and their applications in computer vision",
            "John mentioned that he's working on a new deep learning project",
            "We talked about the challenges of training large language models",
            "John shared his experience with transformer architectures"
        ]
        
        for i, content in enumerate(episodic_memories, 1):
            memory = memory_manager.add_memory(
                content=content,
                memory_type=MemoryType.EPISODIC,
                agent_id="demo-agent",
                session_id="conversation-1",
                importance=7.0,
                tags=["conversation", "john", "ml"]
            )
            print(f"   {i}. Added episodic memory: {content[:50]}...")
        
        # Semantic memories (facts)
        semantic_memories = [
            "Machine learning is a subset of artificial intelligence",
            "Neural networks are inspired by biological brain structures",
            "Deep learning uses multiple layers of neural networks",
            "Transformers revolutionized natural language processing",
            "Computer vision deals with understanding visual information"
        ]
        
        for i, content in enumerate(semantic_memories, 1):
            memory = memory_manager.add_memory(
                content=content,
                memory_type=MemoryType.SEMANTIC,
                agent_id="demo-agent",
                importance=8.0,
                tags=["fact", "ml", "ai"]
            )
            print(f"   {i+5}. Added semantic memory: {content[:50]}...")
        
        # Demo 2: Semantic Search
        print("\n🔍 Demo 2: Semantic Search")
        print("-" * 30)
        
        search_queries = [
            "What did John say about neural networks?",
            "Tell me about machine learning basics",
            "What are transformers used for?",
            "Computer vision applications"
        ]
        
        for query in search_queries:
            print(f"\n   Query: '{query}'")
            results = memory_manager.search_memory(query, limit=3)
            print(f"   Results ({len(results)} found):")
            for i, memory in enumerate(results, 1):
                print(f"     {i}. [{memory.memory_type.value}] {memory.content[:60]}...")
                print(f"        Score: {getattr(memory, 'score', 'N/A')}")
        
        # Demo 3: Filtered Search
        print("\n🎯 Demo 3: Filtered Search")
        print("-" * 30)
        
        # Search only episodic memories
        print("   Searching only episodic memories:")
        episodic_results = memory_manager.search_memory(
            query="neural networks",
            memory_type=MemoryType.EPISODIC,
            limit=5
        )
        for i, memory in enumerate(episodic_results, 1):
            print(f"     {i}. {memory.content[:60]}...")
        
        # Search only semantic memories
        print("\n   Searching only semantic memories:")
        semantic_results = memory_manager.search_memory(
            query="neural networks",
            memory_type=MemoryType.SEMANTIC,
            limit=5
        )
        for i, memory in enumerate(semantic_results, 1):
            print(f"     {i}. {memory.content[:60]}...")
        
        # Demo 4: Timeline
        print("\n⏰ Demo 4: Timeline")
        print("-" * 30)
        
        timeline = memory_manager.get_timeline(agent_id="demo-agent", limit=10)
        print(f"   Timeline ({len(timeline)} memories):")
        for i, memory in enumerate(timeline, 1):
            time_str = memory.timestamp.strftime("%H:%M:%S")
            print(f"     {i}. [{time_str}] {memory.content[:50]}...")
        
        # Demo 5: Memory Statistics
        print("\n📊 Demo 5: Memory Statistics")
        print("-" * 30)
        
        all_memories = memory_manager.get_all_memories()
        episodic_count = len([m for m in all_memories if m.memory_type == MemoryType.EPISODIC])
        semantic_count = len([m for m in all_memories if m.memory_type == MemoryType.SEMANTIC])
        
        print(f"   Total memories: {len(all_memories)}")
        print(f"   Episodic memories: {episodic_count}")
        print(f"   Semantic memories: {semantic_count}")
        
        # Demo 6: Store Factory
        print("\n🏭 Demo 6: Store Factory")
        print("-" * 30)
        
        available_stores = StoreFactory.get_available_stores()
        print(f"   Available stores: {available_stores}")
        
        # Test auto-detection
        print("\n   Testing auto-detection:")
        auto_memory_manager = MemoryManager()  # Should auto-detect Pinecone
        print(f"   Auto-detected store type: {auto_memory_manager.store_type}")
        
        print("\n✅ Pinecone demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Valid Pinecone API key and environment")
        print("   2. Installed pinecone: pip install pinecone>=7.0.0")
        print("   3. Created a Pinecone index")


def demo_store_comparison():
    """Compare SQLite and Pinecone stores"""
    print("\n🔄 Store Comparison Demo")
    print("=" * 50)
    
    if not check_pinecone_setup():
        print("   Skipping comparison (Pinecone not configured)")
        return
    
    try:
        # Test SQLite
        print("\n📦 Testing SQLite Store:")
        sqlite_manager = MemoryManager(store_type="sqlite", db_path="comparison_test.db")
        
        # Add test memory to SQLite
        sqlite_memory = sqlite_manager.add_memory(
            content="This is a test memory in SQLite",
            memory_type=MemoryType.EPISODIC,
            agent_id="test-agent"
        )
        print(f"   Added memory with ID: {sqlite_memory.id}")
        
        # Search in SQLite
        sqlite_results = sqlite_manager.search_memory("test memory")
        print(f"   SQLite search results: {len(sqlite_results)} found")
        
        # Test Pinecone
        print("\n🌲 Testing Pinecone Store:")
        pinecone_manager = MemoryManager(store_type="pinecone", index_name="comparison-test")
        
        # Add test memory to Pinecone
        pinecone_memory = pinecone_manager.add_memory(
            content="This is a test memory in Pinecone",
            memory_type=MemoryType.EPISODIC,
            agent_id="test-agent"
        )
        print(f"   Added memory with ID: {pinecone_memory.id}")
        
        # Search in Pinecone
        pinecone_results = pinecone_manager.search_memory("test memory")
        print(f"   Pinecone search results: {len(pinecone_results)} found")
        
        print("\n✅ Store comparison completed!")
        
    except Exception as e:
        print(f"\n❌ Error during comparison: {e}")


if __name__ == "__main__":
    print("🌲 Pinecone Memory OS Demo")
    print("=" * 50)
    
    # Main demo
    demo_pinecone_memory()
    
    # Store comparison
    demo_store_comparison()
    
    print("\n🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("   - Try different search queries")
    print("   - Experiment with different memory types")
    print("   - Test with your own Pinecone index")
    print("   - Integrate with LangChain or LangGraph") 