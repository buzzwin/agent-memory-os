#!/usr/bin/env python3
"""
Debug script for Pinecone configuration
"""

import os
import sys

def debug_pinecone_config():
    """Debug Pinecone configuration"""
    print("🔍 Pinecone Configuration Debug")
    print("=" * 50)
    
    # Check environment variables
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    
    print(f"API Key: {'✅ Set' if api_key else '❌ Not set'}")
    if api_key:
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
    
    print(f"Environment: {'✅ Set' if environment else '❌ Not set'}")
    if environment:
        print(f"   Environment: {environment}")
    
    # Try to import pinecone
    try:
        import pinecone
        print("✅  installed")
    except ImportError:
        print("❌ Pinecone client not installed")
        print("   Install with: pip install pinecone>=7.0.0")
        return
    
    # Try to initialize Pinecone
    try:
        pc = pinecone.Pinecone(api_key=api_key)
        print("✅ Pinecone client initialized")
        
        # List existing indexes
        indexes = pc.list_indexes()
        print(f"📋 Existing indexes: {list(indexes.names())}")
        
        # Test environment mapping
        env_to_region = {
            "gcp-starter": "us-east1",
            "gcp-west1-gcp": "us-west1",
            "us-east1-gcp": "us-east1",
            "us-west1-gcp": "us-west1",
            "us-central1-gcp": "us-central1",
            "eu-west1-gcp": "eu-west1",
            "ap-southeast1-gcp": "ap-southeast1"
        }
        
        if environment in env_to_region:
            region = env_to_region[environment]
            print(f"🗺️  Environment '{environment}' maps to region '{region}'")
        else:
            print(f"⚠️  Unknown environment '{environment}'")
            
    except Exception as e:
        print(f"❌ Error initializing Pinecone: {e}")
    
    print("\n💡 Recommendations:")
    print("1. For free tier, try: export PINECONE_ENVIRONMENT=gcp-starter")
    print("2. Check your Pinecone dashboard for supported regions")
    print("3. Consider upgrading to a paid plan for more region options")

if __name__ == "__main__":
    debug_pinecone_config() 