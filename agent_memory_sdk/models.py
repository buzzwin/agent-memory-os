"""
Data models for Agent Memory OS

Contains shared data structures to avoid circular imports.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid


class MemoryType(Enum):
    """Types of memory supported by the system"""
    EPISODIC = "episodic"  # Specific events/interactions
    SEMANTIC = "semantic"  # Facts/knowledge
    TEMPORAL = "temporal"  # Time-based events


@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    memory_type: MemoryType = MemoryType.EPISODIC
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    importance: float = 5.0  # Default importance score (0-10)
    tags: List[str] = field(default_factory=list)  # List of tags
    last_accessed: Optional[datetime] = None  # Last access timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "embedding": self.embedding,
            "importance": self.importance,
            "tags": self.tags,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create memory entry from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            agent_id=data.get("agent_id"),
            session_id=data.get("session_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
            importance=data.get("importance", 5.0),
            tags=data.get("tags", []),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None
        ) 