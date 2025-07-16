#!/usr/bin/env python3
"""
Cleanup script to delete all existing Pinecone memories
"""

import os
import pinecone
from agent_memory_sdk import MemoryManager, MemoryType

def cleanup_pinecone():
    """Delete all existing Pinecone memories"""
    print("🧹 Pinecone Cleanup")
    print("=" * 50)
    
    # Get environment variables
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    
    if not api_key:
        print("❌ PINECONE_API_KEY not set")
        return
    
    print(f"🔑 Using API key: {api_key[:10]}...{api_key[-4:]}")
    print(f"🌍 Environment: {environment}")
    
    # Initialize Pinecone
    pc = pinecone.Pinecone(api_key=api_key)
    
    # List all indexes
    indexes = pc.list_indexes()
    print(f"📋 Found {len(indexes.names())} indexes: {list(indexes.names())}")
    
    # Delete specific indexes that we created
    indexes_to_delete = [
        "agent-memory-demo",
        "comparison-test", 
        "debug-test",
        "agent-memory-os"
    ]
    
    for index_name in indexes_to_delete:
        if index_name in indexes.names():
            print(f"🗑️  Deleting index: {index_name}")
            try:
                pc.delete_index(index_name)
                print(f"✅ Deleted index: {index_name}")
            except Exception as e:
                print(f"❌ Error deleting index {index_name}: {e}")
        else:
            print(f"ℹ️  Index {index_name} not found, skipping")
    
    print("\n🎉 Cleanup completed!")
    print("💡 You can now run the demo again with a fresh start")

if __name__ == "__main__":
    cleanup_pinecone() 