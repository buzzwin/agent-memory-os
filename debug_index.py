#!/usr/bin/env python3
"""
Debug script to check Pinecone index status
"""

import os
import pinecone
import time

def debug_index():
    """Debug Pinecone index status"""
    print("🔍 Pinecone Index Debug")
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
    
    # Check specific index
    index_name = "debug-test"
    if index_name in indexes.names():
        print(f"\n🔍 Checking index: {index_name}")
        
        # Get index stats
        try:
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print(f"✅ Index stats: {stats}")
        except Exception as e:
            print(f"❌ Error getting index stats: {e}")
        
        # Try to fetch any vectors
        try:
            # Try to get all vectors (this might not work with empty index)
            response = index.query(
                vector=[0] * 1024,
                top_k=10,
                include_metadata=True
            )
            print(f"✅ Query response: {len(response.get('matches', []))} matches")
        except Exception as e:
            print(f"❌ Error querying index: {e}")
    else:
        print(f"❌ Index {index_name} not found")

if __name__ == "__main__":
    debug_index() 