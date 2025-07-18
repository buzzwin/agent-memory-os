import os
from typing import Optional, Dict, Any, List
from .base_store import BaseStore
from .sqlite_store import SQLiteStore
from .pinecone_store import PineconeStore
from .postgresql_store import PostgreSQLStore


class StoreFactory:
    """Factory class for creating different types of memory stores."""
    
    @staticmethod
    def create_store(store_type: Optional[str] = None, **kwargs) -> BaseStore:
        """
        Create a store instance based on the specified type.
        
        Args:
            store_type: Type of store to create ('sqlite', 'pinecone', 'postgresql', or None for default)
            **kwargs: Additional arguments to pass to the store constructor
            
        Returns:
            BaseStore: Instance of the specified store type
            
        Raises:
            ValueError: If store_type is not supported
        """
        # Default to sqlite if no store_type provided
        if store_type is None:
            store_type = "sqlite"
        
        store_type = store_type.lower()
        
        if store_type == 'sqlite':
            return SQLiteStore(**kwargs)
        elif store_type == 'pinecone':
            return PineconeStore(**kwargs)
        elif store_type == 'postgresql':
            return PostgreSQLStore(**kwargs)
        else:
            raise ValueError(f"Unsupported store type: {store_type}. "
                           f"Supported types: sqlite, pinecone, postgresql")
    
    @staticmethod
    def get_available_stores() -> List[str]:
        """
        Get list of available store types.
        
        Returns:
            List of available store type names
        """
        return ["sqlite", "pinecone", "postgresql"]
    
    @staticmethod
    def create_store_from_env() -> BaseStore:
        """
        Create a store instance based on environment variables.
        
        Environment variables:
        - MEMORY_STORE_TYPE: Type of store ('sqlite', 'pinecone', 'postgresql')
        - PINECONE_API_KEY: Pinecone API key (for pinecone store)
        - PINECONE_ENVIRONMENT: Pinecone environment (for pinecone store)
        - DATABASE_URL: Database URL (for postgresql store)
        
        Returns:
            BaseStore: Instance of the specified store type
            
        Raises:
            ValueError: If MEMORY_STORE_TYPE is not set or not supported
        """
        store_type = os.getenv("MEMORY_STORE_TYPE", "sqlite")
        return StoreFactory.create_store(store_type)
