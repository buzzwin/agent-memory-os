"""
Store factory for Agent Memory OS

Creates appropriate storage backends based on configuration.
"""

import os
from typing import Optional

from .base_store import BaseStore
from .sqlite_store import SQLiteStore
from .pinecone_store import PineconeStore
from .postgresql_store import PostgreSQLStore


class StoreFactory:
    """Factory for creating storage backends"""
    
    @staticmethod
    def create_store(store_type: str = None, **kwargs) -> BaseStore:
        """
        Create a storage backend based on configuration
        
        Args:
            store_type: Type of store ('sqlite', 'pinecone', or None for auto-detect)
            **kwargs: Additional arguments for the store
            
        Returns:
            Configured storage backend
        """
        # Auto-detect store type if not specified
        if not store_type:
            if os.getenv("POSTGRESQL_HOST") or os.getenv("POSTGRESQL_CONNECTION_STRING"):
                store_type = "postgresql"
            elif os.getenv("PINECONE_API_KEY"):
                store_type = "pinecone"
            else:
                store_type = "sqlite"
        
        store_type = store_type.lower()
        
        if store_type == "sqlite":
            db_path = kwargs.get("db_path", "agent_memory.db")
            return SQLiteStore(db_path=db_path)
        
        elif store_type == "pinecone":
            api_key = kwargs.get("api_key")
            environment = kwargs.get("environment")
            index_name = kwargs.get("index_name", "agent-memory-os")
            return PineconeStore(
                api_key=api_key,
                environment=environment,
                index_name=index_name
            )
        
        elif store_type == "postgresql":
            connection_string = kwargs.get("connection_string")
            return PostgreSQLStore(connection_string=connection_string, **kwargs)
        
        else:
            raise ValueError(f"Unknown store type: {store_type}. Supported types: sqlite, pinecone, postgresql")
    
    @staticmethod
    def get_available_stores() -> list:
        """Get list of available store types"""
        stores = ["sqlite"]
        
        # Check if PostgreSQL is available
        try:
            import psycopg2
            if os.getenv("POSTGRESQL_HOST") or os.getenv("POSTGRESQL_CONNECTION_STRING"):
                stores.append("postgresql")
        except ImportError:
            pass
        
        # Check if Pinecone is available
        try:
            import pinecone
            if os.getenv("PINECONE_API_KEY"):
                stores.append("pinecone")
        except ImportError:
            pass
        
        return stores 