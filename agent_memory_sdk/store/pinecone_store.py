"""
Pinecone vector store backend for Agent Memory OS

Provides semantic search capabilities using Pinecone's vector database.
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("Warning: Pinecone not installed. Install with: pip install pinecone-client")

from ..models import MemoryEntry, MemoryType
from ..utils.embedding_utils import generate_embedding
from .base_store import BaseStore


class PineconeStore(BaseStore):
    """Pinecone-based vector storage backend for memory entries"""
    
    def __init__(self, api_key: str = None, environment: str = None, index_name: str = "agent-memory-os"):
        """
        Initialize Pinecone store
        
        Args:
            api_key: Pinecone API key (defaults to PINECONE_API_KEY env var)
            environment: Pinecone environment (defaults to PINECONE_ENVIRONMENT env var)
            index_name: Name of the Pinecone index
        """
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone client not installed. Install with: pip install pinecone-client")
        
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.environment = environment or os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = index_name
        
        if not self.api_key:
            raise ValueError("Pinecone API key is required. Set PINECONE_API_KEY environment variable or pass api_key parameter.")
        
        if not self.environment:
            raise ValueError("Pinecone environment is required. Set PINECONE_ENVIRONMENT environment variable or pass environment parameter.")
        
        # Initialize Pinecone with new API
        self.pc = pinecone.Pinecone(api_key=self.api_key)
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        
        # Get index
        self.index = self.pc.Index(self.index_name)
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        if self.index_name not in self.pc.list_indexes().names():
            print(f"Creating Pinecone index: {self.index_name}")
            try:
                # Try the newer model-based approach first
                try:
                    self.pc.create_index_for_model(
                        name=self.index_name,
                        cloud="aws",
                        region="us-east-1",
                        embed={
                            "model": "llama-text-embed-v2",
                            "field_map": {"text": "content"}
                        }
                    )
                    print("✅ Created index with llama-text-embed-v2 model")
                except Exception as model_error:
                    print(f"⚠️  Model-based index creation failed: {model_error}")
                    print("🔄 Falling back to manual dimension specification...")
                    
                    # Extract region from environment
                    region = self._extract_region_from_environment()
                    
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=1536,  # OpenAI embedding dimension
                        metric="cosine",
                        spec=pinecone.ServerlessSpec(
                            cloud="gcp",
                            region=region
                        )
                    )
                    print("✅ Created index with manual dimension specification")
                
                # Wait for index to be ready
                import time
                time.sleep(10)
            except Exception as e:
                if "free plan does not support" in str(e):
                    print(f"❌ Free plan region restriction: {e}")
                    print("💡 Try upgrading your Pinecone plan or use a different region")
                    print("   Supported free plan regions: us-east1, us-west1")
                    print(f"   Your current environment: {self.environment}")
                    print(f"   Attempted region: {self._extract_region_from_environment()}")
                    raise
                elif "NOT_FOUND" in str(e) and "region" in str(e):
                    print(f"❌ Region not found: {e}")
                    print(f"💡 Your environment '{self.environment}' maps to region '{self._extract_region_from_environment()}'")
                    print("   Try using a different environment or check your Pinecone account settings")
                    raise
                else:
                    raise
    
    def _extract_region_from_environment(self) -> str:
        """Extract region from Pinecone environment string"""
        # Common environment to region mappings
        env_to_region = {
            "gcp-starter": "us-east1",
            "gcp-west1-gcp": "us-west1",
            "us-east1-gcp": "us-east1",
            "us-west1-gcp": "us-west1",
            "us-central1-gcp": "us-central1",
            "eu-west1-gcp": "eu-west1",
            "ap-southeast1-gcp": "ap-southeast1"
        }
        
        # Try to map environment to region
        if self.environment in env_to_region:
            return env_to_region[self.environment]
        
        # If no mapping found, try to extract region from environment string
        if "west" in self.environment.lower():
            return "us-west1"
        elif "central" in self.environment.lower():
            return "us-central1"
        elif "east" in self.environment.lower():
            return "us-east1"
        else:
            # Default to us-east1 for free tier
            print(f"⚠️  Could not determine region from environment '{self.environment}', using us-east1")
            return "us-east1"
    
    def _memory_to_vector(self, memory: MemoryEntry) -> Dict[str, Any]:
        """Convert MemoryEntry to Pinecone vector format"""
        # Generate embedding if not present
        if not memory.embedding:
            try:
                memory.embedding = generate_embedding(memory.content)
            except Exception as e:
                print(f"Warning: Could not generate embedding: {e}")
                return None
        
        # Create metadata
        metadata = {
            "content": memory.content,
            "memory_type": memory.memory_type.value,
            "agent_id": memory.agent_id or "",
            "session_id": memory.session_id or "",
            "timestamp": memory.timestamp.isoformat(),
            "importance": memory.importance,
            "tags": json.dumps(memory.tags),
            "last_accessed": memory.last_accessed.isoformat() if memory.last_accessed else "",
            "metadata": json.dumps(memory.metadata)
        }
        
        return {
            "id": memory.id,
            "values": memory.embedding,
            "metadata": metadata
        }
    
    def _vector_to_memory(self, vector_data: Dict[str, Any]) -> MemoryEntry:
        """Convert Pinecone vector data to MemoryEntry"""
        metadata = vector_data["metadata"]
        
        return MemoryEntry(
            id=vector_data["id"],
            content=metadata["content"],
            memory_type=MemoryType(metadata["memory_type"]),
            agent_id=metadata["agent_id"] if metadata["agent_id"] else None,
            session_id=metadata["session_id"] if metadata["session_id"] else None,
            timestamp=datetime.fromisoformat(metadata["timestamp"]),
            metadata=json.loads(metadata["metadata"]) if metadata["metadata"] else {},
            embedding=vector_data["values"],
            importance=float(metadata["importance"]),
            tags=json.loads(metadata["tags"]) if metadata["tags"] else [],
            last_accessed=datetime.fromisoformat(metadata["last_accessed"]) if metadata["last_accessed"] else None
        )
    
    def save_memory(self, memory: MemoryEntry) -> bool:
        """
        Save a memory entry to Pinecone
        
        Args:
            memory: MemoryEntry to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try model-based upsert first (text-based)
            try:
                # For model-based indexes, we need to use the correct format
                print(f"🔍 Upserting memory with ID: {memory.id}")
                print(f"   Embedding length: {len(memory.embedding) if memory.embedding else 'None'}")
                
                self.index.upsert(
                    vectors=[{
                        "id": memory.id,
                        "values": memory.embedding,  # Use the embedding values
                        "metadata": {
                            "content": memory.content,  # Store the original content
                            "memory_type": memory.memory_type.value,
                            "agent_id": memory.agent_id or "",
                            "session_id": memory.session_id or "",
                            "timestamp": memory.timestamp.isoformat(),
                            "importance": memory.importance,
                            "tags": json.dumps(memory.tags),
                            "last_accessed": memory.last_accessed.isoformat() if memory.last_accessed else "",
                            "metadata": json.dumps(memory.metadata)
                        }
                    }]
                )
                print(f"✅ Memory upserted successfully")
                return True
            except Exception as model_error:
                print(f"⚠️  Model-based upsert failed, falling back to vector upsert: {model_error}")
                
                # Fall back to vector-based approach
                vector_data = self._memory_to_vector(memory)
                if not vector_data:
                    return False
                
                self.index.upsert(vectors=[vector_data])
                return True
        except Exception as e:
            print(f"Error saving memory to Pinecone: {e}")
            return False
    
    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            MemoryEntry if found, None otherwise
        """
        try:
            response = self.index.fetch(ids=[memory_id])
            # Handle the new Pinecone API response format
            if hasattr(response, 'vectors') and memory_id in response.vectors:
                vector_data = response.vectors[memory_id]
                return self._vector_to_memory(vector_data)
            elif isinstance(response, dict) and memory_id in response.get("vectors", {}):
                vector_data = response["vectors"][memory_id]
                return self._vector_to_memory(vector_data)
            return None
        except Exception as e:
            print(f"Error retrieving memory from Pinecone: {e}")
            return None
    
    def search_memories(self, query: str = None, memory_type: Optional[MemoryType] = None,
                       agent_id: Optional[str] = None, session_id: Optional[str] = None,
                       limit: int = 50) -> List[MemoryEntry]:
        """
        Search for memories with semantic search and filters
        
        Args:
            query: Text search in content (semantic search)
            memory_type: Filter by memory type
            agent_id: Filter by agent ID
            session_id: Filter by session ID
            limit: Maximum number of results
            
        Returns:
            List of matching MemoryEntry objects
        """
        try:
            # Build filter
            filter_dict = {}
            if memory_type:
                filter_dict["memory_type"] = memory_type.value
            if agent_id:
                filter_dict["agent_id"] = agent_id
            if session_id:
                filter_dict["session_id"] = session_id
            
            if query:
                # Use vector search with generated embedding
                query_embedding = generate_embedding(query)
                response = self.index.query(
                    vector=query_embedding,
                    filter=filter_dict,
                    top_k=limit,
                    include_metadata=True
                )
            else:
                # Get all vectors with filter - try a simple approach
                try:
                    # Try using a simple query to get all memories
                    response = self.index.query(
                        vector=[0] * 1024,  # Dummy vector for metadata-only query (1024 for llama-text-embed-v2)
                        filter=filter_dict,
                        top_k=limit,
                        include_metadata=True
                    )
                except Exception as dummy_error:
                    print(f"⚠️  Dummy vector query failed: {dummy_error}")
                    # Try without any vector (just metadata query)
                    try:
                        response = self.index.query(
                            filter=filter_dict,
                            top_k=limit,
                            include_metadata=True
                        )
                    except Exception as no_vector_error:
                        print(f"⚠️  No-vector query failed: {no_vector_error}")
                        # Last resort: try with a real embedding
                        dummy_embedding = generate_embedding("test")
                        response = self.index.query(
                            vector=dummy_embedding,
                            filter=filter_dict,
                            top_k=limit,
                            include_metadata=True
                        )
            
            # Handle the new Pinecone API response format
            if hasattr(response, 'matches'):
                matches = response.matches
            elif isinstance(response, dict):
                matches = response.get('matches', [])
            else:
                matches = []
            
            print(f"🔍 Search response: {len(matches)} matches found")
            memories = []
            for i, match in enumerate(matches):
                # Handle different match formats
                if hasattr(match, 'id'):
                    match_id = match.id
                    match_values = getattr(match, 'values', None)
                    match_metadata = getattr(match, 'metadata', {})
                elif isinstance(match, dict):
                    match_id = match.get("id")
                    match_values = match.get("values")
                    match_metadata = match.get("metadata", {})
                else:
                    print(f"⚠️  Unknown match format: {type(match)}")
                    continue
                
                print(f"🔍 Processing match {i+1}: {match_id}")
                print(f"   Metadata keys: {list(match_metadata.keys()) if match_metadata else 'None'}")
                
                vector_data = {
                    "id": match_id,
                    "values": match_values,
                    "metadata": match_metadata
                }
                try:
                    memory = self._vector_to_memory(vector_data)
                    memories.append(memory)
                    print(f"✅ Successfully converted match {i+1}")
                except Exception as conv_error:
                    print(f"❌ Error converting match {i+1}: {conv_error}")
                    print(f"   Metadata: {match_metadata}")
            
            print(f"✅ Converted {len(memories)} memories from search results")
            return memories
        except Exception as e:
            print(f"Error searching memories in Pinecone: {e}")
            return []
    
    def get_timeline(self, agent_id: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    limit: int = 100) -> List[MemoryEntry]:
        """
        Get chronological timeline of memories
        
        Args:
            agent_id: Filter by agent ID
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of results
            
        Returns:
            List of MemoryEntry objects in chronological order
        """
        try:
            # Build filter
            filter_dict = {}
            if agent_id:
                filter_dict["agent_id"] = agent_id
            
            # Get all memories with filter
            response = self.index.query(
                vector=[0] * 1024,  # Dummy vector for metadata-only query (1024 for llama-text-embed-v2)
                filter=filter_dict,
                top_k=1000,  # Get more to filter by time
                include_metadata=True
            )
            
            # Handle the new Pinecone API response format
            if hasattr(response, 'matches'):
                matches = response.matches
            elif isinstance(response, dict):
                matches = response.get('matches', [])
            else:
                matches = []
            
            memories = []
            for match in matches:
                # Handle different match formats
                if hasattr(match, 'id'):
                    match_id = match.id
                    match_values = getattr(match, 'values', None)
                    match_metadata = getattr(match, 'metadata', {})
                elif isinstance(match, dict):
                    match_id = match.get("id")
                    match_values = match.get("values")
                    match_metadata = match.get("metadata", {})
                else:
                    continue
                
                vector_data = {
                    "id": match_id,
                    "values": match_values,
                    "metadata": match_metadata
                }
                memory = self._vector_to_memory(vector_data)
                
                # Apply time filters
                if start_time and memory.timestamp < start_time:
                    continue
                if end_time and memory.timestamp > end_time:
                    continue
                
                memories.append(memory)
            
            # Sort by timestamp and limit
            memories.sort(key=lambda x: x.timestamp)
            return memories[:limit]
        except Exception as e:
            print(f"Error getting timeline from Pinecone: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.index.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"Error deleting memory from Pinecone: {e}")
            return False
    
    def get_all_memories(self, limit: int = 10000) -> List[MemoryEntry]:
        """
        Get all memories in the system
        
        Args:
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of all MemoryEntry objects
        """
        return self.search_memories(limit=limit) 