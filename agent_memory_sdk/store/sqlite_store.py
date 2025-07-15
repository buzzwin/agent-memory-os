"""
SQLite storage backend for Agent Memory OS

Provides persistent storage using SQLite database.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..models import MemoryEntry, MemoryType


class SQLiteStore:
    """SQLite-based storage backend for memory entries"""
    
    def __init__(self, db_path: str = "agent_memory.db"):
        """
        Initialize SQLite store
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            
            # Create indexes for better query performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
    
    def save_memory(self, memory: MemoryEntry) -> bool:
        """
        Save a memory entry to the database
        
        Args:
            memory: MemoryEntry to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories 
                    (id, content, memory_type, agent_id, session_id, timestamp, metadata, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    memory.content,
                    memory.memory_type.value,
                    memory.agent_id,
                    memory.session_id,
                    memory.timestamp.isoformat(),
                    json.dumps(memory.metadata),
                    json.dumps(memory.embedding) if memory.embedding else None
                ))
                return True
        except Exception as e:
            print(f"Error saving memory: {e}")
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, content, memory_type, agent_id, session_id, 
                           timestamp, metadata, embedding
                    FROM memories WHERE id = ?
                """, (memory_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_memory_entry(row)
                return None
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return None
    
    def search_memories(self, query: str = None, memory_type: Optional[MemoryType] = None,
                       agent_id: Optional[str] = None, session_id: Optional[str] = None,
                       limit: int = 50) -> List[MemoryEntry]:
        """
        Search for memories with various filters
        
        Args:
            query: Text search in content (simple LIKE search for now)
            memory_type: Filter by memory type
            agent_id: Filter by agent ID
            session_id: Filter by session ID
            limit: Maximum number of results
            
        Returns:
            List of matching MemoryEntry objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                sql = "SELECT id, content, memory_type, agent_id, session_id, timestamp, metadata, embedding FROM memories WHERE 1=1"
                params = []
                
                if query:
                    sql += " AND content LIKE ?"
                    params.append(f"%{query}%")
                
                if memory_type:
                    sql += " AND memory_type = ?"
                    params.append(memory_type.value)
                
                if agent_id:
                    sql += " AND agent_id = ?"
                    params.append(agent_id)
                
                if session_id:
                    sql += " AND session_id = ?"
                    params.append(session_id)
                
                sql += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(sql, params)
                return [self._row_to_memory_entry(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error searching memories: {e}")
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
            with sqlite3.connect(self.db_path) as conn:
                sql = "SELECT id, content, memory_type, agent_id, session_id, timestamp, metadata, embedding FROM memories WHERE 1=1"
                params = []
                
                if agent_id:
                    sql += " AND agent_id = ?"
                    params.append(agent_id)
                
                if start_time:
                    sql += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                
                if end_time:
                    sql += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                
                sql += " ORDER BY timestamp ASC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(sql, params)
                return [self._row_to_memory_entry(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting timeline: {e}")
            return []
    
    def _row_to_memory_entry(self, row) -> MemoryEntry:
        """Convert database row to MemoryEntry"""
        return MemoryEntry(
            id=row[0],
            content=row[1],
            memory_type=MemoryType(row[2]),
            agent_id=row[3],
            session_id=row[4],
            timestamp=datetime.fromisoformat(row[5]),
            metadata=json.loads(row[6]) if row[6] else {},
            embedding=json.loads(row[7]) if row[7] else None
        ) 