"""
Provides vector-based storage using Pinecone for semantic search capabilities.
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

try:
    # The official package is now 'pinecone', not 'pinecone-client'
    from pinecone import Pinecone, ServerlessSpec, Index
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("Warning: Pinecone not installed. Install with: pip install pinecone>=7.0.0") # Updated install command

import sys
print("Installed packages:", sys.modules.keys())
print("Pinecone module location:", sys.modules.get("pinecone"))


from ..models import MemoryEntry, MemoryType
from ..utils.embedding_utils import generate_embedding
from .base_store import BaseStore


class PineconeStore(BaseStore):
    """Pinecone-based vector storage backend for memory entries"""

    def __init__(self, api_key: str = None, environment: str = None,
                 index_name: str = "agent-memory-os", dimension: int = 1024,
                 metric: str = "cosine", **kwargs):
        """
        Initialize Pinecone store

        Args:
            api_key: Pinecone API key (defaults to PINECONE_API_KEY env var)
            environment: Pinecone environment (defaults to PINECONE_ENVIRONMENT env var)
                         Note: Environment might be less critical for serverless indexes
                         but still good practice for initial client setup.
            index_name: Name of the Pinecone index
            dimension: Vector dimension (default 1024, e.g., for llama-text-embed-v2)
            metric: Distance metric ('cosine', 'euclidean', 'dotproduct')
            **kwargs: Additional configuration (currently not directly used but kept for flexibility)
        """
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone client not installed. Install with: pip install pinecone>=7.0.0")

        # Get credentials from parameters or environment variables
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.environment = environment or os.getenv("PINECONE_ENVIRONMENT") # Retained for older/pod-based usage if needed

        if not self.api_key:
            raise ValueError("Pinecone API key is required. Set PINECONE_API_KEY environment variable or pass api_key parameter.")

        # For Serverless indexes, the 'environment' is largely handled by Pinecone internally
        # based on your API key and index region. However, keeping it for compatibility
        # or if using pod-based indexes where it's explicitly part of the connection.
        # If you exclusively use serverless, the `environment` passed to `Pinecone()`
        # might not be strictly necessary, but it doesn't hurt.

        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric

        # Initialize Pinecone client using the modern pattern
        self.pc = Pinecone(api_key=self.api_key, environment=self.environment)

        # Ensure index exists
        self._ensure_index_exists()

        # Get index instance directly
        self.index: Index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        try:
            # Check if index exists using the modern pattern
            existing_indexes = self.pc.list_indexes()
            existing_index_names = [idx.name for idx in existing_indexes]

            if self.index_name not in existing_index_names:
                print(f"Creating Pinecone index: {self.index_name}")

                # Create index with serverless spec for easier management
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(
                        cloud="aws", # Example: "aws", "gcp", "azure"
                        region="us-east-1" # Example: "us-east-1", "us-west-2", "eu-west-1"
                    )
                )

                # Wait for index to be ready
                print("Waiting for index to be ready...")
                self.pc.wait_for_ready(self.index_name)
                print(f"Pinecone index {self.index_name} is ready.")

            else:
                print(f"Using existing Pinecone index: {self.index_name}")

        except Exception as e:
            print(f"Error ensuring Pinecone index exists: {e}")
            raise

    def _memory_to_vector(self, memory: MemoryEntry) -> Dict[str, Any]:
        """Convert MemoryEntry to Pinecone vector format"""
        # Generate embedding if not present or if it's not a list of floats
        if not memory.embedding or not (isinstance(memory.embedding, list) and
                                        all(isinstance(x, (int, float)) for x in memory.embedding)):
            # Handle potential byte strings from database storage if not properly deserialized
            if isinstance(memory.embedding, bytes):
                try:
                    decoded_embedding = json.loads(memory.embedding.decode('utf-8'))
                    if isinstance(decoded_embedding, list) and all(isinstance(x, (int, float)) for x in decoded_embedding):
                        memory.embedding = decoded_embedding
                    else:
                        print(f"Warning: Decoded embedding from bytes is not a list of numbers. Re-generating for memory ID: {memory.id}")
                        memory.embedding = generate_embedding(memory.content)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    print(f"Warning: Failed to decode embedding from bytes. Re-generating for memory ID: {memory.id}")
                    memory.embedding = generate_embedding(memory.content)
            else:
                print(f"Warning: Memory embedding is not a list of numbers or is missing. Re-generating for memory ID: {memory.id}")
                memory.embedding = generate_embedding(memory.content)
        
        # Ensure embedding has the correct dimension
        if len(memory.embedding) != self.dimension:
            print(f"Warning: Embedding dimension mismatch for memory ID {memory.id}. Expected {self.dimension}, got {len(memory.embedding)}. Re-generating embedding.")
            memory.embedding = generate_embedding(memory.content)


        # Prepare metadata
        metadata = {
            "content": memory.content,
            "memory_type": memory.memory_type.value,
            # Pinecone metadata values should be strings, numbers, or booleans.
            # Convert None to empty string for filterability in Pinecone.
            "agent_id": memory.agent_id if memory.agent_id is not None else "",
            "session_id": memory.session_id if memory.session_id is not None else "",
            "timestamp": memory.timestamp.isoformat(),
            "importance": memory.importance,
            "tags": json.dumps(memory.tags), # Store tags as JSON string
            "last_accessed": memory.last_accessed.isoformat() if memory.last_accessed else ""
        }
        # Add any additional metadata from the MemoryEntry's metadata field
        if memory.metadata:
            for key, value in memory.metadata.items():
                if key not in metadata: # Avoid overwriting core fields
                    # Pinecone metadata must be JSON serializable primitive types (str, int, float, bool)
                    if not isinstance(value, (str, int, float, bool)):
                        # Attempt to JSON serialize complex objects or convert to string
                        try:
                            metadata[key] = json.dumps(value)
                        except TypeError:
                            metadata[key] = str(value)
                    else:
                        metadata[key] = value

        return {
            "id": memory.id,
            "values": memory.embedding,
            "metadata": metadata
        }

    def _vector_to_memory(self, vector_data: Dict[str, Any]) -> MemoryEntry:
        """Convert Pinecone vector data to MemoryEntry"""
        metadata = vector_data.get("metadata", {})

        # Extract core fields and remove from metadata dictionary
        content = metadata.pop("content", "")
        memory_type_str = metadata.pop("memory_type", "episodic")
        agent_id = metadata.pop("agent_id", None)
        session_id = metadata.pop("session_id", None)
        timestamp_str = metadata.pop("timestamp", "")
        importance = metadata.pop("importance", 5)
        tags_json = metadata.pop("tags", "[]") # Default to empty JSON array string
        last_accessed_str = metadata.pop("last_accessed", None)

        # Parse tags from JSON string
        try:
            tags = json.loads(tags_json) if tags_json else []
        except json.JSONDecodeError:
            print(f"Warning: Could not decode tags JSON: {tags_json}. Defaulting to empty list.")
            tags = []

        # Parse timestamps from ISO format string
        try:
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
        except ValueError:
            print(f"Warning: Could not parse timestamp: {timestamp_str}. Defaulting to current time.")
            timestamp = datetime.now()

        try:
            last_accessed = datetime.fromisoformat(last_accessed_str) if last_accessed_str else None
        except ValueError:
            print(f"Warning: Could not parse last_accessed timestamp: {last_accessed_str}. Defaulting to None.")
            last_accessed = None

        # Convert empty strings from Pinecone metadata back to None for agent_id and session_id
        if agent_id == "":
            agent_id = None
        if session_id == "":
            session_id = None
        if last_accessed_str == "":
            last_accessed = None

        return MemoryEntry(
            id=vector_data["id"],
            content=content,
            memory_type=MemoryType(memory_type_str),
            agent_id=agent_id,
            session_id=session_id,
            timestamp=timestamp,
            metadata=metadata,  # Remaining items in metadata are custom metadata
            embedding=vector_data.get("values"), # 'values' might not always be returned in current SDK for all ops
            importance=importance,
            tags=tags,
            last_accessed=last_accessed
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
            # Convert memory to vector format
            vector_data = self._memory_to_vector(memory)

            # Upsert to Pinecone. Pinecone's upsert handles both inserts and updates based on ID.
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
            # Fetch from Pinecone
            response = self.index.fetch(ids=[memory_id])

            if memory_id in response.vectors:
                vector_obj = response.vectors[memory_id]
                vector_data = {
                    "id": memory_id,
                    "values": vector_obj.values,
                    "metadata": vector_obj.metadata
                }
                return self._vector_to_memory(vector_data)

            return None
        except Exception as e:
            print(f"Error retrieving memory from Pinecone: {e}")
            return None

    def search_memories(self, query: str = None, memory_type: Optional[MemoryType] = None,
                       agent_id: Optional[str] = None, session_id: Optional[str] = None,
                       limit: int = 50) -> List[MemoryEntry]:
        """
        Search for memories using vector similarity and metadata filters

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
            # Build metadata filter
            filter_dict = {}

            if memory_type:
                filter_dict["memory_type"] = memory_type.value

            if agent_id:
                filter_dict["agent_id"] = agent_id

            if session_id:
                filter_dict["session_id"] = session_id

            # Generate embedding for the query
            query_vector = None
            if query:
                query_vector = generate_embedding(query)
            else:
                # Pinecone's query requires a vector. If no specific query, use a generic one.
                # This allows metadata filtering to still function.
                # For a true "get all" or "get recent N" with filters,
                # you might need a different strategy depending on index size and filtering needs.
                query_vector = generate_embedding("default query for all memories") # A generic vector

            # Search in Pinecone
            response = self.index.query(
                vector=query_vector,
                filter=filter_dict if filter_dict else None,
                top_k=limit,
                include_metadata=True,
                include_values=True # Ensure values (embeddings) are returned for _vector_to_memory
            )

            # Convert results to MemoryEntry objects
            memories = []
            for match in response.matches:
                # The match object directly contains id, values, and metadata
                vector_data = {
                    "id": match.id,
                    "values": match.values,
                    "metadata": match.metadata
                }

                memory = self._vector_to_memory(vector_data)

                # Add similarity score if available
                if hasattr(match, 'score'):
                    memory.metadata['similarity_score'] = match.score

                memories.append(memory)

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
            # Build metadata filter
            filter_dict = {}

            if agent_id:
                filter_dict["agent_id"] = agent_id

            # Pinecone supports range filtering on string fields (like ISO 8601 timestamps)
            timestamp_filter = {}
            if start_time:
                timestamp_filter["$gte"] = start_time.isoformat()
            if end_time:
                timestamp_filter["$lte"] = end_time.isoformat()

            if timestamp_filter:
                filter_dict["timestamp"] = timestamp_filter

            # Use a dummy query to retrieve relevant vectors for timeline (as query is required)
            query_embedding = generate_embedding("timeline query for chronological memory retrieval")

            # Fetch more results than 'limit' to allow for sorting and slicing
            # Pinecone's `top_k` has a maximum of 1000. If more than 1000 memories are needed
            # for a timeline within a specific filter, consider more advanced pagination
            # or cursor-based approaches if your data scale demands it.
            fetch_limit = min(limit * 2, 1000)

            response = self.index.query(
                vector=query_embedding,
                filter=filter_dict if filter_dict else None,
                top_k=fetch_limit,
                include_metadata=True,
                include_values=True # Ensure values (embeddings) are returned
            )

            # Convert to MemoryEntry objects
            memories = []
            for match in response.matches:
                vector_data = {
                    "id": match.id,
                    "values": match.values,
                    "metadata": match.metadata
                }
                memory = self._vector_to_memory(vector_data)
                memories.append(memory)

            # Sort by timestamp (newest first, typical for a timeline)
            memories.sort(key=lambda x: x.timestamp, reverse=True)

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
            # Delete from Pinecone
            self.index.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"Error deleting memory from Pinecone: {e}")
            return False

    def get_all_memories(self, limit: int = 1000) -> List[MemoryEntry]:
        """
        Get all memories in the system (up to the Pinecone top_k limit).
        Note: Retrieving truly "all" memories from a large Pinecone index can be inefficient
        and might require pagination using `list_ids` and then `fetch` in batches,
        or more complex scan operations not directly exposed by a single `query`.
        This implementation uses a generic query and might not return truly "all" memories
        if the index is very large and the generic query doesn't cover all vector space.

        Args:
            limit: Maximum number of memories to retrieve (Pinecone's top_k limit applies, max 1000).

        Returns:
            List of all MemoryEntry objects (up to the limit).
        """
        try:
            # Use a generic query to get a broad set of vectors.
            # This is not a scan; it's still a similarity search with a generic vector.
            query_embedding = generate_embedding("retrieve all memories from the store")

            # Pinecone's query top_k has a maximum of 1000.
            response = self.index.query(
                vector=query_embedding,
                top_k=min(limit, 1000), # Cap at Pinecone's max top_k
                include_metadata=True,
                include_values=True
            )

            memories = []
            for match in response.matches:
                vector_data = {
                    "id": match.id,
                    "values": match.values,
                    "metadata": match.metadata
                }
                memory = self._vector_to_memory(vector_data)
                memories.append(memory)

            return memories
        except Exception as e:
            print(f"Error getting all memories from Pinecone: {e}")
            return []

    def delete_index(self):
        """Delete the entire Pinecone index (use with caution!)"""
        try:
            self.pc.delete_index(self.index_name)
            print(f"Deleted Pinecone index: {self.index_name}")
        except Exception as e:
            print(f"Error deleting Pinecone index: {e}")

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index"""
        try:
            stats = self.index.describe_index_stats()
            # The structure of stats.namespaces can be complex,
            # so we'll simplify for typical use cases.
            namespace_counts = {}
            if hasattr(stats, 'namespaces') and stats.namespaces:
                for ns_name, ns_data in stats.namespaces.items():
                    namespace_counts[ns_name] = ns_data.vector_count

            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": namespace_counts # Simplified representation
            }
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {}

    def get_index_host(self) -> Optional[str]:
        """Get the host URL for the Pinecone index (useful for performance optimization)"""
        try:
            # `describe_index` now returns an `IndexModel` which has a `.host` attribute.
            index_description = self.pc.describe_index(self.index_name)
            return getattr(index_description, 'host', None)
        except Exception as e:
            print(f"Error getting index host: {e}")
            return None

    def save_memories_batch(self, memories: List[MemoryEntry], batch_size: int = 100) -> bool:
        """
        Save multiple memory entries to Pinecone in batches

        Args:
            memories: List of MemoryEntry objects to save
            batch_size: Number of memories to process in each batch

        Returns:
            True if successful, False otherwise
        """
        if not memories:
            return True # Nothing to save

        try:
            total_memories = len(memories)
            for i in range(0, total_memories, batch_size):
                batch = memories[i:i + batch_size]
                vectors = [self._memory_to_vector(memory) for memory in batch]

                # Upsert batch to Pinecone
                self.index.upsert(vectors=vectors)

                # Print progress
                current_batch_num = (i // batch_size) + 1
                total_batches = (total_memories + batch_size - 1) // batch_size
                print(f"Saved batch {current_batch_num}/{total_batches} ({len(batch)} memories)")

            return True
        except Exception as e:
            print(f"Error saving memories batch to Pinecone: {e}")
            return False