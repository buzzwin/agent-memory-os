"""
PostgreSQL store backend for Agent Memory OS

Provides persistent storage using PostgreSQL database with full CRUD operations.
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    print("Warning: PostgreSQL not installed. Install with: pip install psycopg2-binary")

from ..models import MemoryEntry, MemoryType
from ..utils.embedding_utils import generate_embedding
from .base_store import BaseStore


class PostgreSQLStore(BaseStore):
    """PostgreSQL-based storage backend for memory entries"""
    
    def __init__(self, connection_string: str = None, **kwargs):
        """
        Initialize PostgreSQL store
        
        Args:
            connection_string: PostgreSQL connection string
            **kwargs: Additional connection parameters (host, port, database, user, password)
        """
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("PostgreSQL client not installed. Install with: pip install psycopg2-binary")
        
        # Build connection string from kwargs if not provided
        if connection_string:
            self.connection_string = connection_string
        else:
            # Extract connection parameters from kwargs or environment variables
            host = kwargs.get('host') or os.getenv('POSTGRESQL_HOST', 'localhost')
            port = kwargs.get('port') or os.getenv('POSTGRESQL_PORT', '5432')
            database = kwargs.get('database') or os.getenv('POSTGRESQL_DATABASE', 'agent_memory')
            user = kwargs.get('user') or os.getenv('POSTGRESQL_USER', 'postgres')
            password = kwargs.get('password') or os.getenv('POSTGRESQL_PASSWORD', '')
            
            self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        # Initialize database
        self._ensure_table_exists()
    
    def _get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(self.connection_string)
    
    def _ensure_table_exists(self):
        """Create the memories table if it doesn't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS memories (
            id VARCHAR(36) PRIMARY KEY,
            content TEXT NOT NULL,
            memory_type VARCHAR(20) NOT NULL,
            agent_id VARCHAR(255),
            session_id VARCHAR(255),
            timestamp TIMESTAMP NOT NULL,
            importance FLOAT DEFAULT 5.0,
            tags JSONB DEFAULT '[]',
            metadata JSONB DEFAULT '{}',
            embedding JSONB,
            last_accessed TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_memories_agent_id ON memories(agent_id);
        CREATE INDEX IF NOT EXISTS idx_memories_session_id ON memories(session_id);
        CREATE INDEX IF NOT EXISTS idx_memories_memory_type ON memories(memory_type);
        CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);
        CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
        CREATE INDEX IF NOT EXISTS idx_memories_content_gin ON memories USING gin(to_tsvector('english', content));
        """
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                conn.commit()
    
    def save_memory(self, memory: MemoryEntry) -> bool:
        """
        Save a memory entry to PostgreSQL
        
        Args:
            memory: MemoryEntry to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding if not present
            if not memory.embedding:
                memory.embedding = generate_embedding(memory.content)
            
            insert_sql = """
            INSERT INTO memories (
                id, content, memory_type, agent_id, session_id, timestamp,
                importance, tags, metadata, embedding, last_accessed
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                memory_type = EXCLUDED.memory_type,
                agent_id = EXCLUDED.agent_id,
                session_id = EXCLUDED.session_id,
                timestamp = EXCLUDED.timestamp,
                importance = EXCLUDED.importance,
                tags = EXCLUDED.tags,
                metadata = EXCLUDED.metadata,
                embedding = EXCLUDED.embedding,
                last_accessed = EXCLUDED.last_accessed,
                updated_at = CURRENT_TIMESTAMP
            """
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, (
                        memory.id,
                        memory.content,
                        memory.memory_type.value,
                        memory.agent_id,
                        memory.session_id,
                        memory.timestamp,
                        memory.importance,
                        json.dumps(memory.tags),
                        json.dumps(memory.metadata),
                        json.dumps(memory.embedding) if memory.embedding else None,
                        memory.last_accessed
                    ))
                    conn.commit()
            return True
        except Exception as e:
            print(f"Error saving memory to PostgreSQL: {e}")
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
            select_sql = """
            SELECT * FROM memories WHERE id = %s
            """
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(select_sql, (memory_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        return self._row_to_memory(row)
            return None
        except Exception as e:
            print(f"Error retrieving memory from PostgreSQL: {e}")
            return None
    
    def search_memories(self, query: str = None, memory_type: Optional[MemoryType] = None,
                       agent_id: Optional[str] = None, session_id: Optional[str] = None,
                       limit: int = 50) -> List[MemoryEntry]:
        """
        Search for memories with text search and filters
        
        Args:
            query: Text search in content
            memory_type: Filter by memory type
            agent_id: Filter by agent ID
            session_id: Filter by session ID
            limit: Maximum number of results
            
        Returns:
            List of matching MemoryEntry objects
        """
        try:
            # Build WHERE clause
            conditions = []
            params = []
            
            if query:
                conditions.append("to_tsvector('english', content) @@ plainto_tsquery('english', %s)")
                params.append(query)
            
            if memory_type:
                conditions.append("memory_type = %s")
                params.append(memory_type.value)
            
            if agent_id:
                conditions.append("agent_id = %s")
                params.append(agent_id)
            
            if session_id:
                conditions.append("session_id = %s")
                params.append(session_id)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Build query
            if query:
                # Use full-text search with ranking
                select_sql = f"""
                SELECT *, ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) as rank
                FROM memories 
                WHERE {where_clause}
                ORDER BY rank DESC, timestamp DESC
                LIMIT %s
                """
                params.insert(0, query)  # Add query at the beginning for ts_rank
            else:
                select_sql = f"""
                SELECT * FROM memories 
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT %s
                """
            
            params.append(limit)
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(select_sql, params)
                    rows = cursor.fetchall()
                    
                    memories = []
                    for row in rows:
                        memory = self._row_to_memory(row)
                        if memory:
                            memories.append(memory)
                    
                    return memories
        except Exception as e:
            print(f"Error searching memories in PostgreSQL: {e}")
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
            conditions = []
            params = []
            
            if agent_id:
                conditions.append("agent_id = %s")
                params.append(agent_id)
            
            if start_time:
                conditions.append("timestamp >= %s")
                params.append(start_time)
            
            if end_time:
                conditions.append("timestamp <= %s")
                params.append(end_time)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            select_sql = f"""
            SELECT * FROM memories 
            WHERE {where_clause}
            ORDER BY timestamp ASC
            LIMIT %s
            """
            params.append(limit)
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(select_sql, params)
                    rows = cursor.fetchall()
                    
                    memories = []
                    for row in rows:
                        memory = self._row_to_memory(row)
                        if memory:
                            memories.append(memory)
                    
                    return memories
        except Exception as e:
            print(f"Error getting timeline from PostgreSQL: {e}")
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
            delete_sql = "DELETE FROM memories WHERE id = %s"
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(delete_sql, (memory_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting memory from PostgreSQL: {e}")
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
    
    def _row_to_memory(self, row: Dict[str, Any]) -> MemoryEntry:
        """Convert database row to MemoryEntry"""
        try:
            return MemoryEntry(
                id=row['id'],
                content=row['content'],
                memory_type=MemoryType(row['memory_type']),
                agent_id=row['agent_id'],
                session_id=row['session_id'],
                timestamp=row['timestamp'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {},
                embedding=json.loads(row['embedding']) if row['embedding'] else None,
                importance=float(row['importance']),
                tags=json.loads(row['tags']) if row['tags'] else [],
                last_accessed=row['last_accessed']
            )
        except Exception as e:
            print(f"Error converting row to memory: {e}")
            return None 